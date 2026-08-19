<!-- Generated from shared/. Do not edit directly. -->

# Behavior Observation Kernel v1

Kernel identity: `behavior-observation-kernel-v1`.
Kernel dependencies: `none`.

この共有規範は、解決済みの Behavior から「その成立・不成立を区別するために何を観測できる必要があるか」を導出する共有 Method である。正本はこのファイルであり、各 platform の配布物では `references/behavior-observation-kernel.md` として生成される。各 role は全文を複製せず、この規範との自分の既存返却形式への mapping だけを持つ。parent は package reference を読み、role には既存の判定基準または必要な周辺 context の一部として identity / 必要な本文を渡す。

Kernel 自体は planner、reviewer、test generator、test runner、または consumer 固有の出力形式ではない。異なる consumer が、それぞれの責務に応じて利用できる共通の導出手法を提供する。

中核となる考え方は次である。

> 観測観点は Behavior から導出する。Kernel は、Behavior が成立しているかどうかを区別するために、何を観測できる必要があるかへ変換する。

Kernel は一貫して Behavior-first とする。consumer 固有の評価対象、実装構造、mock、assert、具体的な I/O 手段を出発点にはしない。

意味上の結果は次で閉じる。

```text
Resolved Behavior + relevant Context
        ↓
Behavior Observation Kernel
        ↓
Expected Observations
Collective Sufficiency
Relevant Unresolved Viewpoints
```

## Contract

### 入力

consumer は次を Kernel へ渡す。

- **解決済みの Behavior**
- その Behavior を探索するために必要な **relevant Context**

Behavior の解決自体は consumer の責務とする。

ここで「解決済み」とは、対象 Behavior の identity と中核的な意味が consumer によって確定していることをいう。Expected Observations の導出に影響する周辺条件まで、すべて確定済みであることは要求しない。

未解決事項または新しい情報が Behavior の identity または中核的な意味を変え得る場合、Kernel はそれを内部で解決せず、consumer に再解決を委ねる。

Behavior は、一つのまとまりとして成立・不成立を問える意味的な振る舞いである。複数の Observation を必要としてよいが、独立して成立判定できる別 Behavior を混在させない。

Behavior の代表例には、外部的な意味として観測可能な次のようなものがある。

- 結果
- 状態遷移
- 意味のある非変化・保持
- 副作用
- 拒否・保護動作
- invariant
- 条件・状態・操作間の関係

これらは閉じた taxonomy ではなく、代表例である。

### relevant Context

consumer は、自身の scope と responsibility に応じて必要な Context を選択し、Kernel へ注入する。

必要に応じて、たとえば次を含められる。

- specification
- contract
- constraint
- invariant
- public surface
- 関連コード
- 周辺の既存テスト
- schema / configuration
- その他 repository 上の evidence

情報が期待 Behavior を規定する根拠になれるかどうかは、**ファイル種別ではなく authority によって判断する**。

既知の authority / precedence は、可能な範囲で consumer が解決してから注入する。Kernel は source type から固定的な優先順位を推測しない。

authority を持つ Context 間に conflict があり、precedence が解決されていない場合、Kernel は一方を選択したり統合したりしない。解決結果が Expected Observations または Collective Sufficiency を変え得る場合、Relevant Unresolved Viewpoint として保持する。

必要な Context が不足している場合、Kernel は「何を確定できないか」「何の情報があれば確定できるか」までは示せる。ただし、自身で scope を広げて追加 Context を取得しない。追加取得と再注入は consumer の責務とする。

Context が存在しないという事実だけでは、Relevant Unresolved Viewpoint としない。Behavior または注入された relevant Context に、当該情報が Behavior の成立判定または Expected Observations の導出に必要であることを示す具体的な signal がある場合に限り、missing Context を Relevant Unresolved Viewpoint として保持する。そのような signal がない場合、Collective Sufficiency は注入された Behavior と relevant Context に対する相対評価として扱う。

### consumer-owned evaluation context

Kernel の導出根拠と、consumer が自身の責務で評価・設計・照合する対象を混同しない。

- repository 上の既存仕様、関連コード、周辺の既存テストなどは、consumer の責務と authority 判断に従って reference / discovery Context として利用できる。
- Kernel は、consumer が何を評価・設計・照合するかを規定しない。
- consumer 固有の評価対象や成果物から Expected Observations を逆算してはならない。
- consumer が評価対象として扱う内容を、同じ導出において reference / discovery Context として再利用してはならない。
- reference / discovery Context と consumer 固有の評価対象の分離は、必ずしもファイル単位ではない。同一 artifact に authoritative input と評価対象が共存する場合、各 claim または section の役割を分離して扱う。
- 評価対象となる claim 自身を、その claim の評価に使用する Expected Observation の grounding として再利用してはならない。

