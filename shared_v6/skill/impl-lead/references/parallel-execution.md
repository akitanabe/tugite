# impl-lead parallel execution v1

この reference は、`impl-lead` の並列 dispatch の適格性、isolation、統合を定義する。親は `SKILL.md` の
Parallel minimal pre-screen を通過した候補についてだけ、指定された時点に全文を読み、判断と Action を自身の
execution data として扱う。

## Safe parallel dispatch and integration

ここで扱う並列化は実装 batch に限る。immutable snapshot と no writer を満たす reviewer の同時 read-only 観測は、実装 batch と重ねない別の実行として許す。候補間の依存がなく、path、derived output、semantic invariant、shared mutable state、
external namespace の競合がなく、同じ再現可能な base から隔離され、個別 QA と統合 verification が可能で、適用順が
結果を変えないことをすべて説明できる場合だけ並列に dispatch する。要求されても一つでも説明できない場合、ユーザーが
parallel を要求していなければ直列化できるが、要求している場合は無断で直列化せず確認または `stop-incomplete` とする。
判断理由と isolation を execution data に残す。並列中に hidden dependency、scope overlap、base drift が判明した場合は
新規の並列 dispatch を止め、返却を個別候補として QA し、無理に merge しない。

親が eligibility と順序不変を確定した並列返却の統合は `parallel-candidate-integration` へ渡す。この Flow の
`final combined verification` は run closeout の repository gate を省略しない。

<!-- @contract impl-programmatic-flow-parallel-candidate-integration -->
### parallel-candidate-integration

Trigger: 親が parallel eligibility と適用順不変を確定した batch の候補が返却されたとき。
Inputs: 親が固定した候補順、最後の Green な run baseline、各候補の diff・AC・scope・precondition・dirty state・side effect・native verification Data。
Procedure: 最後の Green な baseline へ候補を一件ずつ統合・検証し、Green の候補だけを accept する。failure は accept せず最後の Green へ rollback・再検証し、戻せなければ `blocked` とする。最後の候補の統合 verification を `final combined verification` とし、別の combined gate を重ねない。
Outcomes: accepted 候補を含む latest Green baseline と final combined verification Data、または rollback 済み / rollback 不能の `blocked`。hidden dependency の扱いは Agentic な親へ返す。
<!-- @/contract -->
