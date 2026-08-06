---
name: impl-lead
description: >-
  明示起動時だけ、親が一つ以上の Work Unit を正規化し、direct または各単位の worker を選び、
  必要な場合だけ risk-directed review を選び、必須の final writing gate、TDD と親 QA を経て accept または stop-incomplete で安全に閉じる v5 実装 loop。
---
<!-- Generated from shared/. Do not edit directly. -->

# Active v5 main

この skill はユーザーが `$impl-lead` を明示した場合だけ起動する。自然言語の作業内容、規模、現在の
context から暗黙に起動しない。起動後も、親が受け入れ判断と最終報告を保持する。単一 Work Unit の direct または
一名 worker という既存経路は保ちつつ、同じ run で複数単位を安全に処理できる。
`risk-directed review` は固定 phase や全作業の必須手順ではなく、親が具体的な risk と判断への影響を説明できる場合だけ実行する。
これは run を閉じる直前の必須 `final writing gate` とは別責務である。

## Intake and Work Unit normalization

親は実装を始める前に要求、対象 repository、現在の dirty state、基準状態を観測する。Issue または doc と対象
file、その周辺、呼び出し元・先、関連 test を読み、run の目的を一つ以上の Work Unit に正規化する。複数であること
だけを停止理由にしない。各単位は次の Work Unit Data を持つ。

- `id`: run 内で一意な識別子。
- `purpose`: 単一の目的。
- `acceptance_criteria`: 外部から観測可能で検証可能な Acceptance Criteria。
- `scope`: `change`（変更を許す範囲）と `exclude`（変更しない範囲）。
- `implementation_freedom`: worker に任せてよい局所判断。なければ空。
- `constraints`: ユーザー指定、互換性、依存、実行環境その他の制約。
- `depends_on`: Work Unit ID の依存と、外部・repository・environment の precondition を分けた記述。
- `verification`: AC ごとの native test、focused test、必要な最終 gate。

Work Unit は、単一 purpose、観測可能な完結成果、単独で Green になる検証、無関係な変更なしに accept/revert できる
変更集合（後続依存の cascade rollback は許す）、独立した副作用と rollback 境界をすべて満たすものとする。同じ
test でしか Green にならない過分割、片方だけでは invariant が成立しない分割、layer 横割りは統合する。価値の
ない共通依存は最初に価値を生む単位が所有する。

不足、矛盾、または scope を閉じられない状態が品質に影響する場合、推測で補わず必要な情報を親へ戻すか、理由・
未完了範囲・evidence・残存 risk を含む `stop-incomplete` とする。要求と repository の状態を観測せずに worker を
起動しない。既存の dirty/untracked は scope に含めず、勝手に変更・削除しない。

Work Unit Data は run 内一意の `id`、目的、AC、scope、implementation_freedom、constraints、depends_on、verification だけを
表す。worker、base、route、order、isolation、result は実行時の execution data として親が記録し、Work Unit の
意味を書き換えない。review goal、reviewer handoff、finding、QA result、persistence resource も Work Unit の意味ではなく
execution data として扱う。

### Optional work-unit design step

Intake または再正規化で分割、統合、責任境界、依存の設計が非自明な場合だけ、親は同じ context の内部工程として
`work-unit-design` の手順を任意に参照できる。返された `work_units`、分割／統合 signal、`blocking_gaps` は候補であり、
親が要求、AC、scope、既存 Work Unit、repository 状態を再検査してから採用する。候補の `acceptance_criteria` は accept の
確定ではなく、worker、base、isolation、route、実行、後続 Skill の起動権限、保存を候補工程へ含めない。

Codex runtime が Skill 間起動を提供しない場合は、親が `work-unit-design` 本文を同じ Intake／再正規化工程として直接参照する。
親が候補を採用・差し戻し・stop-incomplete とする判断と、実装・委譲の実行責務は変わらない。

## Dependencies, snapshots, and isolation

