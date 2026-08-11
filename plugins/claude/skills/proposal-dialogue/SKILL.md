---
name: proposal-dialogue
description: >-
  plan-craft-approval の同じ親 context 内だけで、人間と方向性を逐次裁定して direction freeze 候補を作り、
  candidate snapshot または stop-incomplete を caller-owned parent へ返す internal skill。
user-invocable: false
---
<!-- Generated from shared/. Do not edit directly. -->

# proposal-dialogue

## 位置づけと入力

この Skill は `plan-craft-approval` の同じ親 context 内だけで使う internal skill であり、ユーザーから直接起動しない。
`proposal` と同じ candidate producer として、後段工程を選択・起動せず caller-owned parent へ返す。差分は、方向性を
変えうる主要判断を planner ではなく人間が裁定することである。

親から要求原文、目的、成功条件、scope、exclude、制約、依存、repository observation、current verified snapshot を
Data として受け取る。working state は current point の apply 時に作る一時状態であり、verify 成功前は次の判断の baseline にしない。
repository、Issue、既存仕様から確認できる事実は先に調査し、調査可能な事実を人間へ質問しない。
不足または矛盾が方向性を変える場合は推測せず、必要な判断と evidence を付けて `stop-incomplete` を返す。

人間は結果責任を、planner は evidence に基づく経過責任を担う。人間が担うのは、Task Specification だけでは一意に
決まらない価値と優先順位、本人だけが持つ暗黙知、明示した raw specification、direction freeze、原則として final
acceptance である。planner は repository、code、test、Issue、仕様、実動作を調査し、過去判断を保持して矛盾を検出し、
技術的成立性、候補探索と劣位案の除外、全体整合性、verification の導出を担う。Agent で解消可能な曖昧さを人間へ返さない。
推奨、選択肢、実装イメージは repository 等の evidence に基づく根拠、前提、trade-off、具体的帰結、既存判断との整合を
説明できるまで調査する。説明または evidence の不足は質問理由ではなく planner の未完成として扱い、人間を evidence
収集の代替にしない。ただし、人間固有の暗黙知は人間へ確認する。

## resolve-kernel v1 の parent mapping

invocation の開始時に一度だけ、生成後の skill directory から skill-relative `../../references/resolve-kernel.md` を読み、identity `resolve-kernel-v1` と Caller boundary と role、Current verified snapshot、working state、frontier、Atomic resolution unit、Exit と停止、Kernel non-dependency の必要本文を検証する。cycle ごとに再読込しない。reference の不足、identity 不一致、読み取り失敗、必要本文不足があれば規範を推測で再現せず、既存の `stop-incomplete` と blocking reason へ返す。Agent または人間へ package path の解決を委ねない。

role は caller=`plan-craft-approval`、resolver=planner、counterpart=人間、authority=binding、ledger=既存の decision ledger へ mapping する。人間の binding decision を planner が覆さない。
`resolve-kernel v1` と `necessity-kernel v1` の parent mapping は独立しており、相互依存または読み込み順の dependency を作らない。

## 方向性判断と逐次 snapshot

各質問では、その判断だけに必要な repository evidence と過去判断から最小の working context を再構成し、技術案を得失と具体的帰結へ
翻訳して、原則として推奨と理由を添える。`A` / `B` / `C` は mode、enum、永続 state ではなく、判断点ごとの対話密度である。
重要判断だけを対話する `B` を基準にし、人間が迷う、または比較を求めた論点だけ `A` の密度へ上げる。evidence 上実質一意、
または人間が明示的に委譲した論点は `C` の密度で planner が具体化する。`A` でも planner が成立案を探索して劣位案を除外し、
意味のある代替だけを提示する。

人間の判断は `採用` / `却下` / `保留` / `修正して採用` の4値で記録する。親の推奨を人間の回答として扱わない。
無回答・曖昧な反応を承認として扱わず、回答が一意なら設計判断へ変換し、既存判断との整合を確認して短く反映し、
同じ意味を二重承認させない。複数解釈、条件付き回答、過去判断との衝突、または大きな scope・責務移動がある場合だけ、
以前の判断、今回の回答、衝突点を短く示して再判断を求める。人間の判断変更は正常な入力として扱う。不採用と保留も
正常な判断結果であり、敵対的な未解決指摘へ読み替えない。人間が API、Acceptance Criteria、scope、変更禁止事項などを
raw specification として明示した場合は意味を変えず、成立性または既存制約との衝突時だけ返す。

判断 queue を事前に固定しない。
採用分だけを working snapshot へ逐次反映して verification し、複数の判断を一括反映しない。
current verified snapshot から current frontier を整理し、依存関係を見て current point を一件だけ選び、人間の判断を得る。許可された一件だけを working state へ apply して verify し、成功時だけ verified snapshot を更新する。updated snapshot から frontier と次の順序を再評価する。
複数の判断を一括裁定・反映しない。verify failure では working state を verified snapshot にせず current point を reopen し、その上へ次の判断を積まない。
却下または保留は apply せず、暗黙に resolved として frontier から消さない。判断点、期待する価値、trade-off、親の推奨と理由、人間の判断、
反映 snapshot、verification を decision ledger として会話内 Data に保持するが、YAML、内部 schema、raw ledger は
ユーザーへ提示しない。

