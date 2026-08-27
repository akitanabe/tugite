#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

new_repository_copy() {
  local destination="$1"

  mkdir -p "$destination"
  tar \
    --exclude=.git \
    --exclude=.local \
    --exclude=node_modules \
    -C "$repo_root" \
    -cf - \
    . | tar -C "$destination" -xf -
}

assert_projection_inventory() {
  local repository="$1"
  local projection="$repository/.local/gunte/shared-v7-contracts/documents"
  local expected=(
    agentic-model-construction.md
    behavior-model-observation.md
    model-construction.md
    reality-model-observation.md
  )
  local actual=()

  mapfile -t actual < <(find "$projection" -maxdepth 1 -type f -printf '%f\n' | sort)
  [[ "${actual[*]}" == "${expected[*]}" ]] || fail "unexpected projection inventory: ${actual[*]}"
  [[ ! -e "$projection/README.md" ]] || fail "README.md was projected"
  [[ ! -e "$projection/agents/research-agent.md" ]] || fail "research-agent.md was projected"
}

replace_once() {
  local file="$1"
  local before="$2"
  local after="$3"

  MUTATION_BEFORE="$before" MUTATION_AFTER="$after" perl -0pi -e '
    BEGIN {
      $before = $ENV{"MUTATION_BEFORE"};
      $after = $ENV{"MUTATION_AFTER"};
      $count = 0;
    }
    $count += s/\Q$before\E/$after/g;
    END { exit 1 unless $count == 1; }
  ' "$file" || fail "mutation source did not occur exactly once: $file"
}

assert_contract_mutation_fails() {
  local name="$1"
  local source_path="$2"
  local before="$3"
  local after="$4"
  local contract_id="$5"
  local related_path="$6"
  local projection_path="$7"
  local failure_kind="$8"
  local repository="$tmp_dir/$name"
  local output
  local projection_hash_before
  local projection_hash_after

  mkdir -p "$repository"
  cp -a "$baseline_template/." "$repository"
  projection_hash_before="$(sha256sum "$repository/$projection_path")"
  replace_once "$repository/$source_path" "$before" "$after"

  if output="$(cd "$repository" && gunte emit --target shared-v7-contracts 2>&1)"; then
    fail "$name unexpectedly passed"
  fi

  [[ "$output" == *"$contract_id"* ]] || fail "$name did not report $contract_id: $output"
  [[ "$output" == *"target shared-v7-contracts"* ]] || fail "$name did not report target shared-v7-contracts: $output"
  [[ "$output" == *"$related_path"* ]] || fail "$name did not report $related_path: $output"
  [[ "$output" == *"$failure_kind"* ]] || fail "$name did not report $failure_kind: $output"
  projection_hash_after="$(sha256sum "$repository/$projection_path")"
  [[ "$projection_hash_after" == "$projection_hash_before" ]] || fail "$name rewrote the projection after validation failed"
}

assert_requires_mutation_fails() {
  local name="$1"
  local source_path="$2"
  local before="$3"
  local after="$4"
  local contract_id="$5"

  assert_contract_mutation_fails \
    "$name" \
    "$source_path" \
    "$before" \
    "$after" \
    "$contract_id" \
    "$source_path" \
    ".local/gunte/shared-v7-contracts/documents/$(basename "$source_path")" \
    requires_violation
}

test_fresh_repository_builds_shared_v7_projection() {
  local repository="$tmp_dir/baseline"

  new_repository_copy "$repository"
  [[ ! -e "$repository/.local/gunte/shared-v7-contracts" ]] || fail "fresh copy already has a projection"
  (
    cd "$repository"
    gunte emit --target shared-v7-contracts
    gunte check --target shared-v7-contracts
  )
  assert_projection_inventory "$repository"
}

test_model_construction_ownership_is_required() {
  assert_requires_mutation_fails \
    model-ownership \
    shared-v7/model-construction.md \
    '- **`1 top-level workflow invocation = exactly 1 task-local Local Model`** とする。' \
    '- top-level workflow invocation ごとに任意数の Local Model を持てる。' \
    shared-v7-model-owner-5e2b8b392201
}