`depends_on` の Work Unit ID は dispatch 前に run 内で存在し、unknown と cycle を解消する。当該 Work Unit の dispatch 直前に
依存先が accepted であることを確認する。
外部・repository・environment の precondition には、観測方法、成立条件、安定性、pin 方法を記録する。mutable な
状態は dispatch 開始直前、外部 Action 直前、accept 直前に再観測する。drift または観測不能なら Action と accept を
禁止する。pin できる precondition は親が dispatch 前に `base_snapshot` へ固定し、handoff はその識別を参照する。drift 時は
新しい `base_snapshot` を確定し、task-owned isolation に安全に再適用できる場合だけ進む。ユーザー所有 branch や dirty
checkout の ref・履歴を書き換えず、対象・所有権・旧 snapshot への復旧可能性を確認できなければ、確認・再正規化・
`stop-incomplete` のいずれかにする。観測不能時は確認・再正規化・`stop-incomplete` とし、推測で Action を実行しない。

各 Work Unit の dispatch 直前に、親は repository、protected dirty/untracked、依存、現在の run baseline を再観測し、
`protected_dirty_record` を更新する。統合と QA では現在状態をこの record と比較し、drift があれば Action と accept を
止めて再正規化・確認・`stop-incomplete` を選ぶ。

`base_snapshot` は編集前内容を後から比較・再現できる不変の識別を持つ（commit に限定しない）。保護対象の dirty
state は `protected_dirty_record` として別管理し、uncommitted の変更を暗黙に commit、移送、破棄しない。snapshot
を再現できなければ別 snapshot、直列化、確認、`stop-incomplete` のいずれかにする。review target は対象内容を不変に識別できる
snapshot とし、review 中はその checkout へ writer を入れない。複数 reviewer は同じ snapshot を参照し、read-only と isolation が
保証できる場合だけ同時に起動できる。実装、親 QA、integration、その他の書き込み Action とは重ねない。reviewer 起動前後に
target と protected dirty/untracked state を再観測し、意味のある drift があればその snapshot の finding を受け入れ根拠に使わず、
新しい snapshot で再 review、確認または `stop-incomplete` を選ぶ。

isolation は execution data であり、全環境に固定 path や branch を要求しない。user constraint、dirty overlap、base、同時
writer、external resource、integration/rollback の必要性から選び、`base`、`owner`、`single_writer`、`paths`（1件でも list）、
`integration`、`cleanup` を確定する。親 direct、worker、継続修正、generator、formatter、write test などを含め、
同一 checkout への同時 writer は禁止する。既存変更を commit、move、discard して isolation を作らない。

### Default run-owned checkout

ユーザーが既存 checkout、別の isolation/worktree、または worktree を使わない制約を指定していない場合、親は
`base_snapshot` を確定し、保護する dirty/untracked を記録した後、最初の書き込み Action より前に、その snapshot から
run-owned worktree を一つ作成する。作成 Action が run の最初の書き込みであり、source、test、generator、formatter、integration
を既存の current checkout で先に実行してはならない。run-owned worktree は run 全体の既定 checkout とする。Work Unit 数だけでは追加 worktree を作らない。
既定実行順は直列のまま、並列 writer や immutable review target など具体的な必要がある場合だけ、既存の
safe-parallel 条件に従って追加 isolation を選ぶ。

この既定の作成では、execution data に `base`（`base_snapshot`）、`owner`（run が所有する resource）、`single_writer`（その時点の
親または委譲 worker）、`paths`（worktree の絶対 path を含む list）、`integration`（親 QA、review、final writing gate、統合、rollback
の責任）、`cleanup`（未統合成果、evidence、再開可能性、user constraint を確認してから決める条件）を確定する。worktree が存在する
こと自体は quality の evidence または accept の根拠にせず、既存の parent QA、review、final writing gate、integration、rollback を
省略しない。

ユーザーが指定した既存 checkout、別 isolation/worktree、または不使用の制約は execution constraint として既定より優先する。
その指定と品質下限が衝突する場合、無断で run-owned または別経路へ変更せず、確認を求めるか `stop-incomplete` とする。run-owned
worktree を作成できない場合も current checkout へ暗黙 fallback しない。未完了範囲と evidence を付けて `stop-incomplete` とする。
作成のために既存の dirty/untracked を commit、move、stash、discard しない。run-owned resource は親が所有し、cleanup は
run の accept 成否だけで機械的に削除せず、user-owned resource（ユーザー指定の checkout/worktree や branch）を無断変更・削除しない。

## Route and execution order