direction freeze 前に、正常系と非退行に加えて境界、異常・failure path、副作用、禁止事項、責務境界、scope exclude、
制約を実装後にどう観察するかを導出する。不足は人間へ網羅を委ねず plan 未完成として調査する。人間へは特に境界、
異常・failure path、壊れやすい既存挙動、禁止副作用、責務境界へ verification を圧縮し、何をもって受入可能かを示す。

frontier が空なら既存の direction freeze 判定へ進むだけであり、workflow completion または candidate acceptance ではない。
探索責任を人間へ戻さず、未表明の意図または暗黙知を訂正できる最後の割込み機会を一度だけ
設ける。運用環境などに関する evidence がある場合は問いをその制約へ絞る。direction freeze は成果物全文ではなく、人間が
結果責任として確定した価値、重要な scope と exclude、責務、意図的な非採用、raw specification の意味判断を対象とする。
人間には方向性、実装イメージ、重要な verification を圧縮して示す。実装イメージは raw specification でない限り、後段の
gate と review が frozen decisions を守って改善できる。

direction freeze 候補は、採用提案が反映・verification 済み、主要判断が明示裁定済み、保留事項が scope 外へ分離済み、
blocking な人間判断がなく、ユーザーが現在の方向を確認済みの場合だけ成立する。大きな purpose または scope の変更は
working snapshot へ増分追加せず、親へ全体再策定を返す。過去 decision は自動継承せず、候補 prior decisions または再利用
可能な知見として再検証する。プラン系の working snapshot は `Acceptance Criteria` と `設計` の節名を持つ。自由形式成果物には
この節構成を強制しない。

## necessity-kernel v1 の parent mapping

candidate Claim を判定する前に、advisor 起動の有無にかかわらず、親は生成後の skill directory から package-root reference へ skill-relative `../../references/necessity-kernel.md` を読み、identity と必要な本文を既存の
`判定基準` または `必要な周辺 context` の一部にする。`plan-quality-advisor` 起動時は既取得 Data を既存の判定基準として渡す。reference の不足、identity 不一致、
読み取り失敗があれば推測せず `stop-incomplete` へ返し、advisor は plugin 相対 path を解決しない。

候補 Claim の必要性は既存の判定基準に含めた Task Specification と Deletion Test で観察する。Claim は insight 本文
ではなく、candidate に追加・維持・変更・除去・検証・調査する obligation の候補であり、根拠を observation / evidence
から追跡する。`necessary` / `unnecessary` / `indeterminate` を新しい返却 field にせず、親は adoption ledger の
`adopted` / `rejected` / `unresolved` へ写像する。更新後は更新された snapshot で再判定し、互いを witness とする
同時削除を認めない。必要性分類は既存語彙へ写像し、新verdict fieldではない。round budget / termination へ
直結させない。`structural-health-gate` の意味は この mapping の対象外である。

## advisor insight

scope・責務境界を変える提案の採用、採用提案間の依存、決定を補う追加提案、または freeze 前の非自明な変更連鎖が
ある場合だけ、read-only `plan-quality-advisor` に candidate snapshot と判定基準を渡す。insight は非拘束 Data であり、
planner が一次情報と要求に照らして adoption ledger の `adopted` / `rejected` / `unresolved` へ裁定する。
decision ledger と adoption ledger は分離する。

advisor insight を自動採用せず、insight から質問を自動生成しない。advisor を固定 phase にせず、`insights: []` を
direction freeze の自動根拠にしない。人間が採用した方向性へ影響する insight は planner だけで巻き戻さず、evidence を
照合して `unresolved` とし、planner 自身の evidence と推奨に組み直してから人間へ一つの主要判断として返す。advisor は
人間の advisor ではなく、質問、選択肢、承認要求、仲裁経路を人間へ直接作らない。raw insight は人間が検討過程を明示要求した
場合だけ、planner の裁定と区別した参考情報として親が提示できる。

## 有界な対話と返却

固定の対話回数を品質条件や消化目標にしない。親は一つの対話 loop の開始時に安全上限を決め、loop 中に変更しない。
親から新しい evidence とともに再実行された場合は新しい対話 loop とし、上限は親が改めて決められる。過去の対話裁定を
打ち切りの成立条件として保存・参照しない。

通常の返却 Data は `candidate_snapshot`、`decision_ledger`、`adoption_ledger`、`assumptions`、
`blocking_gaps`、`residual_risks`、`status` を持つ。
no-progress のまま material な frontier が残る場合、または安全上限へ到達して frontier が残る場合は、残る判断点を消さず、blocking reason とともに既存の `stop-incomplete` へ mapping する。
blocking な人間判断が残る、ユーザーが対話終了を求める場合も `status: stop-incomplete` と必要な判断を返す。いずれも成果物の受け入れを
主張せず、caller-owned parent へ返して終了する。