test_current_semantic_witnesses_are_required() {
  assert_requires_mutation_fails \
    model-nested-owner \
    shared-v7/model-construction.md \
    '- nested workflow、consumer、reviewer、Research Agent は独自 Local Model を所有しない。' \
    '- nested workflow、consumer、reviewer、Research Agent は独自 Local Model を所有してよい。' \
    shared-v7-model-nested-owner-07ed8500dbb9
  assert_requires_mutation_fails \
    model-transition \
    shared-v7/model-construction.md \
    'Recomposition は、Reintegration または grounded dependency evaluation により current Local Model の material semantic region が invalidated した場合の repair である。' \
    'Recomposition は、Reintegration より前に常に実行する repair である。' \
    shared-v7-model-transition-8ee2eab59f2e
  assert_requires_mutation_fails \
    model-completion \
    shared-v7/model-construction.md \
    'Projection Sufficiency は Method completion と同一ではなく、Method completion は workflow readiness とも同一ではない。' \
    'Projection Sufficiency、Method completion、workflow readiness は同一である。' \
    shared-v7-model-completion-1b7e4dca6359

  assert_requires_mutation_fails \
    agentic-human-boundary \
    shared-v7/agentic-model-construction.md \
    '違いは construction 中に新しい Human interaction channel を開始しないことである。' \
    'construction 中に新しい Human interaction channel を開始してよい。' \
    shared-v7-agentic-human-boundary-c33e46f73b82
  assert_requires_mutation_fails \
    agentic-nonmaterial-completion \
    shared-v7/agentic-model-construction.md \
    '次工程の方向・範囲・結果を実質的に変えない unresolved uncertainty は qualification として保持したまま completion してよい。' \
    'すべての unresolved uncertainty が消えるまで completion してはならない。' \
    shared-v7-agentic-nonmaterial-completion-5f912b7d0e29
  assert_requires_mutation_fails \
    agentic-material-stop \
    shared-v7/agentic-model-construction.md \
    'Agent-side で合理的に利用可能な bounded resolution route を用いても gap が解消できず、その gap が次工程の方向・範囲・結果を実質的に変え得る場合は停止する。' \
    'material gap が残っていても常に completion する。' \
    shared-v7-agentic-material-stop-e5166be41edb
  assert_requires_mutation_fails \
    agentic-stop-owner \
    shared-v7/agentic-model-construction.md \
    'Agentic Model Construction 自身は Human に質問せず、Interactive Model Construction への切り替えも行わない。停止後の扱いは calling workflow が所有する。' \
    'Agentic Model Construction 自身が Human に質問し、停止後の route を所有する。' \
    shared-v7-agentic-stop-owner-3136cb2bc843

  assert_requires_mutation_fails \
    bmo-projection-only \
    shared-v7/behavior-model-observation.md \
    '**projection-only specialization**' \
    '**observation-and-verdict specialization**' \
    shared-v7-bmo-projection-only-33629d55190f
  assert_requires_mutation_fails \
    bmo-stop-point \
    shared-v7/behavior-model-observation.md \
    'BMO はこの停止点までを所有する。' \
    'BMO は停止後の workflow continuation も所有する。' \
    shared-v7-bmo-stop-point-3712e1702b95
  assert_requires_mutation_fails \
    bmo-grounding \
    shared-v7/behavior-model-observation.md \
    'candidate は Behavior または authority を持つ Context に grounding があり、かつ入力 Behavior の意味上の distinction である場合だけ `Admit` する。' \
    'candidate は測定可能であれば grounding なしに `Admit` する。' \
    shared-v7-bmo-admission-grounding-d30b3d4ac064
  assert_requires_mutation_fails \
    bmo-no-self-grounding \
    shared-v7/behavior-model-observation.md \
    '評価対象 claim 自身を、その claim の Expected Observation の grounding に再利用しない。' \
    '評価対象 claim 自身を Expected Observation の唯一の grounding にする。' \
    shared-v7-bmo-no-self-grounding-7e0e9275fd8e
  assert_requires_mutation_fails \
    bmo-collective-nonverdict \
    shared-v7/behavior-model-observation.md \
    'consumer 固有の成果物・評価対象・downstream quality、workflow readiness、Reality verification、Real / Reality の完全性、Behavior 自体の真理を判定するものではない。' \
    'consumer 固有の成果物と downstream quality の verdict を返す。' \
    shared-v7-bmo-collective-nonverdict-3140677fb21c
  assert_requires_mutation_fails \
    bmo-stop-boundary \
    shared-v7/behavior-model-observation.md \
    'Expected Observation Model と Collective Sufficiency を返したら停止する。' \
    'Expected Observation Model を返した後に remediation を開始する。' \
    shared-v7-bmo-stop-boundary-57ed70177942

  assert_requires_mutation_fails \
    rmo-problem-stop \
    shared-v7/reality-model-observation.md \
    'RMO は Problem Derivation で停止する。' \
    'RMO は Problem Derivation 後に remediation を開始する。' \
    shared-v7-rmo-problem-stop-2611ec071d14
  assert_requires_mutation_fails \
    rmo-no-remediation \
    shared-v7/reality-model-observation.md \
    '- remediation、implementation、Improvement Candidate、Change Proposal' \
    '- remediation を所有する' \
    shared-v7-rmo-no-remediation-efff1b0e698e
  assert_requires_mutation_fails \
    rmo-no-acquisition \
    shared-v7/reality-model-observation.md \
    '- evidence acquisition、Research Agent の dispatch、same Local Model への Reintegration / Recomposition' \
    '- evidence acquisition と Research Agent dispatch を所有する' \
    shared-v7-rmo-no-acquisition-56faea4219fd
  assert_requires_mutation_fails \
    rmo-model-nonreadiness \
    shared-v7/reality-model-observation.md \
    $'`Sufficient` は Reality 全体の completeness、External Real への到達、actual evidence の取得、workflow\nreadiness を意味しない。' \
    '`Sufficient` は Reality 全体の completeness と workflow readiness を意味する。' \
    shared-v7-rmo-model-nonreadiness-2cb56aecc2c7
  assert_requires_mutation_fails \
    rmo-observation-gate \
    shared-v7/reality-model-observation.md \
    $'Model Sufficiency が `Sufficient` の場合、caller が許可した boundary 内で、frozen な criteria / conditions\nに沿って concrete evidence と接触する。' \
    'Model Sufficiency に関係なく concrete evidence と接触する。' \
    shared-v7-rmo-observation-gate-f1bf5d41b1c3
  assert_requires_mutation_fails \
    rmo-sufficiency-distinction \
    shared-v7/reality-model-observation.md \
    $'`Model Sufficiency` と\n`Observed Evidence Sufficiency` は別であり' \
    '`Model Sufficiency` と `Observed Evidence Sufficiency` は同一であり' \
    shared-v7-rmo-sufficiency-distinction-49d148234a56
  assert_requires_mutation_fails \
    rmo-membership-problem \
    shared-v7/reality-model-observation.md \
    '- **Yes** — current Target に属する discrepancy として Target-relative Problem を導出できる。' \
    '- **Yes** — Target 外の discrepancy も Problem にする。' \
    shared-v7-rmo-membership-problem-56eaf462e93f
  assert_requires_mutation_fails \
    rmo-membership-incidental \
    shared-v7/reality-model-observation.md \
    '- **No** — Target を拡張せず、必要なら Incidental Finding として返して停止する。' \
    '- **No** — Target を拡張して Problem にする。' \
    shared-v7-rmo-membership-incidental-efb328f8a783
  assert_requires_mutation_fails \
    rmo-membership-uncertainty \
    shared-v7/reality-model-observation.md \
    $'- **Unclear** — Target semantics、authority、または observed evidence の解決が必要な `Uncertainty` として\n  停止する。' \
    '- **Unclear** — 推測で Target Membership を確定する。' \
    shared-v7-rmo-membership-uncertainty-a85b6abb25de
  assert_requires_mutation_fails \
    rmo-caller-dispatch \
    shared-v7/reality-model-observation.md \
    $'RMO は Research Agent を dispatch しない。RMO の Required Reality Distinction に対して追加 evidence が必要\nな場合、caller が bounded objective、scope、authority、relevant context / evidence surface を確定して\nResearch Agent に委譲してよい。' \
    'RMO が Research Agent の objective と dispatch を所有する。' \
    shared-v7-rmo-caller-dispatch-d4a48b959269
  assert_requires_mutation_fails \
    rmo-caller-reintegration \
    shared-v7/reality-model-observation.md \
    $'caller は result の authority と semantic effect を判断し、必要なら同じ top-level invocation の同じ\ntask-local Local Model へ Reintegration / Recomposition する。' \
    'Research Agent が独自 Local Model へ Reintegration する。' \
    shared-v7-rmo-caller-reintegration-a95b84105a71
}

