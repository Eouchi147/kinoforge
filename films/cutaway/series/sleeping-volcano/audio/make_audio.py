#!/usr/bin/env python3
"""Sound for The Sleeping Volcano (20 s, no music, no voice): real recordings only (BigSoundBank CC0, release
sfx-bank; sources in ../../SOUND.md). Every sound is something we see or feel.

    python3 films/cutaway/series/sleeping-volcano/audio/make_audio.py   # writes audio/mix.m4a + mix.json (mix.wav local)

Story (blender.py, 23 Oct): the island sleeps at golden hour (a thin steam wisp, gulls); the chamber brightens (4.0 s),
magma climbs the conduit (6.9 to 13.2 s), birds burst from the trees (10.9 s), steam turns to smoke (10 to 13 s); at
dusk a gentle eruption (first fountain 14.2 s), a lava stream runs down to the sea (14.7 to 17.7 s) and steams there.
The sound: surf, gulls and birds; below, a slow boil (a boiling pot slowed far down) and a felt rumble (thunder slowed)
that grow as the magma climbs, rock cracking (ice cracks slowed), the birds lifting, steam hissing, then the
eruption's roar, fire, stones falling back and the hiss where the lava meets the sea.
Event times: blender.py constants (T_WAKE, T_CLIMB, T_BIRDS, T_SMOKE, T_ERUPT, T_FLOW); NOTES.md table when it lands.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import audio_kit as K  # noqa: E402

EV = {
    'island': (0.0, 6.5),
    'wake': 4.0,                   # the chamber starts to brighten
    'climb': (6.9, 13.2),          # magma front climbs the conduit
    'cracks': [7.8, 9.4, 11.3, 12.7],
    'birds': 10.9,                 # birds burst from the trees
    'smoke': (10.0, 13.0),
    'erupt': 14.2,                 # first lava fountain
    'flow': (14.7, 17.7),          # lava stream from the rim to the sea
    'sea_steam': 16.9,             # lava reaches the sea and steams
}


def main():
    m = K.Mix(seed=19)
    e = EV['erupt']; b = EV['birds']; c0, c1 = EV['climb']; wk = EV['wake']
    m.bed('small_waves_ocean', start=50, gain=-9, t0=0, t1=20, fi=0.8, fo=1.0, env=[(0, 0), (e, -2), (e + 1, -8), (20, -6)])
    m.bed('forest', start=5, gain=-7, hp=400, t0=0, t1=b + 0.4, fi=0.8, fo=0.4)
    m.spot('gulls_harbor', 1.0, gain=-20, p=0.45, start=40, length=4.5, hp=700, fi=0.6, fo=1.2, trim=False, label='gulls')
    m.spot('steam_hiss_3', 0.8, gain=-30, p=0.0, length=2.6, lp=3000, fi=0.8, fo=1.5, speed=0.7, trim=False, label='thin steam wisp')
    # the chamber wakes and the magma climbs: a slow boil and a felt rumble, growing
    m.bed('big_broth', start=0.5, gain=-10, speed=0.35, lp=900, t0=wk, t1=20, fi=2.0, fo=1.0, xf=0.4,
          env=[(wk, -12), (c0, -6), (c1, -1), (e, 0), (20, -4)])
    m.bed('thunder_3', start=0, gain=-8, speed=0.5, lp=220, t0=wk + 1.0, t1=20, fi=3.0, fo=1.0,
          env=[(wk, -16), (c0, -9), (e - 1.0, -2), (e, 0), (20, -6)])
    for k, t in enumerate(EV['cracks']):
        m.spot(('ice_crack_1', 'ice_crack_2', 'ice_crack_3', 'ice_crack_1')[k], t, gain=-12 + k, p=(-0.3, 0.25, 0.0, -0.1)[k],
               speed=0.5, lp=3000, length=1.2, fo=0.5, label='rock cracks as magma climbs')
    m.spot('flight_pigeon', b, gain=-10, p=-0.4, length=2.2, fo=0.6, label='birds burst from the trees')
    m.spot('flight_bird_2', b + 0.2, gain=-12, p=0.4, length=2.0, fo=0.6, label='birds burst from the trees')
    m.spot('flight_bird_1', b + 0.35, gain=-14, p=0.1, length=2.4, fo=0.6, label='birds burst from the trees')
    m.spot('crows_1', b + 0.4, gain=-17, p=0.2, start=4.0, length=2.4, hp=300, fo=0.8, label='alarm calls as they lift')
    s0, s1 = EV['smoke']
    m.spot('steam_hiss_1', s0, gain=-17, p=0.1, length=s1 - s0, hp=400, speed=0.75, fi=0.8, fo=1.0, trim=False,
           label='steam turns to smoke')
    # the eruption: a deep roar, fire, stones falling back, the sea hissing where the lava meets it
    m.spot('thunder_2', e, gain=-2, speed=0.6, lp=600, length=5.5, fi=0.08, fo=2.5, label='the eruption roars')
    m.bed('fireplace_2', start=5, gain=-12, lp=5000, t0=e + 0.3, t1=20, fi=1.0, fo=1.0)
    for k, t in enumerate((e + 1.2, e + 2.1, e + 3.0)):
        m.spot('fall_of_stone', t, gain=-16, p=(-0.5, 0.4, -0.1)[k], start=4.0 + 5 * k, length=1.0, fo=0.5, label='stones fall back')
    m.spot('water_that_burns', EV['sea_steam'], gain=-6, p=0.45, start=12.6, length=3.0, fi=0.3, fo=1.2, trim=False,
           label='lava meets the sea')
    m.spot('steam_hiss_3', EV['sea_steam'] + 0.1, gain=-16, p=0.45, length=2.6, fi=0.2, fo=1.2, trim=False, label='the sea steams')
    m.master(HERE, notes='surf, gulls and birds; slow boil and rumble growing below; rock cracks; birds lift; steam to smoke; '
                         'the eruption roar, fire, falling stones, the sea hissing under the lava')


if __name__ == '__main__':
    main()
