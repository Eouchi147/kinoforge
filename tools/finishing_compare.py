"""Raw-vs-finished wipe (the p14 example): renders a scene twice (once with ?finish=0) and composes a moving wipe with labels.
Usage: node harness/render.cjs proto/<scene> --out out/<scene>-raw --param finish=0 --jpg ; node harness/render.cjs proto/<scene> --mp4 --audio ... ; then edit the paths below and run.
"""
from PIL import Image, ImageDraw, ImageFont
import math, os
W, H, FPS = 1280, 720, 24
bold = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Bold.otf', 26)
reg = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Regular.otf', 18)
small = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Regular.otf', 15)
shots = [(0, 2.2), (2.2, 5.2), (5.2, 7.6), (7.6, 8.1), (8.1, 10.0)]
def ease(t): return t * t * (3 - 2 * t)
for i in range(240):
    t = i / FPS
    raw = Image.open(f'out/p05-relic-raw/frames/{i:05d}.jpg').convert('RGB')
    fin = Image.open(f'out/p05-relic/frames/{i:05d}.png').convert('RGB')
    # wipe position: within each shot, sweep from all-raw to all-finished over the first 70% of the shot, then hold finished for 15%, then show split 50/50
    s0, s1 = [s for s in shots if s[0] <= t < s[1]][0] if t < 10 else shots[-1]
    u = (t - s0) / (s1 - s0)
    if s1 - s0 < 1.0: x = W  # black shot: finished only
    elif u < 0.7: x = int(W * ease(u / 0.7))
    else: x = W
    out = fin.copy()
    if x < W: out.paste(raw.crop((0, 0, W - x, H)) if False else raw.crop((x, 0, W, H)), (x, 0))  # finished reveals from the LEFT: left = finished, right = raw
    d = ImageDraw.Draw(out, 'RGBA')
    if 0 < x < W:
        d.rectangle([x - 1, 0, x + 1, H], fill=(255, 255, 255, 230))
    # labels
    if x > 160: 
        d.rectangle([24, 24, 24 + 176, 24 + 44], fill=(0, 0, 0, 150)); d.text((36, 31), 'FINISHED', font=bold, fill=(255, 230, 200))
    if x < W - 180:
        d.rectangle([W - 24 - 196, 24, W - 24, 24 + 44], fill=(0, 0, 0, 150)); d.text((W - 24 - 184, 31), 'RAW RENDER', font=bold, fill=(220, 220, 220))
    cap = 'finish pass: grade · halation · grain · vignette · chromatic edge · bloom · 2.39 scope · designed sound'
    tw = d.textlength(cap, font=small)
    d.rectangle([W / 2 - tw / 2 - 14, H - 56, W / 2 + tw / 2 + 14, H - 24], fill=(0, 0, 0, 160)); d.text((W / 2 - tw / 2, H - 49), cap, font=small, fill=(235, 225, 210))
    out.save(f'frames/{i:05d}.jpg', quality=93)
print('frames done')
