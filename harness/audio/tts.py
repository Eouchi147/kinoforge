"""Narration & dialogue: Kokoro-82M (ONNX, CPU) + Rhubarb lip-sync visemes.

    from tts import say, visemes
    wav, dur = say("Three weeks. In the mirror.", voice='am_adam', speed=1.0, out='line1.wav')
    cues = visemes('line1.wav')      # [(t_seconds, 'A'|'B'|'C'|'D'|'E'|'F'|'G'|'H'|'X'), ...]  (Rhubarb mouth shapes)

Model files: $KOKORO_DIR (default /home/claude/vp/tools/kokoro) must hold kokoro-v1.0.onnx and voices-v1.0.bin
(from https://github.com/thewh1teagle/kokoro-onnx/releases). Rhubarb binary: $RHUBARB (default under /home/claude/vp/tools/rhubarb).
Voices (American/British English): af_heart, af_bella, af_nicole, af_sarah, af_sky, am_adam, am_michael, am_echo, am_eric, am_liam, am_onyx,
bf_emma, bf_isabella, bm_george, bm_lewis, bm_daniel, bm_fable. Speed 0.8–1.2. Prosody tip (R-9-13): split lines into clauses, vary speed per clause, keep breaths as short pauses.
"""
import os, glob, json, subprocess
import numpy as np
import soundfile as sf

KOKORO_DIR = os.environ.get('KOKORO_DIR', '/home/claude/vp/tools/kokoro')
_k = None
def _kokoro():
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        _k = Kokoro(os.path.join(KOKORO_DIR, 'kokoro-v1.0.onnx'), os.path.join(KOKORO_DIR, 'voices-v1.0.bin'))
    return _k

def say(text, voice='af_heart', speed=1.0, lang='en-us', out=None, pause_after=0.0, sr_out=48000):
    """Returns (float32 mono at 48 kHz, duration). Writes a wav if `out` is given."""
    k = _kokoro(); samples, sr = k.create(text, voice=voice, speed=speed, lang=lang)
    x = np.asarray(samples, dtype=np.float32)
    if sr != sr_out:
        from scipy.signal import resample_poly
        from math import gcd
        g = gcd(sr_out, sr); x = resample_poly(x, sr_out // g, sr // g).astype(np.float32)
    if pause_after: x = np.concatenate([x, np.zeros(int(pause_after * sr_out), dtype=np.float32)])
    x = x / (np.max(np.abs(x)) + 1e-6) * 0.7
    if out: sf.write(out, x, sr_out, subtype='PCM_16')
    return x, len(x) / sr_out

def rhubarb_bin():
    b = os.environ.get('RHUBARB')
    if b and os.path.exists(b): return b
    c = glob.glob('/home/claude/vp/tools/rhubarb/**/rhubarb', recursive=True) + glob.glob(os.path.expanduser('~/rhubarb/**/rhubarb'), recursive=True)
    if not c: raise FileNotFoundError('rhubarb binary not found; set RHUBARB')
    return c[0]

def visemes(wav_path, text=None):
    """Run Rhubarb (phonetic recogniser, no PocketSphinx data needed) -> list of (time, shape). Shapes: A closed (M/B/P), B slightly open (consonants), C open (E/AE), D wide open (A/AH), E rounded (O), F puckered (U/W), G F/V, H L, X rest."""
    args = [rhubarb_bin(), '-f', 'json', '-r', 'phonetic', '--machineReadable']
    if text:
        tp = wav_path + '.txt'; open(tp, 'w').write(text); args += ['-d', tp]
    r = subprocess.run(args + [wav_path], capture_output=True, text=True);
    if r.returncode != 0: raise RuntimeError(r.stderr[-800:])
    j = json.loads(r.stdout); return [(c['start'], c['value']) for c in j['mouthCues']]

def viseme_at(cues, t):
    s = 'X'
    for st, v in cues:
        if t >= st: s = v
        else: break
    return s
