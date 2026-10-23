#!/usr/bin/env python3
"""Validator of the Cutaway line: everything about a spec that code can judge, in about a second, with no Blender.

    python3 films/lib/cutaway/tools/validate.py <film dir> [--spec spec.json] [--out report.json] [--quiet]

Checks: the schema and the presets (sets, eggs, animals, props, cameras), every cue-time reference against cues.json,
the scene list (CRAFT.md 2), a written reason on every cut (CRAFT.md 3), shot count and length, camera speed on screen
(CRAFT.md 4: a pan at most 0.25 frames per second, a push at most 10 % per second; twice that is an error), the eggs
(per set, unique, inside the block, not overlapping, ordered by depth), labels (house rules for words, slots that
collide, ground shots), title and end cards, and the render cost on the free runners.
Writes {ok, hard, soft, stats, cost} (hard = the film cannot be made like this; soft = fix if you can).
Exit 0 with a report; 2 if the validator itself broke.
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__)); LIB = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(LIB)))
for p in (LIB, os.path.join(ROOT, 'films', 'styles', 'cutaway')):
    if p not in sys.path: sys.path.insert(0, p)

import presets as P  # noqa: E402
from camera import speed  # noqa: E402
from plan import Plan  # noqa: E402

CRAFT = {'scenes_max': 9, 'max_shots_per_3min': 40, 'avg_shot_s': (4.0, 12.0), 'min_shot_s': 2.0, 'hard_min_shot_s': 1.0,
         'pan': 0.25, 'push': 0.10, 'hard_factor': 2.0}
# Render cost model (free 4-core GitHub runner, 1280x720, 24 samples, plain day light): seconds per frame. Calibrated on
# Venice r4 (about 45 to 60 s a frame), the cinematic board (r3, r4) and the meadow stills r1 and r2 (23 Oct: golden, 20 samples: map about 55 s, crane 70 to 90 s, macro 30 to 40 s, hero about 50 s).
BASE_S = 40.0
SETUP_S = 180.0            # per render part: checkout, apt, pip bpy, scene build
PART_LIMIT_MIN = 280.0     # films-render.yml gives each part 300 minutes


def frame_seconds(L, cam, fmt, samples, W, H):
    s = BASE_S * P.TIME_COST[L.time] * (samples / 24.0) ** 0.8 * (W * H) / (1280 * 720)
    s *= 0.8 if cam in P.CLOSE else (1.1 if cam == 'map' else 1.0)
    s *= 1.0 + (1.6 if cam not in P.CLOSE else 0.5) * min(1.0, L.fog)
    s *= {'lagoon': 1.3, 'river': 1.1, 'stream': 1.05, 'pond': 1.1, 'none': 0.9}[L.water_kind]
    s *= 1.0 + 0.012 * len(L.eggs) + 0.004 * len(L.animals) + 0.02 * len(L.houses) * (1 if L.time == 'dusk' else 0)
    s *= 0.85 + 0.15 * min(2.0, L.veg['grass'])
    return s


def validate(film_dir, spec_rel='spec.json'):
    spec = json.load(open(os.path.join(film_dir, spec_rel))); cues = json.load(open(os.path.join(film_dir, 'cues.json')))
    fj = os.path.join(film_dir, 'film.json'); meta = json.load(open(fj)) if os.path.exists(fj) else {}
    hard, soft = [], []
    raw = json.dumps(spec)
    if len(raw) > 40000: hard.append(f'the spec is {len(raw) // 1000} KB; keep it under 40 KB (it is data, not code)')
    pl = Plan(spec, cues); hard += pl.errors; soft += pl.warnings
    dur = pl.duration; shots = pl.shots; fmt = pl.fmt
    stats = {'duration': round(dur, 2), 'format': fmt, 'scenes': len(pl.scenes), 'shots': len(shots), 'sets': {k: L.summary() for k, L in pl.sets.items()}}
    if cues.get('estimated'): soft.append('cues.json is an estimate (no narration yet): word times will move when the narration is recorded')
    # ---- scenes and shots (CRAFT.md 2, 3)
    lo = max(2, round(dur / 30.0))
    if pl.scenes and not lo <= len(pl.scenes) <= CRAFT['scenes_max']: soft.append(f'{len(pl.scenes)} scenes; a film of {dur:.0f} s has {lo} to {CRAFT["scenes_max"]} (CRAFT.md 2)')
    if shots:
        mx = max(1, round(CRAFT['max_shots_per_3min'] * dur / 180))
        if len(shots) > mx: hard.append(f'{len(shots)} shots in {dur:.0f} s (at most {mx}): fewer, longer shots (CRAFT.md 2)')
        avg = dur / len(shots); stats['avg_shot_s'] = round(avg, 2)
        a, b = CRAFT['avg_shot_s']
        if not a <= avg <= b: soft.append(f'average shot {avg:.1f} s (aim {a:g} to {b:g} s; CRAFT.md 2)')
        for s in shots:
            d = s['t1'] - s['t0']
            if d < CRAFT['hard_min_shot_s']: hard.append(f'{s["where"]}: {d:.2f} s is a flash, not a shot (at least {CRAFT["min_shot_s"]:g} s)')
            elif d < CRAFT['min_shot_s']: soft.append(f'{s["where"]}: {d:.2f} s; short shots only at the climax (CRAFT.md 2)')
        for x, y in zip(shots[:-1], shots[1:]):
            if x['set'] == y['set'] and x['camera'] == y['camera'] and x['camera'] in ('orbit', 'map', 'hero') and y.get('transition') != 'dip':
                soft.append(f'{y["where"]}: same set and same camera ({y["camera"]}) as the shot before: a jump cut; change the scale or the angle')
    # ---- camera speed (CRAFT.md 4)
    spd = []
    for s in shots:
        L = pl.sets.get(s['set'])
        if L is None or s['camera'] not in P.CAMERAS: continue
        try: v = speed(s, L, s['t1'] - s['t0'], fmt)
        except Exception as e: hard.append(f'{s["where"]}: camera failed: {e}'); continue
        spd.append({'shot': s['i'], 'camera': s['camera'], **v})
        for key, lim, unit in (('pan', CRAFT['pan'], 'frames per second'), ('push', CRAFT['push'], 'of the frame per second')):
            if v[key] > lim * CRAFT['hard_factor']:
                hard.append(f'{s["where"]} ({s["camera"]}, {s["t1"] - s["t0"]:.1f} s): the camera moves {v[key]:.2f} {unit} at its peak, faster than a real camera '
                            f'(at most {lim:g}): make the shot longer, the move smaller, or cut instead (CRAFT.md 4)')
            elif v[key] > lim:
                soft.append(f'{s["where"]} ({s["camera"]}): {key} {v[key]:.2f} {unit} at its peak (aim at most {lim:g}; CRAFT.md 4)')
    stats['camera'] = spd
    # ---- eggs
    for name, L in pl.sets.items():
        kinds = [e['kind'] for e in L.eggs]; ids = [e['id'] for e in L.eggs]
        if len(L.eggs) > P.MAX_EGGS_PER_SET: hard.append(f'sets.{name}: {len(L.eggs)} eggs; at most {P.MAX_EGGS_PER_SET} (each has its own light)')
        for kd in set(kinds):
            if kinds.count(kd) > (2 if kd == 'geode' else 1): hard.append(f'sets.{name}: {kinds.count(kd)} eggs of kind {kd}; one of each (two geodes at most)')
        if len(set(ids)) != len(ids): hard.append(f'sets.{name}: two eggs share an id; give each its own "id"')
        shown = [s for s in shots if s['set'] == name and s['camera'] in ('crane', 'macro', 'ground', 'hero')]
        if shown and not L.eggs: soft.append(f'sets.{name}: no easter eggs in the cut faces (Sam, 22 Oct: easter eggs in the soil that make people smile)')
        for e in L.eggs:
            fl = L.face_len(e['face']); u0, u1, z0, z1 = L.footprint(e)
            if u0 < -fl / 2 + 0.02 or u1 > fl / 2 - 0.02:
                (soft if e['kind'] == 'gold' else hard).append(f'sets.{name}: egg {e["id"]} runs off the {e["face"]} face (u {u0:.2f} to {u1:.2f}; the face spans {-fl / 2:.2f} to {fl / 2:.2f})')
            if e['depth'] < 0.05 or e['depth'] > L.depth - 0.05: hard.append(f'sets.{name}: egg {e["id"]} at depth {e["depth"]:.2f} m is outside the block (0.05 to {L.depth - 0.05:.2f} m)')
        for i, a in enumerate(L.eggs):
            for b in L.eggs[i + 1:]:
                if a['face'] != b['face']: continue
                fa, fb = L.footprint(a), L.footprint(b)
                if 'gold' in (a['kind'], b['kind']) or 'well' in (a['kind'], b['kind']):
                    hit = fa[0] < fb[1] and fb[0] < fa[1] and fa[2] < fb[3] and fb[2] < fa[3]
                else:
                    ca = ((fa[0] + fa[1]) / 2, (fa[2] + fa[3]) / 2); cb = ((fb[0] + fb[1]) / 2, (fb[2] + fb[3]) / 2)
                    q = ((ca[0] - cb[0]) / ((fa[1] - fa[0] + fb[1] - fb[0]) / 2)) ** 2 + ((ca[1] - cb[1]) / ((fa[3] - fa[2] + fb[3] - fb[2]) / 2)) ** 2
                    hit = q < 1.0
                if hit: hard.append(f'sets.{name}: eggs {a["id"]} and {b["id"]} overlap on the {a["face"]} face; move one (u or depth)')
        by = sorted(L.eggs, key=lambda e: e['depth'])
        for a, b in zip(by[:-1], by[1:]):
            if P.EGG_ORDER[P.EGGS[a['kind']]['cls']] > P.EGG_ORDER[P.EGGS[b['kind']]['cls']] and a['kind'] != 'well':
                soft.append(f'sets.{name}: {a["id"]} ({P.EGGS[a["kind"]]["cls"]}) sits above {b["id"]} ({P.EGGS[b["kind"]]["cls"]}): the layers read as time, recent near the top')
        stats.setdefault('eggs', {})[name] = len(L.eggs)
    # ---- labels: slots at the same time, ground shots, how many at once
    for s in shots:
        lbs = s['labels'] + ([{'slot': s['counter'].get('slot', 'upper-right'), 'pos': s['counter']['pos'], 'at': s['counter']['at'], 'until': s['counter']['until'], 'text': 'counter'}] if s.get('counter') else [])
        for i, a in enumerate(lbs):
            if s['camera'] == 'ground' and a['pos'][1] < 0:
                hard.append(f'{s["where"]}: "{a["text"]}" sits low in a ground shot, where the grass in front would hide it: use an upper slot')
            for b in lbs[i + 1:]:
                if a['at'] < b['until'] and b['at'] < a['until'] and math.hypot(a['pos'][0] - b['pos'][0], a['pos'][1] - b['pos'][1]) < 160:
                    hard.append(f'{s["where"]}: "{a["text"]}" and "{b["text"]}" are on screen together in the same place; give one another slot or time')
        if pl.title and s['t0'] < pl.title['until'] and pl.title['at'] < s['t1']:
            for a in lbs:
                if a['pos'][1] > 250 and a['at'] < pl.title['until'] and pl.title['at'] < a['until']:
                    hard.append(f'{s["where"]}: "{a["text"]}" is on screen with the title card, in its place; use a lower slot or a later time')
        for t in [x['at'] + 0.1 for x in lbs]:
            n = sum(1 for x in lbs if x['at'] <= t < x['until'])
            if n > 2: soft.append(f'{s["where"]}: {n} labels on screen at {t:.1f} s; at most two at once reads cleanly'); break
    if pl.title:
        tl = pl.cues.get('title_line')
        if tl and tl in pl.T.lines and abs(pl.title['at'] - pl.T.lines[tl]['start']) > 1.5:
            soft.append(f'title: the title card starts {pl.title["at"]:.1f} s, away from the title line {tl} ({pl.T.lines[tl]["start"]:.1f} s)')
    # ---- render cost
    W, H = (int(meta.get('render_w') or P.RENDER[fmt][0]), int(meta.get('render_h') or P.RENDER[fmt][1]))
    samples = int((spec.get('look') or {}).get('samples', meta.get('samples', 20)))
    fps = int(meta.get('fps', 24)); total = 0.0; per = []
    for s in shots:
        L = pl.sets.get(s['set'])
        if L is None: continue
        fs = frame_seconds(L, s['camera'], fmt, samples, W, H); n = (s['t1'] - s['t0']) * fps; total += fs * n
        per.append({'shot': s['i'], 'camera': s['camera'], 's_per_frame': round(fs, 1), 'frames': int(round(n))})
    frames = int(math.ceil(dur * fps)); parts = max(4, min(20, math.ceil(frames / 48)))   # films-render.yml: 48 frames a part for Blender films
    part_min = (total / parts + SETUP_S) / 60.0
    cost = {'frames': frames, 'samples': samples, 'size': [W, H], 'runner_hours': round(total / 3600.0, 1), 'parts': parts,
            'minutes_per_part': round(part_min, 1), 'avg_s_per_frame': round(total / max(1, frames), 1), 'per_shot': per, 'usd': 0.0,
            'note': 'free: CPU Cycles on GitHub runners of the public repo; estimate, runner speed varies by 2x or more'}
    if part_min > PART_LIMIT_MIN: hard.append(f'render cost: about {part_min:.0f} minutes per part on {parts} runners, over the 300 minute job limit: '
                                             f'fewer samples, fog off, a shorter film, or split the render')
    elif part_min > 180: soft.append(f'render cost: about {part_min:.0f} minutes per part on {parts} runners (aim under 180): lower samples or fog')
    stats['cost'] = cost
    hard = list(dict.fromkeys(hard)); soft = list(dict.fromkeys(soft))
    return {'ok': not hard, 'hard': hard, 'soft': soft[:40], 'stats': stats, 'cost': cost, 'spec': spec_rel}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('film'); ap.add_argument('--spec', default='spec.json'); ap.add_argument('--out'); ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()
    try: rep = validate(a.film, a.spec)
    except Exception as e:
        import traceback; traceback.print_exc()
        rep = {'ok': False, 'hard': [f'validator crashed: {type(e).__name__}: {e}'], 'soft': [], 'stats': {}, 'cost': {}}
        if a.out: os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); json.dump(rep, open(a.out, 'w'), indent=1)
        sys.exit(2)
    if a.out: os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); json.dump(rep, open(a.out, 'w'), indent=1)
    if a.quiet: print(json.dumps({'ok': rep['ok'], 'hard': len(rep['hard']), 'soft': len(rep['soft']), 'runner_hours': rep['cost'].get('runner_hours')}))
    else:
        print('OK' if rep['ok'] else 'NOT OK')
        for h in rep['hard']: print('  HARD', h)
        for s in rep['soft']: print('  soft', s)
        c = rep['cost']; print(f"  cost: {c.get('frames')} frames, {c.get('avg_s_per_frame')} s a frame, {c.get('runner_hours')} runner-hours, "
                               f"{c.get('parts')} parts of about {c.get('minutes_per_part')} min, US$0")
        print('  camera peaks:', ', '.join(f"{x['shot']}:{x['camera']} pan {x['pan']} push {x['push']}" for x in rep['stats'].get('camera', [])))


if __name__ == '__main__':
    main()
