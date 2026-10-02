<!-- Generated from shared/. Do not edit directly. -->

# Test Acceptance Gate

## Identity and responsibility

Test Acceptance Gate は candidate commit の changed test artifact を Unit acceptance evidence として信用できるか確認する独立した gate である。Parent QA が必要な evidence を設計し、この gate は artifact の coverage / validity を観測する。Completion Gate は writing-only の最終確認を所有する。

```toml
policy_id = "impl-lead-test-acceptance-v1"
lifecycle = ["implementation", "parent-qa", "risk-directed-review", "candidate-commit", "test-acceptance-gate", "completion-gate", "unit-accepted"]
applicability = "candidate diff changes automated test, fixture, oracle, or executable test contract"
test_only = "applicable"
production_only = "not-applicable"
reviewers = ["test-coverage-reviewer", "test-validity-reviewer"]
snapshot = "same immutable candidate commit and comparison base"
reviewer_access = "fresh / context-isolated; read-only / report-only"
parent_ownership = ["obligation", "oracle", "validation plane", "Expected Observation", "necessary verification", "mutation applicability", "finding adjudication", "Unit acceptance"]
correction = "implementation correction; rerun Parent QA and affected Test Acceptance review"
```

## Applicability and input packet

親は expected accepted baseline と candidate commit の diff から changed test artifact と変更の種別を識別する。automated test、fixture、oracle、executable test contract の追加・変更・削除を対象とし、skip / assertion 弱体化も変更に含む。Gunte predicate / contract や EVAL case も executable test contract として扱う。test-only Unit は必ず applicable とする。production code だけの Unit は `not-applicable` とし、既存テスト全体の再審査を要求しない。

両 reviewer に同じ Unit Data、Task Spec、comparison base、candidate commit / immutable diff、changed artifact 一覧、AC、親が確定した Expected Observation、surrounding context、Parent QA baseline evidence、test execution evidence、mutation applicability と applicable mutation evidence を渡す。fixture の authoritative source と input consistency を確認できる context も含める。不足する evidence は実行結果や reviewer Pass で補わない。

coverage reviewer は必要な observable behavior と test artifact の対応、validity reviewer はその artifact が信頼できる verification evidence かを観測する。test input は意図した振る舞いと対象となるもっともらしい誤実装の結果を区別できなければならない。test framework / style の好み、fixed quality score / threshold は受入基準にしない。

mutation applicability と evidence generation は Parent QA / execution が所有する。reviewer は mutation を実行せず、渡された evidence が対象 obligation の meaningful failure protection を支えるか観測する。恒久的または常時の mutation testing は要求しない。

## Programmatic Flow

### test-acceptance-review-control

Trigger: Parent QA と必要な risk review が Green で candidate commit が存在する。

Inputs: Unit Data、expected accepted baseline、candidate commit / immutable diff、changed test artifact 一覧、applicability、共通 input packet、repository state。

Procedure:

1. candidate commit が expected accepted baseline から当該 Unit の全変更だけを含み、HEAD が candidate commit と一致し、index と working tree が clean であることを確認する。不一致では reviewer を起動しない。
2. changed test artifact がない場合は `not-applicable` を返す。ある場合は同じ immutable candidate snapshot と共通 input packet を両 reviewer に渡す。
3. fresh / context-isolated な `test-coverage-reviewer` と `test-validity-reviewer` を起動し、read-only / report-only で finding Data を回収する。両結果の回収まで target に writer を入れない。
4. 両結果を `parent-adjudication-required` として親へ返す。Flow 内で finding の採否や Unit acceptance を決めない。

Outcomes: `not-applicable`、`parent-adjudication-required`、または candidate integrity / input / reviewer result の不足を伴う `stop-incomplete`。

## Parent adjudication and correction

親は両 reviewer の finding を evidence、AC、scope、risk と照合して `adopted`、`rejected`、`unresolved` に裁定する。material finding がないことや reviewer Pass だけを accept 根拠にしない。必要な evidence が十分で、adopted correction が完了し、acceptance を妨げる unresolved finding がない場合だけ `test-accepted` とする。

adopted finding は通常の implementation correction として元 Implementer または適した fresh Implementer へ渡す。semantic な test correction を含められるため、Completion Gate の writing-only bounded correction には制限しない。変更後は Parent QA と applicable verification を再実行し、影響する risk review を確認して同じ未受入 Unit の candidate commit を amend する。新しい immutable candidate に affected coverage / validity goal の fresh review を行い、親が再裁定する。変更の影響を受けない review evidence は before / after diff とともに保持する。

AC、production behavior、scope、Unit responsibility の変更が必要な finding は gate 内で意味を再設計せず、既存の authority / incomplete boundary へ返す。input authority 内で閉じない、必要な evidence を得られない、同じ evidence で進展しない場合は `stop-incomplete` とする。

`test-accepted` または `not-applicable` の candidate だけを Completion Gate へ渡す。後続の writing-only amendment は、親が before / after diff から coverage / validity evidence が引き続き有効か確認する。影響する test semantics がある場合は writing-only exception で受け入れず、Test Acceptance review が必要な correction として authority / incomplete boundary へ返す。
