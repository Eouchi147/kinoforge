#!/usr/bin/env python3
"""Music for the drainage sample ad: a light, warm 15 s cue from the free score engine (films/lib/score/score.py).

    SCORE_SAMPLES=<folder with Strings/ and Woodwinds/ of VSCO-2 CE (CC0)> python3 films/cutaway/ads/drainage/music.py

The engine plans long films (its tonic resolve sits 11 s before the end), so the plan in score_plan.json is 22.5 s long:
that puts the lift chord on 6.5 s (the fix starts), the swell peak at about 8 s and the tonic resolve with a harp chime on
11.5 s (the sun). This script keeps 0 to 15 s, lets the tonic ring and fades it out over the last 2.4 s (a clean ending),
loudness-normalises to -14 LUFS integrated (peak held under -2 dBFS) and writes audio/mix.m4a (AAC 256 kbit/s) into
both delivery folders (v916, v169), plus audio/score.json with the numbers. Free: numpy, scipy, soundfile, ffmpeg.
"""
import json, os, subprocess, sys, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '../../../..'))
sys.path.insert(0, os.path.join(ROOT, 'films/lib/score'))
import score, dsp  # noqa: E402
from dsp import SR  # noqa: E402

LEN, FADE, LUFS = 15.0, 2.4, -14.0

def main():
    plan = json.load(open(os.path.join(HERE, 'score_plan.json')))
    y, info = score.render_plan(plan, 'auto', -23.0, log=lambda *a: print('  ', *a, flush=True))
    n = int(LEN * SR); y = y[:n].copy()
    nf = int(FADE * SR); y[-nf:] *= (np.cos(np.linspace(0, np.pi / 2, nf)) ** 2)[:, None]
    y0 = y; y, meas = score.finalise(y0, LUFS, -2.0)
    y, meas = score.finalise(y0, 2 * LUFS - meas['lufs'], -2.0)              # the limiter costs a little: aim once more
    nz = int(0.02 * SR); y[-nz:] = 0.0                                            # true silence on the last frame
    import soundfile as sf
    with tempfile.TemporaryDirectory() as td:
        wav = os.path.join(td, 'mix.wav'); sf.write(wav, y, SR, subtype='PCM_24')
        for v in ('v916', 'v169'):
            out = os.path.join(HERE, v, 'audio'); os.makedirs(out, exist_ok=True)
            subprocess.run(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-i', wav, '-c:a', 'aac', '-b:a', '256k', '-ar', '48000',
                            '-movflags', '+faststart', os.path.join(out, 'mix.m4a')], check=True)
            rep = {'what': 'drainage sample ad music: score engine cue, 0 to 15 s of a 22.5 s plan, end fade 2.4 s',
                   'engine': info['engine'], 'lufs': meas['lufs'], 'peak_dbfs': meas['peak_dbfs'], 'seconds': LEN,
                   'chords': info['chords'], 'hits': info['hits'], 'plan': '../../score_plan.json'}
            json.dump(rep, open(os.path.join(out, 'score.json'), 'w'), indent=1)
    print('mix:', meas, 'chords', info['chords'])

if __name__ == '__main__':
    main()
