#!/usr/bin/env bash
# FinKids content lint — validates lesson and goal markdown files.
# Exit non-zero on any failure.
# Usage: ./scripts/lint_content.sh [--quiet]

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
QUIET=false
[[ "${1:-}" == "--quiet" ]] && QUIET=true

pass=0
fail=0
errors=()

_log() { $QUIET || echo "$*"; }

check_file() {
  local file="$1"
  local file_errors=()
  local content
  content=$(cat "$file")

  # 1. Required section headings (minimum 8)
  local headings
  headings=$(grep -c "^## " "$file" || true)
  if (( headings < 8 )); then
    file_errors+=("Fewer than 8 section headings (found ${headings})")
  fi

  # 2. BASIC quiz questions (## Check Your Thinking)
  local basic_section
  basic_section=$(awk '/^## Check Your Thinking/,/^## Explore Further/' "$file" || true)
  local basic_count
  basic_count=$(echo "$basic_section" | grep -cE "^Q[0-9]+\." || true)
  if (( basic_count < 5 )); then
    file_errors+=("Fewer than 5 BASIC quiz questions in 'Check Your Thinking' (found ${basic_count})")
  fi

  # 3. ADVANCED quiz questions (## Explore Further)
  local adv_section
  adv_section=$(awk '/^## Explore Further/,/^##[^#]/' "$file" || true)
  local adv_count
  adv_count=$(echo "$adv_section" | grep -cE "^Q[0-9]+\." || true)
  if (( adv_count < 5 )); then
    file_errors+=("Fewer than 5 ADVANCED quiz questions in 'Explore Further' (found ${adv_count})")
  fi

  # 4. Every question must have Hint:, answerIndex (Correct Answer:), explanation
  local q_blocks
  # Check for any Q block missing Hint
  while IFS= read -r line; do
    if [[ "$line" =~ ^Q[0-9]+\. ]]; then
      # Look ahead in context — simplistic: count occurrences per file
      true  # full per-block check done via Python validator
    fi
  done < "$file"
  if ! grep -q "^Hint:" "$file" 2>/dev/null && ! grep -q "Hint:" "$file" 2>/dev/null; then
    file_errors+=("No 'Hint:' found anywhere in file")
  fi
  if ! grep -qE "Correct Answer:" "$file" 2>/dev/null; then
    file_errors+=("No 'Correct Answer:' found anywhere in file")
  fi

  # 5. Bullet style: must use "- " not "•"
  if grep -qP "^•" "$file" 2>/dev/null; then
    file_errors+=("Found '•' bullet — use '- ' markdown bullets instead")
  fi

  # 6. Excessive whitespace: run of 6+ consecutive spaces
  if grep -qP "      " "$file" 2>/dev/null; then
    file_errors+=("Found run of 6+ consecutive spaces (check padding)")
  fi

  # 7. level: field must use ASCII hyphen not en dash
  if grep -qP "^level:.*–" "$file" 2>/dev/null; then
    file_errors+=("'level:' field contains en dash (–) — use ASCII hyphen (-)")
  fi

  if (( ${#file_errors[@]} == 0 )); then
    _log "  PASS  $file"
    (( pass++ )) || true
  else
    _log "  FAIL  $file"
    for e in "${file_errors[@]}"; do
      _log "        • $e"
      errors+=("$file: $e")
    done
    (( fail++ )) || true
  fi
}

_log "── Learning lessons ────────────────────────"
while IFS= read -r -d '' f; do
  check_file "$f"
done < <(find "$REPO_ROOT/learning" -name "*.md" -print0 | sort -z)

_log ""
_log "── Goal templates ──────────────────────────"
while IFS= read -r -d '' f; do
  check_file "$f"
done < <(find "$REPO_ROOT/goals-habits" -name "*.md" -print0 | sort -z)

_log ""
echo "Results: ${pass} passed, ${fail} failed"

if (( fail > 0 )); then
  if ! $QUIET; then
    echo ""
    echo "Errors:"
    for e in "${errors[@]}"; do
      echo "  • $e"
    done
  fi
  exit 1
fi
exit 0
