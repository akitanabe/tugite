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

## Concrete counterexamples in both directions

見逃し（false negative）は、要求に違反する具体的な入力・実装変更でも対象 assertion が成功する条件を探します。誤拒否（false positive）は、独立した要求・契約を満たす具体的な変更でも対象 assertion が失敗する条件を探します。対象 test 自身の期待値や現実装だけから変種の正当性を導出しません。

値、順序、内部構造、呼び出し回数、表現形式、環境情報への固定について、公開契約、互換性、非機能要求、authoritative Context と provenance / 適用範囲を読みます。要求に明記されていないことは不要である証拠ではありません。mock、assertion 数、test の長さ、fixture 共有は探索の手掛かりであり、それ自体を finding にしません。
要求と無関係な制約は原因、正当変更への脆弱性は影響として同じ反例に結び付け、機械的に二件へ分けません。別 assertion / Case、契約や production boundary が反例を否定する可能性も調べます。

次の例は契約によって結論が変わる観測例です。具体的な source location と条件へ置き換えて使い、固定の smell 判定表にはしません。

- JSON: `{"a":1,"b":2}` と `{"b":2,"a":1}` を同じ object として許す契約なら、文字列完全一致 assertion は後者を誤拒否し得ます。署名用の canonical byte order が公開契約ならその一致は正当です。serialization 契約が不明なら未確定です。
- 内部呼び出し順序: 独立な二つの read を入れ替えても同じ公開結果・副作用を満たすなら、call sequence assertion が正当変種を拒否し得ます。順序が transaction、protocol、安全性の契約なら順序の検証は必要です。独立性が未確認なら正当変種と断定しません。
- 環境依存: 許容される timezone / temporary directory が変わっても要求結果が同じなら、固定されたローカル表現・絶対 path が誤拒否の候補です。timezone、path、locale が公開形式や対応環境として指定されていればその制約は正当です。対応環境の根拠がなければ材料不足です。
- 見逃し: 除外対象の金額が 0 の fixture だけでは、除外せず合計する変更も同じ合計 assertion を通り得ます。除外の要求と入力条件、他 Case が非ゼロ金額でその違反を検出するかを照合し、局所的な識別不足を suite 全体の見逃しと同一視しません。

## Diagnose with an explicit confirmation state

静的に確認できた問題は、要求・条件と assertion / config の具体的な不一致や識別不能を、観測範囲と成立条件を伴って示します。実行時の失敗・成功や production defect の実証へ拡張しません。

実行確認が必要な疑いは、観測事実と仮説を分け、まだ確認していない因果関係・環境条件と、その確認方法を示します。判断材料の不足は、欠けた要求根拠・source・対応関係などを特定し、問題が成立したという verdict にしません。

例えば、異なるはずの計算結果が fixture の 0 または同値入力では一致し、assertion が仕様準拠と具体的な仕様違反を区別できない場合があります。どの値・条件・assertion で、どの違反が同じ観測になるかを source に即して説明します。0 の使用自体は問題ではなく、別の assertion や Case がその違反を識別する可能性も調べます。候補となる違反の成立が実行依存なら疑いとして残します。

各指摘には識別子と確認状態、要求 / Expected Observation と test / source / config の根拠、影響する条件、見逃しうる問題、次に確認する点を含めます。優先度を示す場合は影響と根拠を説明し、件数や配置を品質の代用にしません。指摘がない部分も観測済み範囲を提示し、静的に問題が見つからないことを runtime correctness の保証にしません。

各反例 finding は、要求・契約 / Expected Observation の根拠と所在、存在する Case / Evidence と test / source / config location、具体的な入力・変更・assertion、成立条件、見逃す違反または誤拒否する正当変種、counterevidence、確認状態、未確認事項、次の検証点を保持します。静的に確認できた問題、実行確認が必要な疑い、判断材料不足を区別し、反例未発見を品質保証にしません。

対応 Case / Evidence がない欠落は架空の Case / Evidence で埋めず、要求 / Expected Observation の根拠と所在、absence を判断した bounded observed scope と completeness basis、対応 Evidence が観測されなかった事実を残します。未読、未実行、対応不明を absence に変換しません。

## Preserve full-scope detail

概要と問題一覧は入口です。本文または明示された report artifact に、observed scope 全体の Behavior、Expected Observation、Case、Evidence、条件、実際の assertion、source location を残し、概要から辿れるようにします。正常・境界・異常系は観測された意味に応じて扱い、存在しない Case を埋め合わせで発明しません。

根拠へのリンクだけで詳細の代用にはせず、何を期待し何を実際に assert しているかを読者が理解できる内容を添えます。共通 fixture や assertion は参照共有できますが、各対応と条件を失わせません。指摘の優先度や回答の短さを理由に問題のない領域・未対応 Evidence・evidence gap を削りません。

report の repository / ref と dirty state が観測可能なら記録し、不明なら明示します。選択用の識別子を根拠・確認状態と結び付け、verify が古い報告を再確認できる参照先を残します。report の発見は修復権限ではありません。