ユーザーの direct または委譲の制約をそのまま execution constraint として扱う。execution constraint には direct/委譲、
指定 worker、isolation、order、parallel の禁止または要求を含める。direct が指定された単位は親が実装し、
委譲が指定された単位は一名の worker にだけ割り当てる。指定が同時に存在して解決できない場合、無断で経路を変えず
`stop-incomplete` とする。経路の指定がない場合、各単位について、親 direct の方が安く安全なら direct、それ以外で
安全に委譲できるなら一名の worker を選ぶ。worker の能力は実装自由度、残存判断、推論難度、手戻り、検証可能性、
実行コストを相対比較して選び、単なる変更量や file 数だけで上位の worker を選ばない。選択理由を execution data に
記録する。

委譲時は v5 の4候補から、仕様が明確で既存 pattern を適用できる通常の `implementer` を原則とする。scope が特に狭く
検証が明確なら `focused-implementer`、残存判断や手戻りが大きいなら `senior-implementer`、親相当の推論を必要とする
具体的な理由があり品質を左右する場合だけ `expert-implementer` を選ぶ。単なる変更量や file 数で上位へ昇格せず、迷えば
`implementer` とする。選択した worker、理由、`base_snapshot`、execution constraint を execution data に記録する。
ユーザーが指定した worker が品質下限を満たせない場合も無断で変更・続行せず、制約緩和を確認するか、未完了範囲と判断点を
付けて `stop-incomplete` とする。固定閾値や決定表、暗黙の追加実行環境は持ち込まない。

既定の実行順は直列である。各 worker の結果は accept 候補に過ぎず、親が run の baseline に適用して確認するまで
accepted ではない。統合後の diff、dirty state、AC、scope、precondition、side effect、repository-native verification
を親が確認し、Green で再現可能な accepted baseline だけを後続単位の base にする。

## Fresh context and continuation

委譲する新しい ID の Work Unit は、Work Unit Data、依存、`base_snapshot`、選択 worker と route、execution constraint、
isolation、外部副作用の状態、禁止範囲、verification を含む自己完結 handoff で fresh context へ渡す。direct の単位は
親 context で実行し、新しい worker を起動しない。

委譲する新しい単位は新しい worker の起動で `fork_turns: "none"` の新しい worker context に起動する。同じ ID の
実装上の限定修正だけを`followup_task`で同じ context に返す。

AC、scope、責任境界、依存の意味が変わる再正規化は新しい ID とし、旧 context を継続しない。置換理由を execution
data に残し、依存 edge を再接続する。一意に再接続できなければ `stop-incomplete` とし、同じ成果を二重計上しない。accepted 単位
を書き換える修正・revert も新しい Work Unit とする。部分成果は、独立した新 ID、AC、QA、baseline への統合がすべて
完了した場合だけ accept する。

## Safe parallel dispatch and integration

ここで扱う並列化は実装 batch に限る。immutable snapshot と no writer を満たす reviewer の同時 read-only 観測は、実装 batch と重ねない別の実行として許す。候補間の依存がなく、path、derived output、semantic invariant、shared mutable state、
external namespace の競合がなく、同じ再現可能な base から隔離され、個別 QA と統合 verification が可能で、適用順が
結果を変えないことをすべて説明できる場合だけ並列に dispatch する。要求されても一つでも説明できない場合、ユーザーが
parallel を要求していなければ直列化できるが、要求している場合は無断で直列化せず確認または `stop-incomplete` とする。
判断理由と isolation を execution data に残す。並列中に hidden dependency、scope overlap、base drift が判明した場合は
新規の並列 dispatch を止め、返却を個別候補として QA し、無理に merge しない。

並列の返却は accept 候補として、最後の Green な run baseline へ一件ずつ統合する。既に accepted な単位を含む現在
baseline の diff、AC、scope、precondition、dirty state、side effect、native verification を毎回確認してから accept
し、最後の候補の統合 verification をこの parallel batch の `final combined verification` とする。全候補を accepted
とした後に別の combined gate は置かない。この扱いは run closeout の repository gate を省略するものではない。候補が失敗したら
accept せず最後の Green へ rollback して再検証する。戻せなければ dispatch を停止し、再正規化または `stop-incomplete`
とする。隠れた依存を無理に merge しない。

## Risk-directed review selection and handoff

