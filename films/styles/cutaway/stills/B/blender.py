"""Board still of Cutaway look B for the rc-render stills workflow (aspect follows --w/--h: 1920x1080 or 1080x1920)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from scene import make  # noqa: E402
DURATION, SETTINGS, build, frame = make('B', duration=8.0, move='none', samples=128)
