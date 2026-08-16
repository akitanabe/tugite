# Programmability Boundary audit

> Point-in-time evidence (2026-08-16). Current workflow source owns rule meaning; this audit is not a registry or generation input.

## Inventory boundary and editorial method

Included: eight `shared/skill/*/SKILL.md` files, three skill references, twelve agents, four Kernels, `shared/repository-guidelines.md`, and the two platform-owned installer skills. Gunte-generated plugin projections, contracts/declarations/tests used only as assurance locators, and historical `docs/audits/issue-215-*` evidence are excluded to avoid double counting.

All 30 sources were read as Markdown/source documents. Each state is partitioned into variable-length semantic spans: one coherent frontmatter or structured Data block, one wrapped prose paragraph, one list obligation with its continuations, or context. Headings, blank separators, projection/contract markers, document-map prose, and illustrative Casebook examples are context with an explicit reason. A physical line containing coordinated clauses remains one indivisible occurrence and says so through its complete summary; line coverage is not used as a substitute for semantic classification.

## State identities and counts

| state | inventory identity | paths | lines | rule occurrences | context spans |
| --- | --- | ---: | ---: | ---: | ---: |
| baseline (`0d47f9730f24b549323136dbaf37ec591ad3eaf7`) | `fdd1ff9601406225c8a84e039fe96a666c1d9bb95cfbf4a45561d1e7f1bc8193` | 30 | 4619 | 1025 | 1517 |
| final (working-tree source set) | `cf7761126287431ae4ad404885110cc5b040165bc9f0aa3e8e2f39eed59c448b` | 30 | 4644 | 1028 | 1524 |

Union identity is `0f4883d8e72185e041709fbdf6262acf72723463392943fa4241fd976f569aae` over 999 stable semantic families. State identities hash ordered path/blob/line-count tuples; the union separately reconciles rule-family identity across baseline and final.

| state | deterministic-mechanized | deterministic-contract-only | autonomous | derived-duplicate | unclassified |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 65 | 621 | 311 | 28 | 0 |
| final | 66 | 623 | 311 | 28 | 0 |

## Classification and assurance

Classification was adjudicated by outcome determinacy and source responsibility, not isolated words or section membership. `deterministic-mechanized` is limited to coherent metadata/Contract Data with a named existing Gunte predicate/projector or platform loader; each row distinguishes mechanism owner and assurance limit. `deterministic-contract-only` records its actual Action, necessary Data, pre-Action interception point, concrete candidate Calculation, and occurrence-specific reason the current tree does not intercept it. `autonomous` is limited to semantic/value/quality/risk selection among multiple acceptable outcomes. `derived-duplicate` is limited to platform metadata projections whose consumer and exact same-state, same-family, non-derived canonical occurrence resolve.

Cross-source readback retained platform invocation frontmatter as projection but returned worker boundary and writable-scope handoff spans to contract-only where a canonical occurrence did not bear every role-local clause. Similar-sounding parent/worker/reviewer rules remain distinct where owner, input, interception, or outcome responsibility differs. The Boundary predicate verifies policy identity, required fields, and coherent relation only. It does not prove runtime semantics or oracle absence.

The contract-only packet identity check found 621 distinct owner/action/input/interception/candidate/defer packets for 621 baseline occurrences and 623 distinct packets for 623 final occurrences. This proves that no packet is byte-identical; it does not prove that every packet identifies the correct semantic responsibility. Representative installer rows separately model inventory observation, scope resolution, non-writing check, prior-check disposition, authorization, force execution, and restart/reload boundaries. Deterministic re-audit moved fixed numeric default/validation/error handling and the Japanese-output obligation out of `autonomous`.

## Parent-QA regression examples

- `plugins/codex/skills/install-custom-agents/SKILL.md:1-8` is one `deterministic-mechanized` frontmatter occurrence. `description: >-` is no longer a standalone rule.
- Wrapped prose is one variable-length occurrence; for example the installer step 2 obligation spans lines 18-19 instead of being split by physical wrapping.
- `shared/writable-scope-kernel.md:52-54` is one `deterministic-contract-only` occurrence: a parent-owned scope-change prohibition and canonical-boundary rule. It is not autonomous merely because the prose contains judgment terminology.

## Accepted limitation and v6 follow-up

This audit completes Issue #225 as a point-in-time, line-based inventory and establishes the Programmability Boundary policy, source ownership, assurance planes, and absence of an autonomous expected-output oracle. Its zero-gap and zero-unclassified counts describe structural line coverage; they do not prove that every semantic clause has the correct classification.

The baseline contains physical lines that join obligations from different sides of the boundary. In particular, `shared/skill/impl-lead/SKILL.md:165` ends the deterministic user-specified-route conflict rule and begins autonomous direct/delegate selection on the same line. The current non-overlapping line coordinates cannot represent those clauses as separate occurrences without changing the baseline blob. Review also identified fixed Calculations that may remain `autonomous`, including `shared/skill/plan-craft/SKILL.md:61-62` and `shared/skill/review-loop/SKILL.md:278-282`, and contract-only packets whose input/output responsibility needs further semantic readback.

These known limitations are accepted for Issue #225 rather than hidden by choosing an inaccurate single classification. [Issue #246](https://github.com/akitanabe/tugite/issues/246) owns clause-level coordinates, deterministic reclassification, packet correction, and the corresponding mutation evidence for v6. Until that follow-up is complete, this audit must not be used as a semantic-completeness oracle or as a basis for deleting natural-language source obligations.

## Reconciliation and mutation evidence

The one-shot checker rebuilt both inventories, verified exact source-byte hashes, variable-length gap/overlap-free coverage, unique state occurrence IDs, required rule/context fields, occurrence-specific contract-only details, and forward/reverse path reconciliation. Every derived witness resolves to a complete non-derived occurrence in the same state and family. Positive control: `PASS`; shortened, nonexistent, and different-family witness mutations each fail. Deleting an occurrence and shortening a multi-line span each produce `coverage mismatch`. The checker was removed after generating this evidence; no persistent audit parser was added.

Boundary predicate evidence remains separate: initial missing span, required-field deletion, policy reversal, and span-external decoy each failed; unchanged Data passed. Gunte success is not used as the semantic classification oracle.

## Autonomous-oracle readback

Tracked-file and source/test inventory searches found no current decision corpus, runner, assertion artifact, or expected-output oracle fixing direct/delegate, worker/reviewer, finding adoption, approach, or risk outcome. Historical audit prose is excluded. This is point-in-time negative evidence, not a Gunte guarantee; EVAL was neither added nor run.

## Residual risk

Editorial atomicity and classification remain human-reviewable evidence rather than machine-proven semantics. Physical lines containing multiple coordinated clauses cannot be subdivided without overlapping line coordinates and therefore remain one documented occurrence; known cross-boundary cases are tracked by Issue #246. Future source changes make this audit stale. Contract-only rules remain dependent on their named owner Actions, and packet uniqueness does not establish that every Action/Data/Calculation boundary is semantically correct.
