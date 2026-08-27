# Plan artifact publication

Publication reference identity: `plan-artifact-publication-v1`.

この reference は plan-family の Agentic workflow が確定した成果物を安全に保存するための deterministic publication boundary である。
Kernel ではなく、呼び出し元が選択して確定した target を受け取る shared reference として扱う。

destination の選定と unique comparison の正本は `destination-selection-v1` である。この reference は選定・比較 procedure を持たず、pointer だけを残す。caller は skill-relative `../../references/destination-selection.md` で destination を確定してから、この reference の `publication_target` を組み立てる。

## Agentic / mixed publication target

Agentic または mixed side は、確定した qualified destination から単一 filename component を導出し、exact destination、exact filename、finite retry bound を確定する。
既存 destination の candidate は destination object identity も確認できなければ `publication_target` にしない。Flow はこの選定を再実行せず、別 target を
暗黙に選び直さない。

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
      exclusive_creation_intent
    }
  }
}
```

既存 destination では、qualification 後に観測した既存 destination object identity を記録する。OS-temp では top-level
`exact_destination` が作成予定の run-owned directory path であり、verified temp-root 直下への canonical containment を満たす。
pre-creation に記録する branch 固有 Data は verified temp-root identity と exclusive creation intent だけである。Agentic / mixed side は filename / retry bound / `publication_target` 組み立てと、verified temp-root identity、top-level `exact_destination`、exclusive creation intent の確定 Data を返すまでを所有し、directory を作成しない。directory の object identity は Flow が作成成功後に記録し、作成前に将来の identity を推測・要求しない。

OS-temp では verified temp-root の identity、top-level exact destination の root 直下 containment、symlink / junction 非追従を確認してから、exclusive creation intent を確定 Data として返す。directory の exclusive / non-follow 作成は `programmatic-publication` Flow だけが実行する。

自動 filename は成果物内容由来の短い安全な単一 component とし、空文字、`.`、`..`、absolute path、path separator を採用しない。既存 final path は
bytes が同一でも上書きせず collision とする。retry bound は invocation 開始時に有限値として固定し、collision の場合だけ numeric suffix を変える。
各 exact path の資格は staging 作成直前と publish 直前に再確認し、資格喪失は `destination-reselection-required` として親へ返す。write-time の ignored/index 再確認は write safety の remaining witness であり、selector 一次欠格の代替にしない。

OS-temp の verified temp-root が資格を満たす場合だけ、その直下の top-level exact destination と exclusive creation intent を選択結果に含める。
final / staging の全 component について canonical containment と non-follow を確認できる Data を渡し、root、run-owned directory、containment、
repository との関係が unknown なら Flow を起動せず `incomplete` とする。

## Programmatic publication Flow

<!-- @contract plan-artifact-publication-flow -->
この Flow は、親が意味判断を完了して確定した `publication_target` に対する fixed deterministic procedure だけを実行する。
target selection、candidate ranking、filename の導出、retry bound の変更は Flow の責務ではない。`programmatic-publication` は選定を再実行しない。

### programmatic-publication

<!-- @anchor publication-flow-trigger -->
Trigger: Agentic / mixed side が semantic eligibility と exact `publication_target` を確定し、親が publication を要求したとき。
<!-- @anchor publication-flow-inputs -->
Inputs: 凍結した artifact bytes、exact destination、exact filename、finite retry bound、qualification evidence、既存 destination では観測済み destination object identity、OS-temp では verified temp-root identity / exclusive creation intent。
<!-- @anchor publication-flow-procedure -->
Procedure: 既存 destination では資格と観測済み destination object identity を再確認する。OS-temp では verified temp-root identity と top-level exact destination の root 直下 containment を再確認し、exact destination の directory を same-filesystem の secure / exclusive / non-follow で作成して、その object identity を記録する。directory 作成後、staging 作成前に、資格と destination object identity を再確認する。verified destination identity の下で、同じ filesystem 上に symlink / junction を追従しない atomic / exclusive staging を作成し、作成した staging object identity を記録する。staging を write して close し、同一 object の byte-identical readback を確認する。readback failure は `incomplete` として publish を行わず、complete のときだけ no-clobber publish を行い、既存 final との collision だけを finite retry bound の範囲で filename suffix により再試行する。資格喪失または別 target が必要な場合は、記録した staging identity と現 object identity が一致することを確認して所有 staging だけを cleanup し、`destination-reselection-required` を返す。publish commit 後は published final を保持し、publish 前の failure では所有 identity と一致する staging / empty run-owned directory だけを non-recursive / non-follow で cleanup する。
<!-- @anchor publication-flow-outcomes -->
Outcomes: published result、collision retry の後の `published result`、安全に所有 cleanup できる `destination-reselection-required`、または `incomplete`。target 確定前の unsafe / unknown、identity mismatch、cleanup failure、readback failure、retry bound 到達は blind fallback や target reselection をせず `incomplete` とする。target 確定後の資格喪失または別 target の必要は `destination-reselection-required` とする。published final は cleanup 対象にせず保持する。

Flow は canonical containment、symlink / junction non-follow、ignored / index qualification、no-clobber、exact ownership identity cleanup を各再確認に含める。
他者の object、identity 不一致の staging、既存 final、publish 済み final を変更・削除しない。`destination-reselection-required` は親へ返す結果であり、Flow が別 destination を選択することを意味しない。
<!-- @/contract -->

## Consumer boundary

consumer はこの reference を skill-relative `../../references/plan-artifact-publication.md` から一度だけ load し、identity と必要本文を検証してから
`programmatic-publication` を使う。consumer 固有の semantic eligibility、final acceptance / opt-out、artifact body、incomplete 境界、outward status、
stdout の projection は consumer が所有する。reference はそれらを再定義せず、consumer は publication procedure を複製しない。
