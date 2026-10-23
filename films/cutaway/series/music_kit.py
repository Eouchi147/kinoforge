"""Quiet ambient score for the Cutaway showcase series (Sam, 22 Oct 22:54: "ambient, peaceful subtle music ... artistic,
cinema direction, self contained"). Written note by note per film, played by the free score engine's instruments:
VSCO-2 CE samples (CC0) when the sample folder is found ($SCORE_SAMPLES, see films/lib/score/README.md), else its own
synthesis (wavetable pads, Karplus-Strong plucks, breathy winds). Long warm pads, one sparse solo voice for the place,
a hall; the film's make_audio.py writes the chords and the phrase, audio_kit.Mix.music() places it under the nature.

    import music_kit as MK
    s = MK.Score(seed=3)
    s.pad(0.0, 6.0, [50, 57, 62, 66])                  # a chord: MIDI notes, strings by register plus a synth cushion
    s.note('harp', 69, 2.4, ring=3.0, vel=0.45)         # a pluck or a solo note
    y = s.render(env=[(0, -6), (12, 0), (20, -4)])      # stereo, 20 s, with a dB envelope (the swell at the turn)
"""
import os, sys
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'films', 'lib', 'score'))
import dsp, voices  # noqa: E402

SR = dsp.SR
DUR = float(os.environ.get('KF_SOUND_DUR', '20.0'))  # the series films are 20 s; other films set KF_SOUND_DUR
N = int(DUR * SR)
TAIL = int(6 * SR)
FOLDERS = {
    'cello': ['Strings/Cello Section/susvib'], 'viola': ['Strings/Viola Section/susvib'], 'violin': ['Strings/Violin Section/susVib'],
    'bass': ['Strings/Solo Contrabass/SusNV'], 'harp': ['Strings/Harp'], 'pizz': ['Strings/Violin Section/Pizz'],
    'cello_pizz': ['Strings/Cello Section/pizzT'], 'flute': ['Woodwinds/Flute/susvib'], 'clarinet': ['Woodwinds/Clarinet/susLong'],
    'bassoon': ['Woodwinds/Bassoon/sus'], 'solo_violin': ['Strings/Solo Violin/Arco Vib'], 'glock': ['Percussion/Glock'],
}
PLUCKED = {'harp', 'pizz', 'cello_pizz', 'glock'}
SYNTH = {'harp': ('pluck', 'lyre'), 'pizz': ('pluck', 'lute'), 'cello_pizz': ('pluck', 'lute'), 'glock': ('pluck', 'lyre'),
         'dulcimer': ('pluck', 'lute'), 'flute': ('wind', 'flute'), 'clarinet': ('wind', 'reed'), 'bassoon': ('wind', 'reed'), 'solo_violin': ('wind', 'bowed')}
_I = {}


def inst(name):
    if name not in _I:
        s = voices.Sampled(FOLDERS[name], name)
        _I[name] = s if s.ok else None
    return _I[name]


def engine():
    return 'samples (VSCO-2 CE, CC0) + synth' if voices.sample_root() else 'synth only (no sample folder found)'


class Score:
    def __init__(self, seed=1):
        self.rng = np.random.default_rng(seed)
        self.pads = np.zeros((N + TAIL, 2), np.float32)
        self.lead = np.zeros((N + TAIL, 2), np.float32)
        self.used = set()

    def _add(self, bus, x, t, gain_db, pan):
        if x.ndim == 1: x = np.stack([x, x], 1)
        l, r = dsp.pan_gains(pan); i = int(round(t * SR)); m = min(len(x), len(bus) - i)
        if m > 0: bus[i:i + m] += x[:m] * np.array([l, r], np.float32) * 1.414 * dsp.db(gain_db)

    def pad(self, t, dur, notes, vel=0.5, att=2.2, rel=3.0, gain=0.0, cushion=-9.0):
        """A sustained chord: each note on the string section of its register, a synthesised cushion under it."""
        for k, m in enumerate(notes):
            name = 'bass' if m < 40 else 'cello' if m < 55 else 'viola' if m < 67 else 'violin'
            s = inst(name) if not (name == 'bass' and inst('bass') is None) else inst('cello')
            pan = float(self.rng.uniform(-0.35, 0.35))
            if s is not None and s.has(m):
                x = s.note(m, dur, self.rng, vel=vel, attack=att, release=rel, xfade=2.0); self.used.add(name)
                self._add(self.pads, x, t, gain - 1.5 * k / max(1, len(notes) - 1), pan)
                under = gain + cushion
            else:
                under = gain
            y = (voices.synth_bass_note(m, dur, self.rng, attack=att, release=rel, vel=vel) if m < 48 else
                 voices.synth_pad_note(m, dur, self.rng, attack=att, release=rel, vel=vel, voices=4))
            y = y / (np.sqrt((y ** 2).mean()) + 1e-9) * dsp.db(-24) * (0.25 + 0.75 * vel)
            self._add(self.pads, y, t, under, 0.0)

    def note(self, name, midi, t, dur=1.0, ring=3.0, vel=0.5, gain=0.0, pan=0.1, att=0.12, rel=0.8):
        """One note of the solo voice (sustained) or of a plucked voice (rings for `ring` s)."""
        s = inst(name) if name in FOLDERS else None; plucked = name in PLUCKED
        if s is not None and s.has(midi):
            if plucked:
                x = s.note(midi, ring, self.rng, vel=vel, attack=0.003, release=min(1.4, ring * 0.5), pluck=True)
                x = x / (np.abs(x).max() + 1e-9) * dsp.db(-9) * (0.25 + 0.75 * vel)
            else:
                x = s.note(midi, dur, self.rng, vel=vel, attack=att, release=rel, xfade=1.0)
            self.used.add(name)
        else:
            kind, sub = SYNTH.get(name, ('wind', 'flute'))
            if kind == 'pluck':
                x = voices.synth_pluck(midi, ring, self.rng, sub, vel); x = x / (np.abs(x).max() + 1e-9) * dsp.db(-9) * (0.25 + 0.75 * vel)
            else:
                x = voices.synth_wind_note(midi, dur, self.rng, kind=sub, vel=vel, attack=att, release=rel, vibrato=0.35)
                x = x / (np.sqrt((x ** 2).mean()) + 1e-9) * dsp.db(-24) * (0.25 + 0.75 * vel)
        self._add(self.lead, x, t, gain, pan)

    def render(self, env=None, rt60=3.6, lead_db=-3.0, lp=9000, warm=True):
        """Pads and lead through a hall, a gentle EQ, a dB envelope over the film; returns (N, 2) float32."""
        dry = self.pads + self.lead * dsp.db(lead_db)
        hall = dsp.make_ir(rt60, np.random.default_rng(101), damp=0.4)
        wet = dsp.convolve(self.pads * 0.35 + self.lead * dsp.db(lead_db) * 0.55, hall)
        x = dry * 0.8 + wet
        x = dsp.highpass(x, 45, 2)
        if warm: x = dsp.eq(x, [dsp.peaking_sos(2500, -2.0, 0.7), dsp.peaking_sos(250, 1.0, 0.8)])
        x = dsp.lowpass(x, lp, 1)[:N]
        if env is not None:
            ts = np.array([p[0] for p in env], float); vs = np.array([p[1] for p in env], float)
            x = x * dsp.db(np.interp(np.arange(N) / SR, ts, vs)).astype(np.float32)[:, None]
        return x.astype(np.float32)