reviewer はユーザーが明示した review goal、または親が AC、diff、test、外部副作用、責務境界その他から特定した具体的な
risk があり、review 結果が修正、`accept`、`stop-incomplete` の判断を変えうる場合だけ選ぶ。ただし、この risk-directed な
任意選択とは別に、全 Work Unit の run を閉じる直前には `writing-principles-reviewer` の final writing gate を必ず実施する。
全作業を reviewer に通す固定 phase、非選択 reviewer の台帳、固定 threshold、巨大な decision table は作らない。明示された
reviewer、目的、回数その他の制約は守る。指定 reviewer が利用不能で、親と代替 evidence だけでは許容不能 risk を検証できない
場合は確認を求めるか、`stop-incomplete` とする。

既存 reviewer の責務は review goal に対応するものだけを選ぶ。

- `plan-adversarial-reviewer`: 実装前 plan の具体的な failure path。
- `test-quality-reviewer`: test 設計、欠落 case、Gunte antipattern。
- `responsibility-boundary-reviewer`: 責務混在、境界、分散した副作用。
- `security-side-effect-reviewer`: security、破壊的操作、外部副作用。
- `writing-principles-reviewer`: How / What / Why / Why Not の配置。
- `over-engineering-reviewer`: 除去しても AC と制約を失わない要素。

汎用 reviewer を作らず、選択理由と期待する判断変更を execution data に記録する。各 reviewer へは固有の既存入力・出力形式を
保った自己完結 handoff を渡す。diff reviewer には task / Work Unit、AC、scope と constraints、base / target snapshot、
commit range、変更 file、完全な diff text、必要な test 結果と周辺 context を含め、checkout path、repository path、commit ID
だけで diff text を代替しない。plan reviewer には plan 全文と AC / constraints を渡す。diff artifact の存在は必須にせず、
inline か reviewer が全文を読み込める artifact のいずれかを使う。

## Review findings and continuation

親は reviewer の固有出力を execution data に正規化する。各 finding は `source_reviewer`、`target_snapshot`、reviewer の
native ID（なければ run 内一意の normalized finding ID）、evidence、影響する AC / risk、提案、親の採否と理由を持つ。
成立性は主張に応じた一次情報で確認する。repository 内の事実は diff / code / test、ユーザー制約は要求原文、外部契約は
authoritative な契約または文書、外部状態は Action が観測した Data を根拠にする。repository 内に根拠がないという理由だけで
不採用にしない。

各 finding を `adopted`、`rejected`、`unresolved` のいずれかに確定し、evidence、AC、risk、上位制約に基づく理由を示す。
reviewer の severity や結論を `accept` に直結させず、unresolved finding または許容不能 risk を残したまま accept しない。
同じ snapshot の全 reviewer 結果を集めてから、AC、evidence、security / data loss などの許容不能 risk、scope、rollback、
検証可能性、最小性で競合を解消する。安全に解消できない競合は確認、再正規化または `stop-incomplete` とする。

以下の一般的な `adopted` finding の修正・継続規則は `risk-directed review` に限る。`final writing gate` の finding はこの規則の
対象外であり、後段の final writing gate 固有の stop / remediation 規則に従う。`adopted` finding の修正は既存の route / context 規則へ戻す。同じ ID で AC、scope、責任境界、依存が不変の限定修正だけを
同じ context へ返す。意味契約が変わる修正は新しい ID と fresh context へ再正規化し、固定修正 agent を導入しない。修正後は
親 QA と repository-native verification を再実行し、影響を受けた review goal
だけを新しい snapshot で再 review する。親 QA、新 diff、新 test、副作用 evidence が新しい具体的 risk を示し、結果が判断を
変えうる場合だけ新しい review goal と対応 reviewer を追加する。影響も新 risk もない reviewer を一律再起動しない。

review を `continue` するのは、次に確認する具体的な未解決 risk と期待する新しい evidence を説明できる場合だけとする。
固定 round、0 findings、reviewer の Pass は打ち切りや accept の条件にしない。親が品質下限、known finding の処理、残存 risk
の許容を独立して確認し、必要な判断が完了した時点で review を打ち切る。

## Final writing acceptance gate

