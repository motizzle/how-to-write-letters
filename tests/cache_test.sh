#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-python3}
ROOT="$PWD"
pass=0; fail=0
ok()   { printf '  ok   %s\n' "$1"; pass=$((pass+1)); }
bad()  { printf '  FAIL %s\n' "$1"; fail=$((fail+1)); }
check(){ [ "$2" = "$3" ] && ok "$1" || { bad "$1"; printf '       want %s\n       got  %s\n' "$3" "$2"; }; }

SCRATCH=$(mktemp -d)
trap 'rm -rf "$SCRATCH"' EXIT
mkdir -p "$SCRATCH/strokes"
cp "$ROOT"/strokes/*.py "$SCRATCH/strokes/"
cp -r "$ROOT/strokes/fonts" "$SCRATCH/strokes/"
GEN="$SCRATCH/strokes/engine.py"

fp() { "$PY" "$GEN" --fingerprint; }
base=$(fp) || { echo "fingerprint mode failed"; exit 1; }

diffcount() {
  "$PY" - "$1" "$2" <<'PYEOF'
import json, sys
a = json.loads(sys.argv[1]); b = json.loads(sys.argv[2])
n = []
for deck in a["decks"]:
    for ch, h in a["decks"][deck].items():
        if b["decks"].get(deck, {}).get(ch) != h:
            n.append(f"{deck}/{ch}")
print(len(n), " ".join(sorted(n)[:8]))
PYEOF
}
algo() { "$PY" -c "import json,sys;print(json.loads(sys.argv[1])['algorithm'])" "$1"; }
total=$("$PY" -c "import json,sys;d=json.loads(sys.argv[1]);print(sum(len(v) for v in d['decks'].values()))" "$base")
echo "== $total letters, algorithm $(algo "$base") =="

echo
echo "1. a comment-only edit reaches NO letter"
cp "$GEN" "$SCRATCH/keep.py"
printf '\n# a comment that changes nothing\n' >> "$GEN"
check "comment edit: 0 letters stale" "$(diffcount "$base" "$(fp)" | cut -d' ' -f1)" "0"
cp "$SCRATCH/keep.py" "$GEN"

echo
echo "2. reformatting the data tables reaches NO letter"
"$PY" - "$GEN" <<'PYEOF'
import sys
p = sys.argv[1]; s = open(p, encoding="utf-8").read()
i = s.index("MANIFEST = {"); j = s.index("\nRULES_LATIN")
s = s[:i] + s[i:j].replace('\n    "', '\n        "') + s[j:]
open(p, "w", encoding="utf-8").write(s)
PYEOF
check "reformat MANIFEST: 0 letters stale" "$(diffcount "$base" "$(fp)" | cut -d' ' -f1)" "0"
cp "$SCRATCH/keep.py" "$GEN"

echo
echo "3. editing ONE letter's strokes reaches only that letter"
"$PY" - "$GEN" <<'PYEOF'
import re, sys
p = sys.argv[1]; s = open(p, encoding="utf-8").read()
i = s.index('MANIFEST = {')
m = re.search(r'"pts":\s*\[\s*\[\s*([0-9.]+)', s[i:])
assert m, "could not find a pts literal in MANIFEST"
old = m.group(1); new = str(round(float(old) + 0.011, 3))
at = i + m.start(1)
open(p, "w", encoding="utf-8").write(s[:at] + new + s[at + len(old):])
PYEOF
check "one stroke edit: only print/A stale" "$(diffcount "$base" "$(fp)")" "1 print/A"
cp "$SCRATCH/keep.py" "$GEN"

echo
echo "3b. a Hebrew letter's edit reaches only that letter"
"$PY" - "$GEN" <<'PYEOF'
import re, sys
p = sys.argv[1]; s = open(p, encoding="utf-8").read()
i = s.index('MANIFEST = {'); j = s.index('\nRULES_LATIN')
m = re.search(r'"ב":\s*\[\s*\n\s*\{"pts":\s*\[\s*\[\s*([0-9.]+)', s[i:j])
assert m, "could not find the bet manifest entry"
old = m.group(1); new = str(round(float(old) + 0.013, 3)); at = i + m.start(1)
open(p, "w", encoding="utf-8").write(s[:at] + new + s[at + len(old):])
PYEOF
check "bet: only hebrew/bet stale" "$(diffcount "$base" "$(fp)")" "1 hebrew/ב"
cp "$SCRATCH/keep.py" "$GEN"

echo
echo "4. editing the algorithm reaches EVERY letter"
"$PY" - "$GEN" <<'PYEOF'
import sys
p = sys.argv[1]; s = open(p, encoding="utf-8").read()
s = s.replace("RAY_STEP = 2.0", "RAY_STEP = 2.5", 1)
open(p, "w", encoding="utf-8").write(s)
PYEOF
after=$(fp)
check "algorithm edit: every letter stale" "$(diffcount "$base" "$after" | cut -d' ' -f1)" "$total"
[ "$(algo "$base")" != "$(algo "$after")" ] && ok "algorithm hash moved" || bad "algorithm hash did not move"
cp "$SCRATCH/keep.py" "$GEN"

echo
echo "5. a half-written entry is not a hit"
"$PY" - "$GEN" <<'PYEOF'
import importlib.util, os, sys, tempfile
spec = importlib.util.spec_from_file_location("gen", sys.argv[1])
gen = importlib.util.module_from_spec(spec); spec.loader.exec_module(gen)
d = tempfile.mkdtemp(); gen.CACHE_DIR = d
open(os.path.join(d, "deadbeef.json"), "w").write('{"letter": {"aspec')
assert gen._cache_read("deadbeef") is None, "truncated entry read as a hit"
open(os.path.join(d, "cafe.json"), "w").write('{"letter": {}}')
assert gen._cache_read("cafe") is None, "entry missing min_half read as a hit"
assert gen._cache_read("nothing-here") is None
gen._cache_write("beef", {"letter": {"a": 1}, "min_half": 0.5})
assert gen._cache_read("beef") == {"letter": {"a": 1}, "min_half": 0.5}
assert not [f for f in os.listdir(d) if f.endswith(".tmp")], "temp file left behind"
print("cache read/write rules hold")
PYEOF
[ $? -eq 0 ] && ok "truncated / short / missing entries all rebuild" || bad "cache read rules"

if [ "${1:-}" = "--full" ]; then
  echo
  echo "6. a cold run and a fully cached run both reproduce docs/data byte for byte"
  for run in cold warm; do
    s=$(date +%s)
    "$PY" "$GEN" 2>/dev/null || bad "$run run failed"
    echo "     $run run $(( $(date +%s) - s ))s"
    for a in print hebrew; do
      if cmp -s "$SCRATCH/docs/data/$a.json" "$ROOT/docs/data/$a.json"; then
        ok "$run $a.json is byte-identical to the committed one"
      else
        bad "$run $a.json DIFFERS from the committed one"
      fi
    done
  done
fi

echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
