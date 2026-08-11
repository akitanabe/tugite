<!-- @only claude -->
---
name: proposal
description: >-
  plan-craft の同じ親 context 内だけで、要求と repository の観測から計画 candidate を起草し、
  read-only advisor の非拘束な insight を裁定して candidate snapshot または stop-incomplete を caller-owned parent へ返す internal skill。
user-invocable: false
---
<!-- @/only -->
<!-- @only codex -->
---
name: proposal
description: >-
  plan-craft の同じ親 context 内だけで、要求と repository の観測から計画 candidate を起草し、
  read-only advisor の非拘束な insight を裁定して candidate snapshot または stop-incomplete を caller-owned parent へ返す internal skill。
---
<!-- @/only -->

# proposal

## 位置づけと発火

この Skill は `plan-craft` の同じ親 context 内だけで使う internal skill であり、ユーザーから直接起動しない。
要求、repository、既存仕様を観測して計画 candidate を作る producer を担う。
自身は実装、委譲、worktree 操作、保存、最終受入を行わず、caller-owned parent へ判断材料を返す。

## 入力と観測

親から次の Data を受け取る。

- `request`: 要求原文、目的、成功条件、scope、exclude、制約、既知の依存。
- `repository_observation`: current state、既存仕様、関連成果物、検証可能な境界。
- `caller_context`: `plan-craft` が同じ context で保持する判断と、必要なら既存の current verified candidate snapshot。

要求、対象、成功条件、scope、exclude、依存、制約の不足または矛盾が品質を変える場合は推測せず、
`stop-incomplete` として必要な判断を返す。軽微な不足は根拠付き `assumptions` として分離する。

<!-- @contract proposal-resolve-kernel-loader -->
## resolve-kernel v1 の parent mapping

<!-- @anchor proposal-resolve-kernel-loader-start -->
proposal invocation の開始時に、親は生成後の skill directory から skill-relative
`../../references/resolve-kernel.md` を一度だけ読み、identity `resolve-kernel-v1` と、この Skill が必要とする
role mapping、discretionary resolution、current verified snapshot discipline の本文を検証する。resolution cycle
ごとには再読込しない。reference の不足、identity 不一致、読み取り失敗、必要本文不足があれば、本文を推測で
再現せず既存の `stop-incomplete` へ返す。proposal planner と `plan-quality-advisor` に package / plugin 相対 path
の解決、reference の探索、読み込みを委ねない。
<!-- @anchor proposal-resolve-kernel-use -->
検証済み本文だけを、以降の resolution cycle の既存の `判定基準` または `必要な周辺 context` に注入する。
<!-- @/contract -->

<!-- @contract proposal-resolution-role-mapping -->
## resolve-kernel v1 の role mapping

この invocation の mapping は caller=`plan-craft`、resolver=planner、counterpart=`plan-quality-advisor`、authority=discretionary
であり、ledger は既存の adoption ledger（`adopted` / `rejected` / `unresolved`）である。advisor insight は非拘束の
Data に留まり、planner が要求、一次情報、current verified snapshot を基準に裁定する。

この resolve-kernel mapping と後述の necessity-kernel mapping は別 section の独立した規範である。互いの本文を前提にせず、相互の読み込み順に依存させない。
<!-- @/contract -->

<!-- @anchor proposal-verified-baseline-start -->
<!-- @contract proposal-verified-snapshot-baseline -->
## current verified candidate の caller mapping

`caller_context` で既存 candidate を受け取る場合は current verified candidate snapshot とし、未検証の working state を
baseline にしない。初回は要求、一次情報、観測可能な条件から working candidate を起草し、それらに対する verify の成功と semantic progress の確認後にだけ、初期 current verified snapshot として確立する。
各改善は working state へ apply し、verify と semantic progress が成功した後にだけ current verified snapshot を更新する。
失敗時の snapshot 維持と current point の扱いは後述の serial resolution に従い、working state を昇格させない。
<!-- @/contract -->

<!-- @contract candidate-producer-boundary -->
## candidate の起草と advisor insight

planner は一次情報（要求原文、repository、既存仕様）を調査し、観測可能な AC、設計、scope、依存、制約、
verification、残存 risk を含む working candidate を起草する。上記 caller mapping に従って検証した内容だけを、
同じ内容を識別できる current verified `candidate snapshot` として保持する。

## necessity-kernel v1 の parent mapping

<!-- @anchor proposal-kernel-reference -->
candidate Claim を判定する前に、advisor 起動の有無にかかわらず、親は生成後の skill directory から package-root reference へ skill-relative `../../references/necessity-kernel.md` を読み、identity と必要な本文を既存の
<!-- @anchor proposal-kernel-criteria -->
`判定基準` または `必要な周辺 context` の一部にする。`plan-quality-advisor` 起動時は既取得 Data を既存の判定基準として渡す。reference の不足、identity 不一致、
読み取り失敗があれば推測せず `stop-incomplete` へ返し、advisor は plugin 相対 path を解決しない。

