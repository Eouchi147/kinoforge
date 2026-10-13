#!/usr/bin/env python3
"""P08 TWO CHAIRS — dialogue build: Kokoro TTS -> trimmed line wavs -> Rhubarb visemes + word times -> cue times -> lines/cues.json.

    python3 proto/p08-two-chairs/build_lines.py            # synthesise + analyse + write cues.json
    python3 proto/p08-two-chairs/build_lines.py --cues     # re-time only (keeps the existing wavs / rhubarb data)

Needs the Kokoro model ($KOKORO_DIR) and the Rhubarb binary (see harness/audio/tts.py). The wavs it writes are the
dialogue stems that audio.py places; scene.js fetches lines/cues.json (one source of truth for picture AND sound).
"""
import sys, os, json, math, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'harness', 'audio'))
import numpy as np
import soundfile as sf

FPS = 24
TOTAL_F = 12 * FPS             # 288 frames
SR = 48000
HEAD = 0.020                   # pre-roll kept before the detected speech onset (s)
TAIL = 0.080                   # decay kept after the detected offset (s)
LOOKAHEAD = 0.035              # mouth leads the sound by 0..35 ms -> audio never >7 ms early (R-9-14: lead<=15 ms, lag<=45 ms)
BEAT_F = 18                    # R-8-08 beat before the punchline (frames of nothing)
LINES = [
    dict(id='L1', who='remi', text="I rehearsed this speech for three weeks.", voice='am_michael', speed=1.08, nominal=0.6),
    # Kokoro's G2P spells "Mm-hm" out as letter names; feed phonemes instead (ASR check hears "hum hum").
    dict(id='L2', who='bo', text="Mm-hm.", phonemes="əm hˈəm.", voice='bm_george', speed=0.92, nominal=3.1),
    dict(id='L3', who='remi', text="Three weeks. In the mirror. With hand gestures.", voice='am_michael', speed=1.08, nominal=4.0,
         min_pause=0.26, pauses=2),   # comic list rhythm: open the two full stops to >= 0.26 s (Kokoro ran them at 60/240 ms)
    dict(id='L4', who='bo', text="And?", voice='bm_george', speed=0.92, nominal=7.4),
    dict(id='L5', who='remi', text="The mirror said no.", voice='am_michael', speed=1.08, nominal=8.6),
]
LDIR = os.path.join(HERE, 'lines')


def wav_path(L): return os.path.join(LDIR, f"{L['id']}-{L['who']}.wav")


def env_db(x, win=0.010, hop=0.005):
    n, h = int(win * SR), int(hop * SR)
    idx = np.arange(0, max(1, len(x) - n), h)
    e = np.array([np.sqrt(np.mean(x[i:i + n] ** 2) + 1e-12) for i in idx])
    return idx / SR, 20 * np.log10(e + 1e-12)


