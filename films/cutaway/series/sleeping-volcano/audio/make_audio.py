#!/usr/bin/env python3
"""Sound for The Sleeping Volcano (20 s, no music, no voice): real recordings only (BigSoundBank CC0, release
sfx-bank; sources in ../../SOUND.md). Every sound is something we see or feel.

    python3 films/cutaway/series/sleeping-volcano/audio/make_audio.py   # writes audio/mix.m4a + mix.json (mix.wav local)

Story: a green island; below, the magma chamber glows and rises through cracks; birds lift; smoke, then a gentle
eruption at dusk. The sound: surf and birdsong on the island; under it the chamber's slow boil (boiling water slowed
far down) and a felt rumble (thunder slowed), rock cracking as the magma rises (ice cracks slowed: brittle and
deep), the birds lifting off as one, steam hissing from the vents, then the eruption: a deep roar, fire, falling
stones, and the island quiet under it at dusk.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import audio_kit as K  # noqa: E402

# Events (s): from the film's NOTES.md event table when it lands, else the README story.
EV = {
    'island': (0.0, 4.0),     # green island, surf, birds
    'chamber': (3.5, 20.0),   # the magma chamber glows below
    'cracks': [7.2, 8.6, 9.8],  # magma rises through cracks
    'birds_lift': 10.8,
    'smoke': (11.8, 14.5),    # smoke and steam from the vents
    'erupt': 14.8,            # the gentle eruption at dusk
}


def main():
    m = K.Mix(seed=19)
    e = EV['erupt']; b = EV['birds_lift']
    m.bed('small_waves_ocean', start=50, gain=-8, t0=0, t1=20, fi=0.8, fo=1.0, env=[(0, 0), (e, -3), (e + 1, -10), (20, -8)])
    m.bed('forest', start=5, gain=-8, hp=400, t0=0, t1=b + 0.6, fi=0.8, fo=0.5)
    # the chamber: slow boil and a felt rumble, building to the eruption
    c0 = EV['chamber'][0]
    m.bed('big_broth', start=0.5, gain=-10, speed=0.35, lp=900, t0=c0, t1=20, fi=2.0, fo=1.0,
          env=[(c0, -10), (EV['cracks'][0], -4), (e, 0), (e + 2, 0), (20, -4)], xf=0.4)
    m.bed('thunder_3', start=0, gain=-8, speed=0.5, lp=220, t0=c0 + 1.0, t1=20, fi=3.0, fo=1.0,
          env=[(c0, -14), (e - 2, -4), (e, 0), (20, -6)])
    for k, t in enumerate(EV['cracks']):
        m.spot(('ice_crack_1', 'ice_crack_2', 'ice_crack_3')[k], t, gain=-10, p=(-0.3, 0.25, 0.0)[k], speed=0.5, lp=3000,
               length=1.2, fo=0.5, label='rock cracks as magma rises')
    m.spot('flight_pigeon', b, gain=-10, p=-0.4, length=2.5, fo=0.6, label='birds lift')
    m.spot('flight_bird_2', b + 0.25, gain=-12, p=0.4, length=2.0, fo=0.6, label='birds lift')
    m.spot('crows_1', b + 0.4, gain=-16, p=0.2, start=4.0, length=2.4, hp=300, fo=0.8, label='alarm calls as they lift')
    s0, s1 = EV['smoke']
    m.spot('steam_hiss_1', s0, gain=-14, p=0.2, length=s1 - s0, hp=500, fi=0.5, fo=1.0, label='steam from the vents')
    # the eruption: a deep roar, fire, stones falling back
    m.spot('thunder_2', e, gain=-2, speed=0.6, lp=600, length=6.0, fi=0.08, fo=2.5, label='the eruption roars')
    m.bed('fireplace_2', start=5, gain=-14, lp=5000, t0=e + 0.3, t1=20, fi=1.0, fo=1.0)
    for k, t in enumerate((e + 1.6, e + 2.6, e + 3.4)):
        m.spot('fall_of_stone', t, gain=-16, p=(-0.5, 0.4, -0.1)[k], start=4.0 + 5 * k, length=1.0, fo=0.5, label='stones fall back')
    m.master(HERE, notes='surf and birds; slow boil and rumble below; rock cracks; birds lift; steam; the eruption roar, fire, falling stones')


if __name__ == '__main__':
    main()
