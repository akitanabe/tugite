# plan-interactive pre-freeze-advisor v1

この reference は `plan-interactive` が freeze 前に `plan-quality-advisor` を起動する場合の handoff と adoption
procedure だけを定義する。親が root `SKILL.md` の trigger predicate を確定した Data を受けて実行し、load predicate や
4 条件、Human boundary invariant をここで再定義・拡張・上書きしない。advisor が non-binding であること、自動採用・
自動質問・direct Human question を禁止する境界の意味の正本は root である。

## handoff と adoption procedure

親確定の `trigger satisfied` Data を受けたときだけ、次を実行する。

1. root の advisor 親 Data（`advisor`、`input`、`insight`、`adjudicator`、`mapping`、`ledger_boundary`）に従い、
   read-only `plan-quality-advisor` へ candidate snapshot と verified criteria Data を渡す。
2. 返却 insight を non-binding Data として受け取り、親が primary evidence と要求に対して
   `adopted` / `rejected` / `unresolved` を adoption ledger へ記録する。
3. decision ledger と adoption ledger を混同せず、`insights: []` を direction freeze の根拠にしない。
4. insight を自動採用せず、insight から質問を自動生成せず、advisor を Human への直接質問主体にしない。
5. Human direction に影響しうる unresolved は、親が evidence を検証して自身の recommendation を再構成したうえで
   clarify-it application へ返す。

この reference は fixed phase を導入せず、trigger 不成立の run では load されない。
