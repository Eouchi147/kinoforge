#!/usr/bin/env python3
"""remix.py: re-score a Battle Map film with the procedural score engine, narration untouched.

    python3 films/lib/score/remix.py films/battles/cannae [--engine auto|synth] [--keep-plan] [--no-encode]

Keeps what the picture follows: cues.json (line starts) and audio/vo/line*.mp3 are read, never written.
Writes in <film>/audio/:
    score_plan.json  the plan built from the film's story (edit it and re-run with --keep-plan to steer by hand)
    score.json       what was made: palette, key, chords, hits, drum beats, intensity curves, loudness checks
    score.wav        the score alone, stereo 48 kHz (not committed: *.wav is ignored; it is rebuilt in seconds-to-minutes)
    mix.m4a          narration on top, score ducked under it, -14 LUFS integrated, end fade (AAC 256k)
    mix_lyria.m4a    the previous mix, kept once (never overwritten by later runs)
"""
import os, sys, json, shutil, subprocess, argparse, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import dsp, score, plan_from_cues
from dsp import SR, db

TARGET_LUFS = -14.0
CEILING_DB = -2.0          # sample-peak ceiling before AAC, so the encoded file stays under -1.5 dBTP
SCORE_BELOW_VOICE_DB = 11.0  # in the pauses, the score (unducked) sits this far below the narration's loudness
DUCK_DB = 7.0              # and dips a further this much while the voice speaks: about 18 dB under the voice
END_FADE = 2.4


def decode(path, sr=SR):
    raw = subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-i', path, '-f', 'f32le', '-ac', '2', '-ar', str(sr), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)


def voice_track(film_dir, cues, D):
    n = int(D * SR); v = np.zeros((n, 2), np.float32); spans = []
    for l in cues['lines']:
        x = decode(os.path.join(film_dir, l['file'])); i = int(round(l['start'] * SR)); m = min(len(x), n - i)
        if m > 0: v[i:i + m] += x[:m]
        spans.append((l['start'], l['start'] + len(x) / SR))
    return v, spans


def duck_curve(voice, depth_db, sr=SR, thresh_db=-46.0, hold=0.28, attack=0.10, release=0.65):
    """gain (linear, 1 = untouched) that dips under speech: speech is found from the voice's own level, bridged across
    word gaps (hold), eased in over `attack` and out over `release`, so the bed breathes instead of pumping"""
    hop = int(0.01 * sr); n = len(voice) // hop
    e = np.sqrt((voice[: n * hop].reshape(n, hop, 2) ** 2).mean(axis=(1, 2)))
    act = (20 * np.log10(e + 1e-9) > thresh_db).astype(np.float32)
    from scipy.ndimage import maximum_filter1d
    act = maximum_filter1d(act, size=int(hold / 0.01) * 2 + 1)
    a_c = np.exp(-0.01 / attack); r_c = np.exp(-0.01 / release); y = np.empty(n, np.float32); cur = 0.0
    for i in range(n):
        c = a_c if act[i] > cur else r_c
        cur = c * cur + (1 - c) * act[i]; y[i] = cur
    g = 10 ** (-depth_db * y / 20.0)
    t = np.arange(len(voice)) / sr
    return np.interp(t, (np.arange(n) + 0.5) * 0.01, g).astype(np.float32), y


