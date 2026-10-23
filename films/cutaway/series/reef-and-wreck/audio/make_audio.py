#!/usr/bin/env python3
"""Sound for Reef and Wreck (20 s, no music, no voice): real recordings only (BigSoundBank CC0, release sfx-bank;
sources in ../../SOUND.md). Every sound is something we see or feel.

    python3 films/cutaway/series/reef-and-wreck/audio/make_audio.py   # writes audio/mix.m4a + mix.json (mix.wav local)

Story (blender.py, 23 Oct): a small island on a block of clear sea; the diver rolls back off a little boat (splash
5.35 s); the camera sinks with her through the glass past light rays, the school turns (10.2 s), the turtle glides
across (10.5 to 13 s); close on the wreck, she arrives (15.9 s) and her torch finds the gold (17 s).
The sound: surf and terns on the island, the roll and splash; under the line the underwater hush with the surf heard
through water, her breath going up in bubbles, the school's turn as a soft rush of water, the old hull creaking; the
torch and the gold are light, not sound.
Event times: blender.py constants (T_ROLL, T_IN, T_SWIM, T_ARRIVE, T_TURN) and its shot list; NOTES.md table when it lands.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import numpy as np
import audio_kit as K  # noqa: E402
import music_kit as MK  # noqa: E402

EV = {
    'arrive': (0.0, 7.0),          # the island, above water
    'laps': (2.0, 4.8),            # the boat bobs, water laps its hull
    'roll': 4.8,                   # she tips back off the gunwale
    'splash': 5.35,
    'muffle': 5.7,                 # under the surface
    'under': 7.0,                  # cut under water (split view)
    'puffs': [5.35 + 1.6 * k for k in range(1, 10)],   # regulator exhales every 1.6 s (6.95 to 19.75)
    'turn': 10.2,                  # the school turns together
    'turtle': [10.5, 13.1],        # flipper strokes
    'wreck': 13.5,                 # cut to the wreck: reef crackle closer, the hull creaks
    'creaks': [13.8, 16.9],
    'hover': 15.9,                 # she arrives and hovers: slow fin swishes
}


def main():
    m = K.Mix(seed=11)
    u = EV['under']; sp = EV['splash']; mu = EV['muffle']
    # above: soft surf, terns and gulls, the boat on the water
    m.bed('small_waves_ocean', start=20, gain=-6, t0=0, t1=20, fi=0.8, fo=1.5,
          env=[(0, 0), (mu - 0.2, 0), (mu + 0.6, -14), (u - 0.2, -14), (u + 0.4, -30), (20, -30)])
    m.bed('sea_tern', start=8, gain=-15, hp=700, t0=0, t1=mu + 0.3, fi=0.8, fo=0.6)
    l0, l1 = EV['laps']
    for k, t in enumerate(np.arange(l0, l1, 0.9)):
        m.spot('splash_small_1', t, gain=-28, p=-0.3, length=0.5, lp=2500, fo=0.25, label='water laps the hull')
    m.spot('creaking_door_2', EV['roll'], gain=-22, p=-0.3, length=0.7, lp=2500, fo=0.3, label='the boat creaks as she tips back')
    m.spot('cloth', EV['roll'] + 0.1, gain=-20, p=-0.3, length=0.4, hp=600, fo=0.2, label='a rustle of gear')
    m.spot('splash_big_1', sp, gain=0, p=-0.3, length=2.6, fo=0.8, label='the diver splashes in')
    # under water: the hush, the surf through water, the reef's crackle, her breath every 1.6 s
    m.bed('underwater', start=5, gain=-8, t0=mu - 0.2, t1=20, fi=0.8, fo=1.5, env=[(mu, -8), (u, 0), (20, 0)])
    m.bed('small_waves_ocean', start=20, gain=-11, lp=320, t0=mu - 0.2, t1=20, fi=1.0, fo=1.5, env=[(u, 0), (EV['wreck'], -3), (20, -5)])
    m.bed('water_bubbles', start=5.0, gain=-30, lp=3000, hp=900, t0=u, t1=20, fi=1.0, fo=1.5,
          env=[(u, -4), (EV['wreck'], 0), (20, 0)])
    m.spot('bubbles_burst', mu + 0.1, gain=-17, p=-0.2, start=0.0, length=1.4, lp=3500, fi=0.05, fo=0.6, label='first bubbles')
    for k, t in enumerate(EV['puffs']):
        m.spot('bubbles_burst', t, gain=-17 - 2 * (k % 2), p=(0.1, -0.1, 0.2)[k % 3], start=(3.6, 7.0, 10.0, 14.2, 18.0, 23.0, 26.5, 30.5, 33.8)[k],
               length=1.2, lp=3500, fi=0.05, fo=0.5, send=-6, label='her regulator exhales')
    m.spot('whoosh_3', EV['turn'] - 0.15, gain=-20, lp=900, speed=0.6, length=1.4, fi=0.2, fo=0.5, sweep=(0.5, -0.5),
           label='the school turns (a rush of water)')
    for t in EV['turtle'] + [EV['hover'], EV['hover'] + 1.4]:
        m.spot('whoosh_5', t, gain=-24, lp=600, speed=0.5, length=1.0, fi=0.2, fo=0.5, sweep=(-0.3, 0.3), label='a slow stroke through water')
    for k, t in enumerate(EV['creaks']):
        m.spot('creaking_door_2', t, gain=-16, p=(-0.4, 0.3)[k], start=0.5 + k, length=2.0, lp=1100, speed=0.65, fi=0.2, fo=0.8,
               send=-3, label='the hull creaks')
    m.room(rt60=1.2, wet=0.35, seed=29)
    y, info = score()
    m.music(y, under=10.0, info=info)
    m.master(HERE, notes='surf, terns, the boat and the splash; underwater hush, reef crackle and her breath every 1.6 s; the '
                         'school turns; the hull creaks; a quiet oceanic score with a soft bell for the gold')


def score():
    """Airy pads and harp in E, oceanic: the island (Eadd9), under the water (C#m7), the school's turn and the turtle
    (Aadd9, the swell), the wreck (B sus), and the gold found (E, a soft bell)."""
    s = MK.Score(seed=43)
    for t, d, ch in ((0.0, 7.4, [40, 52, 59, 66, 68]), (7.0, 3.6, [49, 56, 59, 64, 68]), (10.2, 3.6, [45, 57, 64, 69, 71]),
                     (13.5, 2.8, [47, 59, 64, 66, 71]), (16.0, 4.0, [40, 52, 59, 64, 68, 71])):
        s.pad(t, d, ch, vel=0.42, att=2.6, rel=3.4)
    for t, m in ((0.8, 64), (1.6, 68), (2.6, 71), (4.0, 73), (8.0, 71), (9.5, 76), (11.0, 73), (12.5, 71), (18.4, 83)):
        s.note('harp', m, t, ring=3.4, vel=0.38, pan=-0.2)
    for t, m in ((17.0, 76), (17.6, 80)):
        s.note('glock', m, t, ring=3.0, vel=0.3, gain=-6, pan=0.2)
    y = s.render(env=[(0, -3), (7, -3), (10.2, 0), (12, -1), (13.5, -3), (17, -1), (20, -3)], rt60=4.2, lp=7500)
    return y, {'engine': MK.engine(), 'voices': sorted(s.used), 'key': 'E', 'turn': 'the school turns, 10.2 s; the gold, 17 s'}


if __name__ == '__main__':
    main()
