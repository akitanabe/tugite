<!-- Generated from shared/. Do not edit directly. -->

# Research Agent Delegation

## Boundary

この文書は caller が Research Agent を利用するための共通 delegation / operation policy を所有する。
actual Research Agent prompt の正本は `agents/research-agent.md` とし、この文書は agent の探索手順や task-relative semantic judgment を
所有しない。

## Delegation input

caller は invocation 前に、少なくとも次の意味を確定する。

- **objective**: 何を知るための bounded evidence acquisition / exploration か
- **scope**: 探索できる source、repository、context、target boundary
- **authority**: 実行可能な observation-oriented Action とその上限
- **relevant context / evidence surface**: objective に関係する既知情報と接触可能な evidence surface

固定 serialized schema は要求しない。不足または矛盾が探索範囲、authority、結果の意味を変える場合、caller は推測で補完させず、
Research Agent が limitation / unresolved point を返せる boundary を維持する。

## Action and authority

caller は通常の evidence acquisition として、scope 内の read / search / source inspection、test、lint、build、typecheck、diagnostic、
CLI、existing script、isolated temporary verification と temporary resource を許可できる。command の transitive side effect を isolated
temporary target 内へ限定できない場合は persistent / shared operation として扱う。

persistent / shared / destructive operation は evidence acquisition に不可欠で、caller が exact authority を明示した場合だけ許可する。
authority は operation、target、最大試行回数、retry condition を特定し、利用可能な場合は idempotency key / precondition も含める。
この authority は implementation、remediation、成果物変更、公開の ownership を与えない。

## Retry, partial result, and cleanup

caller は authority にない retry を許可しない。partial / unknown result は success として扱わず、実行回数、観測できた状態、
limitation / unresolved point を保持する。再実行には新しい明示 authority を必要とする。

Research Agent が作る temporary resource は objective の観測に必要な isolated target に限定する。success / failure のいずれでも
可能な範囲で cleanup し、cleanup failure、residual state、状態不明は target とともに result に保持する。既存または共有 target を
temporary resource として扱わない。

## Result usability

grounded result は固定 schema ではなく、objective に必要な次の意味を caller が追跡できる形で保持する。

- acquired / observed evidence と source basis
- relevant execution result、実行回数、retry の有無
- bounded local inference と observation / inference の区別
- scope、authority、observability、environment による limitation
- caller の判断または追加 acquisition が必要な unresolved point

caller は result の evidence / authority relation と task-relative semantic effect を判断する。partial / unknown result や limitation を
plausible inference で埋めず、利用できる evidence と未解決事項を区別する。

## Semantic ownership

Research Agent に次を委譲しない。

- caller-owned task-local Local Model と Exploration Projection の task-relative meaning
- gap の materiality、priority、resolution completion
- task direction、scope expansion、planning
- implementation、remediation、finding の採否
- Reintegration、Recomposition、workflow continuation / completion

Research Agent は grounded result を返して停止する。caller は必要な result を同じ task-local Local Model へ Reintegration し、
Recomposition、再観測、continuation の要否を判断する。
