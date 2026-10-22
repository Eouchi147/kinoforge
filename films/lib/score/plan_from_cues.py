#!/usr/bin/env python3
"""plan_from_cues.py: build a score plan for a Battle Map film from its own story.

    python3 films/lib/score/plan_from_cues.py films/battles/cannae [-o plan.json]

Reads <film>/cues.json (line starts and text, duration, which line is the title) and <film>/ad.json (the subject and
year), works out the palette (era and place), then finds the shape of the story in the narration:

    hook (calm) -> title -> setup (curious) -> plan (curious, a little more) -> battle (tension, drums enter)
    -> turn (the one swell) -> result (triumph or aftermath) -> epilogue (aftermath, resolves)

Every choice is a default that can be overridden in hints/<film id>.json next to this file (line ids, key, mode, tempo,
solo instrument, result mood), so a director can steer one film without touching the code. The narration's own timing
is never changed: sections start where lines start.
"""
import os, sys, re, json, zlib, argparse

HERE = os.path.dirname(os.path.abspath(__file__))

# place words decide Middle East versus the ancient Mediterranean, era decides the rest
PLACE = {
    'middle_east_central_asia': {'tigris': 3, 'iraq': 3, 'galilee': 3, 'palestine': 3, 'jerusalem': 2, 'tiberias': 2, 'damascus': 2, 'baghdad': 2,
                                 'egypt': 1, 'syria': 1, 'persia': 1, 'persian': 1, 'saladin': 2, 'mamluk': 2, 'mongol': 2, 'mongols': 2, 'sultan': 1,
                                 'crusader': 1, 'crusaders': 1, 'samarkand': 2, 'steppe': 2},
    'ancient_med': {'greece': 2, 'greek': 1, 'greeks': 1, 'sparta': 2, 'spartan': 2, 'spartans': 2, 'italy': 2, 'rome': 1, 'roman': 1, 'romans': 1,
                    'carthage': 1, 'thermopylae': 3, 'athens': 1, 'salamis': 1, 'hannibal': 1, 'scipio': 1},
}
ERA_WORDS = {'napoleon': 'early_modern_europe', 'wellington': 'early_modern_europe', 'bayonets': 'early_modern_europe', 'musket': 'early_modern_europe'}

ATTACK = re.compile(r"attack|charg|arrows? (went|thud)|advance|clash|fought|rode around|poured|stormed|marched at|hurled|archers.*shoot", re.I)
PLAN_RE = re.compile(r"\bplan\b|strateg|sneak|secret weapon|trick|\bbait\b", re.I)
TURN_RE = re.compile(r"surround|ambush|\bgap\b|fled|flee|turned (them|and)|shut the back|swung around|wedge|imperial guard|red tent|rose up|stepped in|"
                     r"immortals climbed|hidden path|squeezed|pretended|used one of|middle gave way|broke into pieces|chariot", re.I)
RESULT_RE = re.compile(r"over\b|lost\b|killed|won\b|beaten|defeat|captured|broke apart|broken|fell apart|ran\b|fled|died|surrender|by evening|within a few hours|tens of thousands", re.I)
EPILOGUE_RE = re.compile(r"later|today|years|went on|lesson|still|four days|christmas|never|ever since|so hannibal|so the persians|as for|almost two hundred", re.I)
WIN_RE = re.compile(r"\bwon\b|beaten|smashed|master|crowned|victory|conquer|champion|never conquered|broken\b", re.I)


def year_of(text):
    m = re.search(r'\((\d{1,4})\s*(BC|BCE)?\)', text)
    if not m: return None
    y = int(m.group(1)); return -y if m.group(2) else y


def palette_for(ad, cues):
    txt = ' '.join(l['text'] for l in cues['lines']).lower() + ' ' + (ad.get('_', '') if ad else '').lower()
    words = re.findall(r"[a-z]+", txt)
    sc = {k: sum(w.get(x, 0) for x in words) for k, w in PLACE.items()}
    year = year_of(ad.get('_', '')) if ad else None
    if year is None:
        m = re.search(r'\b(1[0-9]{3})\b', txt); year = int(m.group(1)) if m else None
    for w in words:
        if w in ERA_WORDS: return ERA_WORDS[w], year, sc
    if sc['middle_east_central_asia'] >= 4 and sc['middle_east_central_asia'] > sc['ancient_med']: return 'middle_east_central_asia', year, sc
    if year is not None and year < 500: return 'ancient_med', year, sc
    if year is not None and year >= 1600: return 'early_modern_europe', year, sc
    return 'medieval_europe', year, sc


KEYS = {'ancient_med': [('D', 'dorian'), ('E', 'phrygian'), ('A', 'dorian')], 'medieval_europe': [('G', 'dorian'), ('E', 'aeolian'), ('D', 'dorian')],
        'middle_east_central_asia': [('D', 'hijaz'), ('A', 'hijaz'), ('E', 'hijaz')], 'early_modern_europe': [('D', 'aeolian'), ('G', 'dorian'), ('A', 'aeolian')]}


