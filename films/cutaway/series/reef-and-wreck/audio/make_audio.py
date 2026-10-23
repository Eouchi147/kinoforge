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
import audio_kit as K  # noqa: E402

EV = {
    'arrive': (0.0, 7.0),          # the island, above water
    'roll': 4.8,                   # she rolls back off the boat
    'splash': 5.35,
    'under': 7.0,                  # descent shot: through the glass, under water
    'breaths': [8.2, 11.6, 15.0, 18.3],   # her regulator exhales
    'turn': 10.2,                  # the school turns together
    'wreck': 13.5,                 # close on the wreck
    'creaks': [14.1, 16.3],
    'arrive_chest': 15.9,
}


def main():
    m = K.Mix(seed=11)
    u = EV['under']; sp = EV['splash']
    # above: surf and terns, the boat rocking
    m.bed('small_waves_ocean', start=20, gain=-5, t0=0, t1=20, fi=0.8, fo=1.0,
          env=[(0, 0), (u - 0.5, 0), (u + 0.5, -28), (20, -28)])
    m.bed('sea_tern', start=8, gain=-14, hp=700, t0=0, t1=u + 0.4, fi=0.8, fo=0.8)
    m.spot('creaking_door_2', EV['roll'], gain=-24, p=-0.3, length=0.7, lp=2500, fo=0.3, label='the boat rocks as she rolls')
    m.spot('splash_big_1', sp, gain=0, p=-0.3, length=2.6, fo=0.8, label='the diver splashes in')
    m.spot('bubbles_burst', sp + 0.2, gain=-20, p=-0.3, start=0.0, length=1.6, lp=4000, fo=0.6, label='foam fizz')
    # under water: the hush, the surf through water, her breath, the school, the hull
    m.bed('underwater', start=5, gain=-8, t0=u - 0.5, t1=20, fi=1.0, fo=1.0)
    m.bed('small_waves_ocean', start=20, gain=-11, lp=320, t0=u - 0.4, t1=20, fi=1.0, fo=1.0,
          env=[(u, 0), (EV['wreck'], -3), (20, -5)])
    for k, t in enumerate(EV['breaths']):
        m.spot('bubbles_burst', t, gain=-15 - (k == 0) * 2, p=(0.1, -0.1, 0.2, 0.1)[k], start=(3.6, 7.0, 10.0, 14.2)[k],
               length=1.4, lp=3500, fi=0.05, fo=0.6, send=-6, label='her breath bubbles up')
    m.spot('whoosh_3', EV['turn'] - 0.15, gain=-22, lp=900, speed=0.6, length=1.4, fi=0.2, fo=0.5, sweep=(0.5, -0.5),
           label='the school turns (a rush of water)')
    m.spot('water_bubbles', 10.5, gain=-26, p=-0.4, start=5.0, length=2.4, lp=2500, fi=0.6, fo=0.8, trim=False,
           label='the reef fizzes as the turtle passes')
    for k, t in enumerate(EV['creaks']):
        m.spot('creaking_door_2', t, gain=-16, p=(-0.4, 0.3)[k], start=0.5 + k, length=2.0, lp=1100, speed=0.65, fi=0.2, fo=0.8,
               send=-3, label='the hull creaks')
    m.room(rt60=1.2, wet=0.35, seed=29)
    m.master(HERE, notes='surf and terns, the roll and splash; underwater hush with the surf through water; her breath '
                         'bubbles; the school turns; the hull creaks')


if __name__ == '__main__':
    main()
