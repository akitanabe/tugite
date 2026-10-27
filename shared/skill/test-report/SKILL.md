<!-- @only claude -->
---
name: test-report
description: >-
  ユーザーが `test-report` を明示した場合、または指定範囲のテスト群の理解・把握を求める意図が明確な場合に使う。
  指定範囲の全体像と振る舞い別詳細、根拠付きの静的診断、未確定事項を報告し、検証・修復する対象の判断を支える。
---
<!-- @/only -->
<!-- @only codex -->
---
name: test-report
description: >-
  ユーザーが `test-report` を明示した場合、または指定範囲のテスト群の理解・把握を求める意図が明確な場合に使う。
  指定範囲の全体像と振る舞い別詳細、根拠付きの静的診断、未確定事項を報告し、検証・修復する対象の判断を支える。
---
<!-- @/only -->
<!-- @only cursor -->
---
name: test-report
description: >-
  ユーザーが `test-report` を明示した場合、または指定範囲のテスト群の理解・把握を求める意図が明確な場合に使う。
  指定範囲の全体像と振る舞い別詳細、根拠付きの静的診断、未確定事項を報告し、検証・修復する対象の判断を支える。
---
<!-- @/only -->

# test-report

<!-- @contract test-report-trigger -->
`test-report` の明示指定、または bounded test scope のテスト群を理解・把握したいことが明確な request で開始します。
<!-- @/contract -->

<!-- @contract test-report-responsibility -->
指定範囲のテスト群について、全体像、振る舞い別詳細、根拠付きの静的診断、未確定事項を提示する public Skill です。検証・修復する対象の判断を支え、実行と修復は明示起動された `test-verify` が所有します。
<!-- @/contract -->

## Inputs and ownership

入力は request、repository / ref、source / test / config、要求・仕様と Context、bounded scope、requested report、明示された destination / write authority です。path / directory と機能・領域の自然言語指定を受け付けます。

<!-- @contract test-report-ownership -->
一回の invocation に対して exactly one の task-local Local Model を所有し、scope resolution、static read、Topology input、static diagnosis、report projection に同じ Model を利用します。
<!-- @/contract -->

生成された Skill からの参照は各 platform の generated path を基準に解決します。

- `../../references/model-construction.md`
- `../../references/agentic-model-construction.md`
- `../../references/verification-topology.md`
- `references/observation-and-diagnosis.md`：観測、診断、詳細出力の観点

## Scope and static observation

<!-- @contract test-report-agentic-first -->
Agentic Model Construction を first route とし、repository / source の静的観測から bounded scope、要求・Context、test / target-code membership、runner / config の acquisition scope と根拠を Agent-side で先に決めます。
<!-- @/contract -->

<!-- @contract test-report-local-confirmation -->
bounded な分解・再観測後に残る material gap の fact、scope intent、authority、または部分観測で継続する判断が Human-owned の場合だけ局所確認し、response を同じ Local Model へ reintegrate します。
<!-- @/contract -->

<!-- @contract test-report-limitation-boundary -->
Human-owned でない取得不能や不確かさは Human の選択で埋めず、試した解消経路と limitation を保持します。方向・範囲・意味を確定できなければ qualified な部分報告で停止します。確認によって scope / write authority を暗黙に広げません。
<!-- @/contract -->

<!-- @contract test-report-acquisition-scope -->
resolved-scope Data は bounded test membership、target-code units、要求・Context の read scope、必要な observation surface と根拠を保持します。これは取得範囲の決定であり、Behavior grounding や semantic precedence の最終解決ではありません。
<!-- @/contract -->

決定した membership を `references/observation-and-diagnosis.md` に従って静的に読み、条件、実際の assertion、config facts、source location を取得します。

<!-- @contract test-report-completeness -->
resolved set と observed set の一覧差から completeness を判定し、両 membership と根拠を出力まで保持します。未読 member は再観測を試し、残れば明示します。未読を含む scope の absence を主張しません。
<!-- @/contract -->

<!-- @contract test-report-zero-tests -->
解決済み test scope が zero tests である結果と、scope 自体を解決できない結果を区別します。zero tests でも要求側の候補と観測限界を保持します。
<!-- @/contract -->

