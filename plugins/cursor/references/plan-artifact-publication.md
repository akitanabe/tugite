<!-- Generated from shared/. Do not edit directly. -->

# Plan artifact publication

Publication reference identity: `plan-artifact-publication-v1`.

この reference は plan-family の Agentic workflow が確定した成果物を安全に保存するための deterministic publication boundary である。
Kernel ではなく、呼び出し元が選択して確定した target を受け取る shared reference として扱う。

## Agentic / mixed target selection

Agentic または mixed target selection は、project-local の用途 evidence を比較し、候補を ranking して一つの target を選ぶ。
成果物の内容から単一 filename component を導出し、exact destination、exact filename、finite retry bound を確定する。
用途 evidence、Git の ignored / index 資格、canonical containment、symlink / junction 非追従、destination object identity を確認できない
candidate は選択しない。Flow はこの選択を再実行せず、別 target を暗黙に選び直さない。

`publication_target` は次の Data であり、pre-creation に存在しない identity を要求してはならない。

```text
publication_target = {
  exact_destination,
  exact_filename,
  finite_retry_bound,
  qualification_evidence,
  destination_state = one of {
    existing_destination_object_identity,
    os_temp_creation = {
      verified_temp_root_identity,
      exact_run_owned_directory_path,
      exclusive_creation_intent
    }
  }
}
```

既存 destination では、qualification 後に観測した既存 destination object identity を記録する。OS-temp に新しい run-owned directory を
作る場合は、pre-creation に verified temp-root identity、exact run-owned directory path、exclusive creation intent を記録する。Agentic / mixed side は candidate 比較、verified temp-root identity、exact run-owned directory path、exclusive creation intent の確定 Data を返すまでを所有し、directory を作成しない。directory の object identity は Flow が作成成功後に記録し、作成前に将来の identity を推測・要求しない。

project-local 候補では用途 evidence と ignored / index 資格を満たす exact destination だけを採用する。OS-temp 候補では verified temp-root の
identity、canonical containment、symlink / junction 非追従を確認してから、exact run-owned directory path と exclusive creation intent を確定 Data として返す。directory の exclusive / non-follow 作成は `programmatic-publication` Flow だけが実行する。
canonical path が repository 内に入る OS-temp 候補には project-local と同じ containment、用途、ignored / index 資格を適用する。

明示された destination は最優先であり、path type、canonical containment、symlink / junction 非追従、no-clobber を安全に確認できない場合は
別 destination へ無言で fallback せず `incomplete` とする。未指定の場合だけ、用途が直接 evidence で確認できる既存の project-local 候補を比較し、
候補なし、同順位、non-Git project、または資格を確認できない場合に verified OS-temp を候補として選ぶ。cache、build、vendor など用途が確認できない
decoy directory、ignored であることだけの候補、または path が repository containment 外の候補を選ばない。未指定時も project-local directory や ignore rule を新設しない。

自動 filename は成果物内容由来の短い安全な単一 component とし、空文字、`.`、`..`、absolute path、path separator を採用しない。既存 final path は
bytes が同一でも上書きせず collision とする。retry bound は invocation 開始時に有限値として固定し、collision の場合だけ numeric suffix を変える。
各 exact path の資格は staging 作成直前と publish 直前に再確認し、資格喪失は `destination-reselection-required` として親へ返す。

OS-temp の verified temp-root が資格を満たす場合だけ、その直下の exact run-owned directory path と exclusive creation intent を選択結果に含める。
final / staging の全 component について canonical containment と non-follow を確認できる Data を渡し、root、run-owned directory、containment、
repository との関係が unknown なら Flow を起動せず `incomplete` とする。

## Programmatic publication Flow

この Flow は、親が意味判断を完了して確定した `publication_target` に対する fixed deterministic procedure だけを実行する。
target selection、candidate ranking、filename の導出、retry bound の変更は Flow の責務ではない。

### programmatic-publication

Trigger: Agentic / mixed side が semantic eligibility と exact `publication_target` を確定し、親が publication を要求したとき。
Inputs: 凍結した artifact bytes、exact destination、exact filename、finite retry bound、qualification evidence、既存 destination では観測済み destination object identity、OS-temp では verified temp-root identity / exact run-owned directory path / exclusive creation intent。
Procedure: 既存 destination では資格と観測済み destination object identity を再確認する。OS-temp では verified temp-root identity と exact run-owned directory path を再確認し、その root 直下に same-filesystem の secure / exclusive run-owned directory を symlink / junction 非追従で作成して、作成した directory object identity を記録する。資格と destination object identity を再確認する。verified destination identity の下で、同じ filesystem 上に symlink / junction を追従しない atomic / exclusive staging を作成し、作成した staging object identity を記録する。staging を write して close し、同一 object の byte-identical readback を確認する。readback failure は `incomplete` として publish を行わず、complete のときだけ no-clobber publish を行い、既存 final との collision だけを finite retry bound の範囲で filename suffix により再試行する。資格喪失または別 target が必要な場合は、記録した staging identity と現 object identity が一致することを確認して所有 staging だけを cleanup し、`destination-reselection-required` を返す。publish commit 後は published final を保持し、publish 前の failure では所有 identity と一致する staging / empty run-owned directory だけを non-recursive / non-follow で cleanup する。
Outcomes: published result、collision retry の後の `published result`、安全に所有 cleanup できる `destination-reselection-required`、または `incomplete`。target 確定前の unsafe / unknown、identity mismatch、cleanup failure、readback failure、retry bound 到達は blind fallback や target reselection をせず `incomplete` とする。target 確定後の資格喪失または別 target の必要は `destination-reselection-required` とする。published final は cleanup 対象にせず保持する。

Flow は canonical containment、symlink / junction non-follow、ignored / index qualification、no-clobber、exact ownership identity cleanup を各再確認に含める。
他者の object、identity 不一致の staging、既存 final、publish 済み final を変更・削除しない。`destination-reselection-required` は親へ返す結果であり、Flow が別 destination を選択することを意味しない。

## Consumer boundary

consumer はこの reference を skill-relative `../../references/plan-artifact-publication.md` から一度だけ load し、identity と必要本文を検証してから
`programmatic-publication` を使う。consumer 固有の semantic eligibility、final acceptance / opt-out、artifact body、incomplete 境界、outward status、
stdout の projection は consumer が所有する。reference はそれらを再定義せず、consumer は publication procedure を複製しない。
