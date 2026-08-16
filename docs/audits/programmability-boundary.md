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

Union identity is `08c1f981e33cc835626f1c43267b851844c4934de2a2fa08bd29c66568cff303` over 985 stable semantic families. State identities hash ordered path/blob/line-count tuples; the union separately reconciles rule-family identity across baseline and final.

| state | deterministic-mechanized | deterministic-contract-only | autonomous | derived-duplicate | unclassified |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 65 | 589 | 329 | 42 | 0 |
| final | 66 | 591 | 329 | 42 | 0 |

## Classification and assurance

Classification was adjudicated by source responsibility and section semantics, not isolated words. `deterministic-mechanized` is limited to coherent metadata/Contract Data with an existing Gunte predicate or platform loader. `deterministic-contract-only` records its actual source paragraph/block, owner Action, section-specific inputs and interception, candidate separation, and why cross-workflow enforcement is deferred. `autonomous` is limited to sections whose responsibility is semantic/value/quality/risk selection among acceptable outcomes. `derived-duplicate` is limited to identified platform or worker role-local projections; its consumer and remaining canonical witness are explicit.

Cross-source readback reconciled platform invocation frontmatter and writable-scope worker handoffs as required projections. Similar-sounding parent/worker/reviewer rules remain distinct where owner, input, interception, or outcome responsibility differs; they are not collapsed by text equality. The Boundary predicate verifies policy identity, required fields, and coherent relation only. It does not prove runtime semantics or oracle absence.

## Parent-QA regression examples

- `plugins/codex/skills/install-custom-agents/SKILL.md:1-8` is one `deterministic-mechanized` frontmatter occurrence. `description: >-` is no longer a standalone rule.
- Wrapped prose is one variable-length occurrence; for example the installer step 2 obligation spans lines 18-19 instead of being split by physical wrapping.
- `shared/writable-scope-kernel.md:52-54` is one `deterministic-contract-only` occurrence: a parent-owned scope-change prohibition and canonical-boundary rule. It is not autonomous merely because the prose contains judgment terminology.

## Reconciliation and mutation evidence

The one-shot checker rebuilt both inventories, verified exact source-byte hashes, variable-length gap/overlap-free coverage, unique state occurrence IDs, required rule/context fields, contract-only details, derived consumer/witness data, and forward/reverse path reconciliation. Positive control: `PASS`. Deleting an occurrence and shortening a multi-line span each produce `coverage mismatch`. The checker was removed after generating this evidence; no persistent audit parser was added.

Boundary predicate evidence remains separate: initial missing span, required-field deletion, policy reversal, and span-external decoy each failed; unchanged Data passed. Gunte success is not used as the semantic classification oracle.

## Autonomous-oracle readback

Tracked-file and source/test inventory searches found no current decision corpus, runner, assertion artifact, or expected-output oracle fixing direct/delegate, worker/reviewer, finding adoption, approach, or risk outcome. Historical audit prose is excluded. This is point-in-time negative evidence, not a Gunte guarantee; EVAL was neither added nor run.

## Residual risk

Editorial atomicity and classification remain human-reviewable evidence rather than machine-proven semantics. Physical lines containing multiple coordinated clauses cannot be subdivided without overlapping line coordinates and therefore remain one documented occurrence. Future source changes make this audit stale. Contract-only rules remain dependent on their named owner Actions.
