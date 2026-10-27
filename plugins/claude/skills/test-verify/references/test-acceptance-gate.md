<!-- Generated from shared/. Do not edit directly. -->

# Test Acceptance Gate

## Responsibility and applicability

Test Acceptance Gate は changed test artifact の coverage / validity を受入前に確認する。automated test、fixture、oracle、executable test contract の追加・変更・削除（skip / assertion 弱体化を含む）がある場合に applicable とし、test-only も対象にする。production-only と no-change は not-applicable とし、既存テスト全体の再審査を要求しない。

Gunte predicate / contract、明示された EVAL case は executable test contract に含むが、EVAL corpus の新設や常時 mutation testing を要求しない。

direct owner が obligation、oracle、validation plane、Expected Observation、necessary verification、mutation applicability、finding adjudication、acceptance を所有する。fresh / context-isolated な test-coverage-reviewer と test-validity-reviewer は同じ immutable candidate snapshot を read-only / report-only で観測する。reviewer Pass は受入根拠ではなく、baseline self-QA を代替しない。

## Input and observations

同じ Task Spec、comparison base、candidate snapshot / exact diff、changed artifact 一覧、AC、Expected Observation、surrounding context、baseline self-QA、runtime evidence、mutation applicability と applicable mutation evidence を両 reviewer に渡す。fixture の authoritative source と input consistency を確認できる根拠も含める。必要な evidence がないことを reviewer Pass で補わない。

coverage は normal / boundary / error / exception / side-effect failure の applicable behavior と artifact の対応、削除・skip・弱体化による hole、implementation detail への過剰固定を観測する。validity は oracle independence、fixture と production path の整合、input consistency、mock / shared state の影響と meaningful failure protection を観測する。数量0、単価と金額の同値、按分前後の同値等で意図した振る舞いと plausible incorrect behavior の差が消える場合は、該当 input / assertion と識別できない違反を根拠にする。fixed score や style preference は受入基準にしない。

mutation の適用判断と evidence generation は direct owner が `execution-safety.md` に従って行い、reviewer 自身は実行しない。mutation 非適用なら理由と利用できる識別 evidence を明記する。

## Programmatic Flow

### test-verify-test-acceptance-control

Trigger: baseline self-QA と必要な risk review 後、変更ありの immutable candidate snapshot が固定された。

Inputs: comparison base、candidate snapshot / exact diff、changed artifact 一覧、applicability、共通 input packet、baseline ownership と repository state。

Procedure:

1. candidate snapshot が target-causal scope の変更だけを含み、current content / diff が snapshot と一致し、既存 dirty state が baseline ownership と一致し、temporary mutation artifact を含まないことを確認する。
2. changed test artifact がなければ `not-applicable` を返す。
3. required input を確認し、fresh / context-isolated な `test-coverage-reviewer` と `test-validity-reviewer` に同一 snapshot と packet を渡す。両結果が戻るまで対象への writer を入れない。
4. 両 reviewer の finding Data を `owner-adjudication-required` として返す。Flow 内で finding の採否や acceptance を決めない。

Outcomes: `not-applicable`、`owner-adjudication-required`、または snapshot / input / reviewer result の不足を伴う `stop-incomplete`。


## Adjudication and correction

direct owner は両 finding を evidence、AC、scope、risk に照合して adopted / rejected / unresolved に裁定する。必要な evidence が十分で、採用した correction が完了し、acceptance を妨げる unresolved finding がない場合だけ `test-accepted` とする。

semantic な test correction は direct owner が因果範囲内で行い、baseline self-QA、affected runtime verification、必要な risk review を確認して snapshot を更新する。新 snapshot に affected coverage / validity goal の fresh review を行い再裁定する。影響しない review evidence は before / after diff とともに保持できる。commit / amend は authority がある場合だけ行う。

要求、production behavior、scope の変更が必要なら gate 内で再設計せず authority / incomplete boundary に返す。権限内で閉じない、必要な evidence を得られない、同じ evidence で進展しない場合は stop-incomplete とする。

`test-accepted` または `not-applicable` の snapshot だけを Completion Gate へ渡す。後続の writing-only correction で test semantics が変わる場合は writing-only exception で受け入れず、この gate の affected review に戻す。
