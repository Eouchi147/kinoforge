#!/bin/bash
# contact sheet of stills: bash sheet.sh out.jpg cols tileW f1.jpg f2.jpg ...
OUT=$1; COLS=$2; TW=$3; shift 3
montage "$@" -tile ${COLS}x -geometry ${TW}x+4+4 -background '#222' -quality 88 $OUT
