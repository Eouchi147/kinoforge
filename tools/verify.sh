#!/usr/bin/env bash
# Every KINOFORGE gate in one command (see tools/verify.py for the list). Exit 0 = all pass.
#   bash tools/verify.sh            fast gates, about 1 min
#   bash tools/verify.sh --full     plus Chromium tests, director checks on every Battle Map film, score selftest
set -euo pipefail
cd "$(dirname "$0")/.."
command -v node >/dev/null || { echo "verify: node 22 is needed (https://nodejs.org)"; exit 2; }
if [ ! -d harness/node_modules/playwright ] && [[ " $* " == *" --full "* ]]; then
  echo "verify --full needs the harness packages: (cd harness && npm ci && npx playwright install --with-deps chromium)"; exit 2
fi
exec python3 tools/verify.py "$@"
