"""Why Venice Sinks (Under the Surface, film 1): the picture, in the Cutaway style (films/styles/cutaway, imported, not edited).

Scene contract of harness/blender_render.py: DURATION, SETTINGS, build(bpy, ctx), frame(bpy, ctx, state, i, t).
The shot list (PLAN below, explained cut by cut in NOTES.md) sits on the narration's own times from cues.json (made by
.github/workflows/sound.yml): shots start and end on line starts, line ends and single words, so the picture follows the
voice exactly. Six sets (sets.py) are built at the origin; each shot shows one. Only the sets a render range needs are
built (a still of one frame builds one set). Every motion is a pure function of the film time t: any frame renders alone.
"""
import os, sys, json, math, re

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
for p in (os.path.join(ROOT, 'films', 'styles', 'cutaway'), HERE):
    if p not in sys.path: sys.path.insert(0, p)
import numpy as np  # noqa: E402
import cutaway as cw  # noqa: E402
import arch, sets, overlay as ov  # noqa: E402

# ------------------------------------------------------------------------------------------------ the narration's times
def _cues():
    p = os.path.join(HERE, 'cues.json')
    if os.path.exists(p): return json.load(open(p))
    ad = json.load(open(os.path.join(HERE, 'ad.json'))); t = 1.2; lines = []        # estimate until the sound exists
    for k, l in enumerate(ad['prep']['vo']):
        words = l['text'].split(); d = len(words) / 2.7 + 0.2 * l['text'].count('.'); w = []
        for j, x in enumerate(words): w.append([x, round(t + d * j / len(words), 3), round(t + d * (j + 1) / len(words), 3)])
        lines.append({'id': f'l{k:02d}', 'text': l['text'], 'start': round(t, 3), 'end': round(t + d, 3), 'words': w}); t += d + (3.2 if k == 1 else 0.7)
    return {'duration': round(t + 4.2, 3), 'lines': lines, 'estimated': True}


CUES = _cues(); LN = {l['id']: l for l in CUES['lines']}
DURATION = float(CUES['duration'])


def S(lid, off=0.0): return LN[lid]['start'] + off
def E(lid, off=0.0): return LN[lid]['end'] + off


def W(lid, word, off=0.0, end=True, nth=0):
    """Time of a word in a line (its end by default). Falls back to a proportional estimate if the word is not found."""
    l = LN[lid]; key = re.sub(r"[^a-z0-9]", '', word.lower()); hits = [w for w in l.get('words', []) if re.sub(r"[^a-z0-9]", '', w[0].lower()) == key]
    if len(hits) > nth: return (hits[nth][2] if end else hits[nth][1]) + off
    words = l['text'].split(); idx = next((i for i, x in enumerate(words) if re.sub(r"[^a-z0-9]", '', x.lower()) == key), len(words) - 1)
    return l['start'] + (l['end'] - l['start']) * (idx + (1 if end else 0)) / len(words) + off


SETTINGS = {'samples': 40, 'denoise': True, 'motion_blur': False, 'view_transform': 'AgX', 'look': 'AgX - Base Contrast', 'exposure': 0.2,
            'max_bounces': 8, 'clamp_indirect': 6.0, 'adaptive_min_samples': 12, 'denoising_prefilter': 'ACCURATE'}
REF_W = 1920.0                      # overlay positions and sizes are written for a 1920 x 1080 frame and scaled to the render


# ------------------------------------------------------------------------------------------------ camera keys
def K(az, el, dist, tgt=(0, 0, -0.5), lens=50.0): return {'az': az, 'el': el, 'dist': dist, 'tgt': tgt, 'lens': lens}


def ease(u): u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)


def ease_io(u, a=0.25):
    """Ease in, steady middle, ease out (a real operator's move): a = share of the move spent easing at each end."""
    u = max(0.0, min(1.0, u)); n = 1 - a
    if u < a: return u * u / (2 * a) / n
    if u < 1 - a: return (a / 2 + (u - a)) / n
    return 1 - (1 - u) ** 2 / (2 * a * n)


