"""pad.py: a quiet placeholder score, made in code (free), used only when the procedural score engine is not there yet.

    python3 films/director/pad.py <out.mp3> <seconds> [--bpm 96] [--mood warm|dark]

A warm sustained chord pad (four chords, two bars each), a soft low pulse on every beat and a light pluck on the
downbeats, so the mix has a beat grid to lay the narration on. Deterministic. Not a finished score: the hook in
config.json (music_engines.procedural) replaces it when the engine exists.
"""
import sys, subprocess, numpy as np

SR = 48000


def tone(f, n, harm=(1, .5, .25, .12)):
    t = np.arange(n) / SR
    return sum(a * np.sin(2 * np.pi * f * h * t + h) for h, a in enumerate(harm, 1))


def make(out, seconds, bpm=96, mood='warm'):
    beat = 60 / bpm; bar = 4 * beat; n = int(seconds * SR); x = np.zeros((n, 2))
    prog = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 55, 60, 64], [55, 59, 62, 67]] if mood == 'warm' else [[45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 58], [40, 47, 52, 56]]
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    seg = int(2 * bar * SR); fade = int(0.6 * SR)
    for k, s0 in enumerate(range(0, n, seg)):
        L = min(seg + fade, n - s0); env = np.ones(L); f = max(1, min(fade, L // 2)); env[:f] = np.linspace(0, 1, f); env[-f:] *= np.linspace(1, 0, f)
        ch = sum(tone(hz(m), L) for m in prog[k % 4]) * env * 0.035
        x[s0:s0 + L, 0] += ch * (1 + 0.15 * np.sin(np.arange(L) / SR * 0.7)); x[s0:s0 + L, 1] += ch * (1 + 0.15 * np.cos(np.arange(L) / SR * 0.6))
    nb = int(seconds / beat)
    for b in range(nb):
        s0 = int(b * beat * SR); L = min(int(0.35 * SR), n - s0)
        if L <= 0: break
        e = np.exp(-np.arange(L) / SR * 14); kick = np.sin(2 * np.pi * (52 + 40 * e) * np.arange(L) / SR) * e * (0.16 if b % 4 == 0 else 0.08)
        x[s0:s0 + L] += kick[:, None]
        if b % 4 == 0:
            m = prog[(b // 8) % 4][(b // 4) % 4] + 12; Lp = min(int(0.8 * SR), n - s0); pe = np.exp(-np.arange(Lp) / SR * 5)
            p = tone(hz(m), Lp, (1, .3, .1)) * pe * 0.05; x[s0:s0 + Lp, 0] += p * 0.8; x[s0:s0 + Lp, 1] += p
    x[-int(2 * SR):] *= np.linspace(1, 0, int(2 * SR))[:, None]
    x = x / (np.abs(x).max() + 1e-9) * 0.5
    pcm = (x * 32767).astype('<i2').tobytes()
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', '-b:a', '192k', out], input=pcm, check=True)
    return out


if __name__ == '__main__':
    a = sys.argv[1:]; bpm = float(a[a.index('--bpm') + 1]) if '--bpm' in a else 96; mood = a[a.index('--mood') + 1] if '--mood' in a else 'warm'
    make(a[0], float(a[1]), bpm, mood)
