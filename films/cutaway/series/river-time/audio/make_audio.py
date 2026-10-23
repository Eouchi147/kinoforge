#!/usr/bin/env python3
"""Sound for The River Through Time (20 s, no music, no voice): real recordings only (BigSoundBank CC0, release
sfx-bank; sources in ../../SOUND.md). Every sound is something we see or feel.

    python3 films/cutaway/series/river-time/audio/make_audio.py     # writes audio/mix.m4a + mix.json (mix.wav local)

Story: a thin stream on a flat block cuts down through the layers over ages until a canyon stands; fossils appear in
the walls; the last shot is today, a hiker on the rim. The sound follows the cut: a trickle that grows into a river
as the canyon deepens, the wind finding the walls, stones letting go when layers give, and at the end the present:
open air, a few birds, steps on gravel at the rim.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import audio_kit as K  # noqa: E402

# Events (s): blender.py (shots then 0-6, ages 6-14, today 14-20; the hiker walks 14.6 to 18.2 at 1.6 strides a
# second, so a step every 0.3125 s); fossil times are estimates until NOTES.md gives them.
EV = {
    'title_end': 2.0,
    'cut_deepens': (2.6, 14.0),     # time races, the water cuts down
    'stones': [5.4, 7.6, 9.6, 11.6, 13.2],
    'fossils': [8.5, 10.3, 12.1],   # an ammonite, a fish, a trilobite bared in the wall
    'today': 14.0,                  # time has stopped: golden hour, birds over the canyon
    'steps': [14.6 + 0.3125 * k for k in range(1, 12)],
}


def main():
    m = K.Mix(seed=3)
    t0, t1 = EV['cut_deepens']
    # the water: a small stream that hands over to a river as the canyon deepens
    m.bed('small_stream_4', start=10, gain=-4, hp=150, t0=0, t1=t1 + 1.5, fi=1.5, fo=2.5,
          env=[(0, -2), (t0, -2), (t1, -10), (20, -14)])
    m.bed('mountain_stream_1', start=40, gain=-6, hp=60, t0=t0, t1=20, fi=4.0, fo=1.0,
          env=[(t0, -18), (t1 - 3, -2), (EV['today'], -4), (20, -9)])
    # the wind finds the walls as they rise
    m.bed('wind_plain', start=5, gain=-14, hp=90, lp=4000, t0=4, t1=20, fi=4, fo=1,
          env=[(4, -12), (t1, 0), (EV['today'], -3), (20, -5)])
    for k, t in enumerate(EV['stones']):
        m.spot('fall_of_stone', t, gain=-10 - 2 * (k % 2), p=(-0.4, 0.35, -0.2, 0.5, 0.1)[k], start=(0.5, 6.0, 12.0, 18.0, 25.0)[k],
               length=1.6, hp=80, fo=0.6, label='stones fall')
    for k, t in enumerate(EV['fossils']):
        m.spot('steps_stone_stair', t, gain=-20, p=(0.3, -0.3, 0.1)[k], start=1.0 + 3 * k, length=0.3, hp=400, fo=0.1, label='fossil revealed')
    # today: open air, a few birds far off, the hiker's steps on the rim gravel
    m.bed('evening_birds', start=30, gain=-16, hp=900, t0=EV['today'] - 0.6, t1=20, fi=1.2, fo=1.0)
    for k, t in enumerate(EV['steps']):
        m.spot('steps_gravel_1', t, gain=-19 - 0.4 * k, p=0.25, start=0.3 + 0.8 * k, length=0.28, hp=150, fo=0.1, label='hiker steps')
    m.master(HERE, notes='beds: stream to river, wind; spots: falling stones, fossil ticks, birds and steps of today')


if __name__ == '__main__':
    main()
