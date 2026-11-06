#!/usr/bin/env bash
# Usage: check-docs.sh <platform> <docs-base-url> [--write]
# Prints NEW, UNCHANGED, or CHANGED (with index diff). --write saves the
# current fingerprint and llms.txt to docs/platforms/<platform>/_source/.
set -euo pipefail
platform=$1; base=${2%/}; write=${3:-}
root=$(git rev-parse --show-toplevel)
src="$root/docs/platforms/$platform/_source"
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

fetch() { curl -sSfL -o "$tmp/$1" "$base/$2" 2>/dev/null || return 1; }
fetch llms.txt llms.txt || { echo "ERROR: cannot fetch $base/llms.txt (blocked host or no llms.txt)"; exit 2; }
fetch llms-full.txt llms-full.txt || : > "$tmp/llms-full.txt"
spec=$(grep -o -E '\((/[^)]*openapi[^)]*\.(yaml|json))\)' "$tmp/llms.txt" | grep -v -E 'final|gen' | head -1 | tr -d '()')
fetch openapi "${spec#/}" 2>/dev/null || fetch openapi openapi.yaml || : > "$tmp/openapi"

{
  echo "date: $(date -u +%F)"
  echo "base: $base"
  for f in llms.txt llms-full.txt openapi; do
    printf '%s: %s %s\n' "$f" "$(sha256sum "$tmp/$f" | cut -c1-64)" "$(wc -c < "$tmp/$f")"
  done
} > "$tmp/fingerprint.txt"

if [ "$write" = "--write" ]; then
  mkdir -p "$src"; cp "$tmp/fingerprint.txt" "$tmp/llms.txt" "$src/"
  echo "WROTE $src/fingerprint.txt"; cat "$src/fingerprint.txt"; exit 0
fi

if [ ! -f "$src/fingerprint.txt" ]; then echo "NEW"; exit 0; fi
if diff -q <(grep -v '^date:' "$src/fingerprint.txt") <(grep -v '^date:' "$tmp/fingerprint.txt") >/dev/null; then
  echo "UNCHANGED (cached $(grep '^date:' "$src/fingerprint.txt" | cut -d' ' -f2))"; exit 0
fi
echo "CHANGED"
diff <(grep -v '^date:' "$src/fingerprint.txt") <(grep -v '^date:' "$tmp/fingerprint.txt") || true
echo "--- index changes (llms.txt) ---"
diff "$src/llms.txt" "$tmp/llms.txt" | grep -E '^[<>]' || echo "(index unchanged; page bodies or OpenAPI changed)"
