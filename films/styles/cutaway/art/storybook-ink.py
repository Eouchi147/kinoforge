"""storybook-ink (work in progress)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _npr_lines as NL
import numpy as np

def stylize(P, info):
    c = NL.lin_to_srgb(np.clip(P['img'] / (1 + P['img']) * 1.6, 0, 1))
    return c

def apply(bpy, film, ctx):
    NL.setup(bpy, film, ctx, stylize)

def frame(bpy, film, ctx, t, shot):
    NL.frame(bpy, film, ctx, t, shot)
