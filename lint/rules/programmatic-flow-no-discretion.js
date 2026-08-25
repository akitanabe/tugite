const { analyzeProgrammaticFlowDiscretion } = require("../programmatic-flow");
const { createProgrammaticFlowRule } = require("../textlint-rule");

module.exports = createProgrammaticFlowRule(analyzeProgrammaticFlowDiscretion);
