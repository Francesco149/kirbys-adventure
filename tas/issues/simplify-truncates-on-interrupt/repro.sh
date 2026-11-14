#!/bin/sh
# repro.sh [SECONDS]: interrupt `kt simplify --dry` and watch movie.txt lose its tail.
# Runs in a temporary run directory (not tas/runs/), from a copy of movie.txt (a passing secret-hal movie).
set -u
H=$(cd "$(dirname "$0")" && pwd)
TAS=$(cd "$H/../.." && pwd)
R=$(mktemp -d /tmp/kt-simplify-repro.XXXXXX)
cp "$H/movie.txt" "$R/movie.txt"
cp "$TAS/knowledge/ram-seed.json" "$R/ram.json"
frames() { "$TAS/.venv/bin/python" -c "import sys; sys.path.insert(0, '$TAS'); import env as E; print(len(E.parse_spec(open('$R/movie.txt').read())))"; }
cd "$TAS"
echo "before: $(frames) frames"; ./kt check "$R" tasks/secret-hal.md | head -1
timeout -s TERM "${1:-25}" ./kt simplify "$R" --from 3583 --task tasks/secret-hal.md --mode frames --time-limit 180 --dry >/dev/null 2>&1
echo "kt simplify --dry interrupted (exit $?)"
echo "after:  $(frames) frames"; ./kt check "$R" tasks/secret-hal.md | head -1
echo "(run dir: $R)"