Kernel が導出する Expected Observations は、consumer 固有の評価対象や成果物の存在・内容に依存せず、Behavior と relevant Context から説明できなければならない。

各 Expected Observation は、その必要性を grounding する入力 Behavior の意味、または authoritative Context を説明可能でなければならない。各 Relevant Unresolved Viewpoint も、未確定性を示す具体的な signal へ trace できなければならない。共通 serialized provenance schema は要求しない。

### 出力

Kernel は共通 serialized schema を持たず、意味上の結果として次を返す。

- **Expected Observations**
- **Collective Sufficiency**
- **Relevant Unresolved Viewpoints**

#### Expected Observations

Observation は次のように定義する。

> **入力 Behavior の成立・不成立を区別でき、その必要性が Behavior または authoritative Context に grounding されている観測可能な事実。**

Behavior が複数の観測可能な意味を持つ場合、それぞれを Expected Observation として取り出す。Observation 群全体で Behavior を十分に区別できることを求める。

Observation は **「何を確認するか」** であり、**「どう確認するか」** ではない。

Kernel は次の具体的な確認手段を選ばない。

- test
- assertion
- mock / stub
- database read
- API call
- real I/O

これらは consumer の責務である。

Expected Observation は、Behavior の成立・不成立を区別できるだけ具体的でなければならない。一方で、Behavior または authoritative Context が要求する以上に、実装構造や具体的な検証手段へ降りてはならない。

例:

```text
Behavior:
  権限のない利用者は対象を更新できない。

Expected Observations:
  - 更新が成立しない
  - 対象状態が変化しない
```

HTTP status、exception type、内部 call などが authoritative contract の一部なら Expected Observation になり得るが、根拠がなければ Kernel が具体化しない。

Observation は単一実行の結果だけに限定しない。Behavior が複数の条件・状態・操作間の関係として現れる場合、その関係自体を観測対象にしてよい。

Expected Observation が特定の meaningful variation にのみ適用される場合、その条件または関係を Observation の意味の一部として保持する。異なる条件に属する Observation を、条件を失った独立した事実として平坦化しない。

#### Collective Sufficiency

Collective Sufficiency は、**consumer 固有の成果物や評価対象の十分性ではなく、Behavior に対する Expected Observation model 自体の導出十分性**を表す。

これは、入力された resolved Behavior と relevant Context に対する相対評価である。consumer による Behavior resolution、scope selection、または Context 選択自体の完全性を保証しない。

意味上の状態は次の3つとする。

- **Sufficient** — 入力 Behavior の意味と Admit された meaningful variation を、相互に coherent な Expected Observations 全体で区別でき、Relevant Unresolved Viewpoint が残っていない。
- **Insufficient** — 入力 Behavior の意味または Admit された meaningful variation のうち、Expected Observations で区別できないものが具体的に残っている。
- **Indeterminate** — 既知の coverage gap は確定できないが、Relevant Unresolved Viewpoint が残るため十分性を確定できない。

`Insufficient` は既知の coverage gap を示す rework state でもある。現在の Behavior と relevant Context から不足を補える場合、Kernel は `Observe` または `Explore` へ戻り Expected Observation model を再構成する。最終的に `Insufficient` を返す場合は、未カバーの Behavior の意味または meaningful variation と、なぜ現在の Expected Observations では区別できないかを説明可能でなければならない。

consumer 固有の成果物や評価対象が十分かどうかは、consumer が Kernel の出力を自身の scope / responsibility に従って利用した後に判断する。

#### Relevant Unresolved Viewpoints

Relevant Unresolved Viewpoint として保持するには、次の両方を満たさなければならない。

1. 解決結果によって Expected Observations または Collective Sufficiency が変わり得る
2. Behavior または注入された relevant Context に、その論点が実際に未確定であることを示す具体的な signal がある

単なる論理的可能性、一般的な best practice、または「記述されていない」という事実だけでは Relevant Unresolved Viewpoint として保持しない。

具体的な signal には、たとえば次が含まれる。

- specification 内の曖昧な表現
- authority を持つ情報間の矛盾
- Behavior が参照しているが定義されていない条件
- precedence が未解決な複数の根拠
- Context 内に存在する明示的な TODO や未決事項

