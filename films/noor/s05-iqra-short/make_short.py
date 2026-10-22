#!/usr/bin/env python3
"""make_short.py: the 9:16 short is cut from the Iqra film's own mix (no new narration, nothing paid).

    python3 films/noor/s05-iqra-short/make_short.py            # writes cues.json, film.json, audio/mix.m4a here

Three pieces of films/noor/n05-iqra/audio/mix.m4a are joined with 0.3 s fades: the word (line e3), the first words and the
five verses (e7 to v5), and their meaning (m1, m2). cues.json keeps those lines with times shifted to the short's timeline.
"""
import os, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(HERE, '..', 'n05-iqra')
c = json.load(open(os.path.join(SRC, 'cues.json'))); L = {l['id']: l for l in c['lines']}
SEGS = [('word', 'e3', 'e3', 0.35, 0.7), ('verses', 'e7', 'v5', 0.3, 1.3), ('meaning', 'm1', 'm2', 0.3, 1.6)]
LEAD = 1.0   # silence at the head: the hook title lands first
t = LEAD; lines = []; parts = []; segs = []
for name, a, b, pre, post in SEGS:
    s0 = L[a]['start'] - pre; s1 = L[b]['end'] + post; ids = [l['id'] for l in c['lines'] if L[a]['start'] <= l['start'] <= L[b]['start']]
    for i in ids:
        l = dict(L[i]); d = t - s0; l['start'] = round(l['start'] + d, 3); l['end'] = round(l['end'] + d, 3); l['words'] = [[w, round(x + d, 3), round(y + d, 3)] for w, x, y in l['words']]; lines.append(l)
    segs.append({'name': name, 't0': round(t, 3), 't1': round(t + s1 - s0, 3), 'src': [round(s0, 3), round(s1, 3)]}); parts.append((s0, s1)); t += s1 - s0
D = round(t + 0.4, 3)
cues = {'id': 'noor-descent-05-iqra-short', 'series': 'NOOR', 'title': 'Iqra', 'duration': D, 'lines': lines, 'segments': segs, 'arabic': c['arabic'], 'fps': 24, 'audio': 'audio/mix.m4a',
        'marks': {'hook': [0.0, LEAD + 2.4]}, 'audio_note': 'Excerpts of films/noor/n05-iqra/audio/mix.m4a, joined by make_short.py.'}
json.dump(cues, open(os.path.join(HERE, 'cues.json'), 'w'), indent=1, ensure_ascii=False)
json.dump({'id': cues['id'], 'series': 'NOOR', 'title': 'Iqra (short)', 'duration': D, 'fps': 24, 'audio': 'audio/mix.m4a', 'render_w': 720, 'render_h': 1280, 'w': 1080, 'h': 1920, 'style': 'lantern-road'}, open(os.path.join(HERE, 'film.json'), 'w'), indent=1)
mix = os.path.join(SRC, 'audio', 'mix.m4a')
if os.path.exists(mix):
    os.makedirs(os.path.join(HERE, 'audio'), exist_ok=True); f = []
    for k, (a, b) in enumerate(parts):
        f.append(f'[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.3,afade=t=out:st={b - a - 0.3:.3f}:d=0.3[p{k}]')
    f.append(f'anullsrc=r=48000:cl=stereo,atrim=0:{LEAD}[s]'); f.append('[s]' + ''.join(f'[p{k}]' for k in range(len(parts))) + f'concat=n={len(parts) + 1}:v=0:a=1,apad=pad_dur=0.4[o]')
    subprocess.run(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-i', mix, '-filter_complex', ';'.join(f), '-map', '[o]', '-t', f'{D:.3f}', '-ar', '48000', '-c:a', 'aac', '-b:a', '256k', os.path.join(HERE, 'audio', 'mix.m4a')], check=True)
print(f'short: {D:.1f} s, segments {[(s["name"], s["t0"], s["t1"]) for s in segs]}' + ('' if os.path.exists(mix) else ' (no source mix yet: cues only)'))
