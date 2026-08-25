const assert = require("node:assert/strict");
const { mkdtemp, readFile, rm, writeFile } = require("node:fs/promises");
const { tmpdir } = require("node:os");
const { join, resolve } = require("node:path");
const { describe, it } = require("node:test");
const { pathToFileURL } = require("node:url");
const { parse } = require("@textlint/markdown-to-ast");
const {
  analyzeProgrammaticFlowDiscretion,
  analyzeProgrammaticFlowStructure
} = require("../lint/programmatic-flow");

const repositoryRoot = resolve(__dirname, "..");

const validFlow = (name = "dependency-routing", procedure = "入力 Data に対して固定条件を評価する。") => [
  "## Programmatic Flows",
  "",
  `### ${name}`,
  "",
  "Trigger: 親が固定判定を要求したとき。",
  "Inputs: 親確定 Data。",
  `Procedure: ${procedure}`,
  "Outcomes: `ready` または `blocked`。"
].join("\n");

const analyzeStructure = (source) => analyzeProgrammaticFlowStructure(parse(source), source);
const analyzeDiscretion = (source) => analyzeProgrammaticFlowDiscretion(parse(source), source);

const cliPromise = import(pathToFileURL(
  resolve(repositoryRoot, "node_modules/textlint/lib/src/cli.js")
).href).then(({ cli }) => cli);

const lint = async (source, filePath, ...extraArguments) => (await cliPromise).execute(
  [
    "node", "textlint",
    "--config", ".textlintrc.json",
    "--rulesdir", "lint/rules",
    "--format", "json",
    ...extraArguments,
    "--stdin",
    "--stdin-filename", filePath
  ],
  source
);

describe("Programmatic Flow structure", () => {
  it("accepts each required field exactly once in canonical order", () => {
    assert.deepEqual(analyzeStructure(validFlow()), []);
  });

  for (const [name, source, reason] of [
    ["missing", validFlow().replace("Inputs: 親確定 Data。\n", ""), "不足: Inputs"],
    ["duplicate", validFlow().replace("Procedure:", "Procedure: first\nProcedure:"), "重複: Procedure"],
    [
      "misordered",
      validFlow().replace(
        "Trigger: 親が固定判定を要求したとき。\nInputs: 親確定 Data。",
        "Inputs: 親確定 Data。\nTrigger: 親が固定判定を要求したとき。"
      ),
      "順序"
    ]
  ]) {
    it(`reports ${name} fields locally`, () => {
      const [finding] = analyzeStructure(source);

      assert.equal(analyzeStructure(source).length, 1);
      assert.match(finding.message, new RegExp(reason));
      assert.equal(source.slice(...finding.range), "### dependency-routing");
    });
  }

  it("does not complete one flow with fields from another flow", () => {
    const source = [
      validFlow("complete"),
      "",
      "### incomplete",
      "",
      "Trigger: x",
      "Inputs: y",
      "Outcomes: z"
    ].join("\n");
    const findings = analyzeStructure(source);

    assert.equal(findings.length, 1);
    assert.match(findings[0].message, /incomplete.*不足: Procedure/);
  });

  it("ignores intro prose, nested fields, code, and later sections", () => {
    const source = [
      "## Programmatic Flows",
      "",
      "Trigger: intro",
      "",
      "### nested-fields",
      "",
      "> Trigger: quoted",
      "",
      "- Inputs: listed",
      "",
      "```text",
      "Procedure: code",
      "```",
      "",
      "Outcomes: direct",
      "",
      "## Other",
      "",
      "### not-a-flow",
      "",
      "Trigger: x"
    ].join("\n");

    assert.match(analyzeStructure(source)[0].message, /不足: Trigger, Inputs, Procedure/);
  });

  it("requires exact H2, H3, and field line prefixes", () => {
    assert.deepEqual(analyzeStructure(validFlow().replace("## Programmatic Flows", "## Programmatic Flow")), []);
    assert.deepEqual(analyzeStructure(validFlow().replace("### dependency-routing", "#### dependency-routing")), []);
    const prefixed = validFlow().replace("Trigger:", " Trigger:").replace("Inputs:", "Inputs :");
    assert.match(analyzeStructure(prefixed)[0].message, /不足: Trigger, Inputs/);
  });
});