def lerpk(k0, k1, e):
    f = lambda a, b: a + (b - a) * e
    return {'az': f(k0['az'], k1['az']), 'el': f(k0['el'], k1['el']), 'dist': k0['dist'] * (k1['dist'] / k0['dist']) ** e,
            'tgt': tuple(f(a, b) for a, b in zip(k0['tgt'], k1['tgt'])), 'lens': f(k0['lens'], k1['lens'])}


# ------------------------------------------------------------------------------------------------ the shot list
def plan():
    """23 shots in 8 scenes. Each: set, start and end time, camera from k0 to k1 (eased over the shot unless 'move' says
    otherwise), environment, the set's own parameters, overlays, and the reason for the cut that opens it."""
    sh = []
    def add(set_, t1, k0, k1, env='day', why='', **kw):
        t0 = sh[-1]['t1'] if sh else 0.0
        sh.append(dict(set=set_, t0=t0, t1=t1, k0=k0, k1=k1, env=env, why=why, **kw))
    sea_end = W('l00', 'sea', 0.45)
    # 1. A city in the sea ------------------------------------------------------------------------------------------
    add('city', sea_end, K(-50, 30, 13.6, (0.1, 0.0, -0.45), 50), K(-42, 29, 12.4, (0.1, 0.0, -0.45), 50), env='mist',
        why='open: arrive on Venice floating in the mist; the narration names it')
    add('city', E('l00', 0.7), K(-74, 13, 4.6, (-0.62, -2.0, -0.12), 50), K(-72, 8, 3.7, (-0.62, -2.0, -0.40), 50), env='mist',
        why='end of the sentence "standing in the middle of the sea"; change of scale: push to the cut face to see what is under it (water, then mud)')
    add('city', E('l01', 2.4), K(-40, 38, 16.5, (0.1, 0.1, 0.05), 50), K(-36, 38, 16.0, (0.1, 0.1, 0.05), 50), env='mist',
        why='the title card: the question of the film over the whole city', title=(S('l01', -0.2), E('l01', 2.2)))
    # 2. The lagoon, 1,500 years ago ----------------------------------------------------------------------------------
    add('lagoon', E('l02', 0.6), K(-36, 34, 13.2, (0, 0, -0.45), 50), K(-46, 31, 12.4, (0, 0, -0.45), 50), env='day',
        why='change of time (1,500 years earlier), shown by a dip through the mist; the empty lagoon, boats arrive',
        lagoon={'arrive': S('l02', 0.6)}, dip=True,
        labels=[('lagoon', 'LAGOON', W('l02', 'lagoon', -0.2, False), E('l02', 0.4), (-430, -60), (-0.9, -1.2, sets.LV)),
                ('sand', 'STRIP OF SAND', W('l02', 'sand', -0.6, False), E('l02', 0.4), (300, 300), (0.6, 1.45, -0.01))])
    add('lagoon', E('l03', 0.9), K(-78, 16, 4.0, (0.62, -2.0, -0.07), 50), K(-74, 12, 3.6, (0.62, -2.0, -0.12), 50), env='day',
        why='end of line; wide to close: the stone house on the mud, at the cut, sinks like a spoon in pudding',
        lagoon={'arrive': S('l02', 0.6), 'sink': (W('l03', 'house', 0.0, True, 0), 5.5)})
    # 3. A forest upside down -----------------------------------------------------------------------------------------
    one_end = W('l04', 'mud', 0.35)
    add('site', one_end, K(-58, 14, 2.1, (1.80, -1.98, -0.16), 50), K(-56, 12, 1.95, (1.80, -1.98, -0.22), 50), env='day',
        why='change of place: the clever trick; one pole hammered down, seen above and through the cut', site={'stage': 'one'})
    add('site', E('l04', 0.7), K(-46, 30, 11.0, (0.6, -0.8, -0.35), 50), K(-41, 31, 10.4, (0.6, -0.8, -0.35), 50), env='day',
        why='"Millions of them": close to wide, later the same day; many poles, three drivers', site={'stage': 'many'})
    add('site', E('l05', 0.9), K(-84, 4, 2.5, (1.30, -2.0, -0.22), 50), K(-84, 2, 2.5, (1.30, -2.0, -0.50), 50), env='day',
        why='wide to close on the cut: the poles packed side by side reach the pale, harder clay; the camera tilts down them',
        site={'stage': 'done'},
        labels=[('wood', 'OAK, ALDER, PINE', W('l05', 'oak', -0.3, False), E('l05', 0.6), (-260, 250), (1.26, -2.0, -0.26)),
                ('clay', 'HARDER CLAY', W('l05', 'harder', -0.3, False), E('l05', 0.6), (360, -250), (1.55, -2.0, -0.60))])
    tb, ts, tw = W('l06', 'boards', -0.6), W('l06', 'stone', -0.6), W('l06', 'walls', -0.7)
    add('site', E('l06', 0.9), K(-44, 26, 5.4, (1.30, -1.30, -0.12), 50), K(-50, 23, 5.0, (1.30, -1.30, -0.06), 50), env='day',
        why='new information: what goes on top of the poles, in order; the camera holds on the corner while it builds',
        site={'stage': 'done', 'build': (tb, ts, tw, tw + 3.5)},
        labels=[('boards', 'WOODEN BOARDS', tb + 0.4, ts + 0.5, (-470, -150), (1.0, -2.0, -0.112)),
                ('stone', 'WHITE STONE', ts + 0.4, E('l06', 0.8), (-470, -40), (0.8, -2.0, -0.09))])
    add('city', E('l07', 1.2), K(-30, 21, 4.6, (1.62, -1.62, -0.25), 50), K(-36, 18, 4.3, (1.62, -1.62, -0.32), 50), env='day',
        why='change of place: the real church built this way; low angle for its scale, the cut face packed with poles',
        counter=(W('l07', 'stands', -0.2, False), E('l07', 1.1), W('l07', 'million', 0.3)),
        labels=[('salute', 'SANTA MARIA DELLA SALUTE', S('l07', 0.6), E('l07', 1.1), (-420, 330), (1.55, -1.5, 0.12))])
    # 4. Why the wood lasts -------------------------------------------------------------------------------------------
    add('pole', E('l08', 0.8), K(-90, 8, 3.2, (0.0, -0.7, -0.40), 50), K(-90, 6, 2.9, (0.0, -0.7, -0.46), 50), env='day',
        why='change of scale: one pole deep in the mud; bubbles near the water stop deeper down',
        labels=[('noair', 'NO AIR', W('l08', 'air', -0.5, False), E('l08', 0.7), (330, -170), (0.04, -0.7, -0.62))])
    add('pole', E('l09', 1.0), K(-90, 4, 2.2, (0.0, -0.7, -0.52), 50), K(-90, 3, 2.0, (0.0, -0.7, -0.55), 50), env='day',
        why='closer: the change happens in the wood itself; it turns stony grey as minerals soak in',
        pole={'stone': (S('l09', 1.5), E('l09', 0.4))},
        labels=[('min', 'MINERALS', W('l09', 'minerals', -0.4, False), E('l09', 0.9), (-360, 160), (-0.09, -0.7, -0.40))])
    # 5. Why Venice sinks ---------------------------------------------------------------------------------------------
    sq = (W('l10', 'squeezed', -0.8, False), E('l10', 0.5))
    add('sink', E('l10', 0.7), K(-58, 16, 7.2, (0.0, -2.0, -0.38), 50), K(-56, 15, 6.8, (0.0, -2.0, -0.40), 50), env='day',
        why='change of place and question: why it sinks; reason one, the mud squeezed under the city', sink={'squeeze': sq},
        arrows=[(sq[0], sq[1] + 0.3, (-220, 260), (-220, 120)), (sq[0] + 0.25, sq[1] + 0.3, (90, 260), (90, 120))],
        labels=[('squeeze', 'MUD SQUEEZED', sq[0] + 0.2, E('l10', 0.6), (-60, 330), None)])
    rs = (S('l11', 0.6), E('l11', 0.2))
    add('sink', E('l11', 0.7), K(-16, 13, 3.6, (2.0, -1.0, -0.12), 50), K(-18, 12, 3.4, (2.0, -1.0, -0.10), 50), env='day',
        why='reason two: cut to the sea wall and its gauge; the water line creeps up', sink={'squeeze': sq, 'rise': rs},
        labels=[('sea', 'SEA LEVEL', S('l11', 0.6), E('l11', 0.6), (330, 140), ('wl', 2.0, -0.98))])
    pm = (W('l12', 'pumped', -0.3, False), W('l12', 'faster', 0.3))
    add('sink', W('l12', 'faster', 0.6), K(-70, 15, 5.4, (-1.10, -2.0, -0.32), 50), K(-66, 14, 5.0, (-1.20, -2.0, -0.36), 50), env='day',
        why='new information: the factories; the pipe pulls water from the deep sand, the ground drops',
        sink={'squeeze': sq, 'risen': True, 'pipe': True, 'pump': pm},
        labels=[('pump', 'WATER PUMPED UP', W('l12', 'pumped', -0.3, False), W('l12', 'faster', 0.5), (330, 160), (-1.35, -2.0, -0.40))])
    stop = W('l12', 'stopped', -0.5, False)
    add('sink', E('l12', 1.0), K(-62, 18, 2.6, (-1.25, -2.0, -0.02), 50), K(-62, 17, 2.45, (-1.25, -2.0, -0.04), 50), env='day',
        why='closer, the detail that answers the line: the valve turns, the flow stops',
        sink={'squeeze': sq, 'risen': True, 'pipe': True, 'pumped': True, 'stop': stop},
        labels=[('stop', 'PUMPING STOPPED', stop + 0.3, E('l12', 0.9), (-330, 200), (-1.18, -1.95, 0.03))])
    # 6. High water ----------------------------------------------------------------------------------------------------
    fl0 = S('l13', 0.5)
    flood = lambda t, a=fl0: 0.042 * ease((t - a) / 3.5)
    add('city', W('l13', 'squares', 0.45), K(-32, 34, 6.2, (-0.5, 0.35, -0.05), 50), K(-28, 33, 5.8, (-0.5, 0.35, -0.05), 50), env='grey',
        why='change of place and time: today, a high tide; the sea pours into the campo', city={'flood': flood})
    add('city', E('l13', 0.9), K(-62, 7, 0.30, (-0.56, 0.40, 0.0), 32), K(-54, 7, 0.29, (-0.56, 0.40, 0.0), 32), env='grey',
        why='low and close for people: walking to work on the raised walkways', city={'flood': 0.042, 'walkways': True})
    # 7. The wall under the sea ---------------------------------------------------------------------------------------
    add('inlet', W('l14', 'lagoon', 0.4), K(-40, 32, 12.6, (0.0, -0.4, -0.40), 50), K(-46, 30, 11.8, (0.0, -0.6, -0.40), 50), env='grey',
        why='change of place: an opening of the lagoon; the gates lie on the seabed',
        labels=[('gates', '78 GATES ON THE SEABED', W('l14', 'seventy', -0.2, False), W('l14', 'lagoon', 0.3), (330, -200), (0.0, -1.7, -0.28))])
    rise = (W('l14', 'pumped', -0.4, False), W('l14', 'back', 0.6))
    add('inlet', E('l14', 0.9), K(-88, 5, 2.5, (-0.05, -2.0, -0.17), 50), K(-88, 4, 2.4, (-0.05, -2.0, -0.12), 50), env='grey',
        why='close, side on through the cut: the gates fill with air and swing up (the score swells here)',
        inlet={'rise': rise, 'sea': (rise[1] - 1.0, rise[1] + 3.0)},
        labels=[('air', 'AIR PUMPED IN', rise[0] + 0.2, rise[1] - 0.6, (-330, -230), (-0.12, -1.96, -0.24))])
    add('inlet', W('l15', 'dry', -1.4, False), K(-52, 22, 6.6, (0.0, -1.3, -0.15), 50), K(-56, 21, 6.3, (0.0, -1.3, -0.15), 50), env='grey',
        why='wide again for the result: the sea high outside, the lagoon calm behind the gates',
        inlet={'up': True, 'high': True},
        caption=('OCTOBER 2020', S('l15', 0.3), W('l15', 'dry', -1.5, False)),
        labels=[('seal', 'SEA', S('l15', 0.6), W('l15', 'dry', -1.5, False), (300, -160), (1.0, -1.9, 0.02)),
                ('lagl', 'LAGOON', S('l15', 0.9), W('l15', 'dry', -1.5, False), (-380, -160), (-1.0, -1.9, -0.06))])
    add('city', E('l15', 1.4), K(-24, 22, 3.3, (-0.5, 0.35, 0.0), 50), K(-28, 21, 3.15, (-0.5, 0.35, 0.0), 50), env='day',
        why='cut on "The squares stayed dry": the campo, dry, people walking', city={'flood': 0.0})
    # 8. Dusk ----------------------------------------------------------------------------------------------------------
    add('city', DURATION, K(-40, 31, 9.0, (0.2, -0.2, -0.40), 50), K(-46, 33, 13.0, (0.1, 0.0, -0.45), 50), env='dusk',
        why='passing time to dusk (a dip through the mist): the city lights up; the slow pull back ends the film', dip=True, lights_on=S('l16', -0.6))
    return sh


