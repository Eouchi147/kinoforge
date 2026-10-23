#!/usr/bin/env python3
"""Sound for Reef and Wreck (20 s, no music, no voice): real recordings only (BigSoundBank CC0, release sfx-bank;
sources in ../../SOUND.md). Every sound is something we see or feel.

    python3 films/cutaway/series/reef-and-wreck/audio/make_audio.py   # writes audio/mix.m4a + mix.json (mix.wav local)

Story: a small island; the cut runs through the sea: light rays, a coral reef, fish schools, a turtle, and a sunken
ship with a chest; a diver drops in. The sound: surf and gulls on the island; under the line the world closes into the
underwater hush (the surf heard through water), bubbles from the reef, the old hull's creak, and the diver's splash
and stream of bubbles.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import audio_kit as K  # noqa: E402

# Events (s): from the film's NOTES.md event table when it lands, else the README story.
EV = {
    'island': (0.0, 4.5),     # the island, surf, gulls
    'under': 4.5,             # the camera goes under the surface line
    'reef': (6.0, 10.0),      # coral, fish schools (bubbles)
    'turtle': 9.5,
    'wreck': (11.5, 16.5),    # the sunken ship and its chest
    'creaks': [12.4, 14.6],
    'diver': 16.8,            # the diver drops in
}


def main():
    m = K.Mix(seed=11)
    u = EV['under']
    m.bed('small_waves_ocean', start=20, gain=-4, t0=0, t1=20, fi=0.8, fo=1.0,
          env=[(0, 0), (u - 0.6, 0), (u + 0.6, -26), (EV['diver'] - 0.6, -26), (EV['diver'], -8), (20, -14)])
    m.spot('gulls_harbor', 0.6, gain=-14, p=-0.35, start=12, length=4.4, hp=600, fi=0.5, fo=1.2, trim=False, label='gulls')
    # under water: the hush, the surf heard through water, bubbles from the reef
    m.bed('underwater', start=5, gain=-4, t0=u - 0.6, t1=20, fi=1.2, fo=1.0, env=[(u, 0), (EV['diver'], -2), (20, -4)])
    m.bed('small_waves_ocean', start=20, gain=-10, lp=350, t0=u - 0.3, t1=20, fi=1.0, fo=1.0)
    r0, r1 = EV['reef']
    m.spot('water_bubbles', r0 + 0.4, gain=-20, p=0.3, start=2.0, length=r1 - r0, lp=3500, fi=0.8, fo=1.0, trim=False, label='reef bubbles')
    m.spot('bubbles_burst', EV['turtle'], gain=-22, p=-0.3, start=3.0, length=1.5, lp=3000, fi=0.2, fo=0.5, trim=False, label='turtle breath bubbles')
    # the wreck: the hull's slow creak heard through water
    for k, t in enumerate(EV['creaks']):
        m.spot('creaking_door_2', t, gain=-16, p=(-0.4, 0.3)[k], start=0.5 + k, length=2.0, lp=1200, speed=0.7, fi=0.2, fo=0.8,
               label='the hull creaks')
    # the diver drops in
    d = EV['diver']
    m.spot('splash_big_1', d, gain=-6, p=0.15, length=2.5, fo=0.8, label='diver splash (above)')
    m.spot('bubbles_burst', d + 0.35, gain=-12, p=0.15, start=0.0, length=2.5, lp=4000, fi=0.05, fo=0.8, label='diver bubbles')
    m.master(HERE, notes='surf and gulls; underwater hush with the surf through water; reef bubbles; hull creaks; diver splash')


if __name__ == '__main__':
    main()