探索中に見つかったすべての不確実性を保持するわけではない。

Relevant Unresolved Viewpoint では次を示す。

- 現在何を確定できないか
- 何の情報があれば確定できるか

取得先や具体的な Action までは Kernel が決めない。

## Method

標準 Method は次の3段階とする。解決済み Behavior と relevant Context から観測モデルを導出するときに使う。

```text
Explore
  ↓
Observe
  ↓
Evaluate
```

これは固定 state machine ではなく、標準的な reasoning direction である。

### 1. Explore

Behavior を十分に観測するために、意味のある variation を探索する。

meaningful variation とは、入力 Behavior の identity を維持したまま、条件・状態・操作の違いによって、その成立判定または Expected Observations が変わり得る variation である。値や組み合わせが異なっても観測すべき意味が変わらないものは meaningful variation としない。独立して成立・不成立を判定できる別の意味は、同じ操作を契機としていても variation として取り込まず、別 Behavior として扱う。

内部 Method:

```text
Discover → Ground → Admit
```

#### Discover

Behavior と relevant Context から、意味を変え得る候補を広く拾う。

たとえば次のようなものを探索できる。

- variation
- boundary
- failure
- relation
- interaction
- その他 Behavior の意味を変え得る事項

関連コードや周辺テストなど、観測情報から候補を発見してよい。

Discover は recall 寄りでよい。候補を発見した時点では、それが期待 Behavior である必要はない。

#### Ground

発見した候補が、Behavior または authority を持つ Context に根拠を持つか確認する。

コードや周辺テストから候補を見つけることはできるが、そこに存在するという理由だけで期待 Behavior に昇格させない。

探索は広く行う一方、**不足している期待を推測で補完しない**。

候補は仮説として最後まで探索してよいが、十分な grounding がないまま Expected Observation へ進めない。

#### Admit

grounding できた候補だけを `Observe` へ進める。candidate は、入力 Behavior の meaningful variation または observable consequence である場合に限って Admit する。独立した別 Behavior は Admit しない。

grounding できない候補でも、Relevant Unresolved Viewpoint の条件を満たす場合は保持する。単なる一般論や論理的可能性は unresolved として残さない。

それ以外は Kernel の結果から除外する。

### 2. Observe

入力 Behavior の意味と、Explore で Admit された meaningful variation について、その成立・不成立を区別する Expected Observations を導出する。

Explore で grounding された observable consequence は、Expected Observation を特定するための候補として利用する。

内部 Method:

```text
Identify → Calibrate
```

#### Identify

Behavior またはその meaningful variation が成立しているかどうかを、何から区別できるか特定する。

見るべきものは現在実装の内部手順ではなく、**Behavior の意味**である。

#### Calibrate

Observation を、Behavior の成立・不成立を区別するために適切な抽象度へ整える。

- Behavior を区別できるだけ具体的である
- 「正しく動く」のように抽象すぎない
- Behavior / authoritative Context に根拠がない実装具体へ降りすぎない

結果は、具体的な test technique から独立した Expected Observation とする。

### 3. Evaluate

Expected Observation model 自体を評価する。

内部 Method:

```text
Cover → Trim → Classify
```

#### Cover

Expected Observations 全体で次を区別できるか確認する。

- 入力 Behavior の意味
- Explore で Admit された meaningful variation

Expected Observations は各 meaningful variation の条件を保持し、同一条件下で相互に矛盾してはならない。
複数の Observation が異なる結果を示す場合、その差が Behavior または authoritative Context に grounding された条件差として説明できなければならない。

目的は、すべての入力値や状態を列挙することではない。

#### Trim

新しい Behavior の意味を区別しない Observation を追加要求しない。

同様に、条件の組み合わせ、値の違い、内部手順が増えたという理由だけで追加観測を要求しない。

目指すのは最大列挙ではなく、意味上十分な coverage である。

#### Classify

Observation model は次の順で分類する。

1. 入力 Behavior の意味または Admit された meaningful variation を区別するために必要な Expected Observation が欠けている場合、`Insufficient` とする
2. 既知の coverage gap は確定できないが、Relevant Unresolved Viewpoint が残るため十分性を確定できない場合、`Indeterminate` とする
3. 入力 Behavior の意味と Admit された meaningful variation が、相互に coherent な Expected Observations によって区別され、Relevant Unresolved Viewpoint も残らない場合、`Sufficient` とする

