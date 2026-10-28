<!-- Generated from shared/. Do not edit directly. -->

# Parent QA

## Identity and inputs

Parent QA は direct / delegated の全 Unit に必須であり、親が acceptance oracle と最終裁定を所有する。親は Task Specification、comparison base、Acceptance Criteria、diff、evidence、surrounding context を固定し、同じ input variant 内で evidence identity を維持する。input variant が変わっても共通の parent oracle を維持する。

親は obligation、oracle、validation plane を確定し、reviewer の Pass や Implementer の report を Unit acceptance の根拠にしない。

## Baseline self-QA

meaningful Red または changed behavioral test の妥当性を acceptance evidence に使う場合だけ BMO を適用する。適用時は Expected Observation の導出前に、配布相対 path `../../../references/behavior-model-observation.md` を load し、identity `# Behavior Model Observation` と `Identity and boundary`、`Inputs and ownership`、`Method`、`Result contract`、`Stop boundary and reintegration` の各 section を検証する。load、identity、required section の不足・不一致では対象 evidence の QA を推測で続けず `stop-incomplete` とする。

resolved Behavior と評価対象から独立した authoritative context を BMO consumer input とし、Expected Observation と meaningful variation を評価対象の diff / test から逆算せず導出する。BMO が unresolved meaning を返した場合、親が authority を再解決できなければ accept しない。BMO は actual verification や verdict を所有しない。

mutation evidence は behavior、test、executable contract に applicable な場合だけ必須とする。親は検証方向と必要な evidence を選び、要求違反の変種では obligation の meaningful violation を対応する assertion が検出するか、正当変種では独立した要求・契約を満たす変更を誤拒否しないかを別々に確認する。正当性は対象 test や現実装だけから導出せず、provenance / 適用範囲と成立条件を保持する。outside-slice decoy が誤反応しないことも applicable な場合に確認する。

実行前に baseline と変種の exact target、byte / diff identity、owned dirty state、既知 failure、runner / command / environment / membership、対象 assertion と予測される観測、復元手順と復元確認を固定する。対象 assertion への到達と結果を追い、syntax / setup / runner / 環境 failure、別 Case の failure、未実行を対象の検出や誤拒否の実証と混同しない。復元後は同じ baseline identity と既知 failure に照らして再確認し、baseline が Green なら Green へ戻ったことを確認する。

すべての終了経路で、後続の修正・review・commit より前に baseline byte / diff と owned dirty state を復元して確認する。task-owned かつ安全に完全復元できる範囲だけを一時変更し、mutation-only test / fixture / helper / config / dependency を candidate / deliverable に含めない。復元が不明なら後続の write / commit を止め、状態の evidence を残して stop-incomplete とする。mutation が安全に適用不能なら、その理由と代替 evidence が acceptance に十分か親が裁定し、不足なら accept しない。恒久的な contract mutation test を作らない。

親は Expected Observation を automated test、Gunte predicate / contract、fixture / oracle、明示された場合の EVAL、または native inspection の適切な validation plane に対応させる。prose layout、reviewer Pass、test 数、Gunte check だけから semantics を推論しない。

changed test artifact は normal、boundary、error / exception、side-effect failure の applicable case、observable What、oracle independence、削除・skip・弱体化、mock / stub leakage を確認する。Gunte predicate は empty / overbroad slice、decoy、custom parser、Gunte 自身の projection / serialization / drift 保証との重複を避ける。

Parent QA は diff 全体について AC coverage、scope / exclude、responsibility boundary、dependencies、TDD evidence、side-effect safety、focused / related verification、baseline failure と未実行事項を一次確認する。missing evidence は reviewer で補わない。

Test Acceptance Gate は changed test artifact の追加観測であり、Parent QA を代替しない。obligation、oracle、validation plane、Expected Observation、necessary verification、mutation applicability と最終 adjudication は親が所有する。
