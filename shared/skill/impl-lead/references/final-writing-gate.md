# impl-lead final writing gate v1

この reference は、`impl-lead` が run を accept する直前に行う final writing gate と、採用 finding の remediation 境界を定義する。
親は `SKILL.md` で指定された時点に全文を読み、reviewer の報告を一次情報で裁定する。

<!-- @contract impl-final-writing-loader -->
次の Loader Data が列挙値の唯一の正本である。

```text
path = references/final-writing-gate.md
load_timing = before final writing gate
identity = impl-lead final writing gate v1
required_sections = [Final writing acceptance gate, Final writing findings and remediation]
required_scope = [snapshot, handoff, read-only isolation, finding adjudication, bounded remediation, re-gate, closeout data]
failure = stop-incomplete
owner = impl-lead parent
reviewer_authority = report-only
```

親は上記 Loader Data の field を使って load と必要本文の検証を行い、failure field に従って失敗処理する。
owner / reviewer_authority の境界を維持し、reviewer を writer または受入決定者にしない。
<!-- @/contract -->

<!-- @contract impl-programmatic-flow-final-writing-gate-invocation -->
### final-writing-gate-invocation

Trigger: 全 Implementation Unit が accept 候補で、親 QA が Green、risk-directed finding の処理が完了したと親が確定し、run accept 直前に到達したとき。
Inputs: 検証済み `impl-final-writing-loader` Data、identity と必要 section を検証した reference 本文、親が固定した target snapshot と self-contained handoff Data。
Procedure: `references/final-writing-gate.md` の `Final writing acceptance gate` だけを invocation procedure の唯一の正本として、有効な read-only gate を一回実施する。省略、既実施 review での代替、writer との重複をしない。
Outcomes: snapshot に結び付いた有効な reviewer result Data、または `blocked`。loader / invocation failure は突破せず `stop-incomplete` へ送る。
<!-- @/contract -->

<!-- @contract impl-programmatic-flow-final-writing-result-routing -->
### final-writing-result-routing

Trigger: final writing gate の reviewer result が親へ返却されたとき。
Inputs: target snapshot と照合済み result、finding Data の有無、検証済み `impl-final-writing-loader` Data と reference 本文。
Procedure: `references/final-writing-gate.md` の `Final writing findings and remediation` だけを result routing procedure の唯一の正本として、result を no-finding、parent-adjudication-required、invalid / incomplete に振り分ける。finding の意味的な採否を Flow 内で決めない。
Outcomes: `gate-complete`、`parent-adjudication-required`、または `blocked`。後続 remediation の eligibility、risk、採否は Agentic な親へ返し、invalid / incomplete は `stop-incomplete` へ送る。
<!-- @/contract -->

<!-- @contract final-writing-remediation -->
## Final writing acceptance gate

全 Implementation Unit が accept 候補となり、親 QA が Green で、選択した review goal と finding の採否・処理が完了した後、run を
accept する直前に `writing-principles-reviewer` の read-only final writing gate を有効な一回として必ず実施する。この gate は
risk-directed reviewer の選択数・回数の外にあり、変更が小さい、risk がない、または途中で同 reviewer を実施済みであることを
理由に省略できない。ユーザーが途中または追加 review を指定した場合も実施するが、final writing gate の代替にはならない。
review の回数・時点に衝突がある場合は最初の review 前に確認して解消し、解消できなければ `stop-incomplete` とする。

`review_base_snapshot` は、final gate の対象として残る task-owned 変更集合が始まる前の、最後の accepted repository state とする。
Implementation Unit ごとの統合で `accepted baseline` が更新されても、final gate の `review_base_snapshot` は更新せず、final gate で run が
accept されるまで固定する。gate の `target_snapshot` はその固定 base から元変更と remediation を含む累積候補であり、先行
Implementation Unit の変更を累積 diff から除外しない。protected dirty/untracked は別の `protected_dirty_record` として扱う。final finding
後の remediation run でも未受入候補を新しい baseline にせず、同じ accepted base を継承する。この区別は既存の Implementation Unit 統合を
置き換える状態機械を追加するものではない。
reviewed artifact set は `review_base_snapshot` から `target_snapshot` までの repository 累積 diff、存在する commit range と
各 commit message、reviewer の責務対象として handoff した説明 artifact の集合である。gate handoff には task、全 Implementation Unit、
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

`writing-principles-reviewer` は read-only / report-only のまま finding Data を返し、自身で修正、Implementer、Implementation Unit owner、受入決定者を
担わない。親だけが一次情報を確認して adopted / rejected / unresolved と理由を確定する。

`adopted` finding を修正できるかは reviewer の結論ではなく、親が一次情報で確定する。親は proposed change が次の条件を
すべて満たすかを確認する。

- AC、公開 contract、責任境界、依存、外部副作用を変えない局所的・非semanticな変更である。
- `scope.change` / `scope.exclude`、rollback、verification を修正前に閉じられる。
- 指摘対応以外の変更を含まず、同じ accepted base から前後の target snapshot を比較できる。

条件を満たす場合、親は `final remediation Implementation Unit` を一意な新しい `id` で正規化し、`impl-lead` の `Intake and Implementation Unit normalization` が定める canonical Implementation Unit Data に適合させる。field の意味や一覧はここで再定義しない。

元の Implementation Unit の意味を変更せず、同じ run の最終 remediation として通常の worker 選択、fresh Implementer context、single writer
で実装する。`writing-principles-reviewer` は writer、Implementer、Implementation Unit owner、
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
通常の新しい Implementation Unit に再正規化する。現 run では修正を accept せず `stop-incomplete` とし、修正後の元変更を含む累積 target に
対して `mandatory final writing review` を再実行してから受入判断する。#149 の optional risk-directed review は、影響する review
goal または新しい具体的 risk がある場合だけ再確認し、writing finding の採否だけを理由に全 reviewer を再起動しない。

gate 対象外の execution data の記録は、上記の bounded remediation Implementation Unit に伴う前後 snapshot・verification の更新、または
事実を変えない表現修正だけを許す。ただし上記の eligible remediation exception に該当する reviewed artifact、target_snapshot、
reviewed artifact set、commit range/commit message の変更は、修正前後の identity と比較、QA、verification を記録することで同じ
run に accept できる。exception に該当しないこれらの変更や、final verification が対象を変える変更は accept せず
`stop-incomplete` とし、安全な snapshot 不変の再検証だけを許す。

closeout には writing target、`review_base_snapshot` と remediation 前後の `target_snapshot`、reviewed artifact set、gate result、
各 finding の adopted / rejected / unresolved と理由、remediation Implementation Unit（該当時）、focused / repository-native / final
verification、最終 target、残存 risk を含める。これは execution data の報告であり、固定 QA report、固定 diff artifact、判断点台帳、
全 reviewer 必須化、固定 review loop、固定修正 agent、over-engineering reviewer の mandatory phase を新設するものではない。
<!-- @/contract -->
