const requiredFields = ["Trigger", "Inputs", "Procedure", "Outcomes"];

const hasChildren = (node) => "children" in node;

const collectVisibleText = (node) => {
  if (node.type === "Str") {
    return node.value;
  }
  if (!hasChildren(node)) {
    return "";
  }
  return node.children.map(collectVisibleText).join("");
};

const fieldsInParagraph = (paragraph, source) => {
  const paragraphSource = source.slice(...paragraph.range);
  const fields = [];
  const linePattern = /[^\r\n]*(?:\r?\n|$)/g;

  for (const match of paragraphSource.matchAll(linePattern)) {
    if (match[0].length === 0) {
      continue;
    }
    const line = match[0].replace(/\r?\n$/, "");
    const label = requiredFields.find((candidate) => line.startsWith(`${candidate}:`));
    if (label === undefined) {
      continue;
    }
    const lineStart = paragraph.range[0] + (match.index ?? 0);
    if (source.lastIndexOf("\n", lineStart - 1) + 1 !== lineStart) {
      continue;
    }
    const lineEnd = lineStart + line.length;
    fields.push({
      label,
      range: [lineStart, lineEnd],
      proseRange: [lineStart + label.length + 1, lineEnd],
      paragraph
    });
  }

  return fields;
};

const extractProgrammaticFlows = (document, source) => {
  const flows = [];
  let inProgrammaticFlows = false;
  let currentFlow;

  const finishCurrentFlow = () => {
    if (currentFlow !== undefined) {
      flows.push(currentFlow);
      currentFlow = undefined;
    }
  };

  for (const node of document.children) {
    if (node.type === "Header" && node.depth <= 2) {
      finishCurrentFlow();
      inProgrammaticFlows = node.depth === 2 && collectVisibleText(node) === "Programmatic Flows";
      continue;
    }
    if (!inProgrammaticFlows) {
      continue;
    }
    if (node.type === "Header" && node.depth === 3) {
      finishCurrentFlow();
      currentFlow = {
        name: collectVisibleText(node),
        headingRange: node.range,
        fields: []
      };
      continue;
    }
    if (currentFlow !== undefined && node.type === "Paragraph") {
      currentFlow.fields.push(...fieldsInParagraph(node, source));
    }
  }
  finishCurrentFlow();

  return flows;
};

const structureMessage = (flow) => {
  const counts = new Map(requiredFields.map((label) => [label, 0]));
  for (const field of flow.fields) {
    counts.set(field.label, counts.get(field.label) + 1);
  }
  const missing = requiredFields.filter((label) => counts.get(label) === 0);
  const duplicate = requiredFields.filter((label) => counts.get(label) > 1);
  const sequence = flow.fields.map(({ label }) => label);
  const hasCanonicalSequence = sequence.length === requiredFields.length
    && sequence.every((label, index) => label === requiredFields[index]);
  if (missing.length === 0 && duplicate.length === 0 && hasCanonicalSequence) {
    return undefined;
  }

  const reasons = [
    missing.length > 0 ? `不足: ${missing.join(", ")}` : undefined,
    duplicate.length > 0 ? `重複: ${duplicate.join(", ")}` : undefined,
    !hasCanonicalSequence && missing.length === 0 && duplicate.length === 0
      ? `順序: ${sequence.join(" → ")}`
      : undefined
  ].filter((reason) => reason !== undefined);
  return `Programmatic Flow "${flow.name}" の field 構造が不正です（${reasons.join(" / ")}）。`;
};

const analyzeProgrammaticFlowStructure = (document, source) => extractProgrammaticFlows(document, source)
  .flatMap((flow) => {
    const message = structureMessage(flow);
    return message === undefined ? [] : [{ message, range: flow.headingRange }];
  });

const visibleProse = (paragraph, range, source) => {
  const visibleRanges = [];
  const collect = (node) => {
    if (node.type === "Str") {
      const start = Math.max(node.range[0], range[0]);
      const end = Math.min(node.range[1], range[1]);
      if (start < end) {
        visibleRanges.push([start, end]);
      }
      return;
    }
    if (hasChildren(node)) {
      node.children.forEach(collect);
    }
  };
  paragraph.children.forEach(collect);
  visibleRanges.sort((left, right) => left[0] - right[0]);

  let cursor = range[0];
  let visible = "";
  for (const [start, end] of visibleRanges) {
    if (start < cursor) {
      continue;
    }
    visible += " ".repeat(start - cursor);
    visible += source.slice(start, end);
    cursor = end;
  }
  return visible + " ".repeat(range[1] - cursor);
};

const discretionPatterns = [
  /必要に応じて.{0,32}?(?:選ぶ|選択する|決める|決定する|判断する|採用する)/g,
  /(?:適切|最適)(?:な|に)?.{0,32}?(?:選ぶ|選択する|決める|決定する|判断する|採用する)/g,
  /状況を見て.{0,32}?(?:判断する|選ぶ|選択する|決める)/g,
  /Agent\s*が妥当と考える場合/g,
  /(?:任意に|望ましい場合(?:は)?).{0,32}?(?:実行する|選ぶ|選択する|決める|判断する|採用する|変更する|追加する|省略する)/g
];

const sentenceAround = (text, start, end) => {
  const previousStops = ["。", "！", "？"].map((mark) => text.lastIndexOf(mark, start - 1));
  const sentenceStart = Math.max(...previousStops) + 1;
  const nextStops = ["。", "！", "？"]
    .map((mark) => text.indexOf(mark, end))
    .filter((index) => index >= 0);
  const sentenceEnd = nextStops.length === 0 ? text.length : Math.min(...nextStops) + 1;
  return text.slice(sentenceStart, sentenceEnd);
};

const returnsDiscretion = (sentence) =>
  /(?:(?:Agentic\s*な)?親|Human|人間).{0,16}(?:へ|に).{0,12}(?:返す|委ねる|確認を求める)/.test(sentence);

const negatesLocalDiscretion = (sentence) =>
  /(?:決め|判断せ|判断し|選ば|選択せ|裁定せ|採用せ)(?:ず|ない)/.test(sentence);

const discretionRanges = (field, source) => {
  const prose = visibleProse(field.paragraph, field.proseRange, source);
  const ranges = [];

  for (const pattern of discretionPatterns) {
    pattern.lastIndex = 0;
    for (const match of prose.matchAll(pattern)) {
      const start = match.index ?? 0;
      const end = start + match[0].length;
      const sentence = sentenceAround(prose, start, end);
      if (!returnsDiscretion(sentence) && !negatesLocalDiscretion(sentence)) {
        ranges.push([field.proseRange[0] + start, field.proseRange[0] + end]);
      }
    }
  }

  return ranges
    .sort((left, right) => left[0] - right[0] || left[1] - right[1])
    .filter((range, index, sorted) => index === 0 || range[0] >= sorted[index - 1][1]);
};

const analyzeProgrammaticFlowDiscretion = (document, source) => extractProgrammaticFlows(document, source)
  .flatMap(({ fields }) => fields
    .filter(({ label }) => label === "Procedure")
    .flatMap((field) => discretionRanges(field, source)))
  .map((range) => ({
    message: "Programmatic Flow の Procedure に autonomous な裁量が含まれています。",
    range
  }));

module.exports = {
  analyzeProgrammaticFlowDiscretion,
  analyzeProgrammaticFlowStructure
};
