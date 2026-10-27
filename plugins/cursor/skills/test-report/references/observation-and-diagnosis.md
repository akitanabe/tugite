<!-- Generated from shared/. Do not edit directly. -->

# Static observation and diagnosis

`test-report` が所有する静的観測・診断と詳細出力の観点です。grounding と対応関係の意味は shared `Verification Topology` に従います。

## Observe both requirements and tests

要求・仕様、適用される authoritative Context とその provenance / 適用範囲から Behavior candidate を探します。test は追加の discovery signal です。要求側から見つかった候補に test がなくても保持し、要求の曖昧さや相反をテストの期待値で埋めません。

対象 test、target code、runner / config を静的に読み、条件・入力・fixture、実際の assertion / oracle、観測対象、setup / teardown、静的な選択・skip 条件と source location を取得します。source の実装は観測事実であり、仕様の正当性を自動的に保証する authority ではありません。

resolved / observed membership を分け、未読の file / unit と理由を残します。静的に実行可能な test と実際に実行された test は異なります。既存ログを読む場合も、その ref / command / environment の記録として扱い、この invocation が実行・再現した結果とはしません。

## Interpret evidence and limits

- Expected Observation の条件と実際の assertion / oracle を比較し、何を観測し何を観測していないかを明示します。
- 一つの Case を支える複数の assertion と、一つの test が支える複数の Expected Observation の両方向を保持します。
- 対応が確定しない test / Evidence は独立した参照先と未確定理由を残し、一覧から落としません。
- 要求側で独立 grounding でき、観測範囲が確定している場合の evidence gap と、未読・grounding 不足・対応不明を区別します。
- BMO の Collective Sufficiency は渡した Behavior の導出十分性です。要求候補の探索完了や test coverage 全体の十分性を意味しません。

## Diagnose with an explicit confirmation state

静的に確認できた問題は、要求・条件と assertion / config の具体的な不一致や識別不能を、観測範囲と成立条件を伴って示します。実行時の失敗・成功や production defect の実証へ拡張しません。

実行確認が必要な疑いは、観測事実と仮説を分け、まだ確認していない因果関係・環境条件と、その確認方法を示します。判断材料の不足は、欠けた要求根拠・source・対応関係などを特定し、問題が成立したという verdict にしません。

例えば、異なるはずの計算結果が fixture の 0 または同値入力では一致し、assertion が仕様準拠と具体的な仕様違反を区別できない場合があります。どの値・条件・assertion で、どの違反が同じ観測になるかを source に即して説明します。0 の使用自体は問題ではなく、別の assertion や Case がその違反を識別する可能性も調べます。候補となる違反の成立が実行依存なら疑いとして残します。

各指摘には識別子と確認状態、要求 / Expected Observation と test / source / config の根拠、影響する条件、見逃しうる問題、次に確認する点を含めます。優先度を示す場合は影響と根拠を説明し、件数や配置を品質の代用にしません。指摘がない部分も観測済み範囲を提示し、静的に問題が見つからないことを runtime correctness の保証にしません。

## Preserve full-scope detail

概要と問題一覧は入口です。本文または明示された report artifact に、observed scope 全体の Behavior、Expected Observation、Case、Evidence、条件、実際の assertion、source location を残し、概要から辿れるようにします。正常・境界・異常系は観測された意味に応じて扱い、存在しない Case を埋め合わせで発明しません。

根拠へのリンクだけで詳細の代用にはせず、何を期待し何を実際に assert しているかを読者が理解できる内容を添えます。共通 fixture や assertion は参照共有できますが、各対応と条件を失わせません。指摘の優先度や回答の短さを理由に問題のない領域・未対応 Evidence・evidence gap を削りません。

report の repository / ref と dirty state が観測可能なら記録し、不明なら明示します。選択用の識別子を根拠・確認状態と結び付け、verify が古い報告を再確認できる参照先を残します。report の発見は修復権限ではありません。
