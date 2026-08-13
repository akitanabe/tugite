---
name: install-plugin
description: >-
  Tugite の Cursor local plugin を user scope にインストール、バージョン確認、更新する。
  ユーザーが plugin の導入、再インストール、バージョン確認、更新、上書きを明示的に依頼した場合に使う。
  既存インストールを確認なしで上書きしない。symlink は使わない。
---

# Cursor plugin のインストール

plugin に同梱された `install/install-plugin.sh`（Linux / macOS / WSL / Git Bash）または
`install/install-plugin.ps1`（Windows PowerShell）を唯一のインストール処理として使う。
`plugins/cursor` を手で copy したり symlink したりしない。

## 手順

1. plugin root（`install/` と `skills/` を含む directory）を確定する。導入済みなら通常は
   `~/.cursor/plugins/local/tugite`。repository checkout を検証中なら `plugins/cursor`。
2. 対象は user scope のみとする。`--user` / `-User` を使う。
3. OS に応じて installer を選ぶ。

   - Unix 系（Linux / macOS / WSL / Git Bash）: `install/install-plugin.sh`
   - Windows PowerShell: `install/install-plugin.ps1`

4. 次の確認コマンドを実行する。この操作ではファイルを変更しない。

   ```bash
   "$PLUGIN_DIR"/install/install-plugin.sh --check --user
   ```

   ```powershell
   & "$PLUGIN_DIR\install\install-plugin.ps1" -Check -User
   ```

5. 未インストールなら、同じ scope で `--check` / `-Check` を外して実行する。
6. 既存版と同梱取得版が同一（version と commit）なら、変更せず最新であると報告する。
7. バージョンまたは commit が異なる場合は、installed version / commit、bundled version / commit、
   対象 directory をユーザーへ提示し、上書きしてよいか明示的に確認する。ユーザーが更新や上書きを
   依頼済みでも、この確認を省略しない。
8. 承認された場合だけ、同じ scope へ `--force` / `-Force` を付けて実行する。

   ```bash
   "$PLUGIN_DIR"/install/install-plugin.sh --force --user
   ```

   ```powershell
   & "$PLUGIN_DIR\install\install-plugin.ps1" -Force -User
   ```

9. 完了後は Cursor の再起動、または `Developer: Reload Window` を依頼し、この session では
   委譲計画や実装へ進まない。再読込後に public skill の一覧を再確認する。

`--check` / `-Check` が終了コード `3` を返すのは、未インストールまたは更新候補があることを示す。
エラーとして扱わず、表示された状態に従って上記手順を続ける。
