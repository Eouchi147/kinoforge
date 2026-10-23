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
import music_kit as MK  # noqa: E402

# Events (s): the "Events for the sound designer" table in ../NOTES.md (23 Oct).
EV = {
    'race': 2.6,                    # time starts to race: wind rising
    'cut_starts': 3.2,              # the stream starts cutting: the brook grows
    'wall': 6.0,                    # cut to the canyon wall: the river louder and closer
    'rockfall': 9.5,
    'fossils': [7.99, 11.31, 12.11],  # ammonite, fish, trilobite bared: a trickle of grit each
    'settle': (12.2, 14.4),         # time slows to a stop
    'today': 14.0,                  # golden hour: wind on the rim, the river far below, a raven
    'raven': 15.6,
    'steps': [14.6 + 0.3125 * k for k in range(1, 12)],   # the hiker walks to the rim, stops at 18.2
}


def score():
    """Slow strings and harp in D: the meadow (D), the canyon wall and the ages (Bm7, G), the turn as time slows (A sus4
    to A), today resolved (D, the harp rising to the high D)."""
    s = MK.Score(seed=31)
    for t, d, ch in ((0.0, 6.6, [38, 50, 57, 64, 66]), (6.0, 4.4, [47, 54, 62, 69]), (10.0, 3.9, [43, 55, 62, 69, 71]),
                     (13.4, 1.2, [45, 57, 62, 64, 69]), (14.0, 6.0, [38, 50, 57, 66, 69, 74])):
        s.pad(t, d, ch, vel=0.5)
    for t, m in ((0.9, 66), (1.5, 69), (2.2, 74), (3.5, 73), (4.4, 69), (7.0, 71), (8.6, 74), (11.0, 78), (12.4, 76),
                 (14.5, 74), (15.1, 78), (15.8, 81), (17.1, 78), (18.3, 74)):
        s.note('harp', m, t, ring=3.2, vel=0.42, pan=-0.2)
    y = s.render(env=[(0, -4), (6, -3), (12.0, -1), (13.8, 1), (15, -1.5), (20, -3)])
    return y, {'engine': MK.engine(), 'voices': sorted(s.used), 'key': 'D', 'turn': 'time slows, 12.2 to 14.4 s'}


def main():
    m = K.Mix(seed=3)
    r = EV['race']; c = EV['cut_starts']; w = EV['wall']; s0, s1 = EV['settle']; td = EV['today']
    # morning: a trickling brook, light wind in the grass, songbirds far off
    m.bed('small_stream_4', start=10, gain=-6, hp=200, t0=0, t1=w + 0.4, fi=0.8, fo=0.4, env=[(0, -4), (c, -4), (w - 0.3, 2)])
    m.bed('forest', start=24, gain=-2, hp=600, t0=0, t1=w + 0.3, fi=0.8, fo=0.3)
    # time races: the wind rises, the water grows into a river
    m.bed('wind_plain', start=5, gain=-12, hp=90, lp=4500, t0=0, t1=20, fi=1.0, fo=1.2,
          env=[(0, -12), (r, -12), (w, -3), (s0, 0), (s1, -6), (20, -5)])
    m.bed('mountain_stream_1', start=40, gain=-5, hp=60, t0=c, t1=20, fi=2.0, fo=1.2,
          env=[(c, -16), (w - 0.3, -8), (w, 0), (s0, 0), (s1, -8), (20, -8)])
    m.bed('mountain_stream_1', start=90, gain=-10, lp=300, t0=w - 0.2, t1=s1, fi=0.5, fo=1.5)        # the water's rumble
    m.spot('fall_of_stone', EV['rockfall'], gain=-9, p=0.4, start=0.5, length=1.8, hp=80, fo=0.6, label='a small rockfall')
    for k, t in enumerate(EV['fossils']):
        m.spot('fall_of_stone', t, gain=-17, p=(-0.3, 0.3, -0.1)[k], start=(12.0, 18.0, 25.0)[k], length=0.9, hp=900, fo=0.4,
               label='grit trickles as a fossil is bared')
    # today: wind on the rim, the river far below, a raven, the hiker's steps on dry gravel
    m.bed('mountain_stream_1', start=150, gain=-14, lp=900, t0=td - 0.3, t1=20, fi=1.0, fo=1.2)
    m.bed('evening_birds', start=30, gain=-20, hp=900, t0=td - 0.3, t1=20, fi=1.2, fo=1.2)
    m.spot('crows_1', EV['raven'], gain=-20, p=-0.5, start=9.5, length=1.6, hp=250, fo=0.6, label='a raven over the canyon')
    for k, t in enumerate(EV['steps']):
        m.spot('steps_gravel_1', t, gain=-19 - 0.4 * k, p=0.25, start=0.3 + 0.8 * k, length=0.28, hp=150, fo=0.1, label='hiker steps')
    y, info = score()
    m.music(y, under=10.0, info=info)
    m.master(HERE, notes='brook, wind and songbirds; time races: wind rising, the brook becomes a river, a rockfall, grit '
                         'as each fossil is bared; today: rim wind, the river far below, a raven, the hiker\'s steps')


if __name__ == '__main__':
    main()
