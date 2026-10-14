"""bvh.py — a small, dependency-free BVH reader with forward kinematics (numpy only).

    clip = load('walk.bvh')
    clip.names, clip.parents, clip.fps, clip.rot (F,J,3,3 local rotations), clip.pos (F,J,3 world positions, metres)
"""
import re
import numpy as np

def _rot(axis, deg):
    a = np.radians(deg); c, s = np.cos(a), np.sin(a); z, o = np.zeros_like(a), np.ones_like(a)
    if axis == 'X': m = [[o, z, z], [z, c, -s], [z, s, c]]
    elif axis == 'Y': m = [[c, z, s], [z, o, z], [-s, z, c]]
    else: m = [[c, -s, z], [s, c, z], [z, z, o]]
    return np.moveaxis(np.array(m), [0, 1], [-2, -1])          # (F,3,3)

class Clip:
    pass

def load(path, scale=None):
    txt = open(path, errors='ignore').read()
    head, motion = txt.split('MOTION', 1)
    tok = re.findall(r'\{|\}|[^\s{}]+', head)
    names, parents, offsets, channels = [], [], [], []
    stack, i, cur = [], 0, -1
    while i < len(tok):
        t = tok[i]
        if t in ('ROOT', 'JOINT'):
            names.append(tok[i + 1]); parents.append(stack[-1] if stack else -1); cur = len(names) - 1; offsets.append(None); channels.append([]); i += 2; continue
        if t == 'End':                                           # end site: keep as a leaf joint (useful for toes / head tips)
            names.append(names[stack[-1]] + '_end'); parents.append(stack[-1]); cur = len(names) - 1; offsets.append(None); channels.append([]); i += 2; continue
        if t == '{': stack.append(cur); i += 1; continue
        if t == '}': stack.pop(); cur = stack[-1] if stack else -1; i += 1; continue
        if t == 'OFFSET': offsets[cur] = [float(v) for v in tok[i + 1:i + 4]]; i += 4; continue
        if t == 'CHANNELS':
            n = int(tok[i + 1]); channels[cur] = tok[i + 2:i + 2 + n]; i += 2 + n; continue
        i += 1
    lines = motion.strip().splitlines()
    nf = int(re.search(r'Frames:\s*(\d+)', motion).group(1)); ft = float(re.search(r'Frame Time:\s*([\d.eE+-]+)', motion).group(1))
    data = np.array([[float(v) for v in l.split()] for l in lines[2:2 + nf] if l.strip()], dtype=np.float64)
    J = len(names); F = len(data); off = np.array(offsets, dtype=np.float64)
    rot = np.tile(np.eye(3), (F, J, 1, 1)); root_t = np.zeros((F, 3)); col = 0
    for j in range(J):
        R = np.tile(np.eye(3), (F, 1, 1))
        for ch in channels[j]:
            v = data[:, col]; col += 1
            if ch.endswith('position'): root_t[:, 'XYZ'.index(ch[0])] = v
            else: R = R @ _rot(ch[0], v)
        rot[:, j] = R
    # forward kinematics
    gR = np.zeros_like(rot); gp = np.zeros((F, J, 3))
    for j in range(J):
        p = parents[j]
        if p < 0: gR[:, j] = rot[:, j]; gp[:, j] = root_t + off[j]
        else: gR[:, j] = gR[:, p] @ rot[:, j]; gp[:, j] = gp[:, p] + np.einsum('fij,j->fi', gR[:, p], off[j])
    c = Clip(); c.path = path; c.names = names; c.parents = parents; c.fps = 1.0 / ft; c.rot = rot; c.grot = gR; c.offsets = off
    # units: scale so the standing hip height is ~0.95 m (BVH files come in cm, inches or metres)
    up = 1                                                       # BVH convention: Y up
    feet_y = gp[:, :, up].min(axis=1)
    hip_h = np.median(gp[:, 0, up] - feet_y)
    c.scale = scale or (0.95 / hip_h if hip_h > 0 else 1.0)
    c.pos = gp * c.scale
    c.pos[:, :, up] -= np.percentile(c.pos[:, :, up].min(axis=1), 5)   # floor at y = 0
    return c

def find(clip, *keys, side=''):
    """First joint whose name contains all keys (case-insensitive) and the side letter/word."""
    for j, n in enumerate(clip.names):
        l = n.lower()
        if all(k in l for k in keys) and (not side or l.startswith(side) or ('left' if side == 'l' else 'right') in l): return j
    return None
