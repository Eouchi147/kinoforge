"""Layout of one Cutaway set: a set spec (presets by name) resolved into concrete numbers (pure numpy, no Blender).

The engine builds from a Layout; the validator checks it. Everything is deterministic from the set's seed, so the
validator and every render runner see exactly the same places for houses, animals and eggs.
"""
import math

import numpy as np

import cutaway as cw
import presets as P


class LayoutError(ValueError):
    pass


def _scale_pts(pts, sx, sy):
    return [(x * sx / 4.0, y * sy / 4.0) for x, y in pts]


class Layout:
    def __init__(self, name, spec, fmt='16:9'):
        self.name = name; self.spec = dict(spec or {}); s = self.spec; self.fmt = fmt; self.notes = []
        size = s.get('size', 'standard')
        if size not in P.SIZES: raise LayoutError(f'set {name}: size must be one of {", ".join(P.SIZES)}')
        self.sx, self.sy, self.depth = P.SIZES[size]; self.size = (self.sx, self.sy); self.k = self.sx / 4.0
        self.seed = int(s.get('seed', 4))
        st = s.get('strata', 'time')
        if st not in P.STRATA_NAMES: raise LayoutError(f'set {name}: strata must be one of {", ".join(P.STRATA_NAMES)}')
        self.strata_name = st; self.strata = P.strata(st)
        ter = s.get('terrain', 'rolling')
        if ter not in P.TERRAIN: raise LayoutError(f'set {name}: terrain must be one of {", ".join(P.TERRAIN)}')
        amp, freq, base = P.TERRAIN[ter]; self.top = cw.rolling(amp=amp, freq=freq, seed=self.seed, base=base)
        self.season = s.get('season', 'summer')
        if self.season not in P.SEASONS: raise LayoutError(f'set {name}: season must be one of {", ".join(P.SEASONS)}')
        self.time = s.get('time', 'day')
        if self.time not in P.TIMES: raise LayoutError(f'set {name}: time must be one of {", ".join(P.TIMES)}')
        self.water_kind = s.get('water', 'river')
        if self.water_kind not in P.WATER: raise LayoutError(f'set {name}: water must be one of {", ".join(P.WATER)}')
        self.water = self._water(); self.level = self.water[0]['level'] if self.water else None
        self.veg = {'trees': int(s.get('trees', 12)), 'grass': float(s.get('grass', 1.0)), 'flowers': float(s.get('flowers', 0.5)),
                    'reeds': float(s.get('reeds', 0.5 if self.water else 0.0)), 'lilies': int(s.get('lilies', 10 if self.water_kind in ('river', 'pond') else 0)),
                    'boulders': int(s.get('boulders', 10)), 'corals': int(s.get('corals', 12 if self.water_kind == 'lagoon' else 0))}
        self.fog = float(s.get('fog', 0.0)); self.shafts = float(s.get('shafts', 1.0 if self.time in ('golden', 'dusk') else 0.0))
        self.rng = np.random.default_rng(self.seed + 101)
        self.taken = []                   # (x, y, r) circles used by props, kept clear of grass and trees
        self._props(); self._eggs(); self._animals()

    # ---------------------------------------------------------------- fields
    def height(self, x, y):
        return self.top(np.asarray(x, float), np.asarray(y, float))

    def sd(self, x, y):
        """Signed distance to the water (negative inside), or +9 with no water."""
        x = np.asarray(x, float); y = np.asarray(y, float)
        if not self.water: return np.full(np.shape(x), 9.0)
        return np.min([cw._sdist(w, x, y, self.seed) for w in self.water], axis=0)

    def _water(self):
        w = P.WATER[self.water_kind]
        if not w: return []
        w = dict(w); kx, ky = self.sx / 4.0, self.sy / 4.0
        if w['type'] == 'river':
            return [cw.river(_scale_pts(w['path'], self.sx, self.sy), width=w['width'] * kx, depth=w['depth'], level=w['level'], shelf=w['shelf'])]
        if w['type'] == 'pond':
            c = (w['center'][0] * kx, w['center'][1] * ky)
            return [cw.pond(c, (w['radius'][0] * kx, w['radius'][1] * ky), depth=w['depth'], level=w['level'], shelf=w['shelf'])]
        cx, cy, r, seed = w['center'][0] * kx, w['center'][1] * ky, w['radius'] * kx, self.seed
        return [cw.basin(lambda x, y: np.hypot(x - cx, y - cy) - r + 0.08 * cw.fbm(x, y, seed + 3, 3, 1.4), depth=w['depth'], level=w['level'], shelf=w['shelf'])]

    def dry(self, x, y, margin=0.3, clear=0.0):
        """Is (x, y) dry land, inside the block by `margin`, `clear` metres from the water and from other things?"""
        if abs(x) > self.sx / 2 - margin or abs(y) > self.sy / 2 - margin: return False
        if float(self.sd(np.array([x]), np.array([y]))[0]) < clear: return False
        return all(math.hypot(x - a, y - b) > r + 0.05 for a, b, r in self.taken)

    def spot(self, margin=0.3, clear=0.25, near=None, spread=0.6, tries=400):
        for _ in range(tries):
            if near is not None: x, y = near[0] + self.rng.normal(0, spread), near[1] + self.rng.normal(0, spread)
            else: x, y = self.rng.uniform(-self.sx / 2, self.sx / 2), self.rng.uniform(-self.sy / 2, self.sy / 2)
            if self.dry(x, y, margin, clear): return (float(x), float(y))
        return None

    def river_at(self, f):
        """Point and unit normal at fraction f along the river's centre line (None without a river)."""
        if not self.water or self.water[0]['type'] != 'river': return None
        C = cw.catmull(self.water[0]['path'], 200); seg = np.linalg.norm(np.diff(C, axis=0), axis=1); s = np.concatenate([[0], np.cumsum(seg)])
        d = f * s[-1]; i = int(np.clip(np.searchsorted(s, d) - 1, 0, len(C) - 2)); p = C[i]; t = C[i + 1] - C[i]; t = t / (np.linalg.norm(t) + 1e-9)
        return p, np.array([-t[1], t[0]])

    def water_point(self, toward='-Y'):
        """A point in the water close to a cut face (where the glass shows)."""
        if not self.water: return None
        X, Y = np.meshgrid(np.linspace(-self.sx / 2 + 0.2, self.sx / 2 - 0.2, 41), np.linspace(-self.sy / 2 + 0.15, self.sy / 2 - 0.15, 41))
        X, Y = X.ravel(), Y.ravel(); ok = self.sd(X, Y) <= -0.12
        if not ok.any(): return None
        score = np.where(ok, Y if toward == '-Y' else -X, np.inf); i = int(np.argmin(score))
        return (float(X[i]), float(Y[i]))

    # ---------------------------------------------------------------- props
    def _props(self):
        pr = self.spec.get('props') or {}; k = self.k
        self.houses = []; self.mill = None; self.bridge = None; self.lamps = []; self.pipes = []; self.piles = []
        bad = [p for p in pr if p not in P.PROPS]
        if bad: raise LayoutError(f'set {self.name}: unknown props {bad} (known: {", ".join(P.PROPS)})')
        river = self.water and self.water[0]['type'] == 'river'
        if pr.get('mill'):
            if not river: raise LayoutError(f'set {self.name}: a mill needs water "river" or "stream"')
            p, n = self.river_at(0.72); w = self.water[0]['width']
            side = 1 if (p + n)[0] > p[0] else -1                     # the bank toward +X (the hero side)
            c = p + side * n * (w / 2 + 0.30 * k); yaw = math.atan2(-side * n[1], -side * n[0])
            self.mill = (float(c[0]), float(c[1]), yaw, 0.40 * k); self.taken.append((float(c[0]), float(c[1]), 0.32 * k))
        if pr.get('bridge'):
            if not river: raise LayoutError(f'set {self.name}: a bridge needs water "river" or "stream"')
            p, n = self.river_at(0.42); w = self.water[0]['width']; e = w / 2 + 0.22 * k
            a, b = p - n * e, p + n * e; self.bridge = ((float(a[0]), float(a[1])), (float(b[0]), float(b[1])))
            self.taken += [(float(a[0]), float(a[1]), 0.12), (float(b[0]), float(b[1]), 0.12)]
        for spec in (pr.get('houses') or []):
            x, y = float(spec[0]), float(spec[1]); yaw = float(spec[2]) if len(spec) > 2 else 0.0
            self.houses.append((x, y, yaw)); self.taken.append((x, y, 0.3 * k))
        for _ in range(int(pr.get('village', 0) or 0)):
            near = self.houses[-1][:2] if self.houses else None
            p = self.spot(margin=0.35 * k, clear=0.32 * k, near=near, spread=0.7 * k) or self.spot(margin=0.35 * k, clear=0.3 * k)
            if p is None: self.notes.append('no room for every house'); break
            self.houses.append((p[0], p[1], float(self.rng.uniform(-math.pi, math.pi)))); self.taken.append((p[0], p[1], 0.3 * k))
        for _ in range(int(pr.get('lamps', 0) or 0)):
            near = self.houses[len(self.lamps) % len(self.houses)][:2] if self.houses else None
            p = self.spot(margin=0.25, clear=0.12, near=near, spread=0.25) or self.spot(margin=0.25, clear=0.12)
            if p: self.lamps.append(p); self.taken.append((p[0], p[1], 0.05))
        for path in (pr.get('pipes') or []):
            pts = [tuple(float(v) for v in q) for q in path]
            if len(pts) < 2 or any(len(q) != 3 for q in pts): raise LayoutError(f'set {self.name}: a pipe is a list of at least two [x, y, z] points')
            self.pipes.append(pts)
        for pl in (pr.get('piles') or []):
            self.piles.append((float(pl[0]), float(pl[1]), float(pl[2]) if len(pl) > 2 else 0.8))

    # ---------------------------------------------------------------- eggs
    def face_len(self, face):
        return self.sx if face == '-Y' else self.sy

    def face_top(self, face, u):
        x, y = (u, -self.sy / 2 + 0.004) if face == '-Y' else (self.sx / 2 - 0.004, u)
        return float(self.height(np.array([x]), np.array([y]))[0])

    def face_world(self, face, u, z):
        return (u, -self.sy / 2, z) if face == '-Y' else (self.sx / 2, u, z)

    def _eggs(self):
        self.eggs = []; auto = {f: [] for f in P.FACES}
        for k, e in enumerate(self.spec.get('eggs') or []):
            kind = e.get('kind')
            if kind not in P.EGGS: raise LayoutError(f'set {self.name}: egg {k} kind {kind!r} is not one of {", ".join(P.EGGS)}')
            face = e.get('face', '-Y')
            if face not in P.FACES: raise LayoutError(f'set {self.name}: egg {kind} face must be "-Y" or "+X"')
            pre = P.EGGS[kind]; d = float(e.get('depth', pre['depth']))
            lim = self.depth - 0.12
            if d > lim:
                if 'depth' not in e: self.notes.append(f'{kind}: preset depth {d} m moved to {lim:.2f} m (the block is {self.depth} m deep)'); d = lim
            rec = {'kind': kind, 'id': e.get('id') or kind, 'face': face, 'depth': d, 'u': e.get('u'), 'scale': float(e.get('scale', 1.0)),
                   'span': float(e.get('span', 3.0 * self.k)), 'spec': e}
            if rec['u'] is None: auto[face].append(rec)
            self.eggs.append(rec)
        for face, recs in auto.items():          # spread the eggs without a u along the face, in order of depth
            L = self.face_len(face); n = len(recs)
            for j, r in enumerate(sorted(recs, key=lambda r: r['depth'])):
                r['u'] = round(-L / 2 * 0.72 + L * 0.72 * (j + 0.5) / n, 3) if r['kind'] != 'gold' else round(-0.1 * self.k, 3)
        for r in self.eggs:
            r['u'] = float(r['u']); r['z'] = self.face_top(r['face'], r['u']) - r['depth']
            if r['kind'] == 'well': r['z'] = self.face_top(r['face'], r['u']) - r['depth'] / 2

    def egg(self, ident):
        return next((e for e in self.eggs if e['id'] == ident), None) or next((e for e in self.eggs if e['kind'] == ident), None)

    def egg_point(self, ident):
        """World point an egg's camera and label aim at (the skull for the dino)."""
        e = self.egg(ident)
        if e is None: return None
        u, z = e['u'], e['z']
        if e['kind'] == 'dino': u, z = u + 0.10 * e['scale'], z + 0.31 * e['scale']
        if e['kind'] == 'mole': u = u + 0.3
        return self.face_world(e['face'], u, z)

    def footprint(self, e):
        """(u0, u1, z0, z1) of an egg on its face, for overlap checks."""
        pre = P.EGGS[e['kind']]; hu, hz = pre['size']; s = e['scale']; L = self.face_len(e['face'])
        cu = e['u'] + pre.get('center_du', 0.0) * s; cz = e['z'] + pre.get('center_dz', 0.0) * s
        if e['kind'] == 'gold': return (e['u'] - e['span'] / 2, e['u'] + e['span'] / 2, e['z'] - hz, e['z'] + hz)
        if e['kind'] == 'well': top = self.face_top(e['face'], e['u']); return (e['u'] - hu, e['u'] + hu, top - e['depth'], top)
        hu = hu * s; hz = hz * s
        return (cu - hu, cu + hu, cz - hz, cz + hz)

    # ---------------------------------------------------------------- animals
    def _animals(self):
        self.animals = []; k = self.k
        for j, a in enumerate(self.spec.get('animals') or []):
            kind = a.get('kind')
            if kind not in P.ANIMALS: raise LayoutError(f'set {self.name}: animal {j} kind {kind!r} is not one of {", ".join(P.ANIMALS)}')
            if kind in P.WATER_ANIMALS and not self.water: raise LayoutError(f'set {self.name}: {kind} need water (water is "none")')
            rec = {'kind': kind, 'spec': a, 'n': int(a.get('n', {'ducks': 3, 'fish': 5, 'birds': 4, 'fireflies': 24, 'petals': 40, 'butterflies': 3}.get(kind, 1)))}
            at = a.get('at')
            if kind in ('deer', 'fawn'):
                p = tuple(at) if at else (self.spot(margin=0.4, clear=0.25, near=self.animals[-1]['at'] if self.animals and self.animals[-1]['kind'] in ('deer', 'fawn') else None, spread=0.3) or (0.0, 0.0))
                rec.update(at=p, yaw=float(a.get('yaw', self.rng.uniform(-math.pi, math.pi))))
            elif kind in ('rabbit', 'fox'):
                if a.get('path'): rec['path'] = [tuple(q) for q in a['path']]
                else:
                    p0 = tuple(at) if at else self.spot(margin=0.35, clear=0.2) or (0.0, 0.0); path = [p0]
                    for _ in range(3):
                        q = self.spot(margin=0.3, clear=0.15, near=path[-1], spread=0.35) or path[-1]; path.append(q)
                    rec['path'] = path
            elif kind == 'heron':
                p = tuple(at) if at else self._shallow()
                rec.update(at=p, yaw=float(a.get('yaw', math.pi * 0.92)))
            elif kind == 'ducks':
                rec['path'] = [tuple(q) for q in a['path']] if a.get('path') else self._duck_path()
            elif kind == 'fish':
                rec['center'] = tuple(at) if at else self.water_point('-Y')
            elif kind in ('fireflies', 'butterflies'):
                rec['spots'] = [self.spot(margin=0.4, clear=0.1) or (0.0, 0.0) for _ in range(min(6, max(1, rec['n'])) if kind == 'fireflies' else rec['n'])]
            elif kind == 'birds':
                rec.update(center=tuple(at) if at else (0.2 * k, 0.3 * k), radius=2.2 * k, height=1.1)
            self.animals.append(rec)

    def _shallow(self):
        X, Y = np.meshgrid(np.linspace(-self.sx / 2 + 0.3, self.sx / 2 - 0.3, 31), np.linspace(-self.sy / 2 + 0.25, self.sy / 2 - 0.3, 31))
        X, Y = X.ravel(), Y.ravel(); d = self.sd(X, Y); ok = (d > -0.14) & (d < -0.03)
        if not ok.any(): return (0.0, -self.sy / 2 + 0.3)
        score = np.where(ok, Y + 0.3 * np.abs(X - 0.6 * self.k), np.inf); i = int(np.argmin(score))
        return (float(X[i]), float(Y[i]))

    def _duck_path(self):
        w = self.water[0]
        if w['type'] == 'river':
            C = cw.catmull(w['path'], 60); inside = [(float(x), float(y)) for x, y in C if abs(x) < self.sx / 2 - 0.05 and abs(y) < self.sy / 2 - 0.05]
            return inside[::6] or inside
        c = self.water_point('-Y') or (0.0, 0.0); r = 0.35 * self.k
        return [(c[0] + r * math.cos(a), c[1] + 0.25 + r * 0.6 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 7)]

    # ---------------------------------------------------------------- what the engine needs for the block
    def keep_clear(self):
        return [(x, y, r) for x, y, r in self.taken]

    def summary(self):
        return {'size': [self.sx, self.sy, self.depth], 'strata': self.strata_name, 'water': self.water_kind, 'season': self.season, 'time': self.time,
                'houses': len(self.houses), 'mill': bool(self.mill), 'bridge': bool(self.bridge), 'eggs': [(e['id'], e['face'], round(e['u'], 2), round(e['depth'], 2)) for e in self.eggs],
                'animals': [a['kind'] for a in self.animals], 'fog': self.fog, 'shafts': self.shafts, 'notes': self.notes}