全 Work Unit が accept 候補となり、親 QA が Green で、選択した review goal と finding の採否・処理が完了した後、run を
accept する直前に `writing-principles-reviewer` の read-only final writing gate を有効な一回として必ず実施する。この gate は
risk-directed reviewer の選択数・回数の外にあり、変更が小さい、risk がない、または途中で同 reviewer を実施済みであることを
理由に省略できない。ユーザーが途中または追加 review を指定した場合も実施するが、final writing gate の代替にはならない。
review の回数・時点に衝突がある場合は最初の review 前に確認して解消し、解消できなければ `stop-incomplete` とする。

`review_base_snapshot` は、final gate の対象として残る task-owned 変更集合が始まる前の、最後の accepted repository state とする。
Work Unit ごとの統合で `accepted baseline` が更新されても、final gate の `review_base_snapshot` は更新せず、final gate で run が
accept されるまで固定する。gate の `target_snapshot` はその固定 base から元変更と remediation を含む累積候補であり、先行
Work Unit の変更を累積 diff から除外しない。protected dirty/untracked は別の `protected_dirty_record` として扱う。final finding
後の remediation run でも未受入候補を新しい baseline にせず、同じ accepted base を継承する。この区別は既存の Work Unit 統合を
置き換える状態機械を追加するものではない。
reviewed artifact set は `review_base_snapshot` から `target_snapshot` までの repository 累積 diff、存在する commit range と
各 commit message、reviewer の責務対象として handoff した説明 artifact の集合である。gate handoff には task、全 Work Unit、
AC、scope / constraints、review base / target、commit range、全変更 file、累積 diff 全文、test 結果、周辺 context、artifact set を
含める。checkout path、repository path、commit ID だけでこれらを代替しない。

gate 中の target checkout には writer を入れず、親 QA、実装、integration、generator、formatter、write test を重ねない。開始前と
終了後に target と protected dirty/untracked を再観測し、意味のある drift があればその結果を有効な一回として数えない。安全に
同じ target / artifact set を再試行できなければ `stop-incomplete` とする。reviewer が利用不能、handoff が不足、read-only isolation
を確保できない、または result を取得・照合できない場合も確認または `stop-incomplete` とする。

reviewer の Pass、severity、または 0 findings だけで accept してはならない。親は reviewer の各 finding を一次情報で確認し、
`adopted`、`rejected`、`unresolved` と理由を execution data に確定する。0 findings または全 finding が `rejected` の場合でも、
同じ target_snapshot と reviewed artifact set に対して final verification を実行する。この場合 target は不変であり、finding の
Data と親の理由を closeout に残す。`unresolved` を残したまま accept してはならない。

### Final writing findings and remediation

`writing-principles-reviewer` は read-only / report-only のまま finding Data を返し、自身で修正、Implementer、Work Unit owner、受入決定者を
担わない。親だけが一次情報を確認して adopted / rejected / unresolved と理由を確定する。

`adopted` finding を修正できるかは reviewer の結論ではなく、親が一次情報で確定する。親は proposed change が次の条件を
すべて満たすかを確認する。

- AC、公開 contract、責任境界、依存、外部副作用を変えない局所的・非semanticな変更である。
- `scope.change` / `scope.exclude`、rollback、verification を修正前に閉じられる。
- 指摘対応以外の変更を含まず、同じ accepted base から前後の target snapshot を比較できる。

条件を満たす場合、親は `final remediation Work Unit` を一意な新しい `id` で正規化する。Work Unit Data は `id`、`purpose`、
`acceptance_criteria`、`scope`（`change` / `exclude`）、`implementation_freedom`、`constraints`、`depends_on`、`verification` の
canonical field に統一し、概念名を別 key のように置き換えない。

元の Work Unit の意味を変更せず、同じ run の最終 remediation として通常の worker 選択、fresh Implementer context、single writer
で実装する。`writing-principles-reviewer` は writer、Implementer、Work Unit owner、
受入決定者にならず、reviewer と remediation writer を同一 agent または同時 writer にしない。`focused-implementer` や固定 patch agent を
一律に要求しない。

remediation 後は親が指摘対応、余分な変更なし、AC / public contract / 責任境界 / 依存の不変を diff の一次情報で QA し、
focused / repository-native / final verification を実行する。これらを説明できる場合、親は同じ final writing gate を
`mechanically restart` せず、その finding Data、前後 snapshot、QA、verification を accept 根拠にできる。局所性、非semantic性、
rollback、verification のいずれかを説明できなければ確認または `stop-incomplete` とする。

