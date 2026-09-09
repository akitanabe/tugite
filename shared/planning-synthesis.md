# Planning Synthesis

Planning Synthesis は、caller が確立した理解と authority から request-relative な coherent planning / design artifact candidate を構成する共有 Method です。単なる formatter ではなく、与えられた authority の内側で必要な planning judgment を担います。

## Input and ownership

<!-- @contract planning-synthesis-input-boundary -->
caller は一つの task-local Local Model の owner のまま、requested artifact responsibility、current understanding、established direction、authority constraints、必要なら upstream Researcher evidence を Data として渡す。
<!-- @/contract -->

Planning Synthesis は別の Local Model、artifact kind の fixed enum / schema、永続 artifact を作りません。repository exploration、research、Researcher invocation、Model Construction、Human clarification、review、workflow status の決定も行いません。

## Synthesis responsibility

request と artifact responsibility に material な semantics だけを選びます。実装 plan なら work / dependency / acceptance / verification、設計判断なら context / decision / rationale / alternatives / consequences、比較検討なら comparison axes / evidence / trade-off / recommendation など、requested artifact が必要とする意味を coherent に構成します。

<!-- @contract planning-synthesis-materiality -->
非実装 artifact に Acceptance Criteria、rollback、work decomposition、execution order を儀式的に要求せず、requested artifact に material な semantics だけを選ぶ。
<!-- @/contract -->

十分な evidence がある場合は recommendation-first で一案と理由を示し、material な代替案だけを残します。section 構成、serialization、completeness score、expected-output oracle は固定しません。

## Authority and alternative perspective

<!-- @contract planning-synthesis-authority-boundary -->
Planning Synthesis は supplied direction と authority constraints の意味を保持し、その内側でだけ planning decision を行う。
<!-- @/contract -->

Planning Synthesis は initial coherent candidate 全体に対する alternative implementation perspective の適用結果を扱います。applicability、advice の意味、採否、統合の判断は Agentic workflow に残し、次の Flow は supplied Data に応じた invocation と result routing を所有します。

<!-- @contract planning-synthesis-advisor-boundary -->
Planning Synthesis は initial coherent candidate 全体に対する advisor の non-binding perspective を受け、固定された goal、direction、scope、constraints、required behavior を保ったまま採否を裁定し、coherent に統合します。
<!-- @/contract -->

## Programmatic Flow

<!-- @contract planning-synthesis-advisor-flow -->
Trigger: Planning Synthesis が initial candidate の構成結果、または parent disposition を受け取る。
<!-- @/contract -->

Inputs: initial coherent candidate または material input gap、固定された goal / direction / scope / constraints / required behavior、bounded evidence と読取範囲、advisor applicability と理由、invocation-local advisor state、advisor availability / raw result、parent-owned result classification（normal、no alternative を含む、material comparison insufficiency、invocation failure）、safe-continuation validity、adopted disposition、integrated coherent candidate。

Procedure:

1. initial required Data（advisor applicability、reason、invocation-local state、または構成結果）のいずれかが欠けている場合は、advisor を起動せず material input gap を caller へ返す。
2. candidate coherence を妨げる material input gap がある場合は、advisor を起動せず gap を caller へ返す。
3. coherent candidate があり advisor が nonapplicable の場合は、advisor を起動せず candidate を返す。
<!-- @contract planning-synthesis-advisor-invocation -->
4. coherent candidate があり advisor が applicable で state が未実施の場合は、実行直前に state を実施済みへ更新してから fresh / context-isolated advisor を一回起動する。
<!-- @/contract -->
<!-- @contract planning-synthesis-advisor-failure -->
5. parent-owned result classification が invocation failure または unavailable の場合は `incomplete` を返し、skip、別 agent、呼び直しを選択しない。
<!-- @/contract -->
<!-- @contract planning-synthesis-advisor-reentry -->
6. parent disposition があり state が実施済みの場合は advisor を再起動せず、既存の advice または limitation を再利用する。
7. re-entry で material comparison insufficiency または safe-continuation validity が invalid の場合は、stale advice を統合せず `incomplete` を返す。normal（no alternative を含む）で safe-continuation validity が valid、かつ integrated coherent candidate がある場合だけ coherent candidate を Core へ返す。
<!-- @/contract -->
8. raw advisor result は `parent-adjudication-required` として Synthesis 内に保持し、Core の completion candidate へ渡さない。採否・統合後の re-entry では、上記の supplied classification、disposition、integrated candidate だけを routing し、advisor を追加起動しない。

Outcomes: advisor なしの coherent candidate、parent adjudication を要する fresh advisor result、統合後の coherent candidate、material input gap、または material reason を持つ `incomplete`。

Flow の Outcomes で fresh raw result を受けた後、Planning Synthesis は Flow の外で bounded evidence と固定方向を比較し、result classification（normal、no alternative を含む、material comparison insufficiency、invocation failure）と safe-continuation validity を意味判断として構成します。その classification と validity を入力へ戻し、adopted disposition と integrated coherent candidate を構成して re-entry へ渡します。

applicable な advisor の入力は candidate 全体、固定された goal / direction / scope / constraints / required behavior、bounded evidence とその読取範囲に限ります。prior reasoning、prior advisor result、範囲外探索、新規 research、外部状態変更は入力にも実行にも含めません。

<!-- @only codex -->

fresh `plan-quality-advisor` を起動する場合は `fork_turns = "none"` を指定する。
<!-- @/only -->

advisor は materially different な実装像を原則一つ返し、実装 approach、責務分割、分解、依存、順序、verification strategy の差と条件を示します。有力な alternative がない結果は正常です。

Flow の Outcomes 後、Planning Synthesis は固定された goal、direction、scope、constraints、required behavior への適合、repository fit、complexity、dependency、verification cost、maintainability など今回 material な比較軸で advice を全面採用、部分採用、または不採用に裁定し、adopted disposition と integrated coherent candidate を構成します。採用した要素だけを coherent に統合し、棄却案は material な設計判断を説明する場合に限って最終 Plan へ簡潔に残します。これらの採否・統合判断は Flow の外で行い、再入時に supplied Data として渡します。

<!-- @contract planning-synthesis-advisor-result -->
有力な alternative がない結果は正常として扱い、根拠不足で比較不能な結果は limitation として保持します。
<!-- @/contract -->

## Result boundary

<!-- @contract planning-synthesis-result-boundary -->
返す結果は requested artifact に material な semantics を持つ coherent candidate、candidate coherence を妨げる具体的な material input gap、または advisor route を安全に継続できない理由を持つ `incomplete` です。
<!-- @/contract -->

`parent-adjudication-required` は Synthesis 内の中間結果であり、Core の completion candidate ではありません。

gap には candidate を作れない理由と affected planning semantics を含め、caller が次の Action を判断できる形にします。gap の解消 Action、Human interaction、review、workflow status、final acceptance は caller に残します。

<!-- @contract planning-synthesis-gap-case -->
candidate coherence に material な fact が input にない場合、その fact、candidate を作れない理由、affected semantics を gap として caller へ返す。
<!-- @/contract -->

Planning Synthesis は public entrypoint、review loop、Local Model owner、final acceptance owner ではありません。
