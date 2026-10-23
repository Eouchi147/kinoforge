"""Look board: the seasons loop (films/cutaway/loops/seasons) dressed with the art direction `risograph`
(films/styles/cutaway/art/risograph.py, through art/_adapter.py). Made by films/cutaway/looks/make_seasons.py; do not edit.
Runs the seasons loop's own blender.py in this module, so DURATION, SETTINGS, build and frame are the loop's."""
import os

KF_ART_NAME = 'risograph'
_SRC = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'loops', 'seasons', 'blender.py'))
__file__ = _SRC
exec(compile(open(_SRC).read(), _SRC, 'exec'))