PLAN = plan()

ENVS = {   # sky gradient top, horizon; sun energy, colour, azimuth, elevation; lamps 0..1, windows glow
    'mist': dict(top=(0.62, 0.70, 0.80), hor=(0.86, 0.88, 0.90), light=(0.85, 0.90, 1.0), ls=0.95, sun=2.6, sc=(1.0, 0.95, 0.88), az=-125, el=36, lamps=0.0, win=0.0),
    'day': dict(top=(0.56, 0.68, 0.82), hor=(0.82, 0.85, 0.90), light=(0.85, 0.90, 1.0), ls=0.9, sun=3.1, sc=(1.0, 0.96, 0.90), az=-125, el=40, lamps=0.0, win=0.0),
    'grey': dict(top=(0.52, 0.58, 0.64), hor=(0.74, 0.77, 0.80), light=(0.80, 0.84, 0.90), ls=1.25, sun=1.5, sc=(0.95, 0.96, 1.0), az=-110, el=48, lamps=0.0, win=0.0),
    'dusk': dict(top=(0.16, 0.20, 0.36), hor=(0.86, 0.56, 0.44), light=(0.45, 0.55, 0.95), ls=0.45, sun=1.9, sc=(1.0, 0.60, 0.34), az=-150, el=9, lamps=1.0, win=1.0),
}