この eligible remediation では、修正の結果として reviewed artifact content/identity、target_snapshot、reviewed artifact set、
commit range/commit message が変わりうる。親は before/after identity と比較、指摘対応以外の変更がないこと、QA、verification を
同じ run (same run) の accept 根拠として明示する。この扱いは final writing gate の通常の snapshot 不変規則に対する `same-run accept exception`
であり、commit-message-only remediation もこの経路で実行できる。commit-message-only remediation として扱う場合に限り、commit message
以外の file、test、無関係な commit/range を加えた変更はその subcase の eligible 条件を満たさず、`stop-incomplete` とする。commit
message を対象にしない局所的な code/test/comment remediation は、先行する eligible 条件を満たす限り許可する。

条件を満たさない finding、または semantic / public contract / 責任境界 / AC / 依存の変更や広い構造変更を要する finding は、
通常の新しい Work Unit に再正規化する。現 run では修正を accept せず `stop-incomplete` とし、修正後の元変更を含む累積 target に
対して `mandatory final writing review` を再実行してから受入判断する。#149 の optional risk-directed review は、影響する review
goal または新しい具体的 risk がある場合だけ再確認し、writing finding の採否だけを理由に全 reviewer を再起動しない。

gate 対象外の execution data の記録は、上記の bounded remediation Work Unit に伴う前後 snapshot・verification の更新、または
事実を変えない表現修正だけを許す。ただし上記の eligible remediation exception に該当する reviewed artifact、target_snapshot、
reviewed artifact set、commit range/commit message の変更は、修正前後の identity と比較、QA、verification を記録することで同じ
run に accept できる。exception に該当しないこれらの変更や、final verification が対象を変える変更は accept せず
`stop-incomplete` とし、安全な snapshot 不変の再検証だけを許す。

closeout には writing target、`review_base_snapshot` と remediation 前後の `target_snapshot`、reviewed artifact set、gate result、
各 finding の adopted / rejected / unresolved と理由、remediation Work Unit（該当時）、focused / repository-native / final
verification、最終 target、残存 risk を含める。これは execution data の報告であり、固定 QA report、固定 diff artifact、判断点台帳、
全 reviewer 必須化、固定 review loop、固定修正 agent、over-engineering reviewer の mandatory phase を新設するものではない。

## External side effects

外部副作用は worktree と別に execution data で管理する。各 Action に `未実行`、`実行済み`、`結果不明`、resource、
idempotency、照合方法、補償または rollback を記録する。partial failure または context loss の後は、fresh context で
再観測し、安全に照合して retry できる場合だけ再実行する。結果不明なら再実行せず `stop-incomplete` とする。共有 resource の順序や
競合がある場合は並列化しない。未実行の外部 Action について、選択済み review goal の結果が実行可否、対象 / 入力、
authorization、idempotency、compensation / rollback を変えうる場合、その review 完了と関連 finding の解決を当該 Action の
precondition にする。外部副作用を伴わない code 作成、および外部 Action を含まない local / read-only verification だけは先行できる。
verification command 内に外部 Action が含まれる場合も、同じ review 完了と関連 finding 解決の precondition を適用する。外部 Action 後に初めて risk が判明した場合は
外部状態と result identity を再観測し、既存の外部副作用契約に従って補償、確認または `stop-incomplete` を選ぶ。事後 review を
実行前保証として扱わない。

## Execution data and conditional persistence

Work Unit、plan、finding、QA 結果は会話内 execution data を既定とする。ユーザー要求、後日再開、別 session / 別担当への
handoff、外部 review、PR、監査、tool / repository 運用によって現在 context より長く生存する必要がある場合だけ、必要な data を
一般化した persistence resource へ保存する。complexity、file 数、Work Unit 数を固定 threshold にしない。

