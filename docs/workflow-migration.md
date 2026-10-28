# Workflow の利用先

この変更では4つの新しい公開 workflow を導入し、次の5つの入口を廃止する。固定の自動チェーンではなく、目的に応じて選ぶ。

| 廃止する入口 | 今後の利用先 |
| --- | --- |
| how-it / explorer-this | 調査・初期方針の相談は通常のエージェントへ依頼する。実装の処理を理解したい場合は explain-this。 |
| find-way / plan-agent | 調査・初期プラン作成は通常のエージェントへ依頼する。既存プランの実行単位・分担を確認したい場合は impl-plan。 |
| review-refine | 元プランを保持した案の比較は review-propose。実装済み差分の修正候補は impl-review。 |

impl-plan は委譲文書を返して停止する。内容を確認・変更したうえで、その文書を指定して impl-lead に実装を依頼できる。
impl-lead は準備済み計画を消費し、実行時の前提・権限を再確認する。文書の存在だけで実装は始まらない。
review-propose と impl-review の推奨は自動採用されない。Human が採否を判断し、修正はその後の依頼で進める。

Model Construction、MO/RMO、共有の調査・権限境界と配布 agent は保持する。Planning Core / Planning Synthesis / Deletion Test は廃止入口だけから使われていた経路として整理した。
test-report、test-verify、visualize-that とインストール補助 skill は引き続き利用できる。この workflow 構成の配布 version は 7.5.0 とする。model・effort は変更しない。
