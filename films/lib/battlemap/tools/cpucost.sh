#!/bin/bash
# CPU seconds per frame (independent of machine load): bash cpucost.sh films/battles/cannae <f0> [extra stills args]
# runs 2 frames and 12 frames and reports (cpu12 - cpu2) / 10
SC=$1; F0=$2; shift 2; ROOT=$(cd "$(dirname "$0")/../../../.." && pwd); cd $ROOT
run() { local n=$1; shift; local fr=$(seq -s, $F0 $((F0+n-1))); TIMEFORMAT='%U %S'; local s; s=$( { time node films/lib/battlemap/tools/stills.cjs $SC --f $fr --out /tmp/claude-0/kf-cpu "$@" >/dev/null 2>&1; } 2>&1 | tail -1); echo $s | awk '{print $1+$2}'; }
a=$(run 2 "$@"); b=$(run 12 "$@"); echo "cpu2=$a cpu12=$b per-frame=$(echo "$a $b" | awk '{printf "%.2f", ($2-$1)/10}') cpu-s"