## Verification Topology

<!-- @contract test-report-requirement-derived-candidates -->
要求・仕様と authoritative Context の意味からも Behavior candidate を構成し、既存 test に現れる振る舞いだけを母集団にしません。対象 test は discovery signal、Case、Evidence、scope fact とし、自身の Behavior / Expected Observation の正当性の根拠にはしません。
<!-- @/contract -->

<!-- @contract test-report-topology-input -->
Behavior / Context candidate、provenance と適用範囲、Case / Evidence / config facts、resolved / observed membership と completeness basis、source location を consumer input として準備します。要求側の未解決点と test-only candidate も失わずに渡します。
<!-- @/contract -->

<!-- @contract test-report-topology-method -->
consumer input を唯一の grounding・対応関係の正本である `Verification Topology` Method に渡し、Topology Data を同じ Local Model へ reintegrate します。grounding、precedence、Expected Observation、correspondence、execution state、absence の意味を変更しません。
<!-- @/contract -->

## Static diagnosis

<!-- @contract test-report-diagnosis -->
Topology と観測した要求・test・source・config の根拠を照合し、静的に確認できた問題、実行確認が必要な疑い、判断材料の不足を区別します。各指摘に選択用の識別子、確認状態、根拠と location、見逃しうる問題、次に確認する点を残します。診断は `references/observation-and-diagnosis.md` に従い、静的診断を runtime 実証として扱いません。
<!-- @/contract -->

<!-- @contract test-report-static-boundary -->
test、target code、source、CI を実行せず、source / test / config の修正や remediation、`test-verify` への自動遷移を行いません。次に確認する点の提示は実行・修復の許可ではありません。
<!-- @/contract -->

## Report and handoff

<!-- @contract test-report-full-scope-details -->
概要だけで終了せず、問題のない箇所も含む observed scope 全体の Behavior → Expected Observation ↔ Case → Evidence を辿れる詳細を提示します。正常・境界・異常の観測された条件、実際の assertion、source location、未対応 Evidence、要求側の evidence gap、観測限界を保持します。優先度は表示順に使い、詳細を省く理由にしません。
<!-- @/contract -->

<!-- @contract test-report-case-relation-preservation -->
Case の意味的シナリオ単位と Expected Observation ↔ Case の many-to-many relation を保持し、function / file 単位に平坦化しません。framework、runner、suite、test level は scope と traceability の補助情報です。
<!-- @/contract -->

<!-- @contract test-report-output -->
観測した repository / ref、resolved / observed scope、要求根拠、Behavior、Expected Observation、Case / Evidence の参照先、execution state、対応不明、scope-relative absence、導出・grounding・観測限界と診断を出力します。未読、未実行、skip、対応不明、証拠なしは別の状態として残します。
<!-- @/contract -->

<!-- @contract test-report-handoff -->
report 全体または識別子で選択した指摘を、Human が `test-verify` の入力にできます。report は事前実行の必須要件ではなく、直接の bounded target も verify の入口です。引き継ぎはこの report と参照先で足り、専用台帳や巨大な中間成果物を要求しません。
<!-- @/contract -->

<!-- @contract test-report-human-facing-projection -->
report candidate を確定後、`../../references/human-facing-projection.md` の Final output boundary を適用します。observed scope 全体の詳細、診断の確認状態、qualification、relation、source location と write authority を保持して出力前に確認します。
<!-- @/contract -->

固定 heading、table、tree、report schema は要求しません。長い場合も概要から全文の詳細へ辿れる構成にし、詳細を単なる作成予定にしません。

<!-- @contract test-report-write-boundary -->
明示された destination と write authority がある場合だけ report artifact をその範囲へ書きます。report のために source、test、config、無関係 artifact を変更しません。
<!-- @/contract -->

<!-- @contract test-report-default-output -->
既定では one-shot response を返します。
<!-- @/contract -->

## Completion and stop

scope と観測限界を明示し、observed scope 全体の詳細と診断を traceable に返せたら終了します。未取得の範囲や未確定事項は解消済みとせず部分報告に残します。要求・根拠不足から独立 grounding できない場合も、取得した Case / Evidence を捨てず、判定不能な理由を返します。
