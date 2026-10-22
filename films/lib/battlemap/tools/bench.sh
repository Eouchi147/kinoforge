#!/bin/bash
# wall seconds per frame over N consecutive frames (min and median; the machine is shared so the min is the fairest estimate): bash bench.sh films/battles/cannae <f0> <n> [stills args]
SC=$1; F0=$2; N=$3; shift 3; ROOT=$(cd "$(dirname "$0")/../../../.." && pwd); cd $ROOT
fr=$(seq -s, $F0 $((F0+N-1)))
node films/lib/battlemap/tools/stills.cjs $SC --f $fr --out /tmp/claude-0/kf-bench "$@" 2>&1 | grep "\.jpg" | awk '{gsub("s","",$2); print $2}' | tail -n +2 | sort -n | awk '{a[NR]=$1} END{printf "min %.2f median %.2f max %.2f s/frame (n=%d, first frame excluded)\n", a[1], a[int((NR+1)/2)], a[NR], NR}'
