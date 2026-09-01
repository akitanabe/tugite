<!-- Generated from shared/. Do not edit directly. -->

# Planning Synthesis

Planning Synthesis は、caller が確立した理解と authority から request-relative な coherent planning / design artifact candidate を構成する共有 Method です。単なる formatter ではなく、与えられた authority の内側で必要な planning judgment を担います。

## Input and ownership

caller は一つの task-local Local Model の owner のまま、requested artifact responsibility、current understanding、established direction、authority constraints、必要なら upstream Researcher evidence を Data として渡す。

Planning Synthesis は別の Local Model、artifact kind の fixed enum / schema、永続 artifact を作りません。repository exploration、research、Researcher invocation、Model Construction、Human clarification、review、workflow status の決定も行いません。

## Synthesis responsibility

request と artifact responsibility に material な semantics だけを選びます。実装 plan なら work / dependency / acceptance / verification、設計判断なら context / decision / rationale / alternatives / consequences、比較検討なら comparison axes / evidence / trade-off / recommendation など、requested artifact が必要とする意味を coherent に構成します。

非実装 artifact に Acceptance Criteria、rollback、work decomposition、execution order を儀式的に要求せず、requested artifact に material な semantics だけを選ぶ。

十分な evidence がある場合は recommendation-first で一案と理由を示し、material な代替案だけを残します。section 構成、serialization、completeness score、expected-output oracle は固定しません。

## Authority and advisory boundary

Planning Synthesis は supplied direction と authority constraints の意味を保持し、その内側でだけ planning decision を行う。

局所判断に第二の観点が material に有用な場合だけ fresh / context-isolated な `plan-quality-advisor` を使えます。各 invocation は concrete question と必要 context だけを渡し、advice の採否は Planning Synthesis が所有します。

Planning Synthesis は advice の採否を所有し、advisor output を新しい direction や binding conclusion として扱わない。

## Result boundary

返す結果は requested artifact に material な semantics を持つ coherent candidate、または candidate coherence を妨げる具体的な material input gap である。

gap には candidate を作れない理由と affected planning semantics を含め、caller が次の Action を判断できる形にします。gap の解消 Action、Human interaction、review、workflow status、final acceptance は caller に残します。

input が coherent synthesis に十分なら、advisor を起動せず Planning Synthesis が必要な判断を行い candidate を返せる。

candidate coherence に material な fact が input にない場合、その fact、candidate を作れない理由、affected semantics を gap として caller へ返す。

Planning Synthesis は public entrypoint、review loop、Local Model owner、final acceptance owner ではありません。