describe("Programmatic Flow discretion", () => {
  for (const procedure of [
    "必要に応じて方法を選ぶ。",
    "適切な方法を選択する。",
    "状況を見て判断する。",
    "Agent が妥当と考える場合は実行する。",
    "任意に候補を追加する。",
    "望ましい場合は候補を変更する。",
    "最適なものを選ぶ。"
  ]) {
    it(`reports explicit local discretion: ${procedure}`, () => {
      const source = validFlow("discretion", procedure);
      const [finding] = analyzeDiscretion(source);

      assert.equal(analyzeDiscretion(source).length, 1);
      assert.ok(procedure.includes(source.slice(...finding.range)));
    });
  }

  for (const procedure of [
    "必要に応じて方法を選ぶかは Agentic な親へ返す。",
    "必要に応じて方法を選ぶかを Flow 内で決めず、固定条件を評価する。",
    "判断結果を Data として返す。",
    "採否と裁定は親の責務である。",
    "Agent と Human を入力 Data に含める。"
  ]) {
    it(`does not report a boundary statement: ${procedure}`, () => {
      assert.deepEqual(analyzeDiscretion(validFlow("boundary", procedure)), []);
    });
  }

  it("checks only visible Procedure prose", () => {
    const outside = validFlow().replace(
      "Trigger: 親が固定判定を要求したとき。",
      "Trigger: 必要に応じて方法を選ぶ。"
    );
    const inline = validFlow("inline", "`必要に応じて方法を選ぶ` と記録する。");
    const comment = validFlow("comment", "<!-- 必要に応じて方法を選ぶ。 --> 固定結果を返す。");
    const fenced = `${validFlow("fenced")}\n\n\`\`\`text\nProcedure: 必要に応じて方法を選ぶ。\n\`\`\``;

    assert.deepEqual(analyzeDiscretion(outside), []);
    assert.deepEqual(analyzeDiscretion(inline), []);
    assert.deepEqual(analyzeDiscretion(comment), []);
    assert.deepEqual(analyzeDiscretion(fenced), []);
  });

  it("checks duplicate Procedure occurrences independently", () => {
    const source = validFlow("duplicate-procedure", "必要に応じて方法を選ぶ。")
      .replace("Outcomes:", "Procedure: 任意に候補を追加する。\nOutcomes:");

    assert.match(analyzeStructure(source)[0].message, /重複: Procedure/);
    assert.equal(analyzeDiscretion(source).length, 2);
  });
});

describe("Tugite textlint integration", () => {
  const missingField = [
    "## Programmatic Flows",
    "",
    "### malformed",
    "",
    "Trigger: x",
    "Procedure: 固定条件を評価する。",
    "Outcomes: z"
  ].join("\n");
  const discretionary = validFlow("discretion", "必要に応じて方法を選ぶ。");

  for (const filePath of ["shared/skill/example/SKILL.md", "shared/skill/example/references/flow.md"]) {
    it(`reports each Tugite rule for ${filePath}`, async () => {
      const structureStatus = await lint(missingField, filePath);
      const discretionStatus = await lint(discretionary, filePath);

      assert.equal(structureStatus, 1);
      assert.equal(discretionStatus, 1);
    });
  }

  it("accepts a known-good reference", async () => {
    const status = await lint(validFlow(), "shared/skill/example/references/flow.md");

    assert.equal(status, 0);
  });

  it("does not modify a malformed Flow during a fix run", async () => {
    const directory = await mkdtemp(join(tmpdir(), "tugite-flow-lint-"));
    const filePath = join(directory, "flow.md");
    try {
      await writeFile(filePath, discretionary, "utf8");
      const cli = await cliPromise;
      const status = await cli.execute(
        [
          "node", "textlint",
          "--config", ".textlintrc.json",
          "--rulesdir", "lint/rules",
          "--fix",
          filePath
        ]
      );

      assert.equal(status, 0);
      assert.equal(await readFile(filePath, "utf8"), discretionary);
    } finally {
      await rm(directory, { recursive: true, force: true });
    }
  });

  it("wires common and Tugite-local rules through lint:skills", async () => {
    const [packageJsonText, textlintConfigText] = await Promise.all([
      readFile(resolve(repositoryRoot, "package.json"), "utf8"),
      readFile(resolve(repositoryRoot, ".textlintrc.json"), "utf8")
    ]);
    const packageJson = JSON.parse(packageJsonText);
    const textlintConfig = JSON.parse(textlintConfigText);

    assert.equal(packageJson.scripts["lint:skills"], "textlint --rulesdir lint/rules");
    assert.equal(packageJson.devDependencies["@textlint/markdown-to-ast"], "15.8.0");
    assert.deepEqual(textlintConfig.rules, { "preset-skill-lint": true });
    await Promise.all([
      readFile(resolve(repositoryRoot, "lint/rules/programmatic-flow-fields.js")),
      readFile(resolve(repositoryRoot, "lint/rules/programmatic-flow-no-discretion.js"))
    ]);
  });
});
