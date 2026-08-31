# Parent QA

## Identity and inputs

Parent QA は direct / delegated の全 Unit に必須であり、親が acceptance oracle と最終裁定を所有する。親は Task Specification、comparison base、Acceptance Criteria、diff、evidence、surrounding context を固定し、同じ input variant 内で evidence identity を維持する。input variant が変わっても共通の parent oracle を維持する。

<!-- @contract impl-lead-parent-qa -->
親は obligation、oracle、validation plane を確定し、reviewer の Pass や Implementer の report を Unit acceptance の根拠にしない。
<!-- @/contract -->

## Baseline self-QA

各 obligation の Expected Observation を導出する前に、配布相対 path `../../../references/behavior-model-observation.md` を load し、identity `# Behavior Model Observation` と `Identity and boundary`、`Inputs and ownership`、`Method`、`Result contract`、`Stop boundary and reintegration` の各 section を検証する。load、identity、required section の不足・不一致では Parent QA を推測で続けず `stop-incomplete` とする。

resolved Behavior と評価対象から独立した authoritative context を BMO consumer input とし、Expected Observation と meaningful variation を評価対象の diff / test から逆算せず導出する。BMO が unresolved meaning を返した場合、親が authority を再解決できなければ accept しない。BMO は actual verification や verdict を所有しない。

親は Expected Observation を automated test、Gunte predicate / contract、fixture / oracle、明示された場合の EVAL、または native inspection の適切な validation plane に対応させる。prose layout、reviewer Pass、test 数、Gunte check だけから semantics を推論しない。

changed test artifact は normal、boundary、error / exception、side-effect failure の applicable case、observable What、oracle independence、削除・skip・弱体化、mock / stub leakage を確認する。Gunte predicate は empty / overbroad slice、decoy、custom parser、Gunte 自身の projection / serialization / drift 保証との重複を避ける。

applicable mutation evidence を必須とする。obligation の meaningful violation が対応する artifact を fail させ、outside-slice decoy が誤反応せず、復元後に Green となることを確認する。mutation が安全に適用不能なら、その理由と代替 evidence が acceptance に十分か親が裁定し、不足なら accept しない。恒久的な contract mutation test を作らない。

Parent QA は diff 全体について AC coverage、scope / exclude、responsibility boundary、dependencies、TDD evidence、side-effect safety、focused / related verification、baseline failure と未実行事項を一次確認する。missing evidence は reviewer で補わない。