test_relation_anchor_cannot_move_to_another_document() {
  local repository="$tmp_dir/moved-anchor"
  local model_projection=.local/gunte/shared-v7-contracts/documents/model-construction.md
  local agentic_projection=.local/gunte/shared-v7-contracts/documents/agentic-model-construction.md
  local model_hash_before
  local agentic_hash_before
  local output

  mkdir -p "$repository"
  cp -a "$baseline_template/." "$repository"
  model_hash_before="$(sha256sum "$repository/$model_projection")"
  agentic_hash_before="$(sha256sum "$repository/$agentic_projection")"
  replace_once \
    "$repository/shared-v7/model-construction.md" \
    '<!-- @anchor shared-v7-model-completion-relation -->' \
    ''
  replace_once \
    "$repository/shared-v7/agentic-model-construction.md" \
    '<!-- @anchor shared-v7-agentic-document -->' \
    $'<!-- @anchor shared-v7-agentic-document -->\n<!-- @anchor shared-v7-model-completion-relation -->'

  if output="$(cd "$repository" && gunte emit --target shared-v7-contracts 2>&1)"; then
    fail "moved relation anchor unexpectedly passed"
  fi

  [[ "$output" == *"shared-v7-model-document-before-completion"* ]] || fail "moved anchor did not report its order contract: $output"
  [[ "$output" == *"order_violation"* ]] || fail "moved anchor did not report order_violation: $output"
  [[ "$output" == *"shared-v7/model-construction.md"* ]] || fail "moved anchor did not report model-construction.md: $output"
  [[ "$output" == *"shared-v7/agentic-model-construction.md"* ]] || fail "moved anchor did not report agentic-model-construction.md: $output"
  [[ "$(sha256sum "$repository/$model_projection")" == "$model_hash_before" ]] || fail "moved anchor rewrote model projection"
  [[ "$(sha256sum "$repository/$agentic_projection")" == "$agentic_hash_before" ]] || fail "moved anchor rewrote agentic projection"
}

