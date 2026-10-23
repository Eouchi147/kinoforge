"""Art direction `risograph`: a riso print of the Cutaway, an editorial poster printed with three spot inks.

The world is rendered as usual (depth of field and god rays off), taken to display colours in the compositor, graded a little
bolder, and then separated into three inks by optical density: fluorescent pink, teal and yellow (the 3 x 3 matrix that turns
the picture's log-density into ink coverage is solved in code from each ink's transmittance). Each ink is printed through its
own coarse halftone screen (round dots, 9 px cells at 1280 wide, screens at 15, 75 and 45 degrees), with uneven ink laydown
(white speckle), and the three plates are slightly out of register (a few pixels apart). The plates multiply onto cream
paper with fibre grain, so overprints give the real riso mixes (pink on yellow is orange, teal on yellow is green, all
three is a deep violet-navy). The labels and title are printed afterwards in one dark ink from their own full-resolution
scene so they stay readable. What it changes: compositor, DOF and shafts off. Render cost vs the reference: about the same
(the world is rendered at 8 spp: halftone hides the noise) plus a few seconds for the compositing and the words scene.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _post as P  # noqa: E402

PAPER = (0.965, 0.935, 0.865)
INKS = {                          # display-space transmittance (what the ink lets through of the paper, per channel)
    'pink': (0.98, 0.26, 0.60),
    'teal': (0.06, 0.50, 0.56),
    'yellow': (0.99, 0.90, 0.10),
}
ORDER = ['pink', 'teal', 'yellow']
ANGLE = {'pink': 15.0, 'teal': 75.0, 'yellow': 45.0}
SHIFT = {'pink': (0, 0), 'teal': (3, -2), 'yellow': (-2, 3)}     # misregistration in pixels at 1280 wide
CELL = 9.0
GAIN = {'pink': 0.82, 'teal': 1.3, 'yellow': 0.95}


def separation_matrix():
    M = np.array([[-math.log(max(INKS[k][c], 0.05)) for k in ORDER] for c in range(3)])      # density of ink k in channel c
    return np.linalg.inv(M)


def halftone(W, H, cell, angle_deg, seed):
    y, x = np.mgrid[0:H, 0:W].astype(np.float64); a = math.radians(angle_deg)
    u = (x * math.cos(a) + y * math.sin(a)) / cell; v = (-x * math.sin(a) + y * math.cos(a)) / cell
    fu = u - np.round(u); fv = v - np.round(v); r = np.hypot(fu, fv)
    return (math.pi * r * r) / (math.pi * 0.5)


def grain(W, H, seed, cell=1.0):
    rng = np.random.default_rng(seed); a = rng.random((H, W))
    # a little low-frequency mottling plus fine speckle
    lo = rng.random((H // 6 + 2, W // 6 + 2)); lo = np.kron(lo, np.ones((6, 6)))[:H, :W]
    k = np.ones(5) / 5.0
    lo = np.apply_along_axis(lambda r: np.convolve(r, k, 'same'), 1, lo); lo = np.apply_along_axis(lambda r: np.convolve(r, k, 'same'), 0, lo)
    return 0.6 * a + 0.4 * lo


def apply(bpy, film, ctx):
    W, H = ctx['W'], ctx['H']; sc = bpy.context.scene; r = W / 1280.0
    sc.cycles.samples = min(sc.cycles.samples, 10)
    B = P.split_overlay(bpy, film, ctx)
    P.hide_shafts(film)
    inv = separation_matrix()
    C = P.Comp(bpy, sc)
    rl = C.render(sc); words = C.render(B) if B else None
    col = C.display(rl.outputs['Image'], view='AgX', look='AgX - Medium High Contrast', exposure=P.exposure_of(film) + 0.5)
    col = C.node('CompositorNodeHueSat', {'Image': col, 'Saturation': 1.1, 'Value': 1.0}).outputs['Image']
    col = C.node('CompositorNodeBrightContrast', {'Image': col, 'Brightness': 0.0, 'Contrast': 0.22}).outputs['Image']
    # optical density of the picture against the paper
    s = C.sep(col)
    dens = [C.math('MULTIPLY', C.math('LOGARITHM', C.math('MAXIMUM', C.math('DIVIDE', s[i], PAPER[i]), 0.05), math.e), -1.0) for i in range(3)]
    D = C.comb(*dens)
    plates = {}
    for i, k in enumerate(ORDER):
        cov = C.vmath('DOT_PRODUCT', D, tuple(float(v) for v in inv[i]))
        cov = C.math('MINIMUM', C.math('MAXIMUM', cov, 0.0), 1.0)
        ht = C.image(P.array_image(bpy, f'kf_ht_{k}', halftone(W, H, CELL * r, ANGLE[k], i)))
        gr = C.image(P.array_image(bpy, f'kf_inkgrain_{k}', grain(W, H, 10 + i)))
        thr = C.sep(ht)[0]; gv = C.sep(gr)[0]
        m = C.math('MINIMUM', C.math('MAXIMUM', C.math('ADD', C.math('MULTIPLY', C.math('SUBTRACT', C.math('MULTIPLY', C.math('POWER', cov, 1.15), GAIN[k]), thr), 7.0), 0.5), 0.0), 1.0)
        # uneven laydown: ink thins out where the grain is high
        m = C.math('MULTIPLY', m, C.math('SUBTRACT', 1.0, C.math('MULTIPLY', C.math('MAXIMUM', C.math('SUBTRACT', gv, 0.62), 0.0), 2.2)))
        dx, dy = SHIFT[k]
        plates[k] = C.translate(m, dx * r, dy * r, 'Bilinear') if (dx or dy) else m
    paper_arr = grain(W, H, 77); paper = np.stack([PAPER[c] * (0.955 + 0.075 * paper_arr) for c in range(3)], -1)
    out = C.image(P.array_image(bpy, 'kf_paper', paper))
    for k in ORDER:
        f = C.mix(plates[k], (1.0, 1.0, 1.0, 1.0), tuple(INKS[k]) + (1.0,))
        out = C.mix(1.0, out, f, 'MULTIPLY')
    # words printed in one dark ink (their own scene, crisp)
    if words:
        ow = C.node('CompositorNodeAlphaOver', {'Background': out, 'Foreground': words.outputs['Image']}); out = ow.outputs['Image']
    C.finish(out)
    P.display_raw(sc)


def frame(bpy, film, ctx, t, shot):
    P.set_dof(film, False)
