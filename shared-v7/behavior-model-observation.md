# Behavior Model Observation

## Identity and boundary

`Behavior Model Observation`（BMO）は、Model Observation を Behavior に適用する Tugite consumer method である。BMO は
**projection-only specialization** として、解決済みの Behavior の意味から `Expected Observation Model` を構成し、その導出十分性を評価する。
ここでの projection は将来の concrete observation で区別できるべき意味を表すものであり、Reality の検証や実際の観測ではない。

```text
Resolved Behavior + Relevant Authoritative Context
        ↓
Behavior Semantics
        ↓
Explore → Project → Evaluate
        ↓
Expected Observation Model + Collective Sufficiency
        ↓
STOP
```

BMO はこの停止点までを所有する。`Expected Observation Model` は bounded projection であり、calling workflow の task-local Local Model の所有・更新、第二の Local Model、または persistent state ではない。BMO の利用は caller が目的に応じて選ぶ optional specialization であり、mandatory phase や独立 lifecycle を導入しない。canonical Model Observation の一般理論を runtime に読み込まず、Tugite consumer が必要とするこの specialization の contract だけを保持する。

## Inputs and ownership

consumer は BMO に次を渡す。

- **Resolved Behavior** — 対象 Behavior の identity と中核的な意味が解決済みであること
- **Relevant Authoritative Context** — Behavior の意味、条件、または必要な観測可能差異を確定・補足する Context
- **Authority / responsibility boundary** — authority、precedence、BMO と consumer の責務境界

Behavior の identity または中核的な意味が未解決で、それが Expected Observation または Collective Sufficiency を変え得る場合、BMO は補完せず consumer に再解決を返す。missing Context の追加取得・再注入も consumer が所有する。

Context の authority はファイル種別や存在だけから推測しない。authority を持つ Context 間で precedence が未解決であり、その解決が Expected Observation または Collective Sufficiency を変え得る場合は、一方を選択したり silent merge したりせず、影響とともに `Relevant Unresolved Viewpoint` として保持する。

consumer が評価・設計・照合する対象と、BMO が導出根拠として使う reference / discovery Context は役割を分ける。評価対象 claim 自身を、その claim の Expected Observation の grounding に再利用しない。同一 artifact に両方がある場合も claim / section 単位で分離する。BMO の出力は consumer 固有の評価対象や成果物の存在・内容から逆算しない。

## Method

次の順序は reasoning direction であり、固定 state machine、mandatory phase、共通 serialized schema ではない。

### 1. Explore — Discover → Ground → Admit

Behavior Semantics と Relevant Authoritative Context から、成立・不成立の区別または Expected Observation を変え得る candidate を探索する。

**Meaningful variation** は、入力 Behavior の identity を保ったまま、条件・状態・操作の違いによって成立判定または Expected Observation が変わり得る variation である。値や組み合わせが違うだけで観測すべき意味が変わらないものは Admit しない。

同じ operation を契機としていても、独立して成立・不成立を判定できる意味は別 Behavior である。別 Behavior を variation として BMO の Expected Observation Model に混在させず、consumer が別途扱えるよう区別して返す。

candidate は Behavior または authority を持つ Context に grounding があり、かつ入力 Behavior の意味上の distinction である場合だけ `Admit` する。測定可能であること、既存 artifact・実装・テストに現れること、一般に重要であること、observer が想像できることだけでは admission の根拠にならない。grounding のない候補は推測で補完しない。

### 2. Project — Identify → Calibrate

Admit された Behavior Semantics と meaningful variation から Expected Observations を導出する。

Expected Observation は、**Behavior が成立している状態と成立していない状態を区別するために何を確認できる必要があるか**を表す、grounded な観測可能事実である。これは「何を確認するか」であり「どう確認するか」ではない。必要性を Behavior または authoritative Context に trace できるだけ具体的にし、根拠のない実装内部、threshold、policy、measurement、test technique を追加しない。

Behavior が条件・状態・操作間の relation として現れる場合は relation 自体を観測対象にできる。variation 固有の条件は Expected Observation の意味に保持し、条件を失った独立事実へ flatten しない。

### 3. Evaluate — Cover → Trim → Classify

Expected Observation Model 全体が、入力 Behavior の意味と Admit された meaningful variation を区別できるか評価する。

- **Cover** — 各 admitted variation の条件を保持し、同一条件下で Expected Observations が coherent であることを確認する。全入力値・状態・failure の列挙は目的にしない。
- **Trim** — Behavior-relative な判定を変えない observation、値・組み合わせ・内部手順の違いだけを理由とする observation を必須化しない。
- **Classify** — coverage と unresolved viewpoint に基づき Collective Sufficiency を分類する。

## Result contract

BMO は共通の serialized schema を要求しないが、consumer が意味を復元できる形で次を返す。

