#!/usr/bin/env python3
"""place.py: NOOR films. Narration takes (audio/vo.json from voice_free.py) placed on the film's own timeline.

    python3 films/noor/lib/place.py films/noor/<film>            # writes cues.json, film.json, audio/score_plan.json
    python3 films/noor/lib/place.py films/noor/<film> --prep     # only writes ad.json (the lines the voice reads)

script.json holds the display text (`text`, shown on screen) and, where a name needs help, the spoken text (`say`, read
by the open voice). Each line has a `gap` (seconds of silence after it) and a `sec` (score mood for the section).
A line with `after: "title"` leaves its gap for the title card. Lines with `hit` add a score hit just before them.
Nothing here is paid: the voice is Chatterbox on the runner, the score the free procedural engine (films/lib/score).
"""
import os, sys, json


def prep(d):
    s = json.load(open(os.path.join(d, 'script.json')))
    ad = {'id': s['id'], 'prep': {'voice': s.get('voice', 'chatterbox'),
                                  'voice_settings': s.get('voice_settings', {'exaggeration': 0.5, 'cfg': 0.35, 'temperature': 0.7}),
                                  'vo': [{'id': l['id'], 'text': l.get('say', l['text'])} for l in s['lines']]}}
    json.dump(ad, open(os.path.join(d, 'ad.json'), 'w'), indent=1, ensure_ascii=False)
    print(f'{d}: ad.json with {len(ad["prep"]["vo"])} lines')


def place(d):
    s = json.load(open(os.path.join(d, 'script.json'))); vo = json.load(open(os.path.join(d, 'audio', 'vo.json')))
    if len(vo['lines']) != len(s['lines']): raise SystemExit(f'{len(vo["lines"])} takes for {len(s["lines"])} lines')
    t = float(s.get('lead_in', 1.0)); lines = []; marks = {}; hits = []; sections = []
    for l, v in zip(s['lines'], vo['lines']):
        start = round(t, 3); dur = float(v['dur'])
        words = [[w, round(a + start, 3), round(b + start, 3)] for w, a, b in v['words']]
        row = {'id': l['id'], 'text': l['text'], 'say': l.get('say', l['text']), 'start': start, 'end': round(start + dur, 3),
               'file': v['file'], 'words': words, 'sec': l.get('sec', 'calm'), 'wer': v.get('wer')}
        if 'verse' in l: row['verse'] = l['verse']
        lines.append(row)
        if not sections or sections[-1]['mood'] != row['sec']: sections.append({'t': max(0.0, round(start - 1.2, 2)), 'mood': row['sec']})
        if l.get('hit'): hits.append({'t': round(max(0.0, start - 0.35), 2), 'kind': l['hit'], 'level': 0.55 if l['hit'] == 'swell' else 0.45})
        t = start + dur
        if l.get('after') == 'title': marks['title'] = [round(t + 0.6, 3), round(t + float(l['gap']) - 0.4, 3)]
        t += float(l.get('gap', 0.7))
    D = round(lines[-1]['end'] + float(s.get('tail', 6.0)), 3)
    marks['end'] = [round(lines[-1]['end'] + 0.8, 3), D]
    cues = {'id': s['id'], 'series': s['series'], 'strand': s['strand'], 'night': s.get('night'), 'title': s['title'],
            'title_sub': s.get('title_sub'), 'duration': D, 'end_card_s': round(D - marks['end'][0], 3), 'lines': lines, 'marks': marks,
            'strong_hits': [h['t'] + 0.35 for h in hits], 'fps': 24, 'audio': 'audio/mix.m4a', 'arabic': s.get('arabic', {}),
            'voice': vo.get('voice'), 'audio_note': 'Narration placed by films/noor/lib/place.py; picture follows these times.'}
    json.dump(cues, open(os.path.join(d, 'cues.json'), 'w'), indent=1, ensure_ascii=False)
    sc = dict(s.get('score', {})); sc.update({'duration': D, 'sections': sections, 'hits': hits,
                                               'voice': [[l['start'], l['end']] for l in lines], 'swell_len': 6.0, 'settle': 8.0, 'end_fade': 4.0})
    sc.setdefault('palette', 'middle_east_central_asia')
    json.dump(sc, open(os.path.join(d, 'audio', 'score_plan.json'), 'w'), indent=1)
    fp = os.path.join(d, 'film.json'); film = json.load(open(fp)) if os.path.exists(fp) else {}
    film.update({'id': s['id'], 'series': s['series'], 'title': s['title'], 'duration': D, 'fps': 24, 'audio': 'audio/mix.m4a'})
    for k, v in (('render_w', 1280), ('render_h', 720), ('w', 1920), ('h', 1080), ('style', 'lantern-road')): film.setdefault(k, v)
    json.dump(film, open(fp, 'w'), indent=1)
    bad = [l['id'] for l in lines if (l['wer'] or 0) > 0.2]
    print(f'{d}: {len(lines)} lines, {D:.1f} s, title {marks.get("title")}, sections {[x["mood"] for x in sections]}' + (f'; check these takes: {bad}' if bad else ''))


if __name__ == '__main__':
    d = sys.argv[1].rstrip('/')
    prep(d) if '--prep' in sys.argv else place(d)
