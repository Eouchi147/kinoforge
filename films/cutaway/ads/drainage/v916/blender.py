"""Drainage sample ad, 9:16 delivery (render 720x1280, deliver 1080x1920). The scene is ../ad.py (shared by both
deliveries); this file only picks the aspect. Free: Blender Cycles CPU, procedural; words set in code."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ad  # noqa: E402

DURATION, SETTINGS = ad.DURATION, ad.SETTINGS

def build(bpy, ctx): return ad.build(bpy, ctx, '9:16')

def frame(bpy, ctx, S, i, t): ad.frame(bpy, ctx, S, i, t)
