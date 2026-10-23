"""The Cutaway line's engine: builds and poses a whole film from spec.json + cues.json (Blender bpy 5.2, Cycles, free).

A film folder of the line holds spec.json (data, written by a person or the director's coder seat), cues.json (the
narration's line and word times), film.json and blender.py (a copy of films/lib/cutaway/blender.py, which calls this).
The scene contract is harness/blender_render.py's: DURATION, SETTINGS, build(bpy, ctx), frame(bpy, ctx, state, i, t).

Built on the kit (films/styles/cutaway/cutaway.py) and the cinematic extras (films/styles/cutaway/cinematic/extras.py),
both imported and never edited. Only the sets the render range needs are built (a one-frame still builds one set).
Every motion is a pure function of the film time t, so any frame renders alone on any runner.
Words, labels and numbers are set in code here (overlay.py), never painted by a model.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
for p in (HERE, os.path.join(ROOT, 'films', 'styles', 'cutaway'), os.path.join(ROOT, 'films', 'styles', 'cutaway', 'cinematic')):
    if p not in sys.path: sys.path.insert(0, p)

import numpy as np  # noqa: E402

import camera as C  # noqa: E402
import presets as P  # noqa: E402
from plan import Plan, load  # noqa: E402

FONT = os.path.join(ROOT, 'ads', 'fonts', 'InstrumentSans.ttf')
SHAFT_GAIN = {'map': 0.35, 'ground': 1.0, 'crane': 0.8, 'macro': 0.0, 'hero': 1.0, 'orbit': 0.6, 'push': 0.6, 'pull': 0.6}
FOG_GAIN = {'map': 1.0, 'ground': 0.4, 'crane': 1.0, 'macro': 1.0, 'hero': 0.7, 'orbit': 0.8, 'push': 0.8, 'pull': 0.8}
DOF = {'ground', 'macro'}          # the shots where depth of field shows; elsewhere it is off (sharp, and labels sit close)


class SpecError(RuntimeError):
    pass


def _argv_range(fps, duration):
    a = sys.argv; s = e = None
    try:
        if '--start' in a: s = int(a[a.index('--start') + 1])
        if '--end' in a: e = int(a[a.index('--end') + 1])
    except Exception: pass
    total = int(round(duration * fps)); s = 0 if s is None else s; e = total if (e is None or e < 0) else min(e, total)
    return s / fps, e / fps


class Film:
    def __init__(self, film_dir, spec_path=None):
        self.dir = os.path.abspath(film_dir)
        spec, cues = load(self.dir, spec_path)
        self.plan = Plan(spec, cues)
        if self.plan.errors:
            raise SpecError('the spec has errors (run films/lib/cutaway/tools/validate.py):\n- ' + '\n- '.join(self.plan.errors[:30]))
        fj = os.path.join(self.dir, 'film.json'); self.meta = json.load(open(fj)) if os.path.exists(fj) else {}
        look = spec.get('look') or {}
        self.DURATION = float(self.plan.duration)
        self.SETTINGS = {'samples': int(look.get('samples', self.meta.get('samples', 20))), 'denoise': True, 'motion_blur': False,
                         'view_transform': 'AgX', 'look': look.get('contrast', 'AgX - Medium High Contrast'), 'exposure': float(look.get('exposure', 0.1)),
                         'max_bounces': 8, 'volume_bounces': 0, 'clamp_indirect': 4.0, 'adaptive_min_samples': 8, 'denoising_prefilter': 'FAST',
                         'volume_step_rate': 6.0}
        self.fast = look.get('quality', 'fast') != 'full'

    # ---------------------------------------------------------------- build
    def build(self, bpy, ctx):
        import cutaway as cw
        import extras as ex
        import overlay as ov
        self.cw, self.ex, self.ov = cw, ex, ov
        W, H = ctx['W'], ctx['H']; pl = self.plan
        if ctx.get('times'): need = sorted({pl.shot_at(t)['set'] for t in ctx['times']})
        else:
            a, b = _argv_range(ctx['fps'], self.DURATION); need = pl.sets_between(a, b)
        need = need or [pl.shots[0]['set']]
        self.built = {}
        for name in need:
            before = set(bpy.data.objects.keys())
            st = self._build_set(bpy, pl.sets[name])
            st['objs'] = [bpy.data.objects[k] for k in set(bpy.data.objects.keys()) - before]
            st['hidden'] = {o.name for o in st['objs'] if o.hide_render}
            st['world'] = bpy.context.scene.world
            self.built[name] = st
            print(f'set {name}: {len(st["objs"])} objects, time {pl.sets[name].time}', flush=True)
        ex.finish(bpy, W, H)
        self.cam = ex.ShotCam(self.built[need[0]]['kit'], name='cl_cam')
        self.cam.ob.data.clip_start = 0.01
        okit = cw.Kit(bpy, seed=1)
        self.O = ov.Overlay(okit, self.cam.ob, FONT, W, H, exposure=self.SETTINGS['exposure'])
        self.r = W / P.REF[pl.fmt][0]
        self._overlays()
        cw.apply_cycles(bpy, fast=self.fast)
        sc = bpy.context.scene; cy = sc.cycles
        cy.adaptive_threshold = 0.035; cy.sample_clamp_direct = 12.0; cy.transparent_max_bounces = 16
        cy.volume_bounces = 0; cy.volume_step_rate = self.SETTINGS['volume_step_rate']; cy.volume_max_steps = 128
        try: cy.volume_biased = True
        except Exception: pass
        sc.view_settings.look = self.SETTINGS['look']; sc.view_settings.exposure = self.SETTINGS['exposure']
        self.shown = None
        return {'film': self}

    def _build_set(self, bpy, L):
        cw, ex = self.cw, self.ex; k = L.k; gold = L.time in ('golden', 'dusk')
        kit = cw.Kit(bpy, seed=L.seed)
        land = cw.block(kit, size=L.size, depth=L.depth, strata=L.strata, seed=L.seed, top=L.top, water=L.water, season=L.season,
                        keep_clear=L.keep_clear(), grass=L.veg['grass'], trees=L.veg['trees'], tree_kinds=('round', 'cone', 'round'),
                        boulders=L.veg['boulders'], flowers=L.veg['flowers'], lilies=L.veg['lilies'], reeds=L.veg['reeds'], corals=L.veg['corals'],
                        shore_rock=0.6 if L.water_kind == 'lagoon' else 0.0, sway=1.35,
                        water_density=2.8 if gold else 2.6, water_glow=0.0 if gold else 0.022,
                        water_tint=(0.14, 0.56, 0.58) if gold else (0.24, 0.82, 0.78),
                        bed=((0.40, 0.38, 0.30), (0.28, 0.27, 0.22)) if gold else ((0.80, 0.74, 0.58), (0.70, 0.65, 0.52)),
                        caustics=0.35 if gold else 0.5)
        st = {'kit': kit, 'land': land, 'L': L, 'rig': None, 'shafts': None, 'fog_gain': None}
        # ---- light (time of day)
        if L.time == 'studio': cw.studio(kit, land=land, shadows=0.2)
        elif L.time == 'day': cw.sky(kit, land=land, sun_az=-120, sun_el=40, sun=3.0)
        elif L.time == 'overcast': cw.sky(kit, top=(0.52, 0.58, 0.64), horizon=(0.74, 0.77, 0.80), sun_az=-110, sun_el=48, sun=1.4, land=land)
        elif L.time == 'golden':
            st['rig'] = ex.cine_light(kit, land, 135.0, 11.0, sun=6.0, fill=0.9, amb=0.24)
        else:   # dusk
            st['rig'] = ex.cine_light(kit, land, 150.0, 6.0, sun=3.2, sun_color=(1.0, 0.52, 0.30), fill=0.6, rim=0.8, zenith=(0.06, 0.08, 0.20),
                                      horizon=(0.92, 0.50, 0.32), away=(0.26, 0.22, 0.38), amb=0.16)
        if st['rig']:
            ex.gobo(kit, land, st['rig']['sun_dir'])
            ex.edge_spill(kit, land, '-Y', power=70.0 if L.time == 'golden' else 40.0)
            ex.edge_spill(kit, land, '+X', power=35.0 if L.time == 'golden' else 20.0)
        if L.fog > 0:
            _, st['fog_gain'] = ex.atmosphere(kit, land, haze=0.0, fog=7.0 * L.fog, fog_top=0.16, ceiling=0.25, spill=0.3, aniso=0.7)
        # ---- props
        lit = 1.6 if L.time == 'dusk' else (1.0 if L.time == 'golden' else 0.0)
        roofs = [(0.55, 0.22, 0.14), (0.30, 0.30, 0.34), (0.48, 0.28, 0.18)]
        for j, (x, y, yaw) in enumerate(L.houses):
            cw.house(kit, land, x, y, w=0.21 * k, d=0.15 * k, h=0.13 * k, roof=0.09 * k, yaw=yaw, lit=lit, roof_col=roofs[j % 3], name=f'cl_house{j}')
        if L.mill:
            x, y, yaw, off = L.mill; cw.mill(kit, land, x, y, yaw=yaw, lit=lit, wheel_r=0.11 * k, wheel_off=off)
        if L.bridge: cw.bridge(kit, land, L.bridge[0], L.bridge[1], width=0.09 * k, arch=0.06 * k)
        for j, (x, y) in enumerate(L.lamps): cw.lamp(kit, land, x, y, strength=0.25 if L.time in ('dusk', 'golden') else 0.0, name=f'cl_lamp{j}')
        for j, path in enumerate(L.pipes): cw.pipe(kit, land, path, name=f'cl_pipe{j}')
        for j, (x, y, ln) in enumerate(L.piles): cw.pile(kit, land, x, y, length=ln, name=f'cl_pile{j}')
        # ---- easter eggs, by depth
        if L.eggs:
            eggs = ex.Eggs(kit, land)
            for e in L.eggs:
                f = eggs.faces[e['face']]; u = e['u']; top = f.top(u); z = top - e['depth']; kind = e['kind']
                if kind == 'gold':
                    half = (L.face_len(e['face']) / 2) - 0.12; wob = [0.03, -0.04, 0.03, -0.06, -0.01, -0.05]
                    pts = [(float(np.clip(u - e['span'] / 2 + e['span'] * j / 5, -half, half)), z + wob[j]) for j in range(6)]
                    eggs.gold(e['face'], pts)
                elif kind == 'well': eggs.well(e['face'], u, z_bottom=z)
                elif kind == 'dino': eggs.dino(e['face'], u, z, scale=e['scale'])
                elif kind == 'geode': eggs.geode(e['face'], u, z)
                else: getattr(eggs, kind)(e['face'], u, z)
            eggs.finish(); st['eggs'] = eggs
        ex.soften_roots(land)
        # ---- life
        first = min((s['t0'] for s in self.plan.shots if s['set'] == L.name), default=0.0)
        for j, a in enumerate(L.animals):
            kind = a['kind']; sp = a['spec']
            at = lambda key, dflt: self.plan.T.t(sp[key]) if sp.get(key) is not None else dflt
            if kind in ('deer', 'fawn'):
                la = at('lift_at', first + 3.0 + 1.2 * j)
                ex.deer(kit, land, a['at'][0], a['at'][1], a['yaw'], lift_at=la, lower_at=at('lower_at', la + 4.4), name=f'cl_deer{j}', scale=0.72 if kind == 'fawn' else 1.0)
            elif kind == 'rabbit': ex.rabbit(kit, land, a['path'], t0=0.3 * j, name=f'cl_rabbit{j}')
            elif kind == 'fox': ex.fox(kit, land, a['path'], speed=0.05, name=f'cl_fox{j}')
            elif kind == 'heron': ex.heron(kit, land, a['at'][0], a['at'][1], a['yaw'], strike_at=at('strike_at', first + 5.0), name=f'cl_heron{j}')
            elif kind == 'ducks': ex.ducks(kit, land, a['path'], n=a['n'], speed=0.03, name=f'cl_duck{j}_')
            elif kind == 'fish' and a.get('center'): ex.fish(kit, land, a['center'], n=a['n'], name=f'cl_fish{j}_')
            elif kind == 'fireflies': ex.fireflies(kit, land, a['n'], near=a['spots'], name=f'cl_ff{j}_')
            elif kind == 'petals':
                hx, hy = L.sx / 2, L.sy / 2; ex.petals(kit, land, a['n'], box=((-hx, hx), (-hy, hy), (0.02, 0.75)), name=f'cl_petals{j}_')
            elif kind == 'butterflies': ex.butterflies(kit, land, a['spots'], name=f'cl_bfly{j}_')
            elif kind == 'birds': cw.birds(kit, a['n'], center=a['center'], radius=a['radius'], height=a['height'])
        # ---- god rays: canopy beams, and beams round the crown that sits between the hero camera and the sun
        if st['rig'] and L.shafts > 0:
            sd = st['rig']['sun_dir']; beams = []
            T = np.asarray(getattr(land, 'trees', np.zeros((0, 2))), float).reshape(-1, 2)
            if len(T):
                hero = C.pose({'camera': 'hero'}, L, 0.5, self.plan.fmt)['pos']
                gz = land.height(T[:, 0], T[:, 1]); crowns = np.stack([T[:, 0], T[:, 1], gz + 0.48 * k], 1)
                v = crowns - np.asarray(hero); v /= np.linalg.norm(v, axis=1)[:, None]; best = int(np.argmax(v @ sd))
                beams = ex.Shafts.around(tuple(crowns[best]), 0.2 * k, sd, 12)
            st['shafts'] = ex.Shafts(kit, land, sd, beams=beams, canopy=12, strength=2.4)
        return st

    # ---------------------------------------------------------------- overlays (set in code)
    def _overlays(self):
        ov, O, r, pl = self.ov, self.O, self.r, self.plan; v = pl.fmt == '9:16'
        tsize = (64 if v else 84) * r
        self.G = {'title': O.text('cl_title', pl.title['text'] if pl.title else ' ', tsize, ov.INK, 'CENTER', 1.0, bold=1.2),
                  'kicker': O.text('cl_kicker', (pl.title or {}).get('kicker') or ' ', 26 * r, ov.INK, 'CENTER', 1.4, bold=0.6),
                  'rule': O.line('cl_rule', ov.INK), 'tplate': O.pill('cl_tplate'),
                  'end': O.text('cl_end', pl.end['text'] if pl.end else ' ', (54 if v else 64) * r, ov.INK, 'CENTER', 1.2, bold=1.0),
                  'endsub': O.text('cl_endsub', (pl.end or {}).get('sub') or ' ', 26 * r, ov.INK, 'CENTER', 1.05, bold=0.3),
                  'eplate': O.pill('cl_eplate'),
                  'count': O.text('cl_count', '0', 56 * r, ov.INK, 'CENTER', 1.0), 'countcap': O.text('cl_countcap', ' ', 21 * r, ov.INK, 'CENTER', 1.15),
                  'countpl': O.pill('cl_countpl'),
                  'caption': O.text('cl_caption', ' ', 24 * r, ov.INK, 'LEFT', 1.25), 'cappl': O.pill('cl_cappl'),
                  'dip': O.mesh('cl_dip', (0.90, 0.91, 0.92), 4, [(0, 1, 2, 3)])}
        self.labels = {}
        for s in pl.shots:
            for j, lb in enumerate(s['labels']):
                key = (s['i'], j); self.labels[key] = ov.Label(O, f'cl_lb{s["i"]}_{j}', lb['text'], 26 * r)
        self.fits = {}

    def _fit(self, el, maxw):
        """Shrink a text element so it fits maxw pixels (measured once)."""
        if el.ob.name in self.fits: return self.fits[el.ob.name]
        el.place_text(0, 0); w, h = el.text_size_px(); s = min(1.0, maxw / max(w, 1e-6)); self.fits[el.ob.name] = (s, w * s, h * s); return self.fits[el.ob.name]

    def _draw_overlays(self, t, shot, W, H):
        ov, G, r, pl = self.ov, self.G, self.r, self.plan; O = self.O; O.hide_all(); v = pl.fmt == '9:16'
        Wd = P.REF[pl.fmt][0] * r
        def card(text_el, sub_el, plate, a, y, gap):
            """A title or end card: the main line at y, the second line at y + gap, one paper plate behind both."""
            if a <= 0: return
            s1, w1, h1 = self._fit(text_el, Wd * 0.80); s2, w2, h2 = self._fit(sub_el, Wd * 0.80)
            text_el.set_alpha(a); text_el.place_text(0, y, px=text_el.px * s1)
            sub_el.set_alpha(a); sub_el.place_text(0, y + gap, px=sub_el.px * s2)
            w = max(w1, w2) + 80 * r; pad = 26 * r
            top = max(y + h1 / 2, y + gap + h2 / 2) + pad; bot = min(y - h1 / 2, y + gap - h2 / 2) - pad
            plate.set_alpha(a * 0.92); plate.pill_shape(-w / 2, bot, w / 2, top, min(30 * r, (top - bot) / 2))
        if pl.title:
            a = ov.fade(t, pl.title['at'], pl.title['until'], 0.6, 0.6)
            y = (560 if v else 330) * r
            card(G['title'], G['kicker'], G['tplate'], a, y, (66 if v else 74) * r)
            if a > 0 and pl.title.get('kicker'):
                gy = y + (38 if v else 42) * r; G['rule'].set_alpha(a); G['rule'].line_shape((-50 * r, gy), (50 * r, gy), 2.0 * r)
        if pl.end:
            a = ov.fade(t, pl.end['at'], pl.end['until'] + 1.0, 0.8, 0.01)
            card(G['end'], G['endsub'], G['eplate'], a, 0.0, -(58 if v else 64) * r)
        c = shot.get('counter')
        if c:
            a = ov.fade(t, c['at'], c['until']); n = c['from'] + (c['to'] - c['from']) * C.ease_io((t - c['at']) / max(0.1, c['done'] - c['at']))
            body = f'{int(round(n)):,}' + (c['suffix'] if t >= c['done'] else '')
            x, y = c['pos'][0] * r, c['pos'][1] * r
            G['count'].set_text(body); G['count'].set_alpha(a); G['count'].place_text(x, y + 14 * r)
            G['countcap'].set_text(c['caption'] or ' '); G['countcap'].set_alpha(a); G['countcap'].place_text(x, y - 38 * r)
            G['countpl'].set_alpha(a * 0.9); G['countpl'].pill_shape(x - 190 * r, y - 64 * r, x + 190 * r, y + 60 * r, 18 * r)
        cp = shot.get('caption')
        if cp:
            a = ov.fade(t, cp['at'], cp['until']); x0 = -(Wd / 2) + 56 * r; y = (P.REF[pl.fmt][1] / 2 - 90) * r
            G['caption'].set_text(cp['text']); self.fits.pop(G['caption'].ob.name, None); s, w, h = self._fit(G['caption'], Wd * 0.8)
            G['caption'].set_alpha(a); G['caption'].place_text(x0, y, px=G['caption'].px * s)
            G['cappl'].set_alpha(a * 0.9); G['cappl'].pill_shape(x0 - 24 * r, y - 28 * r, x0 + w + 24 * r, y + 28 * r, 26 * r)
        for j, lb in enumerate(shot['labels']):
            a = ov.fade(t, lb['at'], lb['until'])
            self.labels[(shot['i'], j)].show(a, (lb['pos'][0] * r, lb['pos'][1] * r), lb['anchor'], draw=(t - lb['at']) / 0.6)
        # a dip through pale mist on a change of time: out of the previous shot, into this one
        dip = 0.0; idx = shot['i']
        if shot.get('transition') == 'dip': dip = max(dip, 1.0 - ov.ease((t - shot['t0']) / 0.55))
        if idx + 1 < len(pl.shots) and pl.shots[idx + 1].get('transition') == 'dip': dip = max(dip, ov.ease((t - (shot['t1'] - 0.45)) / 0.45))
        G['dip'].set_alpha(dip)
        if dip > 0:
            hw, hh = W / 2, H / 2
            G['dip'].set_verts([(-hw * 1.2, -hh * 1.2), (hw * 1.2, -hh * 1.2), (hw * 1.2, hh * 1.2), (-hw * 1.2, hh * 1.2)], 0.001)

    # ---------------------------------------------------------------- frame
    def _show(self, name):
        if self.shown == name: return
        for n, st in self.built.items():
            for o in st['objs']:
                try: o.hide_render = (n != name) or (o.name in st['hidden'])
                except ReferenceError: pass
        self.shown = name

    def frame(self, bpy, ctx, S, i, t):
        pl = self.plan; shot = pl.shot_at(t)
        if shot['set'] not in self.built:
            raise RuntimeError(f'frame {i} ({t:.2f} s) needs set {shot["set"]}, which this render range did not build')
        self._show(shot['set']); st = self.built[shot['set']]; L = st['L']
        bpy.context.scene.world = st['world']
        st['kit'].update(t)
        u = (t - shot['t0']) / max(1e-3, shot['t1'] - shot['t0'])
        c = C.pose(shot, L, u, pl.fmt); cam = shot['camera']
        dof = cam in DOF and os.environ.get('KF_DOF', '1') != '0'      # KF_DOF=0: no depth of field (cost tests)
        self.cam.set(c['pos'], c['tgt'], c['lens'], c['focus'], c['fstop'], c['roll']); self.cam.ob.data.dof.use_dof = dof
        if st['shafts'] is not None:
            st['shafts'].update(c['pos']); st['shafts'].gain.default_value = SHAFT_GAIN.get(cam, 0.6) * L.shafts
        if st['fog_gain'] is not None: st['fog_gain'].default_value = FOG_GAIN.get(cam, 0.8)
        self.O.d = (0.97 * c['focus']) if dof else 0.5          # depth of field keeps the overlay sharp only at the focus
        self._draw_overlays(t, shot, ctx['W'], ctx['H'])


def scene(film_dir):
    """DURATION, SETTINGS, build, frame for harness/blender_render.py (spec path from $KF_SPEC, default spec.json)."""
    f = Film(film_dir)
    return f.DURATION, f.SETTINGS, f.build, (lambda bpy, ctx, S, i, t: f.frame(bpy, ctx, S, i, t)), f