- Expected Observations
- Admit された meaningful variation と各 condition / relation
- 各 Expected Observation と Behavior Semantics または authoritative Context の grounding
- Relevant Unresolved Viewpoints と、現在確定できない意味および必要な情報
- Collective Sufficiency
- `Insufficient` の場合の未カバーな Behavior semantics / variation と、現在の model で区別できない理由

### Collective Sufficiency

Collective Sufficiency は、入力された Behavior に対する Expected Observation Model 自体の導出十分性である。consumer 固有の成果物・評価対象・downstream quality、workflow readiness、Reality verification、Real / Reality の完全性、Behavior 自体の真理を判定するものではない。

- **Sufficient** — Behavior の意味と Admit された meaningful variation が、相互に coherent な Expected Observations 全体で区別でき、Relevant Unresolved Viewpoint が残っていない。
- **Insufficient** — Behavior の意味または Admit された meaningful variation のうち、Expected Observations で区別できないものが具体的に残っている。未カバーの意味と理由を保持する。現在の入力から補える場合は Explore または Project へ戻って再導出する。
- **Indeterminate** — 既知の coverage gap は確定できないが、Relevant Unresolved Viewpoint が残るため十分性を確定できない。

### Relevant Unresolved Viewpoint

次の両方を満たす論点だけを保持する。

1. 解決結果により Expected Observations または Collective Sufficiency が変わり得る
2. Behavior または Relevant Authoritative Context に、未確定であることを示す concrete signal がある

単なる論理的可能性、generic best practice、「記述されていない」という事実だけでは unresolved としない。authority conflict、Behavior が参照する未定義条件、明示的な曖昧さ・TODO などは signal になり得る。BMO は取得先や具体的 Action を決めず、consumer に必要情報を返す。

## Stop boundary and reintegration

Expected Observation Model と Collective Sufficiency を返したら停止する。BMO は次を所有・開始しない。

- actual observation、Concrete Observation、Reality verification
- test、assertion、measurement、mock / stub / probe、instrumentation などの technique 選択
- test / execution / I/O や結果の取得
- Research Agent・missing Context の acquisition / dispatch
- consumer 固有の finding、verdict、severity、accept / reject、remediation、implementation change

consumer から新しい authoritative Context が再注入され、既存の variation・grounding・Expected Observation が無効になった場合だけ、最後に信頼できる段階まで戻って依存する導出を再適用する。stale な導出を新しい導出と並置して残さない。Behavior の identity または中核的意味が変わる場合は、BMO 内で再定義せず consumer に Behavior の再解決を返す。

## Case E semantic contrasts

次の対照は、BMO の入力から結果までを追加仕様なしに読み合わせるための代表例である。例中の Behavior と Context は、示された意味だけを authority として持つ。

| 対照 | BMO の判定と結果 |
| --- | --- |
| 同じ Behavior の meaningful variation | Behavior の identity を維持し、条件・状態・操作の差で成立判定または Expected Observation が変わり、Behavior / authoritative Context に grounding がある場合だけ Admit する。条件を Expected Observation に保持する。 |
| 同じ operation に関係する独立 Behavior | 独立して成立・不成立を判定できる意味は variation に畳み込まず、別 Behavior として consumer に返す。BMO の Expected Observation Model は元の Behavior の意味だけを cover する。 |
| 評価対象 claim の自己 grounding | consumer が評価する claim / artifact 自身からその claim の Expected Observation を導出しない。自己 grounding は admission の根拠にならず、評価対象から分離された入力 Behavior の意味または authoritative Context が必要性を説明できる場合だけ Admit / Project する。 |
| independent な grounding | Behavior または評価対象から分離された authoritative Context が Expected Observation の必要性を説明できる場合、その根拠を保持して Admit / Project する。 |
| authority conflict がない、または precedence が解決済み | 解決済み authority に従って Behavior Semantics を導出し、conflict のない範囲で通常どおり Cover / Classify する。 |
| authority conflict があり precedence 未解決 | 解決結果が Expected Observation または sufficiency を変え得るなら silent merge / 選択をせず Relevant Unresolved Viewpoint とし、通常は `Indeterminate` とする。 |
| Admit された全 variation が covered | Behavior の意味と全 variation が coherent に区別され、Relevant Unresolved Viewpoint がなければ `Sufficient`。これは actual observation や downstream quality の成功を意味しない。 |
| Admit された variation の一部が uncovered | 未カバーの variation と区別できない理由を返し、`Insufficient` とする。現在の入力で補える間は再 Explore / Project し、補えなければ partial result として停止する。 |

## Minimal operational question

> この Behavior が成立している状態と成立していない状態では、何が観測可能に異なる必要があるか。その差異は Behavior または authoritative Context に grounding されているか。Expected Observations 全体で、Behavior の意味と admitted meaningful variation を十分に区別できるか。
