"""A Cutaway line film (generic scene): the picture is built from spec.json + cues.json next to this file.

Copy this file, unchanged, into a film folder of the line (the director's sound stage does it). The engine and the
presets are in films/lib/cutaway/ (SPEC.md documents the spec). Scene contract of harness/blender_render.py.
$KF_SPEC picks another spec file in the folder (the director's check renders candidates: KF_SPEC=cand/a.json).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__)); _R = HERE
while not os.path.isdir(os.path.join(_R, 'films', 'lib', 'cutaway')):
    if os.path.dirname(_R) == _R: raise RuntimeError('films/lib/cutaway not found above ' + HERE)
    _R = os.path.dirname(_R)
sys.path.insert(0, os.path.join(_R, 'films', 'lib', 'cutaway'))
import engine  # noqa: E402

DURATION, SETTINGS, build, frame, FILM = engine.scene(HERE)
