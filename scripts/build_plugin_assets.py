#!/usr/bin/env python3
"""Generate Claude and Codex plugin assets from the shared sources."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
PLATFORMS = ("claude", "codex")
# Skill name -> ordered reference names. Adding one entry makes a new skill
# directory a generation target; an empty tuple describes a SKILL.md-only skill.
SKILL_REFERENCE_NAMES = {
    "impl-delegate": (),
    "impl-lead-v5": (),
    "impl-lead": (
        "implementation-branches.md",
        "expert-selection.md",
        "qa-and-integration.md",
        "reviewer-dispatch.md",
        "branch-review.md",
        "finding-routing.md",
        "run-closeout.md",
        "qa-report.md",
        "branch-plan-intake.md",
        "reviewer-findings.md",
    ),
    "branch-design": (
        "branch-plan-schema.md",
        "branch-splitting.md",
        "plan-review.md",
    ),
    "test-audit": (
        "test-inventory-schema.md",
        "gap-catalog.md",
        "suite-scan.md",
        "inventory-report.md",
    ),
    "plan-craft": (
        "plan-artifacts.md",
        "plan-drafting.md",
        "adversarial-review.md",
        "overengineering-plan-review.md",
    ),
    "feature-lead": (),
}
TERM_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
PLACEHOLDER_PATTERN = re.compile(r"\{\{([^{}\n]+)\}\}")
MARKER_LIKE_PATTERN = re.compile(
    r"<!--\s*[A-Za-z0-9_-]+-only(?:\s*:\s*[A-Za-z0-9_-]*)?\s*-->"
)
MARKERS = {
    "<!-- claude-only:start -->": ("claude", "start"),
    "<!-- claude-only:end -->": ("claude", "end"),
    "<!-- codex-only:start -->": ("codex", "start"),
    "<!-- codex-only:end -->": ("codex", "end"),
}
MARKDOWN_WARNING = "<!-- Generated from shared/. Do not edit directly. -->"
TOML_WARNING = "# Generated from shared/. Do not edit directly."


@dataclass(frozen=True)
class Diagnostic:
    """Describe one user-correctable input validation error."""

    path: Path
    message: str
    line: int | None = None

    def format(self, root: Path) -> str:
        """Format a stable repository-relative diagnostic for stderr."""
        try:
            display_path = self.path.relative_to(root).as_posix()
        except ValueError:
            display_path = self.path.as_posix()
        location = f"{display_path}:{self.line}" if self.line is not None else display_path
        return f"{location}: {self.message}"


@dataclass(frozen=True)
class SkillSource:
    """Hold one skill's SKILL.md and its mapped reference sources."""

    name: str
    path: Path
    content: str | None
    references: dict[str, tuple[Path, str]]


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    """Parse the documented generator command-line options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="report generated files that are missing or out of date",
    )
    return parser.parse_args(argv)


def read_source(path: Path, errors: list[Diagnostic]) -> str | None:
    """Read one required UTF-8 source and record a concise failure."""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(Diagnostic(path, "required file is missing"))
    except UnicodeDecodeError as error:
        errors.append(Diagnostic(path, f"file is not valid UTF-8: {error}"))
    except OSError as error:
        errors.append(Diagnostic(path, f"cannot read file: {error}"))
    return None


def toml_error_line(error: tomllib.TOMLDecodeError) -> int | None:
    """Extract a TOML parser line number across supported Python versions."""
    line = getattr(error, "lineno", None)
    if isinstance(line, int):
        return line
    match = re.search(r"at line (\d+)", str(error))
    return int(match.group(1)) if match else None


def load_terms(root: Path, errors: list[Diagnostic]) -> dict[str, dict[str, str]]:
    """Load and validate the non-recursive platform term table."""
    path = root / "shared/terms.toml"
    content = read_source(path, errors)
    if content is None:
        return {}
    try:
        document = tomllib.loads(content)
    except tomllib.TOMLDecodeError as error:
        errors.append(Diagnostic(path, f"invalid TOML: {error}", toml_error_line(error)))
        return {}
    if set(document) != {"terms"} or not isinstance(document.get("terms"), dict):
        errors.append(Diagnostic(path, "expected only [terms.<name>] tables"))
        return {}

    validated: dict[str, dict[str, str]] = {}
    for name, values in document["terms"].items():
        if TERM_NAME_PATTERN.fullmatch(name) is None:
            errors.append(Diagnostic(path, f"invalid term name: {name}"))
            continue
        if not isinstance(values, dict):
            errors.append(Diagnostic(path, f"term {name} must be a table"))
            continue
        unknown = sorted(set(values) - set(PLATFORMS))
        missing = sorted(set(PLATFORMS) - set(values))
        for key in unknown:
            errors.append(Diagnostic(path, f"term {name} has unknown key: {key}"))
        for platform in missing:
            errors.append(Diagnostic(path, f"term {name} is missing {platform}"))
        term_values: dict[str, str] = {}
        for platform in PLATFORMS:
            value = values.get(platform)
            if not isinstance(value, str):
                if platform in values:
                    errors.append(Diagnostic(path, f"term {name}.{platform} must be a string"))
                continue
            if not value or "\n" in value or "\r" in value:
                errors.append(
                    Diagnostic(path, f"term {name}.{platform} must be a non-empty single line")
                )
                continue
            term_values[platform] = value
        if not unknown and not missing and len(term_values) == len(PLATFORMS):
            validated[name] = term_values
    return validated


def load_skills(root: Path, errors: list[Diagnostic]) -> list[SkillSource]:
    """Reject unregistered skill directories and load every mapped skill source."""
    skill_root = root / "shared/skill"
    if skill_root.is_dir():
        for path in sorted(skill_root.iterdir()):
            if path.is_dir() and path.name not in SKILL_REFERENCE_NAMES:
                errors.append(Diagnostic(path, "unknown shared skill directory"))

    skills: list[SkillSource] = []
    for skill_name, reference_names in SKILL_REFERENCE_NAMES.items():
        skill_directory = skill_root / skill_name
        if skill_directory.is_dir():
            for path in sorted(skill_directory.glob("*.md")):
                if path.name != "SKILL.md":
                    errors.append(Diagnostic(path, "unknown shared skill Markdown file"))

        references_directory = skill_directory / "references"
        if references_directory.is_dir():
            expected = set(reference_names)
            for path in sorted(references_directory.glob("*.md")):
                if path.name not in expected:
                    errors.append(
                        Diagnostic(path, "unknown shared skill reference Markdown file")
                    )

        skill_path = skill_directory / "SKILL.md"
        content = read_source(skill_path, errors)
        references: dict[str, tuple[Path, str]] = {}
        for name in reference_names:
            reference_path = references_directory / name
            reference_content = read_source(reference_path, errors)
            if reference_content is not None:
                references[name] = (reference_path, reference_content)
        skills.append(SkillSource(skill_name, skill_path, content, references))
    return skills


def process_markers(
    path: Path,
    content: str,
    start_line: int,
    errors: list[Diagnostic],
) -> dict[str, str]:
    """Validate platform markers once and render both selected line streams."""
    rendered: dict[str, list[str]] = {platform: [] for platform in PLATFORMS}
    active: tuple[str, int] | None = None
    for offset, line in enumerate(content.splitlines(keepends=True)):
        line_number = start_line + offset
        stripped = line.strip()
        marker = MARKERS.get(stripped)
        if marker is None:
            if MARKER_LIKE_PATTERN.search(line):
                errors.append(
                    Diagnostic(path, "platform marker must be a known marker on its own line", line_number)
                )
            if active is None:
                for platform in PLATFORMS:
                    rendered[platform].append(line)
            else:
                rendered[active[0]].append(line)
            continue

        platform, action = marker
        if action == "start":
            if active is not None:
                errors.append(Diagnostic(path, "platform markers must not be nested", line_number))
            else:
                active = (platform, line_number)
        elif active is None:
            errors.append(Diagnostic(path, "platform end marker has no matching start", line_number))
        elif active[0] != platform:
            errors.append(Diagnostic(path, "platform end marker does not match its start", line_number))
            active = None
        else:
            active = None
    if active is not None:
        errors.append(Diagnostic(path, "platform marker is not closed", active[1]))
    return {platform: "".join(lines) for platform, lines in rendered.items()}


def validate_placeholders(
    path: Path,
    content: str,
    start_line: int,
    terms: dict[str, dict[str, str]],
    used_terms: set[str],
    errors: list[Diagnostic],
) -> None:
    """Validate raw placeholders and record every referenced defined term."""
    for match in PLACEHOLDER_PATTERN.finditer(content):
        name = match.group(1)
        line = start_line + content.count("\n", 0, match.start())
        if TERM_NAME_PATTERN.fullmatch(name) is None:
            errors.append(Diagnostic(path, f"invalid placeholder name: {name}", line))
        elif name not in terms:
            errors.append(Diagnostic(path, f"undefined placeholder: {name}", line))
        else:
            used_terms.add(name)


def replace_terms(content: str, platform: str, terms: dict[str, dict[str, str]]) -> str:
    """Replace placeholders once without recursively scanning inserted values."""
    return PLACEHOLDER_PATTERN.sub(
        lambda match: terms[match.group(1)][platform],
        content,
    )


def normalize_body(body: str) -> str:
    """Remove the frontmatter separator newline and ensure one final newline."""
    if body.startswith("\r\n"):
        body = body[2:]
    elif body.startswith("\n"):
        body = body[1:]
    return body.rstrip("\r\n") + "\n"


def render_skill(
    path: Path,
    platform: str,
    content: str,
    errors: list[Diagnostic],
) -> str | None:
    """Validate rendered YAML frontmatter/body and insert the generated warning."""
    lines = content.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        errors.append(Diagnostic(path, f"{platform} skill must start with YAML frontmatter", 1))
        return None
    closing_index = next(
        (index for index, line in enumerate(lines[1:], 1) if line.rstrip("\r\n") == "---"),
        None,
    )
    if closing_index is None:
        errors.append(Diagnostic(path, f"{platform} skill YAML frontmatter is not closed", 1))
        return None
    body = "".join(lines[closing_index + 1 :])
    if not body.strip():
        errors.append(Diagnostic(path, f"{platform} skill Markdown body must not be empty"))
        return None
    frontmatter = "".join(lines[: closing_index + 1])
    return ensure_text(frontmatter + MARKDOWN_WARNING + "\n" + body)


def render_skill_reference(
    path: Path,
    platform: str,
    content: str,
    errors: list[Diagnostic],
) -> str | None:
    """Validate one rendered reference body and add the generated warning."""
    if not content.strip():
        errors.append(
            Diagnostic(path, f"{platform} skill reference Markdown body must not be empty")
        )
        return None
    return ensure_text(f"{MARKDOWN_WARNING}\n\n{normalize_body(content)}")


def ensure_text(content: str) -> str:
    """Normalize generated text to LF with exactly one trailing newline."""
    return content.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n") + "\n"


def build_outputs(root: Path) -> tuple[dict[Path, str], list[Diagnostic]]:
    """Validate every input and construct the complete generated output map."""
    errors: list[Diagnostic] = []
    terms = load_terms(root, errors)
    skills = load_skills(root, errors)

    skill_rendered: dict[str, dict[str, str]] = {}
    reference_rendered: dict[str, dict[str, dict[str, str]]] = {}
    used_terms: set[str] = set()
    for skill in skills:
        if skill.content is not None:
            validate_placeholders(skill.path, skill.content, 1, terms, used_terms, errors)
            skill_rendered[skill.name] = process_markers(skill.path, skill.content, 1, errors)
        reference_rendered[skill.name] = {}
        for name, (path, content) in skill.references.items():
            validate_placeholders(path, content, 1, terms, used_terms, errors)
            reference_rendered[skill.name][name] = process_markers(path, content, 1, errors)

    terms_path = root / "shared/terms.toml"
    for name in sorted(set(terms) - used_terms):
        errors.append(Diagnostic(terms_path, f"unused term: {name}"))

    if errors:
        return {}, errors

    outputs: dict[Path, str] = {}
    for platform in PLATFORMS:
        for skill in skills:
            replaced = replace_terms(skill_rendered[skill.name][platform], platform, terms)
            rendered = render_skill(skill.path, platform, replaced, errors)
            if rendered is not None:
                outputs[
                    root / f"plugins/{platform}/skills/{skill.name}/SKILL.md"
                ] = rendered
            for name, (path, _) in skill.references.items():
                replaced_reference = replace_terms(
                    reference_rendered[skill.name][name][platform],
                    platform,
                    terms,
                )
                rendered_reference = render_skill_reference(
                    path,
                    platform,
                    replaced_reference,
                    errors,
                )
                if rendered_reference is not None:
                    outputs[
                        root
                        / f"plugins/{platform}/skills/{skill.name}/references/{name}"
                    ] = rendered_reference

    if errors:
        return {}, errors
    return outputs, []


def relative_path(path: Path, root: Path) -> str:
    """Return a stable repository-relative output path."""
    return path.relative_to(root).as_posix()


def check_outputs(root: Path, outputs: dict[Path, str]) -> int:
    """Compare every generated file without changing the filesystem."""
    mismatches: list[Path] = []
    for path, expected in sorted(outputs.items()):
        try:
            actual = path.read_bytes()
        except FileNotFoundError:
            actual = None
        if actual != expected.encode("utf-8"):
            mismatches.append(path)
    if mismatches:
        for path in mismatches:
            print(f"out of date: {relative_path(path, root)}", file=sys.stderr)
        return 1
    print("plugin assets are up to date")
    return 0


def write_outputs(root: Path, outputs: dict[Path, str]) -> int:
    """Write only generated files whose UTF-8 bytes have changed."""
    updated: list[Path] = []
    for path, content in sorted(outputs.items()):
        encoded = content.encode("utf-8")
        try:
            current = path.read_bytes()
        except FileNotFoundError:
            current = None
        if current == encoded:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        updated.append(path)
    if updated:
        for path in updated:
            print(f"updated: {relative_path(path, root)}")
    else:
        print("plugin assets are up to date")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Validate, render, then either compare or write the complete asset set."""
    arguments = parse_arguments(sys.argv[1:] if argv is None else argv)
    outputs, errors = build_outputs(ROOT)
    if errors:
        for error in errors:
            print(error.format(ROOT), file=sys.stderr)
        return 1
    if arguments.check:
        return check_outputs(ROOT, outputs)
    return write_outputs(ROOT, outputs)


if __name__ == "__main__":
    raise SystemExit(main())
