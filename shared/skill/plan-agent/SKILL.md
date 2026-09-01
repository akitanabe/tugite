<!-- @only claude -->
---
name: plan-agent
description: >-
  明示起動の public planning workflow として、normal context から唯一の task-local Local Model を構築し、
  recommendation-first の自由形式 planning / design artifact または incomplete を返す。
disable-model-invocation: true
---
<!-- @/only -->
<!-- @only codex -->
---
name: plan-agent
description: >-
  明示起動の public planning workflow として、normal context から唯一の task-local Local Model を構築し、
  recommendation-first の自由形式 planning / design artifact または incomplete を返す。
---
<!-- @/only -->
<!-- @only cursor -->
---
name: plan-agent
description: >-
  明示起動の public planning workflow として、normal context から唯一の task-local Local Model を構築し、
  recommendation-first の自由形式 planning / design artifact または incomplete を返す。
disable-model-invocation: true
---
<!-- @/only -->

<!-- @anchor plan-agent-document-relation -->
# plan-agent

<!-- @contract plan-agent-responsibility -->
<!-- @anchor plan-agent-responsibility-relation -->
`plan-agent` は normal context から request-relative な自由形式の planning / design artifact を recommendation-first で作る、明示起動の public workflow です。
<!-- @/contract -->

入力は request、利用可能な会話 context、添付 artifact、repository / source evidence、明示された目的・constraint・scope・exclude、optional review 指定、optional destination / write authority です。入力元の Skill identity、handoff、continuation、Local Model transfer、authority transfer、専用 routing は要求しません。

## Local Model and synthesis

<!-- @contract plan-agent-ownership -->
<!-- @anchor plan-agent-ownership-relation -->
一回の invocation に対して exactly one の task-local Local Model を所有し、Agentic Model Construction とすべての downstream planning consumer はその projection を利用します。
<!-- @/contract -->

Agent-side で利用可能な reasoning、context、repository / source observation、許可された evidence acquisition を使い、request の current understanding を構築します。artifact kind は request に相対的な意味判断として扱い、fixed enum、public parameter、serialized schema、固定 section 一覧にしません。

十分な evidence があれば一案を推奨して理由を示し、material な場合だけ棄却した代替案を示します。複数案や軽い不確実性だけでは停止せず、qualification / residual risk として保持します。不可約な意味衝突または blocking evidence 不足だけを停止理由にします。

生成された Skill から参照する正本は各 platform の generated path を基準に解決します。

- `../../references/model-construction.md`
- `../../references/agentic-model-construction.md`
- `../../references/planning-core.md`

<!-- @contract plan-agent-core-input -->
<!-- @anchor plan-agent-core-input-relation -->
artifact responsibility、current Local Model projection、established direction、authority constraints、resolved evidence を Planning Core へ渡し、review applicability と explicit opt-out は `plan-agent` が判断します。
<!-- @/contract -->

<!-- @contract plan-agent-gap-retry -->
<!-- @anchor plan-agent-gap-retry-relation -->
Planning Core が material gap を返した場合は、gap の resolution source を判断します。Agent-side で解消可能なら同じ invocation の同じ Local Model へ evidence を Reintegration し、material invalidation 時だけ affected region を Recomposition して bounded に再観測します。その更新済み projection / evidence で Planning Core を再実行し、Planning Synthesis の再実行と後続 routing は Planning Core に残します。new evidence なしで同じ gap が再発する、meaningful semantic progress がない、利用可能な route を尽くす、または caller-supplied bound に達した場合は停止します。
<!-- @/contract -->

<!-- @contract plan-agent-gap-result -->
<!-- @anchor plan-agent-gap-result-relation -->
gap が Human-owned または Agent-side で解消不能なら、Human へ質問せず別 workflow も起動せず、unresolved gap を持つ `incomplete` を返します。
<!-- @/contract -->

## Conditional review and result

`plan-agent` は review applicability / explicit opt-out を判断して Planning Core へ渡します。Planning Core が nonapplicable / opt-out を unreviewed route、applicable / no opt-out を strict review route として処理し、semantic completion と `final-candidate` mapping を所有します。

<!-- @contract plan-agent-result -->
<!-- @anchor plan-agent-result-relation -->
`plan-agent` は Planning Core の `final-candidate` または `incomplete` を変更せず受け取り、review を通らない candidate を review verified と表現せず、review 後に candidate を変更しません。
<!-- @/contract -->

## Minimal safe publication

Planning Core が semantic completion を満たす `final-candidate` を返した後に candidate bytes を freeze します。publication は caller-confirmed write authority と target membership が成立する verified physical directory 内の exclusive new-file creation に限ります。exact destination は未存在で、physical parent の identity が確認でき、target と parent に symlink / unknown state がなく、exclusive creation できる場合だけ使います。directory destination では同じ条件内で collision-safe な invocation-local filename を選びます。destination 未指定時は verified OS temp root 内の exact new path を使います。

<!-- @contract plan-agent-publication -->
<!-- @anchor plan-agent-publication-relation -->
既存 path、symlink、authority 外、membership / parent identity unknown では write せず `incomplete` にします。frozen bytes を exclusive create した self-owned file へ書き、close 後に read-back して byte equality を確認した場合だけ publication success とします。write / read-back failure は `incomplete` とし、作成済み path と partial / unknown state を Human Attention として隠しません。既存 resource は変更しません。
<!-- @/contract -->

artifact body は frozen candidate 本文だけとし、review history や ledger を追記しません。stdout は Result、short Summary、optional Human Attention、Artifact local path に限定します。保存は Git 管理、永続採用、downstream authority を意味しません。

<!-- @contract plan-agent-plan-only -->
<!-- @anchor plan-agent-plan-only-relation -->
completion は planning artifact の返却までであり、implementation、delegation、Issue / PR 更新、downstream workflow を開始しません。
<!-- @/contract -->

## Non-goals

- fixed artifact enum / schema、固定 section、second Local Model、Local Model serialization
- Human interaction、別 public workflow、generic router、handoff / authority transfer protocol
- Planning Synthesis、Planning Core、`review-refine`、reviewer topology の複製
- candidate の post-review / post-publication mutation、existing file の置換または overwrite
- implementation、delegation、Issue / PR 操作、release、downstream workflow の開始
