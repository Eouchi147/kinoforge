"""Cutaway motion test: 8 s, a slow eased orbit (16 degrees) around look A (Studio block); water ripples, grass and
trees sway, lily pads drift, caustics move. Every motion loops on 8 s. Scene code: ../cutaway.py, ../looks.py, ../scene.py."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scene import make  # noqa: E402
DURATION, SETTINGS, build, frame = make('A', duration=8.0, move='orbit', samples=32, deg=16.0, fast=True)
