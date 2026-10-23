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
import music_kit as MK  # noqa: E402

EV = {
    'island': (0.0, 6.5),          # golden hour: waves, wind in leaves, gulls, a far steam wisp
    'wake': 4.0,                   # the chamber brightens: a felt rumble begins
    'under': 6.5,                  # cut to the chamber: waves drop away, rumble and a slow mud-pot bubbling
    'climb': (6.9, 13.2),          # magma climbs: the rumble rises, small rock cracks
    'cracks': [7.8, 9.4, 11.3, 12.7],
    'smoke': (10.0, 13.0),         # the hiss thickens
    'birds': 10.9,                 # a flock takes off, alarm calls
    'wide': 13.5,                  # cut wide at dusk: a beat of near silence, waves back, wind
    'erupt': 14.2,                 # first fountain: a deep boom, a short rock tumble
    'bombs': [15.4, 16.5, 18.3],   # falling bombs
    'sea': 17.7,                   # lava reaches the sea: a loud hiss, then steam
}


def main():
    m = K.Mix(seed=19)
    e = EV['erupt']; b = EV['birds']; c0, c1 = EV['climb']; wk = EV['wake']; u = EV['under']; w = EV['wide']; sea = EV['sea']
    surf = [(0, 0), (u - 0.2, 0), (u + 0.6, -30), (w - 0.1, -30), (w + 0.7, -4), (e, -4), (e + 1, -9), (20, -6)]
    m.bed('small_waves_ocean', start=50, gain=-9, t0=0, t1=20, fi=0.8, fo=1.5, env=surf)
    m.bed('forest', start=5, gain=-7, hp=400, t0=0, t1=u + 0.3, fi=0.8, fo=0.4)
    m.bed('wind_plain', start=30, gain=-20, hp=150, t0=w - 0.2, t1=20, fi=0.9, fo=1.5)
    m.spot('gulls_harbor', 0.3, gain=-20, p=0.45, start=40, length=6.0, hp=700, fi=0.6, fo=1.2, trim=False, label='gulls circling')
    m.spot('steam_hiss_3', 0.5, gain=-32, p=0.0, length=5.5, lp=3000, fi=1.0, fo=1.0, speed=0.5, trim=False, label='far fumarole hiss')
    # the chamber wakes and the magma climbs: a mud-pot boil and a felt rumble, growing; quiet for the cut wide
    m.bed('big_broth', start=0.5, gain=-10, speed=0.35, lp=900, t0=wk, t1=20, fi=2.0, fo=1.5, xf=0.4,
          env=[(wk, -18), (u - 0.2, -14), (u + 0.3, -4), (c1, 0), (w - 0.1, 0), (w + 0.3, -16), (e, -6), (20, -10)])
    m.bed('thunder_3', start=0, gain=-8, speed=0.5, lp=220, t0=wk, t1=20, fi=2.5, fo=1.5,
          env=[(wk, -18), (u, -8), (c1, -1), (w - 0.1, 0), (w + 0.3, -14), (e, -2), (20, -8)])
    for k, t in enumerate(EV['cracks']):
        m.spot(('ice_crack_1', 'ice_crack_2', 'ice_crack_3', 'ice_crack_1')[k], t, gain=-12 + k, p=(-0.3, 0.25, 0.0, -0.1)[k],
               speed=0.5, lp=3000, length=1.2, fo=0.5, label='rock cracks as magma climbs')
    s0, s1 = EV['smoke']
    m.spot('steam_hiss_1', s0, gain=-18, p=0.1, length=s1 - s0, hp=400, speed=0.75, fi=0.8, fo=0.6, trim=False, label='the hiss thickens')
    m.spot('flight_pigeon', b, gain=-10, p=-0.4, length=2.2, fo=0.6, label='a flock takes off')
    m.spot('flight_bird_2', b + 0.2, gain=-12, p=0.4, length=2.0, fo=0.6, label='a flock takes off')
    m.spot('flight_bird_1', b + 0.35, gain=-14, p=0.1, length=2.4, fo=0.6, label='a flock takes off')
    m.spot('crows_1', b + 0.3, gain=-17, p=0.2, start=4.0, length=2.4, hp=300, fo=0.8, label='alarm calls')
    # the eruption: a deep boom and a rock tumble, fire, bombs falling, the sea hissing where the lava meets it
    m.spot('thunder_2', e, gain=-2, speed=0.6, lp=600, length=5.0, fi=0.05, fo=2.5, label='the eruption booms')
    m.spot('fall_of_stone', e + 0.15, gain=-12, p=-0.2, start=10.0, length=1.6, fo=0.6, label='a short rock tumble')
    m.bed('fireplace_2', start=5, gain=-11, lp=5000, t0=e + 0.2, t1=20, fi=0.8, fo=1.5)
    m.bed('fire_branching_1', start=2, gain=-18, lp=4000, p=0.3, t0=e + 0.5, t1=sea + 0.5, fi=1.0, fo=1.0)
    for k, t in enumerate(EV['bombs']):
        m.spot('fall_of_stone', t, gain=-15, p=(-0.5, 0.4, -0.1)[k], start=4.0 + 5 * k, length=1.0, lp=1500, fo=0.5, label='a bomb thuds down')
    m.spot('water_that_burns', sea, gain=-4, p=0.45, start=12.6, length=2.4, fi=0.1, fo=0.8, trim=False, label='lava meets the sea')
    m.spot('steam_hiss_3', sea + 0.05, gain=-12, p=0.45, length=2.6, fi=0.1, fo=1.0, trim=False, label='steam roars up')
    m.bed('steam_hiss_1', start=0.2, gain=-26, speed=0.6, hp=500, p=0.4, t0=sea + 0.6, t1=20, fi=0.8, fo=1.2)
    y, info = score()
    m.music(y, under=10.0, info=info)
    m.master(HERE, notes='waves, gulls and a far fumarole; the chamber: mud-pot boil and a felt rumble growing, rock cracks, '
                         'the hiss thickening, a flock lifting; a beat of quiet at dusk, then the boom, fire, bombs and the sea '
                         'hissing under the lava; deep string drones that swell at the eruption and settle')


def score():
    """Deep drones in C: the island at golden hour (Cmaj9, a few harp tones), the magma wakes and climbs (Abmaj7, Fm9),
    tension (G sus) into the eruption, where the low strings swell (Ab over C), then settle and resolve on open fifths."""
    s = MK.Score(seed=53)
    for t, d, ch in ((0.0, 6.9, [36, 48, 55, 59, 62, 64]), (6.5, 3.8, [44, 51, 56, 60, 67]), (10.0, 3.4, [41, 53, 56, 60, 67]),
                     (13.2, 1.4, [43, 55, 60, 62, 67]), (14.2, 3.2, [36, 44, 51, 56, 60, 63]), (17.0, 3.0, [36, 43, 48, 55, 60, 67])):
        s.pad(t, d, ch, vel=0.52, att=2.0)
    s.pad(0.0, 20.0, [24, 36], vel=0.45, att=4.0, rel=2.0, gain=-3)
    for t, m in ((1.0, 67), (2.0, 72), (3.2, 74), (4.8, 71)):
        s.note('harp', m, t, ring=3.0, vel=0.35, pan=-0.2)
    y = s.render(env=[(0, -6), (4, -6), (10, -3), (13.6, 0), (14.6, 3), (16.2, 0), (18, -4), (20, -5)], lp=6000)
    return y, {'engine': MK.engine(), 'voices': sorted(s.used), 'key': 'C', 'turn': 'the eruption, 14.2 s'}


if __name__ == '__main__':
    main()