test_target_resolution_rejects_unknown_target() {
  local output

  if output="$(cd "$baseline_template" && gunte check --target shared-v7 2>&1)"; then
    fail "unknown shared-v7 target unexpectedly passed"
  fi
  [[ "$output" == *"unknown_target"* ]] || fail "unknown target did not report unknown_target: $output"
}

test_stale_projection_is_detected() {
  local repository="$tmp_dir/stale-projection"
  local output

  mkdir -p "$repository"
  cp -a "$baseline_template/." "$repository"
  replace_once \
    "$repository/shared-v7/model-construction.md" \
    'これは第三の実行 Method ではない。' \
    'これは独立した実行 Method ではない。'

  if output="$(cd "$repository" && gunte check --target shared-v7-contracts 2>&1)"; then
    fail "stale projection unexpectedly passed"
  fi
  [[ "$output" == *"output_mismatch"* ]] || fail "stale projection did not report output_mismatch: $output"
  [[ "$output" == *".local/gunte/shared-v7-contracts/documents/model-construction.md"* ]] || fail "stale projection did not identify model-construction.md: $output"
}

test_missing_projection_is_rebuilt_by_emit() {
  local repository="$tmp_dir/missing-projection"
  local projection=.local/gunte/shared-v7-contracts/documents/reality-model-observation.md
  local output

  mkdir -p "$repository"
  cp -a "$baseline_template/." "$repository"
  rm "$repository/$projection"

  if output="$(cd "$repository" && gunte check --target shared-v7-contracts 2>&1)"; then
    fail "missing projection unexpectedly passed"
  fi
  [[ "$output" == *"output_mismatch"* ]] || fail "missing projection did not report output_mismatch: $output"
  [[ "$output" == *"$projection"* ]] || fail "missing projection path was not reported: $output"

  (
    cd "$repository"
    gunte emit --target shared-v7-contracts
    gunte check --target shared-v7-contracts
  )
}

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

test_fresh_repository_builds_shared_v7_projection
baseline_template="$tmp_dir/template"
new_repository_copy "$baseline_template"
(cd "$baseline_template" && gunte emit --target shared-v7-contracts)
test_model_construction_ownership_is_required
test_current_semantic_witnesses_are_required
test_relation_anchor_cannot_move_to_another_document
test_target_resolution_rejects_unknown_target
test_stale_projection_is_detected
test_missing_projection_is_rebuilt_by_emit

echo "PASS: shared-v7-contracts"