def mix_film(film_dir, engine='auto', keep_plan=False, encode=True, log=print):
    film_dir = film_dir.rstrip('/'); A = os.path.join(film_dir, 'audio')
    cues = json.load(open(os.path.join(film_dir, 'cues.json'))); D = float(cues['duration'])
    plan_path = os.path.join(A, 'score_plan.json')
    if keep_plan and os.path.exists(plan_path): plan = json.load(open(plan_path))
    else: plan = plan_from_cues.build(film_dir); json.dump(plan, open(plan_path, 'w'), indent=1)
    t0 = time.time()
    sc, info = score.render_plan(plan, engine, -23.0, log=log)
    import soundfile as sf
    sf.write(os.path.join(A, 'score.wav'), sc, SR, subtype='PCM_24')
    log(f'score: {info["engine"]}, {info["lufs"]} LUFS, peak {info["peak_dbfs"]} dBFS ({time.time() - t0:.0f} s)')
    # narration on the film's own timeline
    voice, spans = voice_track(film_dir, cues, D)
    n = int(D * SR); sc = sc[:n] if len(sc) >= n else np.pad(sc, ((0, n - len(sc)), (0, 0)))
    v_lufs = dsp.loudness(voice)
    g_duck, act = duck_curve(voice, DUCK_DB)
    base = db(v_lufs - SCORE_BELOW_VOICE_DB - info['lufs'])             # score level relative to the narration
    music = sc * base * g_duck[:, None]
    mix = voice + music
    # end fade of the whole mix (the score has already faded), then loudness and peaks
    nf = int(END_FADE * SR); mix[-nf:] *= (np.cos(np.linspace(0, np.pi / 2, nf)) ** 2)[:, None]
    lu = dsp.loudness(mix); mix = mix * db(TARGET_LUFS - lu)
    mix = dsp.limiter(mix, CEILING_DB)
    lu2 = dsp.loudness(mix)
    if abs(lu2 - TARGET_LUFS) > 0.3:                                      # the limiter took some level: top up once, limit again
        mix = dsp.limiter(mix * db(TARGET_LUFS - lu2), CEILING_DB); lu2 = dsp.loudness(mix)
    gain_total = base * db(TARGET_LUFS - lu)
    # checks: loudness of voice and of the score while the voice speaks (aligned frames), per section
    speak = act > 0.5; hop = int(0.01 * SR); m_e = (music[: len(act) * hop].reshape(len(act), hop, 2) ** 2).mean(axis=(1, 2))
    v_e = (voice[: len(act) * hop].reshape(len(act), hop, 2) ** 2).mean(axis=(1, 2))
    vs = float(10 * np.log10(v_e[speak].mean() + 1e-12)); ms = float(10 * np.log10(m_e[speak].mean() + 1e-12))
    rows = []; secs = score.normalise_plan(plan)['sections']
    for s in secs:
        a, b = int(s['t'] * 100), int(min(s['t1'], D) * 100); sp = speak[a:b]
        if sp.sum() > 100:
            rows.append({'t': round(s['t'], 1), 'mood': s['mood'], 'voice_over_music_db': round(float(10 * np.log10(v_e[a:b][sp].mean() / (m_e[a:b][sp].mean() + 1e-12))), 1)})
    chk = {'voice_lufs_before': round(v_lufs, 1), 'mix_lufs': round(lu2, 2), 'mix_peak_dbfs': round(float(dsp.lin2db(np.abs(mix).max())), 2),
           'voice_over_score_while_speaking_db': round(vs - ms, 1), 'by_section': rows, 'clipped_samples': int((np.abs(mix) >= 0.999).sum())}
    log('mix:', {k: v for k, v in chk.items() if k != 'by_section'})
    out = os.path.join(A, 'mix.m4a'); old = os.path.join(A, 'mix_lyria.m4a')
    if encode:
        if os.path.exists(out) and not os.path.exists(old): shutil.copy2(out, old)
        tmp = os.path.join(A, '_mix_tmp.wav'); tmp_m4a = os.path.join(A, '_mix_tmp.m4a'); sf.write(tmp, mix, SR, subtype='PCM_24')
        subprocess.run(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-i', tmp, '-c:a', 'aac', '-b:a', '256k', '-t', f'{D:.3f}', tmp_m4a], check=True)
        os.remove(tmp); os.replace(tmp_m4a, out)                       # atomic: a half-written mix.m4a is never visible
    meta = {k: v for k, v in info.items() if k not in ('plan',)}
    meta.update({'film': cues.get('id'), 'duration': D, 'palette': plan['palette'], 'key': plan['key'], 'story': plan.get('story'), 'sections': secs,
                 'mix': chk, 'narration_untouched': True, 'note': 'Generated by films/lib/score/remix.py; deterministic for the same plan, seed and engine.'})
    json.dump(meta, open(os.path.join(A, '_score.json.tmp'), 'w'), indent=1); os.replace(os.path.join(A, '_score.json.tmp'), os.path.join(A, 'score.json'))
    return meta


def main():
    ap = argparse.ArgumentParser(description='re-score a Battle Map film (narration timing untouched)')
    ap.add_argument('film_dir'); ap.add_argument('--engine', default='auto', choices=['auto', 'synth', 'samples'])
    ap.add_argument('--keep-plan', action='store_true', help='use the existing audio/score_plan.json instead of rebuilding it')
    ap.add_argument('--no-encode', action='store_true')
    a = ap.parse_args(); t = time.time()
    m = mix_film(a.film_dir, a.engine, a.keep_plan, not a.no_encode, log=lambda *x: print('  ', *x, flush=True))
    print(f"{a.film_dir}: {m['palette']} {m['key']} {m['mode']}, mix {m['mix']['mix_lufs']} LUFS, peak {m['mix']['mix_peak_dbfs']} dBFS, voice over score {m['mix']['voice_over_score_while_speaking_db']} dB, {time.time() - t:.0f} s")


if __name__ == '__main__':
    main()
