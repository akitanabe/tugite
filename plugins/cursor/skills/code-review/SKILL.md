---
name: code-review
description: >-
  ユーザーが `code-review` を明示した場合、または Tugite の code-review によるコードレビュー意図が明確な場合に使う。
  対象 change set を captured snapshot に固定し、専門 reviewer を振り分け、evidence 検証済み findings を報告する。
  修正、採否裁定、レビュー対象への書き込みは行わない。`impl-lead` および plan-family workflow の実行中には内部工程としては起動しない。
---
<!-- Generated from shared/. Do not edit directly. -->

# code-review

この Skill は、Human が任意のタイミングで専門 reviewer 群を直接利用するための public workflow である。
`impl-lead` の内部 review および `review-refine`（成果物 snapshot への bounded review loop）とは独立の兄弟
workflow として動く。親は対象範囲の確定と snapshot の固定、Human 意図の解釈、reviewer 選択、dispatch、
findings の evidence 検証・正規化・明白な重複統合、Human への報告を行う。

本 skill は受入裁定を行わない。

## 発火制御

- ユーザーがこの Skill を明示した場合、または Tugite の `code-review` によるコードレビュー意図が明確な場合だけ起動する。
- 自然言語の作業内容や現在の context から暗黙に起動しない。
- `impl-lead` および plan-family public workflow の実行中に、内部工程としては起動しない。それらは既存経路を使う。
- 各 platform の invocation metadata は上記の発火契約を表し、その範囲を拡張しない。

## 責務境界

親の責務は、対象の確定、captured snapshot の固定、意図の解釈、reviewer の選定と起動、findings の evidence
検証と正規化、明白な重複の統合、Human への報告である。

次は責務外である。

- 修正ループ、finding の採否裁定、実装
- レビュー対象（user の working tree、repository、成果物）への書き込み Action

reviewer はコードを修正しない。test 実行のための一時実行用 copy への書き込み、および親が snapshot 固定のために
構築する captured copy への構築時書き込み（対象 file の commit / index 化を含む。構築完了後は read-only）は、
レビュー対象への書き込みに含めない。

## 対象

全対象 reviewer の指摘範囲は基準 commit からの diff に限定されている。対象は常に、基準（base）を持つ
change set として確定する。ファイル・ディレクトリ指定は change set をその path へ絞り込む指定として扱い、
独立した全文レビュー対象にはしない。基準を持つ change set を構成できない対象（例: 変更のない file の全文
レビュー要求）は、現行 reviewer 群の契約で扱えないことを理由に付して Human に返す。

未指定時の既定対象は、現在の branch の変更一式である。これは base branch との diff、未 commit 変更、
untracked の新規 file を含む（PR に入る予定の全変更）。base branch 直上で branch diff がない場合は
working tree の変更（untracked 含む）のみを対象にする。base を特定できない、対象が空、または解釈が割れる
場合は推測せず Human に確認する。親が選んだ対象は findings 報告の冒頭に必ず明示する。

## snapshot 固定

親は対象確定時に対象内容を一度だけ capture し、以後の reviewer handoff、evidence 検証、報告はすべてその
captured snapshot に対して行う。working tree のその後の変更は review 結果に影響させない。

captured copy は次を満たす。

- 既定対象に含まれる untracked 新規 file を保持できる。
- reviewer が参照する path は live working tree ではなく captured copy を指し、review 中に writer を入れない。
- reviewer の周辺 context 読取も captured copy 内で完結する。
- change set の全 file（untracked 新規 file を含む）が、captured copy 内で reviewer から複製可能な tracked 状態になる。

## reviewer 振り分け

対象 reviewer 集合は次に限る。責務の意味は各 reviewer 正本（runtime inventory に露出する description と
agent 定義）を根拠とし、この本文に責務対応表を複製しない。

- `test-quality-reviewer`
- `responsibility-boundary-reviewer`
- `security-side-effect-reviewer`
- `static-performance-reviewer`
- `writing-principles-reviewer`
- `over-engineering-reviewer`

plan 系（`plan-adversarial-reviewer`、`plan-quality-advisor`）と implementer 系 agent は対象外である。
プラン成果物のレビューは `review-refine` の責務のままとする。

