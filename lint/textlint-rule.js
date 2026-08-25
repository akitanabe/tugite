const createProgrammaticFlowRule = (analyze) => (context) => ({
  [context.Syntax.Document]: (node) => {
    for (const finding of analyze(node, context.getSource(node))) {
      context.report(
        node,
        new context.RuleError(finding.message, {
          padding: context.locator.range(finding.range)
        })
      );
    }
  }
});

module.exports = { createProgrammaticFlowRule };