`Insufficient` で、現在の入力から gap を補完可能な場合は terminal とせず `Observe` または `Explore` へ戻る。partial result として返す場合は未カバーの意味と判定理由を保持する。

この分類は Expected Observation model についてのものであり、consumer 固有の成果物・評価対象・workflow の品質判定ではない。

## Reintegration

`Reintegration` は Method 全体に掛かる横断規則とする。

新しい事実、evidence、constraint、Behavior の理解が得られた場合:

1. 新しい情報を現在の Behavior model へ統合する
2. 既存の導出を再評価する
3. 以前の分解が信頼できなくなった場合、まだ信頼できる地点まで戻る
4. そこから後段の Method を再適用する

ただし、新しい情報によって入力 Behavior の identity または中核的な意味が信頼できなくなった場合、Kernel 内で Behavior を再定義しない。consumer が Behavior を再解決した後、その入力から Method を再適用する。

## Exploration Lenses

探索のための Lens は、網羅 taxonomy ではなく **類推の補助** とする。

### Normal

Behavior の主経路。

- 典型条件
- 期待結果
- 通常状態

### Boundary

意味が切り替わる境界。

境界は数値に限定しない。

- threshold
- zero / empty
- before / after
- state transition
- permission boundary
- lifecycle boundary

重要なのは値そのものではなく、境界を跨ぐことで Behavior が変わるかどうかである。

### Failure

Behavior が成立しない、拒否される、または処理できない条件。

Failure を探索する際も、一般論から例外を増やさず、Behavior / authoritative Context に根拠を持つ失敗だけを Admit する。

### Relation

複数の条件・状態・操作・結果の間に期待される関係。

類推のための例としては、次のような関係があり得る。

- ordering
- interaction
- state transition
- preservation
- contrast
- symmetry / equivalence
- inverse operation

これらは分類表ではなく、類推を助ける例に過ぎない。

Relation を探索することはできるが、期待される関係を推測で補完してはならない。Behavior / authoritative Context に grounding できたものだけを Admit する。

### Lens の扱い

代表 Lens は次である。

```text
Normal / Boundary / Failure / Relation
```

- 非網羅である
- 必須出力 bucket ではない
- 適用できない Lens から何かを生成する必要はない
- この一覧外でも、Behavior から意味のある観点を探索してよい

## Consumer の責務

Kernel は共有 Method であり、Kernel の出力を何に、どのように利用するかは consumer が決める。

consumer は自身の scope / responsibility に従って、次を担う。

- 入力する resolved Behavior の解決
- relevant Context の選択と authority / precedence の解決
- Kernel の出力を利用する目的と評価対象の決定
- consumer 固有の finding、verdict、severity、accept / reject、成果物生成
- 必要な追加 Context の取得と再注入
- Kernel の結果を workflow 上の判断へ変換する責任

Kernel は consumer topology、consumer 名、consumer 固有の成果物、評価対象、workflow phase を正本として保持しない。
consumer が増減・変更されても、それ自体を理由に Kernel の Contract / Method を変更しない。

Kernel は consumer 固有の評価対象を入力として期待 Observation を逆算せず、Behavior + relevant Context から独立に導出する。

Kernel は finding severity、accept / reject、新しい product requirement を返さない。

Collective Sufficiency を consumer 固有成果物の quality verdict と読み替えない。

## 非目標

`Behavior Observation Kernel` は次を行わない。

- 共通 serialized Observation schema の定義
- test execution protocol の定義
- test の実行
- assertion / mocking technique の選択
- Unit / Integration / E2E の分類
- consumer 固有の評価対象から期待 Behavior を逆算すること
- repository 固有の authority precedence の決定
- missing Context を取得するための scope expansion
- consumer 固有の成果物・評価対象・workflow の直接評価
- 入力組み合わせの網羅要求
- 全 Exploration Lens から AC / Red / test case を生成すること
- 現在実装の挙動を自動的に仕様として扱うこと

## 現在の形

現時点の合意を最小化すると、次の構造になる。

```text
Contract
  Input:
    Behavior + relevant Context

  Output:
    Expected Observations
    Collective Sufficiency
    Relevant Unresolved Viewpoints

Method
  Explore
    Discover → Ground → Admit

  Observe
    Identify → Calibrate

  Evaluate
    Cover → Trim → Classify

Cross-cutting
  Reintegration

Exploration Lenses
  Normal / Boundary / Failure / Relation
```

Kernel は小さく保つ。新しい概念を追加する前に、まずこのモデルの既存要素へ吸収できないかを検討する。
