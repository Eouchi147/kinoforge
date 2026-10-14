"""P11 KINETIC — sound cue sheet (8 s @ 24 fps). Run: python3 audio.py out.wav
Every time below comes from timing.js (the very object scene.js imports), so picture and sound cannot drift: change a frame there and both follow.
Phase map: B1 0-1.42 year slam (paper hit, drone enters) | B2 1.42-3.0 verdict on four ticks, paper hit on FOR WITCHCRAFT, everything drops out at f60 (12 f of silence)
| B3/B4 3.0-5.4 interrupt hit + paper rustle with the sheet, quill scratch while the line is written, a bare room tone | B5 5.4-7.0 heartbeat, ink for the last lines
| B6 7.0-8.0 12 f of silence, soft hit on PART 1 OF 3, a faint riser that peaks on the last sample (open loop into the next play's slam)."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'harness', 'audio'))
from sfx import *
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'timing.js')).read()
T = json.loads(src[src.index('export default') + len('export default'):].strip().rstrip(';'))     # strict JSON after `export default`
FPS, TOTAL = T['fps'], T['total']
DUR = TOTAL / FPS
def F(f): return f / FPS                                                                          # frame -> seconds

seed(1111)
out = sys.argv[1] if len(sys.argv) > 1 else 'audio.wav'
m = Mix(DUR)

# ------------------------------------------------------------------ voices built from the kit
def slap(dur=0.12):
    """The paper smack on top of a hit: a short band of noise with a fast decay."""
    t = t_axis(dur); return (bandpass(noise(dur), 900, 7000) * np.exp(-t * 45)).astype(np.float32)
def rustle(dur, kp):
    """Paper crinkle: band-limited noise cut by a fast random gate (crumpling), under a swell given as (time, gain) keypoints."""
    n = int(dur * SR); g = np.abs(lowpass(noise(dur), 45)); g = (g / (g.max() + 1e-9)) ** 1.5
    sw = np.interp(np.arange(n) / SR, [p[0] for p in kp], [p[1] for p in kp])
    return (bandpass(noise(dur), 1800, 8500) * g * sw).astype(np.float32)
def quill(dur, level=1.0, density=700):
    """One pen stroke on paper: highpassed crackle (the grit) plus a thin hiss, shaped like a stroke."""
    n = int(dur * SR); env = np.sin(np.pi * np.linspace(0, 1, n)) ** 0.7
    return ((highpass(crackle(dur, density, 0.9), 2400) + bandpass(noise(dur), 3500, 9000) * 0.12) * env * level).astype(np.float32)
def heart(dur, bpm=60):
    """Kit heartbeat (55/48 Hz lub-dub) plus a mid-band thump so the pulse still speaks on a phone speaker, which gives nothing below ~120 Hz."""
    n = int(dur * SR); base = heartbeat(dur + 0.6, bpm=bpm, level=0.8)[:n]                                    # kit heartbeat() overruns its buffer when the last dub lands < 0.55 s before the end: render long, trim
    mid = np.zeros(n, dtype=np.float32); period = 60 / bpm; t = t_axis(0.18)
    th = (np.sin(2 * np.pi * 130 * t) * np.exp(-t * 38) + 0.5 * lowpass(noise(0.18), 600) * np.exp(-t * 50)).astype(np.float32)
    k = 0.0
    while k < dur - 0.4:
        for at, g in [(k, 0.35), (k + period * 0.3, 0.22)]:
            i = int(at * SR); seg = th[:max(0, n - i)]; mid[i:i + len(seg)] += seg * g
        k += period
    return (base + mid).astype(np.float32)

# ------------------------------------------------------------------ B1 0-1.42 s: the year slams
m.put(hit(0.5, sub=90, tail=False, crunch=0.5), at=F(T['b1']['slam']), db=-10, fade_out=0.18, name='PAPER HIT "1628"')
m.put(slap(), at=F(T['b1']['slam']), db=-15, name='paper smack')
b2_end = F(T['beats'][1]['f1'])                                                                    # the cut: 3.0 s
silence_from = F(T['b2']['witch'] + 2)                                                            # everything drops out two frames after the payoff hit
m.put(drone(silence_from, f0=41, detune=0.5, lp=250, voices=5), at=0.0, db=-24, fade_in=0.35, fade_out=0.15, name='drone F1 (dark cards)')

# ------------------------------------------------------------------ B2 1.42-3.0 s: four ticks, one per word; the payoff hit; then the vacuum
for w, fq in [('A', 3000), ('MAYOR', 3000), ('WAS', 3000), ('EXECUTED', 2300)]:
    m.put(tick(0.08, bpm=120, level=0.8, f=fq), at=F(T['b2']['words'][w]), db=-26, name='tick "%s"' % w)
m.put(hit(0.5, sub=90, tail=False, crunch=0.5), at=F(T['b2']['witch']), db=-10, fade_out=0.18, name='PAPER HIT "FOR WITCHCRAFT"')
m.put(slap(), at=F(T['b2']['witch']), db=-15, name='paper smack')
VAC = (silence_from, b2_end - 0.02)                                                               # 12 frames (0.5 s) of true silence; the duck releases in the 20 ms before the hit, so the hit itself is untouched
m.duck(VAC[0], VAC[1], -90, 0.02)

# ------------------------------------------------------------------ B3/B4 3.0-5.4 s: the interrupt, the letter, the quill
cut = F(T['b3']['cut']); launch = F(T['b3']['launch'])
m.put(hit(0.8, sub=62, tail=False, crunch=0.9), at=cut, db=-6, fade_out=0.3, name='INTERRUPT HIT (big)')
m.put(sub_drop(0.8, 70, 34), at=cut, db=-11, fade_out=0.3, name='sub drop')
m.put(slap(0.16), at=cut, db=-9, name='paper smack (big)')
m.put(rustle(0.8, [(0, 0.35), (launch - cut, 0.3), (launch - cut + 0.04, 1.0), (0.3, 0.7), (0.5, 0.25), (0.8, 0.0)]), at=cut, db=-21, name='paper rustle (letter slides up)')
room_end = F(T['b6']['silenceFrom'])                                                              # 7.0 s: the room tone stops with the heartbeat
m.put(lowpass(noise(room_end - cut, 'pink'), 500) * 0.5, at=cut, db=-36, fade_in=0.3, fade_out=0.05, name='room tone (cream world)')

LINES = ['His last letter', 'survived.']                                                          # the copy, as scene.js lays it out (one slot per glyph, plus one for the wrap space)
slots, s0 = [], 0
for ln in LINES:
    slots += [s0 + j for j, ch in enumerate(ln) if ch != ' ']; s0 += len(ln) + 1
t0, gm, wipe = F(T['b4']['typeStart']), T['b4']['glyphMs'] / 1000, T['b4']['wipeMs'] / 1000
burst = wipe * 0.75                                                                               # pen on paper while a glyph is being laid down (a little shorter than the wipe so word gaps are audible)
span = (slots[-1] * gm + wipe + 0.02)
scratch = np.zeros(int(span * SR) + 1, dtype=np.float32)
for k, sl in enumerate(slots):
    v = quill(burst, level=0.75 + 0.25 * ((k * 7) % 5) / 4); i = int(sl * gm * SR); scratch[i:i + len(v)] += v[:len(scratch) - i]
m.put(scratch, at=t0, db=-22, fade_in=0.004, fade_out=0.03, name='QUILL SCRATCH x%d glyphs, one burst each (%.2f-%.2f s)' % (len(slots), t0, t0 + span))

# ------------------------------------------------------------------ B5 5.4-7.0 s: the pulse, and the ink for the last two lines
t2 = F(T['b5']['t2']); hb0 = F(T['b5']['heartbeats'][0]); hb_end = F(T['b6']['silenceFrom'])
m.put(quill(T['b5']['t2Wipe'] / FPS, level=0.9, density=500), at=t2, db=-24, fade_in=0.004, fade_out=0.02, name='ink wipe "Written in secret."')
m.put(heart(hb_end - hb0, bpm=60), at=hb0, db=-28, fade_out=0.08, name='HEARTBEAT 60 bpm (beats on f%d and f%d)' % tuple(T['b5']['heartbeats']))
ul0, ul1 = F(T['b5']['ulStart']), F(T['b5']['ulEnd'] + 1)
wet = bandpass(noise(ul1 - ul0), 500, 3500) * np.sin(np.pi * np.linspace(0, 1, int((ul1 - ul0) * SR))) ** 0.8
m.put(wet.astype(np.float32), at=ul0, db=-27, fade_in=0.01, fade_out=0.03, name='red ink stroke (underline)')

# ------------------------------------------------------------------ B6 7.0-8.0 s: 12 frames of nothing, a soft hit, an open riser
lab = F(T['b6']['label']); r0 = DUR - 0.8
m.put(hit(0.38, sub=95, tail=False, crunch=0.3, click=False), at=lab, db=-16, fade_out=0.15, name='SOFT HIT "PART 1 OF 3"')
rz = riser(0.8, 160, 1600, noise_mix=0.45, curve=2.2); u = np.linspace(0, 1, len(rz)) ** 1.5          # extra u^1.5 gate: inaudible while the silence lasts, still peaks on the final sample
m.put((rz * u).astype(np.float32), at=r0, db=-22, name='riser, faint (0.8 s, peaks on the last sample = open loop)')

m.write(out)
print('wrote', out); [print(f'  {a:5.2f}s  f{round(a * FPS):3d}  {n:68s} {d:4.2f}s') for a, n, d in sorted(m.cues)]

# ------------------------------------------------------------------ self-check
x, sr = sf.read(out); info = sf.info(out); dur = info.frames / info.samplerate
pk = 20 * np.log10(np.max(np.abs(x)) + 1e-12)
def level(a, b): seg = x[int(a * sr):int(b * sr)]; return 20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-12)
ok = True
def check(name, val, cond, unit='dBFS'):
    global ok; ok &= bool(cond); print(f'  [{"ok" if cond else "FAIL"}] {name}: {val:.2f} {unit}')
print('self-check'); check('duration', dur, abs(dur - DUR) < 1e-9, 's'); check('peak', pk, pk <= -1.0 + 1e-3)
sil_a = level(VAC[0], b2_end - 0.02); check('silence before the cut (f%d-f%d) RMS' % (round(VAC[0] * FPS), round(b2_end * FPS) - 1), sil_a, sil_a < -70)
sil_b = level(room_end, room_end + 0.2); check('silence at 7.0 s, first 5 frames RMS', sil_b, sil_b < -80)
sil_c = level(room_end, lab); hit_b = level(lab, lab + 0.1); check('12 frames of silence (7.0-7.5 s) vs the 7.5 s hit: gap', hit_b - sil_c, hit_b - sil_c >= 30, 'dB below')
print(f'  info: room tone (4.4-5.4 s) {level(4.4, 5.4):.1f} dBFS | heartbeat window (5.5-5.75 s) {level(5.5, 5.75):.1f} | quill (3.4-4.2 s) {level(3.4, 4.2):.1f} | interrupt hit (3.0-3.1 s) {level(cut, cut + 0.1):.1f} | soft hit (7.5-7.6 s) {hit_b:.1f} | riser, last 50 ms {level(DUR - 0.05, DUR):.1f} | riser during silence (7.2-7.5 s) {level(DUR - 0.8, lab):.1f}')
print('OK' if ok else 'FAILED'); sys.exit(0 if ok else 1)