候補 Claim の必要性は既存の判定基準に含めた Task Specification と Deletion Test で観察する。
Claim は finding / insight 本文ではなく、candidate に追加・維持・変更・除去・検証・調査する obligation の候補
であり、必要性の根拠を既存の observation / evidence から追跡する。`necessary` / `unnecessary` /
`indeterminate` を新しい返却 field にせず、親は下記の adoption ledger の語彙へ写像する。候補を更新した後は
更新された snapshot で再判定し、互いを witness とする同時削除を認めない。必要性分類は既存語彙へ写像し、新verdict fieldではない。round budget / termination へ直結させない。`structural-health-gate` の意味は
この mapping の対象外である。

必要な場合だけ `plan-craft` 内の proposal planner は read-only `plan-quality-advisor` に candidate snapshot と判定基準を渡す。
advisor の返す insight は非拘束の Data であり、planner は各 insight を一次情報と要求に照らして次の台帳へ裁定する。

- `adopted`: 根拠があり、candidate の具体的な品質向上になるため採用した insight。
- `rejected`: 一次情報に反する、既存の制約で不要、または scope 外のため採用しない insight。
- `unresolved`: 根拠または人間の判断が不足し、採否を決められない insight。

advisor insight を自動採用せず、採否を根拠なしに planner の推測で埋めない。新仕様、新しい scope、AC、
ユーザー嗜好を advisor から派生させない。
<!-- @/contract -->

<!-- @anchor proposal-serial-resolution-start -->
<!-- @contract proposal-serial-resolution-cycle -->
## current verified snapshot 上の serial resolution

advisor は必要なら複数 insight を一度に返してよいが、planner は一括裁定しない。各 insight を、その insight が
観測された verified snapshot に束縛された frontier candidate として扱う。一件の current point を resolve し、許可された変更だけを apply して verify
し、semantic progress を確認した後にだけ verified snapshot を更新する。
verification が失敗した場合は current point を reopen し、直前の verified snapshot を維持する。未検証 working state
上へ次の判断を積まない。

snapshot 更新後は、未処理 insight を updated snapshot と一次情報で一件ずつ再評価する。まだ material なら frontier
に残し、不要になった場合は理由付き `rejected`、evidence が不足する場合は `unresolved`、別 resolution によって
obligation が充足済みならその理由付き `rejected` とする。未処理 insight を黙って捨てず、`stale`、`superseded`
などの新しい ledger status を作らない。

frontier empty は通常の candidate return 判定へ進む条件にすぎず、workflow completion ではない。念押し review や
latent insight 探索を行わない。semantic progress がなく、安全な candidate を作れない material frontier が残る場合、
または親が固定した bound 到達時に frontier が残る場合は、新statusを作らず既存の `stop-incomplete` と
`blocking_gaps` へ写像する。安全な candidate の可否と最終的な Human adoption は `plan-craft` の既存責務を維持する。
<!-- @/contract -->

<!-- @contract proposal-advisor-reinvocation -->
## advisor invocation と resolution cycle の分離

advisor invocation は resolution cycle と同義ではなく、advisor を毎 cycle 起動しない。既存 evidence だけでは
current frontier を安全に処理できず、再起動に具体的な価値がある場合に限る。具体的には snapshot 更新で前提が
大きく崩れた、新しい material な設計境界が現れた、必要な evidence / option / objection が不足した、または scope / responsibility
境界が変化した場合である。単なる snapshot 更新、frontier が一件減ったこと、一件の insight の採否、frontier empty の念押しだけでは再起動しない。
<!-- @/contract -->

<!-- @anchor proposal-bounded-return-start -->
<!-- @contract proposal-bounded-return -->
## bounded な改善と返却

candidate の改善は、要求と一次情報から具体的な品質向上が残る間だけ bounded に行い、snapshot 更新は上記
current verified candidate の caller mapping に従う。serial resolution で current frontier を処理し、必要な advisor
reinvocation の判断を終えた後にだけ return を判定する。採否台帳と残存 risk を保ち、判断密度が高まり scope や
責務が変わる場合、または material な `unresolved` により安全な candidate を推奨できない場合は、勝手に進めず
判断点・evidence・必要な問いを付けて `stop-incomplete` を返す。軽い不確実性は既存の candidate status Calculation
へ渡し、`unresolved` という分類だけで無条件に停止しない。

改善を終えた通常の返却は、`candidate_snapshot`、`adoption_ledger`（`adopted` / `rejected` /
`unresolved`）、`assumptions`、`blocking_gaps`、`residual_risks`、`status` を持つ Data である。安全な
candidate を作れない返却では `status: stop-incomplete` と未完了範囲、必要な判断、evidence、未検証事項を返す。
いずれも後段工程を選択・起動せず、受け入れを主張せず、caller-owned parent へ返して終了する。
<!-- @/contract -->
