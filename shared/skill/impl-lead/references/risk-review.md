# impl-lead risk review v1

この reference は、`impl-lead` の risk-directed reviewer 選択と handoff、test-quality-reviewer の behavior-observation-kernel v1
mapping、batch-resolve-kernel v1 の risk-directed review mapping、finding 裁定と継続、選択 finding remediation の
Implementation Unit normalization を定義する。親は `SKILL.md` の Review minimal pre-screen を通過した candidate に
ついてだけ、指定された時点に全文を読み、判断と Action を自身の execution data として扱う。

## Risk-directed review selection and handoff

reviewer はユーザーが明示した review goal、または親が AC、diff、test、外部副作用、責務境界その他から特定した具体的な
risk があり、review 結果が修正、`accept`、`stop-incomplete` の判断を変えうる場合だけ選ぶ。ただし、この risk-directed な
任意選択とは別に、全 Implementation Unit の run を閉じる直前には `writing-principles-reviewer` の final writing gate を必ず実施する。
全作業を reviewer に通す固定 phase、非選択 reviewer の台帳、固定 threshold、巨大な decision table は作らない。明示された
reviewer、目的、回数その他の制約は守る。指定 reviewer が利用不能で、親と代替 evidence だけでは許容不能 risk を検証できない
場合は確認を求めるか、`stop-incomplete` とする。

既存 reviewer の責務は review goal に対応するものだけを選ぶ。

- `plan-adversarial-reviewer`: 実装前 plan の具体的な failure path。
- `test-quality-reviewer`: test 設計、欠落 case、Gunte antipattern。
- `responsibility-boundary-reviewer`: 責務混在、境界、分散した副作用。
- `security-side-effect-reviewer`: security、破壊的操作、外部副作用。
<!-- @contract impl-risk-directed-static-performance-reviewer -->
- `static-performance-reviewer`: diff が発火または増幅した、静的 evidence で示せる性能・資源効率リスク。
<!-- @/contract -->
- `writing-principles-reviewer`: How / What / Why / Why Not の配置。
- `over-engineering-reviewer`: 除去しても AC と制約を失わない要素。

汎用 reviewer を作らず、選択理由と期待する判断変更を execution data に記録する。各 reviewer へは固有の既存入力・出力形式を
保った自己完結 handoff を渡す。diff reviewer には task / Implementation Unit、AC、scope と constraints、base / target snapshot、
commit range、変更 file、完全な diff text、必要な test 結果と周辺 context を含め、checkout path、repository path、commit ID
だけで diff text を代替しない。plan reviewer には plan 全文と AC / constraints を渡す。diff artifact の存在は必須にせず、
inline か reviewer が全文を読み込める artifact のいずれかを使う。

<!-- @contract impl-test-quality-behavior-observation-kernel-loader -->
## behavior-observation-kernel v1 の test-quality-reviewer mapping

`test-quality-reviewer` を選んだときだけ注入する。他 reviewer、特に `plan-adversarial-reviewer` へ流さない。

次の Loader Data がこの load の唯一の正本である。

```text
path = ../../../references/behavior-observation-kernel.md
load_timing = immediately before test-quality-reviewer invocation
identity = behavior-observation-kernel-v1
required_sections = [Contract, Method, Reintegration, Consumer の責務, 非目標]
failure = stop-incomplete
owner = impl-lead parent
delegate_path_resolution = false
```
<!-- @/contract -->

<!-- @contract impl-risk-directed-batch-resolve-kernel-parent-mapping -->
## batch-resolve-kernel v1 の risk-directed review mapping

次の Loader Data が列挙値の唯一の正本である。

```text
path = ../../../references/batch-resolve-kernel.md
identity = batch-resolve-kernel-v1
dependencies = none
required_sections = [適用モデル, snapshot discipline, Resolution Transaction, caller boundary]
failure = stop-incomplete
owner = impl-lead parent
```

親は risk-directed review の最初の Resolution Transaction 前に、上記 Loader Data の field を使って load と必要本文の検証を行い、
failure field に従って失敗処理する。owner の path-resolution boundary を維持する。
この loader は finding が0件の review、final writing gate だけの処理のためには起動しない。

次の role Data が列挙値の唯一の正本である。

```text
caller = impl-lead parent
resolver = impl-lead parent
counterpart = risk-directed reviewer
target_snapshot = origin verified snapshot
finding = Resolution Point
same_snapshot_findings = Resolution Batch
dispositions = [adopted, rejected, unresolved]
```

親は上記 role field と後続の transaction field を使って finding の mapping、return、Implementation Unit / run acceptance の
Action を行い、既存の親境界を変更しない。