def build(film_dir, hints=None):
    cues = json.load(open(os.path.join(film_dir, 'cues.json')))
    ad = json.load(open(os.path.join(film_dir, 'ad.json'))) if os.path.exists(os.path.join(film_dir, 'ad.json')) else {}
    fid = cues.get('id') or ad.get('id') or os.path.basename(film_dir.rstrip('/'))
    short = os.path.basename(os.path.abspath(film_dir))
    if hints is None:
        for name in (short, fid):
            p = os.path.join(HERE, 'hints', f'{name}.json')
            if os.path.exists(p): hints = json.load(open(p)); break
        hints = hints or {}
    lines = cues['lines']; D = float(cues['duration']); by_id = {l['id']: i for i, l in enumerate(lines)}
    why = []

    def line(key, default=None):
        v = hints.get(key)
        return by_id[v] if v in by_id else default
    pal, year, sc = palette_for(ad, cues); pal = hints.get('palette', pal)
    seed = zlib.crc32(fid.encode()) % 100000
    key, mode = KEYS[pal][seed % len(KEYS[pal])]
    key, mode = hints.get('key', key), hints.get('mode', mode)
    title_i = by_id.get(cues.get('title_line', 'l01'), 1)
    st = lambda i: float(lines[i]['start'])

    # battle: first attacking line after a third of the film
    battle_i = line('battle_line')
    if battle_i is None:
        battle_i = next((i for i in range(title_i + 3, len(lines)) if st(i) >= 0.36 * D and ATTACK.search(lines[i]['text'])), None)
        if battle_i is None: battle_i = next(i for i in range(len(lines)) if st(i) >= 0.5 * D); why.append('battle: fallback at half way')
    # turn: the line after the battle starts that best matches a decisive moment, weighted to 0.6..0.8 of the film
    turn_i = line('turn_line')
    if turn_i is None:
        best, bs = None, -1
        for i in range(battle_i + 1, len(lines)):
            f = st(i) / D
            if f > 0.9: break
            s = len(TURN_RE.findall(lines[i]['text'])) + (1.0 if 0.58 <= f <= 0.82 else 0)
            if s > bs: best, bs = i, s
        turn_i = best if best is not None else min(len(lines) - 2, battle_i + 3)
    # result: first line at least 8 s after the turn that reads like an outcome
    result_i = line('result_line')
    if result_i is None:
        result_i = next((i for i in range(turn_i + 1, len(lines)) if st(i) >= st(turn_i) + 8.0 and RESULT_RE.search(lines[i]['text'])), None)
        if result_i is None: result_i = next((i for i in range(turn_i + 1, len(lines)) if st(i) >= st(turn_i) + 12.0), len(lines) - 1)
    epi_i = line('epilogue_line')
    if epi_i is None:
        epi_i = next((i for i in range(result_i + 1, len(lines)) if st(i) >= 0.78 * D and EPILOGUE_RE.search(lines[i]['text'])), None)
        if epi_i is None: epi_i = next((i for i in range(result_i + 1, len(lines)) if st(i) >= 0.8 * D), None)
    plan_i = line('plan_line')
    if plan_i is None:
        plan_i = next((i for i in range(title_i + 2, battle_i) if PLAN_RE.search(lines[i]['text']) and st(i) > 0.3 * D and st(battle_i) - st(i) >= 12.0), None)
    result_mood = hints.get('result_mood') or ('triumph' if WIN_RE.search(' '.join(l['text'] for l in lines[result_i:])) else 'aftermath')

    secs = [{'t': 0.0, 'mood': 'calm'}]
    if title_i + 1 < len(lines): secs.append({'t': round(st(title_i + 1), 3), 'mood': 'curious'})
    if plan_i is not None and plan_i > title_i + 1: secs.append({'t': round(st(plan_i), 3), 'mood': 'curious', 'intensity': 0.46})
    secs.append({'t': round(st(battle_i), 3), 'mood': 'tension'})
    secs.append({'t': round(st(turn_i), 3), 'mood': 'turn'})
    secs.append({'t': round(st(result_i), 3), 'mood': result_mood})
    if epi_i is not None: secs.append({'t': round(st(epi_i), 3), 'mood': 'aftermath'})
    for ex in hints.get('extra', []):
        if ex['line'] in by_id: secs.append({'t': round(st(by_id[ex['line']]), 3), 'mood': ex['mood'], **({'intensity': ex['intensity']} if 'intensity' in ex else {})})
    secs.sort(key=lambda s: s['t'])
    hits = [{'t': round(st(title_i) - 0.3, 3), 'kind': 'low', 'level': 0.4}, {'t': round(st(turn_i) - 0.3, 3), 'kind': 'low', 'level': 1.0}]
    if result_mood == 'triumph': hits.append({'t': round(st(result_i) + 0.4, 3), 'kind': 'chime', 'level': 0.8})
    plan = {'palette': pal, 'key': key, 'mode': mode, 'duration': round(D, 3), 'seed': seed, 'sections': secs, 'hits': hits,
            'voice': [[round(l['start'], 3), round(l['end'], 3)] for l in lines],
            'story': {'title_line': lines[title_i]['id'], 'battle_line': lines[battle_i]['id'], 'turn_line': lines[turn_i]['id'], 'result_line': lines[result_i]['id'],
                      'epilogue_line': lines[epi_i]['id'] if epi_i is not None else None, 'plan_line': lines[plan_i]['id'] if plan_i is not None else None,
                      'year': year, 'place_scores': sc, 'notes': why}}
    for k in ('tempo', 'solo', 'drums', 'swell_len', 'settle'):
        if k in hints: plan[k] = hints[k]
    return plan


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('film_dir'); ap.add_argument('-o', '--out')
    a = ap.parse_args(); plan = build(a.film_dir)
    s = json.dumps(plan, indent=1)
    if a.out: open(a.out, 'w').write(s); print('wrote', a.out)
    st = plan['story']; print(f"{plan['palette']} {plan['key']} {plan['mode']}  title {st['title_line']}  battle {st['battle_line']}  turn {st['turn_line']}  result {st['result_line']} ({[x['mood'] for x in plan['sections']][-2]})  epilogue {st['epilogue_line']}")
    for x in plan['sections']: print('  ', x)


if __name__ == '__main__':
    main()
