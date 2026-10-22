#!/usr/bin/env python3
"""cues_from_score.py: make a film's cues.json describe the NEW score, so picture and music agree.

    python3 films/lib/score/cues_from_score.py films/battles/cannae [--dry]

Rewrites only the music fields of <film>/cues.json: bpm, beats, downbeats, strong_hits, energy_hop_s, energy and note.
Every narration field (id, title, duration, outro_s, title_line, lines with starts, ends and word times, audio) is left
exactly as it was, and the script refuses to write if any of them would change.

  strong_hits  onset-strength peaks of audio/score.wav (the top 4 percent, as battle_mix.py did for the old music), plus
               the plan's hits (the title and the turn): the moments the picture can cut or pulse on
  beats        the hand-drum pulse where the drums actually play (the score is in free time elsewhere, so there is no
               grid to claim before the battle starts); downbeats are every fourth beat
  energy       RMS of the score every 0.1 s, scaled to its maximum
"""
import os, sys, json, argparse
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
KEEP = ('id', 'title', 'duration', 'outro_s', 'title_line', 'lines', 'audio')


def build(film_dir):
    import soundfile as sf, librosa
    A = os.path.join(film_dir, 'audio'); raw = open(os.path.join(film_dir, 'cues.json'), encoding='utf-8').read(); cues = json.loads(raw)
    meta = json.load(open(os.path.join(A, 'score.json'))); dur = float(cues['duration'])
    x, sr0 = sf.read(os.path.join(A, 'score.wav'), dtype='float32', always_2d=True)
    y = librosa.resample(x.mean(axis=1)[: int(dur * sr0)], orig_sr=sr0, target_sr=22050)
    env = librosa.onset.onset_strength(y=y, sr=22050); fr = librosa.onset.onset_detect(onset_envelope=env, sr=22050)
    hits = [float(librosa.frames_to_time(f, sr=22050)) for f in fr if env[f] > np.percentile(env, 96)]
    hits += [float(h[0]) for h in meta.get('hits', []) if h[1] in ('low', 'drum')]        # the title and the turn
    hits = sorted(set(round(h, 3) for h in hits if 0 <= h < dur))
    merged = []                                                                               # one hit per 0.25 s at most
    for h in hits:
        if not merged or h - merged[-1] >= 0.25: merged.append(h)
    hop = int(sr0 * 0.1); n = len(x[: int(dur * sr0)]) // hop
    rms = np.sqrt((x[: n * hop].mean(axis=1) ** 2).reshape(n, hop).mean(axis=1))
    perc = meta['curves']['perc']; chz = meta['curve_hz']
    beats = [b for b in meta.get('beats', []) if b < dur and perc[min(len(perc) - 1, int(b * chz))] > 0.05]
    tempo = meta.get('plan', {}).get('tempo') if 'plan' in meta else None
    if tempo is None:
        pl = json.load(open(os.path.join(A, 'score_plan.json'))); import score; tempo = score.normalise_plan(pl)['tempo']
    out = dict(cues)
    out.update({'bpm': float(tempo), 'beats': [round(b, 3) for b in beats], 'downbeats': [round(b, 3) for b in beats[::4]],
                'strong_hits': [round(h, 3) for h in merged], 'energy_hop_s': 0.1,
                'energy': [round(float(v), 3) for v in rms / (rms.max() + 1e-9)],
                'note': 'Narration timing is fixed by the film (lines, starts, words). Music fields (bpm, beats, downbeats, strong_hits, energy) describe '
                        'audio/score.wav from films/lib/score: beats are the hand-drum pulse where drums play; strong_hits include the title and turn hits.'})
    for k in KEEP:
        if out.get(k) != cues.get(k): raise SystemExit(f'refusing: narration field {k} would change')
    return cues, out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('film_dir'); ap.add_argument('--dry', action='store_true'); a = ap.parse_args()
    old, new = build(a.film_dir.rstrip('/'))
    print(a.film_dir, 'beats', len(old['beats']), '->', len(new['beats']), '| strong_hits', len(old['strong_hits']), '->', len(new['strong_hits']), '| bpm', old['bpm'], '->', new['bpm'])
    if not a.dry:
        p = os.path.join(a.film_dir, 'cues.json'); tmp = p + '.tmp'
        json.dump(new, open(tmp, 'w', encoding='utf-8'), indent=1); os.replace(tmp, p)


if __name__ == '__main__':
    main()
