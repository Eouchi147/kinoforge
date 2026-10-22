#!/usr/bin/env python3
"""analyse.py: listen-check by numbers and pictures (no ears needed).

    python3 films/lib/score/analyse.py <audio file> [--info score.json] [--png spectrogram.png] [--voice mix.m4a --score score.wav]

Reports integrated and short-term loudness, peak, clipping, spectral balance (share of energy per band), the loudness
at each section of the plan, and writes a spectrogram with the section boundaries marked.
"""
import os, sys, json, argparse, subprocess
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dsp


def load(path, sr=48000):
    if path.endswith('.wav'):
        import soundfile as sf
        x, r = sf.read(path, dtype='float32', always_2d=True)
        if r != sr: from scipy.signal import resample_poly; x = resample_poly(x, sr, r, axis=0).astype(np.float32)
        return x
    raw = subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-i', path, '-f', 'f32le', '-ac', '2', '-ar', str(sr), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)


BANDS = [('sub <60', 0, 60), ('bass 60-250', 60, 250), ('low-mid 250-800', 250, 800), ('voice 800-3500', 800, 3500), ('presence 3.5-8k', 3500, 8000), ('air >8k', 8000, 24000)]


def band_shares(x, sr=48000):
    m = x.mean(axis=1); n = 1 << int(np.floor(np.log2(min(len(m), sr * 20)))); step = n
    acc = None; cnt = 0
    for s in range(0, len(m) - n + 1, step):
        sp = np.abs(np.fft.rfft(m[s:s + n] * np.hanning(n))) ** 2
        acc = sp if acc is None else acc + sp; cnt += 1
    f = np.fft.rfftfreq(n, 1 / sr); tot = acc.sum() + 1e-12
    return {name: round(float(acc[(f >= lo) & (f < hi)].sum() / tot * 100), 1) for name, lo, hi in BANDS}


def report(x, info=None, sr=48000):
    out = {}
    out['seconds'] = round(len(x) / sr, 2); out['lufs'] = round(dsp.loudness(x), 2)
    out['peak_dbfs'] = round(float(dsp.lin2db(np.abs(x).max())), 2)
    out['clipped_samples'] = int((np.abs(x) >= 0.999).sum())
    st = dsp.short_term(x); out['short_term_lufs_min_max'] = [round(float(st.min()), 1), round(float(st.max()), 1)]
    out['band_energy_pct'] = band_shares(x)
    out['dc_offset'] = round(float(np.abs(x.mean(axis=0)).max()), 6)
    l, r = x[:, 0], x[:, 1]; out['stereo_correlation'] = round(float(np.corrcoef(l[::7], r[::7])[0, 1]), 3)
    if info:
        secs = info['plan']['sections'] if 'plan' in info else info.get('sections', [])
        rows = []
        for s in secs:
            a, b = int(s['t'] * sr), int(min(s['t1'], len(x) / sr) * sr)
            seg = x[a:b]
            if len(seg) > 2 * sr:
                rows.append({'t': round(s['t'], 1), 'mood': s['mood'], 'lufs': round(dsp.loudness(seg), 1), 'peak': round(float(dsp.lin2db(np.abs(seg).max())), 1)})
        out['sections'] = rows
    return out


def spectrogram(x, path, info=None, sr=48000, title=''):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from scipy.signal import spectrogram as spg
    m = x.mean(axis=1)[::2]; f, t, S = spg(m, sr // 2, nperseg=4096, noverlap=3072)
    S = 10 * np.log10(S + 1e-12); S -= S.max()
    fig, ax = plt.subplots(2, 1, figsize=(15, 7), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
    ax[0].pcolormesh(t, f, S, shading='auto', vmin=-90, vmax=-20, cmap='magma'); ax[0].set_yscale('symlog', linthresh=200); ax[0].set_ylim(40, 12000)
    ax[0].set_ylabel('Hz'); ax[0].set_title(title)
    st = dsp.short_term(x, win=3, hop=0.5); ax[1].plot(np.arange(len(st)) * 0.5 + 1.5, st, color='k'); ax[1].set_ylabel('short-term LUFS'); ax[1].grid(alpha=.3)
    if info:
        secs = info['plan']['sections'] if 'plan' in info else info.get('sections', [])
        for s in secs:
            for a in ax: a.axvline(s['t'], color='w' if a is ax[0] else 'r', lw=0.7, alpha=.8)
            ax[0].text(s['t'] + 0.3, 11000, s['mood'], color='w', fontsize=8, va='top')
    ax[1].set_xlabel('seconds'); fig.tight_layout(); fig.savefig(path, dpi=90); plt.close(fig)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('audio'); ap.add_argument('--info'); ap.add_argument('--png'); ap.add_argument('--title', default='')
    a = ap.parse_args(); x = load(a.audio); info = json.load(open(a.info)) if a.info else None
    print(json.dumps(report(x, info), indent=1))
    if a.png: spectrogram(x, a.png, info, title=a.title or os.path.basename(a.audio)); print('spectrogram:', a.png)


if __name__ == '__main__':
    main()