保存時は resource の purpose / content、identity、ownership / authorization、sensitivity、current state、idempotency、照合方法、
retention / lifetime、update / cleanup / compensation を確定する。filesystem / repository では path、tracked / untracked、
protected dirty state、overwrite の有無、書き込み後の content / status を確認する。PR / Issue / API / artifact store では URL、
resource ID、revision、remote state、API result を確認する。ユーザー所有 resource を無断で上書きまたは削除しない。必須の永続化を
安全に実行・照合できなければ確認または `stop-incomplete` とする。artifact が存在すること自体を quality evidence にしない。

## Implementation and TDD

親と worker は、確定した purpose、AC、scope、constraints、depends_on、verification を共有し、指定範囲だけを
編集する。既存 test の削除、skip、期待値の弱体化、未承認の依存追加、生成物の直接編集はしない。

observable な code behavior は各 Work Unit で Red → Green → Refactor を進める。

1. **Red** — AC から正常系、境界値、異常系、例外経路を導いた test を先に追加し、意味のある failing output を記録する。
   これを Red 証跡として返却 data に含める。意味のある failing test が成立しない場合は、変更前の evidence、成立しない
   理由、代替 verification を返す。形式的な mutation は行わない。
2. **Green** — 最小の実装で test を通し、focused test と必要な native verification の command と結果を記録する。
3. **Refactor** — AC、責任境界、error handling、命名を保ったまま重複を整理し、Green を再実行する。意味が変わる場合は
   Green に戻り、同じ Work Unit の範囲を越えない。

## Parent QA and closeout

direct でも委譲でも、親は各単位の結果を受け取った時点の baseline diff、AC、scope、precondition、dirty state、
test、side effect、既知 risk を自分で確認する。親は worker の報告を鵜呑みにせず、Red/Green/Refactor の evidence、focused
test、repository-native verification を再実行し、変更が同じ Work Unit の責任境界内にあることを確認する。

### Run-owned closeout

run-owned worktree は成果保管場所ではなく一時的な実行 resource である。ユーザーが保持を指定していない場合、親は
`accepted` と `stop-incomplete` のどちらで終わる run でも、次の closeout 判定を経て安全なときは削除する既定を持つ。
削除は品質 evidence や accept の根拠ではなく、親 QA、選択した risk-directed review、final writing gate、final verification、
必要な外部副作用の照合がすべて完了した後にだけ行う最後の Action である。PR の有無で分岐を作らず、local/remote の
persistence と integration の観測結果を共通の Data として扱う。

closeout は `Action → Data → Calculation → Data → Action → Data` の順に進める。まず親は target の repository identity、worktree identity、
canonical path、exact full branch ref、`invocation_start_head`、HEAD、clean status、全 writer/reviewer の終了、worktree 内だけに残る
exclusive evidence、ユーザーの保持指定、別 run resource との識別を再観測する。Work Unit の `base_snapshot` と invocation branch の
baseline は別の Data として pin し、同じ HEAD でも branch ref が違えば同一実行先とは扱わない。継続 PR のように
`base_snapshot` と `invocation_start_head` が異なる場合も、各値を混同せず exact identity を再照合する。

次に Calculation が、(a) run-owned で user-owned checkout/worktree/branch、固定 path、別 run resource ではない、(b) 成果を task-owned
local branch の commit に固定済みで、再開に必要な branch/commit（利用可能なら remote ref も）を報告できる、(c) worktree が clean、全
writer/reviewer が終了し、worktree 内だけの未統合成果/evidence がない、(d) target identity と invocation repository/branch ref が一意、
(e) user retention がなく、protected state（dirty/untracked に加えて ignored entry）の観測が完了している、を判定 Data にする。
どれかを観測できない、または false なら削除 Action を実行せず、path、branch、commit、理由を付けた `stop-incomplete` を返す。

local integration は別の Action として、integration 直前に invocation repository identity、worktree identity/canonical path、exact full branch
ref、その ref の target、`invocation_start_head`、protected dirty/untracked/ignored state を再照合する。invocation branch の HEAD は開始時
`invocation_start_head` から drift していないことを確認し、Work Unit の `base_snapshot` と一致することは要求しない。開始時 HEAD..task
commit の変更 path と ancestor path が protected dirty/untracked/ignored entry と衝突しないこと、task commit への fast-forward が可能なことを
Calculation してから `--ff-only` で行う。衝突、identity/ref の不一致、観測不能、drift、protected state の変化、non-FF は統合禁止とし、
task-owned branch/commit を保持して未統合理由を Data にする。無条件 checkout/merge、merge commit、rebase、reset、stash、force、
`branch -D` は使わない。

