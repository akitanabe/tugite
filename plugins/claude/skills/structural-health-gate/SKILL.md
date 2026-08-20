---
name: structural-health-gate
description: >-
  明示起動された plan-family public workflow parent の internal context で、candidate の構造的局所性を evidence として評価する
  internal gate。成果物を再設計・直接編集せず、
  assessment と最終判断を public workflow parent へ残す。
user-invocable: false
---
<!-- Generated from shared/. Do not edit directly. -->

# structural-health-gate

この Skill は、candidate producer が返した candidate snapshot を後段処理へ渡す前に、局所修正で扱える
構造かを評価する。明示起動された plan-family public workflow parent の同じ context 内だけで使い、単独起動、ユーザーからの直接起動、
plan-family 外の workflow からの流用はしない。internal-only policy は維持し、gate 自身は後段の選択や caller routing を行わない。

## 入力

親は不変な `candidate_snapshot`、要求原文、requirements、design、Acceptance Criteria、verification、scope、
既知の repository evidence、producer の判断台帳と assumptions を渡す。必要な source や既存仕様を観測できない
場合は、欠けた evidence を Data として記録し、構造欠陥だと推測しない。

`caller_context` Data は必須の構造化 Data で、次の2 field/valueだけを受け付ける。

```text
{
  "workflow_family": "plan-family",
  "invocation": "explicit-public-parent"
}
```

- `workflow_family`: `plan-family`
- `invocation`: `explicit-public-parent`

これは明示起動された plan-family public workflow parent の同じ context であることだけを安定識別する。
producer の判断、成果物の行き先、後段処理を識別する値はこの gate の入力に含めない。

`caller_context` が欠落している、object でない、field/value が一致しない、または上記以外の field を含む場合は
`context 不成立` Data を親へ返す。この場合は candidate assessment を開始せず、candidate や resource を編集せず、
advisor、producer、その他の後段処理を起動しない。親は別 route へ切り替えず、未成立理由を添えて
`stop-incomplete` とする。

## reality-model-observation-kernel v1 の parent mapping

次の Loader Data が列挙値の唯一の正本である。

```text
path = ../../references/reality-model-observation-kernel.md
load_timing = after caller context is established and immediately before candidate assessment
identity = reality-model-observation-kernel-v1
required_sections = [Contract, Observable Reality Model, Method, Reintegration, Target Membership Check, Consumer Responsibilities, Non-goals]
failure = context-not-established
owner = structural-health-gate parent
delegate_path_resolution = false
```

この load は一度だけ行う。loader failure は `context-not-established` として親の既存 routing で `stop-incomplete` へ返す。これは Reality evidence 不足の `insufficient-evidence` と区別する。推測で継続しない。

Target は candidate の structural locality / health とする。requirements、candidate snapshot、repository evidence は authoritative context である。既存 taxonomy（duplicated source of truth、unresolved responsibility、requirements / design / AC / verification 不整合、state / responsibility、ripple、root defect、exception / stop 増殖）は Observation Viewpoint として使う。taxonomy を verdict にしない。

Target-relative Structural Problem だけを structural finding とする。local wording / detail は Incidental Finding、evidence / authority 不足は Uncertainty とする。同一因果を grounding できる surface だけを root problem に統合し、独立した problem を圧縮しない。根拠のない root 統合はしない。既存 assessment / output に grounding と observation / inference を残す。routing / accept の責務は変えない。

## 観測

caller context は明示起動された plan-family public workflow parent に限る。上記の `caller_context` が成立した場合だけ、
candidate の assessment を開始する。

次を、表現上の指摘ではなく構造上の因果として確認する。これらは Observation Viewpoint であり、
Kernel の taxonomy ではない。

- duplicated source of truth と、同じ判断が複数箇所で独立に更新される責務。
- 未解決の方向性または責務が、新しい設計判断を後段へ要求していないか。
- requirements、design、Acceptance Criteria、verification の対応漏れまたは矛盾。
- 用語、state、priority、responsibility の定義または遷移の不整合。
- 局所修正が他の要件、責務、成果物全体へ広く波及する ripple。
- 複数 finding に見える問題が、一つの structural defect から派生していないか。
- 例外、停止条件、stop contract の追加が増殖し、共通責務の欠落を覆っていないか。

長さ、複雑さ、finding 数だけを理由に `return` しない。局所修正で閉じる密度、詳細不足、文章上の重複は
通常の review で扱えるため、構造欠陥の evidence と混同しない。local wording / detail は Incidental Finding とし、
structural finding にしない。

## evidence Data

finding は同じ原因を統合し、少なくとも次を返す。同一因果を grounding できる surface だけを root problem に
統合し、独立した problem を圧縮しない。根拠のない root 統合はしない。

- `location`: candidate 内の箇所と、照合した要求または source。
- `non_local_reason`: local fix だけでは閉じない理由と、影響する責務または判断。
- `predicted_amplification`: review や実装で同じ欠陥が増幅すると予測する因果。
- `predicted_churn`: 修正の反復、例外増加、AC や verification の再変更として予測される churn。

各 finding は観測事実と推論を分ける。grounding と observation / inference を assessment / output に残す。
必須 field のいずれかを根拠付きで埋められない場合は
`insufficient-evidence` とし、`return` の根拠にしない。これは loader failure の `context-not-established` と混同しない。reviewer または advisor を使う場合、その出力は
evidence のみであり、candidate の採否、修正、再起草、工程の終了を決めさせない。

## 責務境界

この gate は成果物を再設計・直接編集しない。構造的に健全、不健全、または evidence 不足という assessment Data と
finding を返し、public workflow parent が最終的な `pass` / `return` / `stop-incomplete` を決める。
出力 Data は evidence と assessment に限定し、caller routing を決める値を持たない。
`pass` は後段処理の品質判断や成果物の受け入れを意味しない。

## 出力

`candidate_snapshot` の identity、`assessment`、finding 一覧、insufficient evidence、観測した source、未検証事項を
返す。Action と caller routing は親が行い、この Skill は後段処理を起動せず、resource へ書き戻さない。