def _argv_range(fps):
    a = sys.argv; s = e = None
    try:
        if '--start' in a: s = int(a[a.index('--start') + 1])
        if '--end' in a: e = int(a[a.index('--end') + 1])
    except Exception: pass
    total = int(round(DURATION * fps)); s = 0 if s is None else s; e = total if (e is None or e < 0) else min(e, total)
    return s / fps, e / fps


def build(bpy, ctx):
    t_a, t_b = _argv_range(ctx['fps'])
    need = sorted({p['set'] for p in PLAN if p['t1'] > t_a and p['t0'] < t_b + 1e-6}) or ['city']
    kit = cw.Kit(bpy, seed=7); M = arch.Mats(kit); lamps = sets.Lamps(kit)
    built = {}
    for name in need:
        built[name] = sets.BUILDERS[name](kit, M, lamps); print('set', name, len(built[name].objs), 'objects', flush=True)
    class _D: depth = sets.DEPTH
    cw.sky(kit, land=_D(), sun_az=-125, sun_el=38, sun=3.0, clouds=7, mist=True, behind_az=135)
    cw.apply_cycles(bpy)
    world = bpy.context.scene.world; nt = world.node_tree
    ramp = [n for n in nt.nodes if n.type == 'VALTORGB'][0]; bgl = [n for n in nt.nodes if n.type == 'BACKGROUND' and not n.inputs['Color'].is_linked][0]
    sun = bpy.data.objects['cw_sun']
    cam = cw.camera(kit, None, '16:9' if ctx['W'] >= ctx['H'] else '9:16', az=-42, el=30, lens=50, dist=12.0)
    cam.ob.data.clip_start = 0.02
    font = os.path.join(ROOT, 'ads', 'fonts', 'InstrumentSans.ttf')
    O = ov.Overlay(kit, cam.ob, font, ctx['W'], ctx['H'], exposure=SETTINGS['exposure'])
    r = ctx['W'] / REF_W
    G = {'title': O.text('vz_title', 'Why Venice Sinks', 92 * r, ov.INK, 'CENTER', 1.0, bold=1.2),
         'kicker': O.text('vz_kicker', 'UNDER THE SURFACE', 24 * r, ov.INK, 'CENTER', 1.4, bold=0.6),
         'rule': O.line('vz_rule', ov.INK),
         'count': O.text('vz_count', '0', 64 * r, ov.INK, 'CENTER', 1.0),
         'countcap': O.text('vz_countcap', 'POLES UNDER ONE CHURCH', 17 * r, ov.INK, 'CENTER', 1.15),
         'countpl': O.pill('vz_countpl'),
         'caption': O.text('vz_caption', 'OCTOBER 2020', 26 * r, ov.INK, 'LEFT', 1.25),
         'cappl': O.pill('vz_cappl'),
         'dip': O.mesh('vz_dip', (0.90, 0.91, 0.92), 4, [(0, 1, 2, 3)]),
         'arrows': [O.arrow(f'vz_arrow{k}') for k in range(2)]}
    labels = {}
    for p in PLAN:
        for (key, body, *_rest) in p.get('labels', []):
            if key not in labels: labels[key] = ov.Label(O, 'vz_lb_' + key, body, 22 * r)
    sc = bpy.context.scene; sc.view_settings.look = SETTINGS['look']; sc.view_settings.exposure = SETTINGS['exposure']
    return {'kit': kit, 'M': M, 'lamps': lamps, 'sets': built, 'ramp': ramp, 'bgl': bgl, 'sun': sun, 'cam': cam, 'O': O, 'G': G, 'labels': labels,
            'r': r, 'shown': None}


