<!-- Generated from shared/. Do not edit directly. -->

# Implementation Review

## Ownership and inputs

この共有 reference は impl-lead と impl-review のレビュー観点・適用条件・入力・指摘の扱いを所有する。
実装、Parent QA、受入、commit、修正・統合は caller の責務であり、この reference は開始しない。
caller は Task Spec、目的・制約、base、AC、同じ immutable diff / evidence identity、surrounding context、QA baseline と起動理由を渡す。
AGENTS.md の Test QA baseline を適用し、obligation、oracle、validation plane と最終判断は caller が所有する。reviewer は追加観測だけを返す。
Unit Data は impl-lead の追加 context であり、impl-review に Unit 分解を要求しない。不足する根拠は不足として保持する。

## Specialist selection

concrete risk が受入、external Action の可否、修正推奨を変え得る場合だけ specialized reviewer を選ぶ。generic checklist や inventory を理由に全員を起動しない。
責務境界は `responsibility-boundary-reviewer`、security / external side effect は `security-side-effect-reviewer`、static performance / resource は `static-performance-reviewer`、変更による過剰実装は `over-engineering-reviewer` に渡す。
writing review と changed-test coverage / validity は別の適用条件を持つ。

## Changed-test applicability and evidence

差分に automated test、fixture、oracle、executable test contract の追加・変更・削除があれば、`test-coverage-reviewer` と `test-validity-reviewer` の両方を適用する。
skip / assertion 弱体化、Gunte predicate / contract、EVAL case も含む。test-only は applicable、production-only / no-change は not-applicable で、既存テスト全体の再審査へ広げない。
not-applicable は実装のテストが十分という判定ではない。

共通 packet に changed artifact 一覧、Expected Observation、test execution evidence、mutation applicability と applicable mutation evidence、fixture の authoritative source と input consistency を確認する context を加える。
coverage は主に必要な observable behavior と test artifact の対応・欠落、要求違反でも成功する反例を観測する。validity は主に oracle の識別能力と、独立した契約を満たす正当変種でも失敗する反例を観測する。両者の専門観測を合わせて双方向を扱い、各 reviewer に双方の網羅を要求せず専門外の重要な発見も保持する。
要求・公開契約・互換性・非機能要求・authoritative Context の provenance / 適用範囲、反例の成立条件、counterevidence と確認状態を packet / finding に保持する。Case / Evidence のない欠落は要求側の根拠と bounded observed scope / completeness basis で示し、架空の参照を作らない。
framework / style の好みや固定 score は基準にしない。根拠不足を実行結果や reviewer Pass で補わない。
mutation applicability と evidence generation は execution / QA owner の責務であり、reviewer は mutation を実行しない。恒久的・常時の mutation testing を要求しない。

## Writing review

`writing-principles-reviewer` の観点で code の How、test の What、commit の Why、comment / DocBlock の Why Not と文書を確認する。
対象に含む commit がある場合はその message を渡す。未コミット対象のために commit を作る必要はない。impl-lead は自身の Completion Gate で candidate commit を用意する。

## Observation and finding handling

選んだ reviewer には同じ snapshot と必要な根拠・問いを渡し、fresh / context-isolated、read-only / report-only で観測させる。
fresh reviewer は `fork_turns = "none"` で起動する。
全結果を回収するまで target に writer を入れない。対象状態が変わった場合は影響を確認し、古い結果を現状態の完了証拠として使わない。
caller は各 finding を evidence、AC、scope、risk、rollback、verifiability、maintainability に照らして吟味し、重複・競合・依存を整理する。
裏付け不足、対象外、好みだけの指摘を必要な修正へ昇格させない。未解決の判断は未解決として残す。
reviewer Pass、finding 数、固定 round は受入・完了・正しさの証拠ではない。採用、修正、受入、再観測の実行は caller 固有の boundary に従う。
