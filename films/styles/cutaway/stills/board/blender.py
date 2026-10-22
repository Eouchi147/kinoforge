"""All four Cutaway board looks in one film folder, so one stills run renders the whole board: the frame number picks the
look (frame % 4: 0 A, 1 B, 2 C, 3 D), e.g. frames 24,25,26,27. The aspect follows --w/--h."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from scene import make  # noqa: E402

def _start():
    a = sys.argv
    return int(a[a.index('--start') + 1]) if '--start' in a else 0

DURATION, SETTINGS, build, frame = make('ABCD'[_start() % 4], duration=8.0, move='none', samples=128)