def shot_at(t):
    for p in PLAN:
        if t < p['t1']: return p
    return PLAN[-1]


def _env(S, name, t, p):
    e = dict(ENVS[name])
    ramp = S['ramp'].color_ramp.elements; ramp[0].color = cw.srgb(e['hor']); ramp[1].color = cw.srgb(e['top'])
    S['bgl'].inputs['Color'].default_value = cw.srgb(e['light']); S['bgl'].inputs['Strength'].default_value = e['ls']
    sun = S['sun']; sun.data.energy = e['sun']; sun.data.color = e['sc']; sun.rotation_euler = (math.radians(90 - e['el']), 0, math.radians(e['az'] + 90))
    lv = e['lamps']; win = e['win']
    if p.get('lights_on') is not None:
        u = ease((t - p['lights_on']) / 2.5); lv *= u; win *= u
    S['lamps'].level(lv)
    if S['M'].glow is not None: S['M'].glow_socket.default_value = 3.5 * win


def _show_set(S, name):
    if S['shown'] == name: return
    for n, st in S['sets'].items():
        for o in st.objs: o.hide_render = (n != name)
    S['shown'] = name


def frame(bpy, ctx, S, i, t):
    p = shot_at(t); r = S['r']
    if p['set'] not in S['sets']:     # a frame outside the built range (should not happen): build it now
        S['sets'][p['set']] = sets.BUILDERS[p['set']](S['kit'], S['M'], S['lamps'])
    _show_set(S, p['set']); S['shown'] = None
    st = S['sets'][p['set']]; st.update(t, p); S['kit'].update(t); _env(S, p['env'], t, p)
    u = (t - p['t0']) / max(1e-3, p['t1'] - p['t0']); k = lerpk(p['k0'], p['k1'], ease_io(u))
    cam = S['cam']; cam.ob.data.lens = k['lens']; cam.pose(az=k['az'], el=k['el'], dist=k['dist'], target=k['tgt'])
    # ---- overlays
    O = S['O']; G = S['G']; O.hide_all()
    W2, H2 = ctx['W'] / 2, ctx['H'] / 2
    if 'title' in p:
        a = ov.fade(t, p['title'][0], p['title'][1], 0.6, 0.6)
        G['kicker'].set_alpha(a); G['kicker'].place_text(0, 410 * r)
        G['title'].set_alpha(a); G['title'].place_text(0, 330 * r)
        G['rule'].set_alpha(a); G['rule'].line_shape((-60 * r, 383 * r), (60 * r, 383 * r), 2.2 * r)
    for (key, body, t0, t1, pos, anchor) in p.get('labels', []):
        a = ov.fade(t, t0, t1); lb = S['labels'][key]
        if isinstance(anchor, tuple) and anchor and anchor[0] == 'wl':        # the water line on the gauge (moves with the sea)
            sk = S['sets']['sink']; wz = sets.LV + (0.02 * ease((t - p['sink']['rise'][0]) / (p['sink']['rise'][1] - p['sink']['rise'][0])))
            anchor = (anchor[1] + 0.01, anchor[2], wz)
        lb.show(a, (pos[0] * r, pos[1] * r), anchor, draw=(t - t0) / 0.6)
    if 'counter' in p:
        t0, t1, tm = p['counter']; a = ov.fade(t, t0, t1)
        n = int(1_000_000 * ease((t - t0) / max(0.1, tm - t0)) ** 0.8); body = f'{n:,}' + ('+' if t >= tm else '')
        G['count'].set_text(body); G['count'].set_alpha(a); G['count'].place_text(560 * r, 300 * r)
        G['countcap'].set_alpha(a); G['countcap'].place_text(560 * r, 246 * r)
        G['countpl'].set_alpha(a * 0.9); G['countpl'].pill_shape(380 * r, 214 * r, 740 * r, 350 * r, 18 * r)
    if 'caption' in p:
        body, t0, t1 = p['caption']; a = ov.fade(t, t0, t1)
        G['caption'].set_alpha(a); G['caption'].place_text(-860 * r, 440 * r)
        G['cappl'].set_alpha(a * 0.9); G['cappl'].pill_shape(-884 * r, 412 * r, -584 * r, 468 * r, 28 * r)
    for j, (t0, t1, a_px, b_px) in enumerate(p.get('arrows', [])):
        a = ov.fade(t, t0, t1); ar = G['arrows'][j]; ar.set_alpha(a)
        if a > 0: ar.arrow_shape((a_px[0] * r, a_px[1] * r), (b_px[0] * r, b_px[1] * r), ease((t - t0) / 0.8), 2.4 * r, 14 * r)
    # a dip through the mist on a change of time: fades out of the previous shot and into this one
    dip = 0.0
    idx = PLAN.index(p)
    if p.get('dip'): dip = max(dip, 1.0 - ease((t - p['t0']) / 0.55))
    if idx + 1 < len(PLAN) and PLAN[idx + 1].get('dip'): dip = max(dip, ease((t - (p['t1'] - 0.45)) / 0.45))
    G['dip'].set_alpha(dip)
    if dip > 0: G['dip'].set_verts([(-W2 * 1.1, -H2 * 1.1), (W2 * 1.1, -H2 * 1.1), (W2 * 1.1, H2 * 1.1), (-W2 * 1.1, H2 * 1.1)], 0.001)
