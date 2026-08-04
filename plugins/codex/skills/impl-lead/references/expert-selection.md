<!-- Generated from shared/. Do not edit directly. -->

# Expert 選択

`expert-implementer` は v5 agent surface に残るが、expert の選択手順は現 bundle では定義しない。
公開 API、data migration、security、concurrency、変更行数、重要度などの属性から選択経路を推測せず、
expert を候補にする必要が生じた時点で現在の委譲フローを未完了として停止する。

停止時は、タスクと受け入れ条件、確定済みの scope、親相当の能力が必要と考えた判断、senior では不足すると
考えた根拠、未着手・未完了範囲を Data として親へ返す。選択経路、自動 fallback、委譲 prompt の追加 field は、
この reference では定義しない。