def synth(L):
    import tts
    k = tts._kokoro()
    if L.get('phonemes'):
        a, sr = k.create(L['phonemes'], voice=L['voice'], speed=L['speed'], lang='en-us', is_phonemes=True)
    else:
        a, sr = k.create(L['text'], voice=L['voice'], speed=L['speed'], lang='en-us')
    x = np.asarray(a, dtype=np.float32)
    if sr != SR:
        from scipy.signal import resample_poly
        g = math.gcd(SR, sr); x = resample_poly(x, SR // g, sr // g).astype(np.float32)
    return x / (np.max(np.abs(x)) + 1e-9) * 0.7


def trim_and_shape(x, min_pause=None, pauses=0):
    t, e = env_db(x); pk = e.max(); thr = pk - 42.0
    on_i = int(np.argmax(e > thr)); off_i = len(e) - 1 - int(np.argmax(e[::-1] > thr))
    on, off = t[on_i], t[off_i] + 0.010
    gaps = []
    # internal pauses (below threshold for >= 40 ms): stop closures and clause boundaries
    below = e < pk - 38.0; i = on_i
    while i < off_i:
        if below[i]:
            j = i
            while j < off_i and below[j]: j += 1
            if t[j] - t[i] >= 0.04: gaps.append([float(t[i]), float(t[j])])
            i = j
        else: i += 1
    if min_pause and gaps:   # open the N longest pauses (= the full stops) by inserting silence at their quietest sample
        pieces, last = [], 0
        for g0, g1 in sorted(sorted(gaps, key=lambda g: g[0] - g[1])[:pauses]):
            add = min_pause - (g1 - g0)
            if add <= 0: continue
            c = int((g0 + g1) / 2 * SR)
            if 240 < c < len(x) - 240: c = c - 240 + int(np.argmin(np.abs(x[c - 240:c + 240])))   # nearest quiet sample
            pieces += [x[last:c], np.zeros(int(add * SR), dtype=np.float32)]; last = c
        pieces.append(x[last:]); x = np.concatenate(pieces)
        return trim_and_shape(x, None)
    a = max(0, int((on - HEAD) * SR)); b = min(len(x), int((off + TAIL) * SR)); y = x[a:b].copy()
    fi, fo = int(0.003 * SR), int(0.025 * SR); y[:fi] *= np.linspace(0, 1, fi); y[-fo:] *= np.linspace(1, 0, fo)
    sh = a / SR
    return y, dict(speech_on=round(on - sh, 4), speech_off=round(off - sh, 4), gaps=[[round(g0 - sh, 3), round(g1 - sh, 3)] for g0, g1 in gaps])


def rhubarb(L, path):
    import tts
    rb = tts.rhubarb_bin(); log = path + '.log'
    args = [rb, '-f', 'json', '-q', '--logFile', log, '--logLevel', 'Debug']
    if L.get('phonemes'): args += ['-r', 'phonetic']          # non-word hum: phonetic recogniser
    else:
        tp = path + '.txt'; open(tp, 'w').write(L['text']); args += ['-r', 'pocketSphinx', '-d', tp]
    r = subprocess.run(args + [path], capture_output=True, text=True)
    if r.returncode != 0: raise RuntimeError(r.stderr[-800:])
    cues = [[c['start'], c['end'], c['value']] for c in json.loads(r.stdout)['mouthCues']]
    words = []
    for line in open(log, encoding='utf-8', errors='ignore'):
        m = re.search(r'##word\[([\d.]+)-([\d.]+)\]: (\S+)', line)
        if m and not m.group(3).startswith('<'): words.append([float(m.group(1)), float(m.group(2)), re.sub(r'\(\d\)$', '', m.group(3))])
    for f in (log, path + '.txt'):
        if os.path.exists(f): os.remove(f)
    return cues, words


def shape_at(cues, tau):
    s = 'X'
    for st, en, v in cues:
        if tau >= st: s = v
        else: break
    return s


def enforce_holds(seq):
    """Every viseme held >= 2 frames. A 1-frame shape first steals a frame from a long (>=3 f) neighbour — preferring
    the PREVIOUS one, so it shows a frame early (picture-before-sound is the safe side, R-9-14) — and only merges away
    when both neighbours are short. A 1-frame B (generic consonant) or X is merged instead, so it never delays the
    next vowel. p/b/m closures (A) are never dropped."""
    seq = list(seq)
    for _ in range(400):
        runs, i = [], 0
        while i < len(seq):
            j = i
            while j < len(seq) and seq[j] == seq[i]: j += 1
            runs.append([i, j - i, seq[i]]); i = j
        ones = [k for k, r in enumerate(runs) if r[1] == 1]
        if not ones: break
        k = ones[0]; s, n, v = runs[k]
        prv = runs[k - 1] if k > 0 else None; nxt = runs[k + 1] if k + 1 < len(runs) else None
        if v == 'X':                       seq[s] = (prv or nxt)[2]
        elif v == 'B' and prv and prv[2] != 'A': seq[s] = prv[2]    # a 1-frame generic consonant is dropped, never delays a vowel
        elif prv and prv[1] >= 3:          seq[s - 1] = v
        elif nxt and nxt[1] >= 3:          seq[s + 1] = v
        elif v == 'A' and prv:             seq[s - 1] = 'A'
        elif v == 'A' and nxt:             seq[s + 1] = 'A'
        else:                              seq[s] = (prv or nxt)[2]
    return ''.join(seq)


def sync_report(lines, tracks):
    """Measured picture-vs-sound offset of every viseme onset (ms; negative = mouth before sound)."""
    rep = []
    for L in lines:
        tr = tracks[L['who']]
        for st, en, v in L['visemes']:
            if v == 'X': continue
            s_abs = L['start'] + st; f_nom = int(round(s_abs * FPS))
            cand = [f for f in range(max(0, f_nom - 3), min(TOTAL_F, f_nom + 4)) if tr[f] == v and (f == 0 or tr[f - 1] != v)]
            if not cand:
                rep.append(dict(line=L['id'], shape=v, t=round(s_abs, 3), offset_ms=None)); continue
            f = min(cand, key=lambda f: abs(f / FPS - s_abs))
            rep.append(dict(line=L['id'], shape=v, t=round(s_abs, 3), frame=f, offset_ms=round((f / FPS - s_abs) * 1000, 1)))
    return rep


def build_tracks(lines):
    tracks = {'remi': ['X'] * TOTAL_F, 'bo': ['X'] * TOTAL_F}
    for L in lines:
        f0 = L['start_frame']; f1 = min(TOTAL_F, int(math.ceil((L['start'] + L['dur']) * FPS)) + 1)
        seq = [shape_at(L['visemes'], i / FPS - L['start'] + LOOKAHEAD) for i in range(f0, f1)]
        seq = enforce_holds(seq)
        for k, s in enumerate(seq): tracks[L['who']][f0 + k] = s
    for w in tracks:  # holds across line joins too
        tracks[w] = enforce_holds(tracks[w])
    return tracks


def compute_cues(lines):
    """Nominal cue times from the brief, shifted so lines never overlap; the punchline sits exactly 18 frames after
    the end of 'And?'. Returns the cue table + the shot table (12.0 s total) derived from it."""
    fr = lambda s: int(round(s * FPS))
    prev_off = -1.0
    for L in lines:
        st = fr(L['nominal'])
        if L['id'] == 'L5':   # R-8-08: >= 18 frames (0.75 s) between the last sound of "And?" and the first of the punchline
            st = int(math.ceil((lines[3]['off'] + BEAT_F / FPS - L['speech_on']) * FPS - 1e-9))
        while prev_off > 0 and (st / FPS + L['speech_on']) < prev_off + 0.12: st += 1   # >= 120 ms turn gap
        L['start_frame'] = st; L['start'] = st / FPS
        L['on'] = round(L['start'] + L['speech_on'], 4); L['off'] = round(L['start'] + L['speech_off'], 4)
        prev_off = L['off']
    l1, l2, l3, l4, l5 = lines
    beat = l5['on'] - l4['off']
    # shots (frame-exact). Cuts land on the first frame of the next speaker's line (deadpan: the cut IS the beat)
    s2 = l2['start_frame']; s3 = l3['start_frame']; s4 = l4['start_frame']; s5 = l5['start_frame']
    s6 = int(math.ceil(l5['off'] * FPS)) + 8          # let the punchline land in the two-shot (8 f after the last syllable)
    s7 = s6 + 12                                      # 12-frame reaction hold on Bo (R-8-08)
    cuts = [0, s2, s3, s4, s5, s6, s7, TOTAL_F]
    names = ['S1 WS two-shot', 'S2 MCU Bo', 'S3 MCU Remi', 'S4 MCU-tight Bo', 'S5 MS two-shot', 'S6 MCU-tight Bo reaction', 'S7 CU Remi deflation']
    shots = [dict(name=n, start_frame=a, frames=b - a, start=round(a / FPS, 4), dur=round((b - a) / FPS, 4)) for n, a, b in zip(names, cuts[:-1], cuts[1:])]
    # events, all tied to the dialogue
    def word(L, w, k=0):
        hits = [x for x in L['words'] if x[2].lower().strip('.,?') == w]
        return L['start'] + hits[k][0] if len(hits) > k else None
    ev = dict(
        beat_s=round(beat, 4), beat_frames=round(beat * FPS, 2),
        creak1=round(l3['start'] + 0.1, 4),                        # Remi's weight shift as he launches the list (brief: 4.1 s)
        creak2=round(l5['start'], 4),                              # his lean-in on the punchline cut (brief: 8.6 s)
        pad_cut=shots[5]['start'],                                 # silence under the reaction
        hand=word(l3, 'hand'), gestures=word(l3, 'gestures'), mirror3=word(l3, 'mirror'), weeks3=word(l3, 'weeks'),
        speech=word(l1, 'speech'), weeks1=word(l1, 'weeks'), for1=word(l1, 'for'), mirror5=word(l5, 'mirror'), no5=word(l5, 'no'),
    )
    return shots, ev


def main():
    os.makedirs(LDIR, exist_ok=True)
    only_cues = '--cues' in sys.argv
    meta_p = os.path.join(LDIR, 'analysis.json')
    if only_cues and os.path.exists(meta_p):
        lines = json.load(open(meta_p))
    else:
        lines = []
        for L in LINES:
            x = synth(L); y, info = trim_and_shape(x, L.get('min_pause'), L.get('pauses', 0))
            p = wav_path(L); sf.write(p, y, SR, subtype='PCM_16')
            cues, words = rhubarb(L, p)
            d = dict(L); d.update(info); d.update(wav='lines/' + os.path.basename(p), dur=round(len(y) / SR, 4), visemes=cues, words=words)
            d['speech_dur'] = round(info['speech_off'] - info['speech_on'], 4)
            lines.append(d); print(f"{L['id']} {L['who']:4s} dur={d['dur']:.3f}s speech={d['speech_dur']:.3f}s gaps={info['gaps']} words={[w[2] for w in words]}")
        json.dump(lines, open(meta_p, 'w'), indent=1, ensure_ascii=False)
    shots, ev = compute_cues(lines)
    tracks = build_tracks(lines)
    rep = sync_report(lines, {k: ''.join(v) for k, v in tracks.items()})
    out = dict(fps=FPS, total_frames=TOTAL_F, duration=TOTAL_F / FPS, lookahead_s=LOOKAHEAD, beat_frames_rule=BEAT_F,
               lines=[{k: L[k] for k in ('id', 'who', 'text', 'voice', 'speed', 'nominal', 'wav', 'start', 'start_frame', 'dur', 'on', 'off',
                                        'speech_dur', 'gaps', 'visemes', 'words')} for L in lines],
               shots=shots, events=ev, mouth={k: ''.join(v) for k, v in tracks.items()}, sync=rep)
    json.dump(out, open(os.path.join(LDIR, 'cues.json'), 'w'), indent=1, ensure_ascii=False)
    print('\nline  start   on      off     speech  (nominal)')
    for L in lines: print(f"{L['id']}   {L['start']:.3f}  {L['on']:.3f}  {L['off']:.3f}  {L['speech_dur']:.3f}  ({L['nominal']})")
    print('\nshots:'); [print(f"  {s['name']:26s} f{s['start_frame']:3d}-{s['start_frame'] + s['frames']:3d}  {s['start']:.3f}s  {s['dur']:.3f}s ({s['frames']} f)") for s in shots]
    print('\nevents:', json.dumps(ev))
    for w, s in out['mouth'].items(): print(w, s)
    offs = [r['offset_ms'] for r in rep if r['offset_ms'] is not None]; lost = [r for r in rep if r['offset_ms'] is None]
    print(f"\nsync: {len(offs)} onsets, picture-vs-sound offset min {min(offs)} ms / max {max(offs)} ms; dropped: {[(r['line'], r['shape'], r['t']) for r in lost]}")
    print('closures (A):', [(r['line'], r['t'], r.get('frame'), r['offset_ms']) for r in rep if r['shape'] == 'A'])


if __name__ == '__main__':
    main()
