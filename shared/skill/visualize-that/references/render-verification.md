# Render Verification

この reference は `visualize-that` が作成した HTML に対する capability 確認と実行結果の扱いを一意に定めます。表示内容が意味を保つか、どの修正が適切か、十分に読みやすいかという判断は親 Skill が担います。

## Programmatic Flow

<!-- @contract visualize-that-render-flow -->
### render-verification-flow

Trigger: `visualize-that` が authority 内の destination に HTML を保存し、描画確認を開始できる。

Inputs: HTML の exact path、確認に必要な page / region、caller-confirmed authority、installed browser candidates と各 launch command、各実行の bounded timeout / termination condition、screenshot destination、launch / capture / inspection の current result、Node.js / npm availability。

Procedure:

1. caller-confirmed authority 内の installed browser candidates を確認する。候補の存在だけでは available と判定しない。
2. 候補ごとに bounded timeout / termination condition の下で対象 HTML を headless launch する。launch が成功した候補だけ screenshot capture へ進め、失敗または timeout した実行を停止して次の eligible candidate を試す。
3. 説明に必要な page / region を含む screenshot を capture する。長い page は必要な範囲が欠けないよう複数画像に分けられる。capture に失敗した候補は unavailable として、次の eligible candidate を試す。
4. capture した各画像を Agent が実際に inspection する。capture success だけでは inspection success にしない。
5. launch、capture、inspection が完了した場合は、実行結果と確認範囲を `verified-candidate` として親 Skill の意味・視認性判断へ返す。inspection を完了できない場合は inspection stage、それ以外で全候補が失敗した場合は各 launch / capture stage と理由を、観測済み result とともに `render-unverified` として返す。
6. launch と capture を完了できる browser candidate がなく、Node.js と npm が利用可能な場合だけ、Human が選んだ tool directory で `npm install --save-dev --save-exact playwright@1.62.1`、次に authority を確認して `npx playwright@1.62.1 install --with-deps chromium` を実行できると案内する。案内後に自動インストールや再試行をせず `render-unverified` を返す。version と browser command の根拠は [Playwright v1.62.1 release](https://github.com/microsoft/playwright/releases/tag/v1.62.1) と [Browsers documentation](https://playwright.dev/docs/browsers)、対応 runtime の確認先は [Installation documentation](https://playwright.dev/docs/intro) とする。

Outcomes: launch・capture・actual inspection の evidence と確認範囲を持つ `verified-candidate`、または HTML を保持したまま failure stage・reason・observed result・conditional installation guidance を持つ `render-unverified`。どちらも親 Skill の autonomous judgment へ戻し、Flow 内で意味保持、修正内容、visual acceptance を決めない。
<!-- @/contract -->

Playwright の案内は capability を用意する選択肢です。`--with-deps` は browser に加えて OS dependency を変更し得るため、既存の write / execution authority から許可を推測しません。Node.js / npm が利用不能な場合や Human が導入を選ばない場合も、別の installer を探索せず `render-unverified` とします。
