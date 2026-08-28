# Research Agent Delegation
<!-- @anchor shared-research-document -->

## Boundary

<!-- @contract shared-research-boundary -->
<!-- @anchor shared-research-boundary-relation -->
この文書は caller が Research Agent を利用するための共通 delegation / operation policy を所有する。
actual Research Agent prompt の正本は `agents/research-agent.md` とし、この文書は agent の探索手順や task-relative semantic judgment を
所有しない。
<!-- @/contract -->

## Named subagent invocation

<!-- @anchor shared-research-invocation-relation -->
<!-- @contract shared-research-invocation-identity -->
caller は `research-agent` を起動し、delegation input と authority を渡す。agent identity は設定された agent の名前、runtime instance の
label / task name は実行単位の識別情報として、それぞれ独立した data として扱う。
<!-- @/contract -->

<!-- @contract shared-research-invocation-unavailable -->
named agent identity の解決は invocation の成立条件である。解決できない場合、caller は `Research Agent unavailable` と
limitation / unresolved point を保持して返し、Research Agent による evidence acquisition の成功を記録しない。
<!-- @/contract -->

<!-- @contract shared-research-platform-invocation -->
<!-- @only claude -->
`research-agent` を named subagent として起動し、delegation input と authority を渡す。
<!-- @/only -->
<!-- @only codex -->
`research-agent` を named subagent として `fork_turns = "none"` で起動し、delegation input と authority を渡す。
<!-- @/only -->
<!-- @only cursor -->
Cursor Agent の named subagent を `/research-agent` として起動し、delegation input と authority を渡す。
<!-- @/only -->
<!-- @/contract -->

## Delegation input

<!-- @anchor shared-research-input-relation -->
caller は invocation 前に、少なくとも次の意味を確定する。

<!-- @contract shared-research-delegation-input -->
- **objective**: 何を知るための bounded evidence acquisition / exploration か
- **scope**: 探索できる source、repository、context、target boundary
- **authority**: 実行可能な observation-oriented Action とその上限
- **relevant context / evidence surface**: objective に関係する既知情報と接触可能な evidence surface
<!-- @/contract -->

固定 serialized schema は要求しない。不足または矛盾が探索範囲、authority、結果の意味を変える場合、caller は推測で補完させず、
Research Agent が limitation / unresolved point を返せる boundary を維持する。

## Action and authority

<!-- @anchor shared-research-authority-relation -->
caller は通常の evidence acquisition として、scope 内の read / search / source inspection、test、lint、build、typecheck、diagnostic、
CLI、existing script、isolated temporary verification と temporary resource を許可できる。command の transitive side effect を isolated
temporary target 内へ限定できない場合は persistent / shared operation として扱う。

<!-- @contract shared-research-exact-authority -->
persistent / shared / destructive operation は evidence acquisition に不可欠で、caller が exact authority を明示した場合だけ許可する。
authority は operation、target、最大試行回数、retry condition を特定し、利用可能な場合は idempotency key / precondition も含める。
この authority は implementation、remediation、成果物変更、公開の ownership を与えない。
<!-- @/contract -->

## Retry, partial result, and cleanup

<!-- @anchor shared-research-safety-relation -->
<!-- @contract shared-research-retry-authority -->
caller は authority にない retry を許可しない。partial / unknown result は success として扱わず、実行回数、観測できた状態、
limitation / unresolved point を保持する。再実行には新しい明示 authority を必要とする。
<!-- @/contract -->

<!-- @contract shared-research-cleanup-result -->
Research Agent が作る temporary resource は objective の観測に必要な isolated target に限定する。success / failure のいずれでも
可能な範囲で cleanup し、cleanup failure、residual state、状態不明は target とともに result に保持する。既存または共有 target を
temporary resource として扱わない。
<!-- @/contract -->

## Result usability

<!-- @anchor shared-research-result-relation -->
grounded result は固定 schema ではなく、objective に必要な次の意味を caller が追跡できる形で保持する。

<!-- @contract shared-research-result-data -->
- acquired / observed evidence と source basis
- relevant execution result、実行回数、retry の有無
- bounded local inference と observation / inference の区別
- scope、authority、observability、environment による limitation
- caller の判断または追加 acquisition が必要な unresolved point
<!-- @/contract -->

<!-- @contract shared-research-result-usability -->
caller は result の evidence / authority relation と task-relative semantic effect を判断する。partial / unknown result や limitation を
plausible inference で埋めず、利用できる evidence と未解決事項を区別する。
<!-- @/contract -->

## Continued Delegation

<!-- @contract shared-research-continuation -->
<!-- @anchor shared-research-continuation-relation -->
各 continuation は新しい bounded delegation とする。
<!-- @/contract -->

<!-- @contract shared-research-continuation-input -->
caller は objective、scope、authority、relevant context / evidence surface をその都度確認して渡す。
<!-- @/contract -->

<!-- @contract shared-research-continuation-authority -->
prior authority、retry permission、operation target、scope、task semantics を自動継承させない。
<!-- @/contract -->

同じ runtime instance への continuation でも、caller は今回の delegation input を再構成する。

<!-- @contract shared-research-continuation-context -->
<!-- @anchor shared-research-continuation-context-relation -->
prior research context は evidence / source relation / bounded local inference として再利用できるが、今回の objective、scope、authority、task semantics を拡張する入力にはしない。
<!-- @/contract -->

<!-- @contract shared-research-fresh-fallback -->
<!-- @anchor shared-research-fresh-fallback-relation -->
caller が fresh invocation を選んだ場合、必要な delegation input と再利用可能な research context を再構成して渡す。
<!-- @/contract -->

<!-- @contract shared-research-runtime-fallback -->
runtime / platform が continuation capability を提供しない場合は fresh invocation を使う。
<!-- @/contract -->

fallback は delegation failure ではなく continuation capability の不足に対する caller-side の invocation 選択であり、Research Agent 自身は continuation、fresh 切り替え、次の operation を開始しない。

## Semantic ownership

<!-- @anchor shared-research-semantic-relation -->
Research Agent に次を委譲しない。

<!-- @contract shared-research-semantic-boundary -->
- caller-owned task-local Local Model と Exploration Projection の task-relative meaning
- gap の materiality、priority、resolution completion
- task direction、scope expansion、planning
- implementation、remediation、finding の採否
- Reintegration、Recomposition、workflow continuation / completion
<!-- @/contract -->

<!-- @contract shared-research-semantic-ownership -->
Research Agent は grounded result を返して待機する。caller は必要な result を同じ task-local Local Model へ Reintegration し、
Recomposition、再観測、continuation の要否を判断する。
<!-- @/contract -->