`--ff-only` 成功後は同じ exact branch ref の target と HEAD が task commit に一致すること、protected state と内容 identity が不変であることを
再観測する。secret の内容は報告せず、path/type/mode/size と安全な content digest などの identity だけで照合する。`--ff-only` の Action status
だけを terminal outcome にせず、失敗後は exact ref/HEAD を再観測する。再観測が (a) `invocation_start_head` のままなら未統合として扱い、
他の安全条件が成立するときだけ worktree を削除して `stop-incomplete`、(b) task commit なら統合済みとして扱い、protected state/content identity と
全 postcondition が成立するときだけ通常 cleanup と `accepted`、(c) unexpected または観測不能なら worktree を保持して `stop-incomplete` とする。
不一致、照合不能、または Action の結果不明なら branch delete と worktree remove を抑止し、blind retry/force をせず、path、branch、commit、
blocker、risk を含む result Data にする。Action 失敗後は再観測してからでなければ次の Action へ進まない。

統合できない場合でも、task-owned branch/commit に成果が永続化され、worktree が clean、protected state が不変で exclusive evidence がなく、
target identity が一意なら、無理に統合せず `stop-incomplete` と未統合理由を Data にして run-owned worktree を削除する。成果が commit 前、
evidence が worktree 内だけ、writer/reviewer が active、保持指定がある、削除対象 identity が不明、または protected state の照合不能なら
worktree を残す。

安全な local integration 後、または上記の安全な未統合終了後の closeout は run-owned worktree を通常削除し、worktree list から対象 identity
が消えたことを照合する。remove が失敗した、または remove 後も identity が list に残る場合は branch delete を行わず、実際に残る path、branch、
commit、blocker、risk を `stop-incomplete` として報告する。merge 済み task branch の safe delete（`git branch -d` 相当）が不成立・失敗でも
worktree の安全な削除を取り消さず、branch を保持して報告する。user-owned branch や別 run resource は変更・削除しない。
closeout の result Data には、`run_outcome`（`accepted` / `stop-incomplete`）、統合/未統合、削除/保持、対象 path、branch、commit、
protected state identity、観測した blocker、残存 risk を含める。integration と worktree removal が成立した後の task branch retained は
残存 risk として報告するが、それだけで `accepted` を妨げない。

AC、scope、責任境界、依存が不変で同じ単位の実装上の不足だけなら、親は同じ ID と context で `continue` して限定修正を
返す。それ以外は限定修正を続けず、fresh context の新しい ID として再正規化する。親が品質下限を満たし、全要求単位を accepted とし、
選択した review goal と finding の処理結果を確認し、AC、scope、制約、evidence、残存 risk を説明できる場合は、run accept 前に closeout の repository gate を含む final closeout verification を
実施する。その verification が Green なら run を accept する。新しい failure が出た場合は run を accept せず Adapt または
`stop-incomplete` へ戻す。品質下限等を満たせない場合は、未完了範囲、満たせない条件、判断点、evidence、残存 risk、未検証事項を明記して
`stop-incomplete` とする。固定状態機械や常時必須の永続化された実行成果を新設しない。

最終報告には変更 file、baseline からの diff summary、各 Work Unit の `id`、context、base_snapshot、isolation、依存、
route、result、verification、final run baseline、実行した command と結果、AC 対応、選択理由、前提、判断点、残存 risk、
未検証事項、`git status --short` を含める。review を実施した場合は review goal / result、finding の adopted / rejected /
unresolved と理由、残存 risk を含め、persistence resource がある場合だけ identity / ownership / lifecycle も含める。v4 の
identifier/path/mode、固定 worktree、必須の追加報告形式を持ち込まず、explicit-only、暫定名、v4/v5 共存を維持する。v4
mode、Branch Plan、固定 4 phase、over-engineering reviewer の mandatory phase、固定修正経路、永続 artifact の通常必須化を
持ち込まない。固定 review phase、必須 QA report、必須 diff artifact、判断点台帳を v5 契約へ持ち込まない。親は run を accept したか
`stop-incomplete` で停止したかを明示し、未承認の追加作業を残さない。