親は counterpart invocation 前に review set を固定する。必要な全 observation と result を回収し、finding を normalize して
evidence を確認してから Resolution Transaction を開始する。一部でも欠ける場合は暗黙に縮退せず、既存の caller boundary または
`stop-incomplete` へ返す。

### risk-directed review の Resolution Transaction

```text
reviewer_observation = outside Resolution Transaction
result_collection = outside Resolution Transaction
batch_freeze = before mutation
zero_findings = no Resolution Transaction
adopted_findings = coherent remediation
updated_snapshot_re_review = new Resolution Transaction
transaction_closure = not Implementation Unit acceptance, not run acceptance
final_writing_gate = outside mapping
```

上記 Data は impl-lead 固有の caller mapping だけを定める。generic Transaction procedure は Kernel を唯一の正本とし、
既存の Implementation Unit、AC、scope、exclude、責任境界を拡張しない。
<!-- @/contract -->

### selected finding remediation の Implementation Unit normalization

<!-- @contract impl-risk-remediation-grouping-entry -->
同じ origin verified snapshot の Resolution Batch を全件裁定して selected finding set を固定した後、set が非空なら、親は trivial / nontrivial を先に分類せず、mutation / apply の前に関連 remediation candidates を必ず `implementation-unit-design` へ渡す。zero findings では起動しない。
入力は各 finding の identity、obligation、AC、mutation oracle、disposition と既存 Implementation Unit context を保持する。返却される canonical Implementation Unit candidates について、親が要求 coverage、`blocking_gaps`、Implementation Unit Data / execution Data 境界、採否、ID を確定する。
<!-- @/contract -->

<!-- @contract impl-risk-remediation-perspectives -->
remediation の `partition_perspectives` は、origin verified snapshot、finding dependency / shared invariant、coherent apply / combined verification、authority / external side effect、rollback / failure isolation、independent promotion boundary を照らす。元の Skill 数や Implementation Unit 数を根拠にせず、固定 remediation mode、件数 threshold、solver、expected-output oracle、ledger を導入しない。
<!-- @/contract -->

<!-- @contract impl-risk-remediation-regrouping -->
apply / verify / isolate / applicability check により、membership、dependency / conflict / shared invariant、verification point interaction、authority / side effect、rollback / failure isolation、promotion precondition の grouping-relevant evidence が実質変化した場合、親は元の Resolution Batch に閉じた corrective adjudication を行い、次の apply 前に current verified snapshot と未処理 selected obligations だけを `implementation-unit-design` へ再入力する。promoted obligation は再入力、再 apply、別 group への再統合をせず、evidence と membership が不変なら再実行しない。
<!-- @/contract -->

<!-- @contract impl-risk-remediation-continuation -->
各 remediation group 全体を既存の `implementation-unit-continuation-routing` へ渡す。一つの既存 ID に由来する全 obligation が一 group に閉じ、aggregate AC、scope、責任境界、dependency が不変の場合だけ same ID / context を使う。意味変更、accepted 単位の変更、cross-ID、または一つの既存 ID 由来の obligation を複数 group へ split した各 group は `renormalization-required` とし、finding identity は保持する。fresh unique ID / context は mandatory boundary 返却後に親が確定する。
<!-- @/contract -->

<!-- @contract impl-risk-remediation-outer-inner -->
Implementation Unit grouping は外側の accept / dispatch boundary、Batch Resolve Kernel partition は各 Implementation Unit 内側の apply / verify boundary とする。Kernel は一つの Implementation Unit を複数 partition へ refine できるが、複数 Implementation Unit を一つの partition へ coarsen せず、常時 1:1 ともしない。inner transaction closure だけで Implementation Unit を accept しない。
<!-- @/contract -->

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
同じ context へ返す。
<!-- @contract impl-risk-finding-meaning-change-route -->
意味契約が変わる修正は `implementation-unit-continuation-routing` へ渡し、`renormalization-required` のときは mandatory implementation-unit-design boundary へ接続する。固定修正 agent を導入しない。
<!-- @/contract -->
修正後は親 QA と repository-native verification を再実行し、影響を受けた review goal
だけを新しい snapshot で再 review する。親 QA、新 diff、新 test、副作用 evidence が新しい具体的 risk を示し、結果が判断を
変えうる場合だけ新しい review goal と対応 reviewer を追加する。影響も新 risk もない reviewer を一律再起動しない。

review を `continue` するのは、次に確認する具体的な未解決 risk と期待する新しい evidence を説明できる場合だけとする。
固定 round、0 findings、reviewer の Pass は打ち切りや accept の条件にしない。親が品質下限、known finding の処理、残存 risk
の許容を独立して確認し、必要な判断が完了した時点で review を打ち切る。