選択は親の判断とし、意図に対応する必要最小限の集合（1..n）を選ぶ。選択理由は報告に含める。全 reviewer
一律起動の固定 phase、スコアリング、decision table、選択の唯一正解は作らない。

親は選択時に、対象と各 reviewer の入力契約（base 付き diff、AC・制約、test 結果などの必須入力）の適合を
確認し、入力契約を満たせる reviewer だけを選定する。選定可能な reviewer が 0 件になった場合は reviewer を
起動せず、理由を付して Human に返す。

対象 reviewer 6件中5件（`writing-principles-reviewer` 以外）は、タスク要約と AC・制約を必須入力とし、
不足時は判定せず親へ差し戻す入力契約を持つ。親は起動ごとに、観測（change set の内容、commit message、
紐づく issue / PR）と Human 入力から「タスク要約」と「受入境界 Data（review 意図、明示制約、利用可能な
場合は対応する issue / PR の Acceptance Criteria）」を構成し、handoff の必須入力を空にしない。明示 AC が
存在しない場合は、親が構成した受入境界 Data を AC 相当の判定基準として handoff の AC の位置に渡す。
handoff 上で必須入力の欠落を宣言する付記はしない。

ただし AC への適合そのものを判定の軸とする reviewer（`over-engineering-reviewer`、
`test-quality-reviewer`）は、明示 AC（issue / PR の Acceptance Criteria 等）または Human が明示した
受入境界・制約を確認できる起動でだけ選定する。親が review 意図から合成した判定基準だけでは選定しない。
それ以外の reviewer は、合成した受入境界 Data を context として選定できる。

test 結果を必須入力とする reviewer（`test-quality-reviewer`、`over-engineering-reviewer`、
`static-performance-reviewer`）を選定する場合、親は repository の native な test 手段を実行して結果を
渡すか、Human 提供の test 結果を使う。実行は captured copy とは別に派生させた一時実行用 copy 上で行い、
その書き込みを user working tree にも reviewer が参照する captured copy にも影響させない。安全に実行できず
Human 提供もない場合は該当 reviewer を選定せず、その理由を報告に含める。

reviewer が入力不足を返した場合は finding として扱わず、親が入力を補正して再投入するか、その reviewer の
観点を実行できなかった事実として報告する。

Human の明示 reviewer 指定は尊重する。指定 reviewer が対象に不適合な場合は、理由を付して Human 確認へ返す。

## behavior-observation-kernel v1 の test-quality-reviewer mapping

`test-quality-reviewer` を選定したときだけ、親は次の Loader Data で load し、検証済み本文を既存の `判定基準` または `必要な周辺 context` へ注入する。他 reviewer へ流さない。load 失敗時は当該 reviewer を選定せず理由を報告する。返却契約（報告のみ、採否しない）は変えない。

```text
path = ../../references/behavior-observation-kernel.md
load_timing = immediately before test-quality-reviewer invocation
identity = behavior-observation-kernel-v1
required_sections = [Contract, Method, Reintegration, Consumer の責務, 非目標]
failure = 当該 reviewer を選定せず理由を報告
owner = invoking parent
delegate_path_resolution = false
```

## 実行

captured snapshot を基準に read-only reviewer を起動する。全 reviewer が同一の captured snapshot を参照し、
read-only と isolation が保証できる場合だけ並行起動できる。

各 reviewer へは自己完結 handoff を、各 reviewer の既存入出力形式のまま渡す。reviewer の契約は変更しない。
handoff に含める必須入力は次である。

- captured snapshot
- タスク要約
- diff または対象全文
- base / commit range
- 変更ファイル一覧
- 意図から導いた review goal
- 受入境界 Data
- 必要な test 結果
- 必要な周辺 context

## findings の検証と報告

親は各 finding を `source_reviewer`、対象位置、evidence とともに正規化し、evidence を captured snapshot
および handoff で渡した test 結果 Data と突き合わせて検証する。evidence を確認できない finding は除去せず、
その旨を付して区別する。明白な重複は統合し、統合元 reviewer を保持する。

採否の裁定は行わず、全件を Human へ報告する。severity や件数を合否に変換せず、Pass/Fail を出さない。
主成果物は会話への構造化された findings 報告のみとし、永続 artifact は作らない。各 finding は reviewer、
対象、evidence、指摘内容が自己完結し、Human が後続 workflow への入力にそのまま使える形とする。
