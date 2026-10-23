#!/usr/bin/env python3
"""Sound for What Lies Under a Meadow (the Cutaway line's example film, 39.9 s, 16:9): no voice yet (the cues are
estimated), so the story is told by real recordings (BigSoundBank CC0, release sfx-bank, the series kit) and a quiet
score, the way Sam liked the series (22 Oct, 22:54: ambient, peaceful, subtle music under nature sounds).

    python3 films/cutaway/meadow/audio/make_audio.py   # writes audio/mix.m4a + mix.json (mix.wav stays local)

Event times come from cues.json and spec.json (the shot list is cut on the cue words):
  0.0 to 7.2   map: the golden meadow from above, the river, the village, the mill
  7.2 to 12.9  ground: at the edge of the cut, eye on the grass, into the low sun; title at 7.49
  12.9 to 22   crane down the cut face: the mole (15.18), the chest leaking gold (17.62), the Roman jar (19.25)
  22.4 to 29   deep time: the counter rolls to 66 million years (23.96 to 25.5); the giant's bones (27.5)
  29 to 39.9   back on top: a slow arc, the sun bursting round the big tree; end card about 35.8
"""
import os, sys
os.environ.setdefault('KF_SOUND_DUR', '39.937')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'series'))
import numpy as np  # noqa: E402
import audio_kit as K  # noqa: E402
import music_kit as MK  # noqa: E402

D = K.DUR
EV = {
    'ground': 7.2, 'crane': 12.9, 'mole': 15.18, 'chest': 17.62, 'jar': 19.25,
    'deep': 22.4, 'years': (23.96, 25.5), 'bones': 27.5, 'top': 29.0, 'end': 35.8,
}


def main():
    m = K.Mix(seed=11)
    g, c, dp, tp = EV['ground'], EV['crane'], EV['deep'], EV['top']
    # the world above: loud from above and at the grass, muffled as we go under, near silent in deep time, back on top
    above = [(0, -2), (g, 0), (c - 0.2, 0), (c + 1.2, -14), (dp - 0.3, -20), (dp + 1.0, -42), (tp - 0.6, -42), (tp + 1.8, 0), (D, 0)]
    m.bed('evening_birds', start=10, gain=-7, hp=300, t0=0, t1=D, fi=1.0, fo=2.5, env=above)
    m.bed('small_stream_4', start=5, gain=-17, hp=150, t0=0, t1=D, fi=1.2, fo=2.5,
          env=[(0, 0), (g - 0.3, 0), (g + 0.6, -10), (c, -14), (dp, -40), (tp, -40), (tp + 2, -4), (D, -4)])
    m.bed('wind_plain', start=40, gain=-23, hp=200, t0=0, t1=D, fi=1.0, fo=2.5, env=above)
    m.bed('field_cricket', start=3, gain=-20, hp=2500, t0=g - 0.5, t1=D, fi=1.0, fo=2.5,
          env=[(g - 0.5, -6), (g + 0.6, 0), (c, 0), (c + 1.2, -18), (dp, -40), (tp, -40), (tp + 2, -2), (D, -2)])
    m.spot('bumblebee_1', g + 1.0, gain=-15, sweep=(0.6, -0.4), start=1.0, length=2.6, fi=0.5, fo=0.8, trim=False,
           label='a bee crosses the low sun at the grass')
    # under the turf: the meadow muffled above, a close earthy room, then each find on the word that names it
    m.bed('countryside', start=24, gain=-4, lp=650, t0=c - 0.3, t1=dp + 0.6, fi=0.6, fo=0.8)
    for k, t in enumerate(np.arange(EV['mole'], EV['mole'] + 2.2, 1 / 2.2)):
        m.spot('steps_mud', t, gain=-24 + 2 * (k % 2), p=-0.35, start=0.5 + 0.43 * (k % 18), length=0.2, lp=2500, fo=0.08,
               label='the mole digs (paw strokes)')
    m.spot('dig_shovel', EV['mole'] + 2.4, gain=-21, p=-0.35, start=3.0, length=0.6, lp=2200, fo=0.2, label='a dirt trickle')
    m.spot('candle_sparkle_2', EV['chest'] + 0.15, gain=-22, p=0.3, length=1.6, hp=1500, fi=0.1, fo=0.6, trim=False,
           label='the chest leaks a glint of gold')
    m.spot('dig_shovel', EV['jar'] + 0.1, gain=-22, p=0.2, start=7.0, length=0.5, lp=1800, fo=0.2,
           label='earth settles round the Roman jar')
    # deep time: the stone, a slow fall through the years, a single drip in the giant's chamber
    m.bed('cave_1', start=8, gain=-9, lp=900, t0=dp - 0.6, t1=tp + 0.4, fi=1.2, fo=1.0)
    y0, y1 = EV['years']
    m.spot('whoosh_3', y0, gain=-17, length=y1 - y0 + 1.2, lp=900, speed=0.6, fi=0.6, fo=0.8, trim=False,
           label='the years roll into millions (slow, low)')
    m.spot('fall_of_stone', y1 + 0.3, gain=-21, lp=600, length=1.4, fi=0.3, fo=0.8, trim=False, label='deep stone settles')
    for k, t in enumerate((EV['bones'] - 0.6, EV['bones'] + 0.9)):
        m.spot('drops_1', t, gain=-24 - 3 * k, p=(0.2, -0.1)[k], length=0.5, hp=400, fo=0.2, label='a drip in the giant\'s chamber')
    # back on top: a breath of wind as the light bursts round the tree; the meadow full again to the end card
    m.spot('wind_plain', tp + 1.5, gain=-17, hp=150, start=50, length=2.4, fi=0.8, fo=1.2, trim=False, label='the sun bursts round the tree')
    y, info = score()
    m.music(y, under=10.0, info=info)
    m.master(HERE, fi=1.0, fo=2.5, notes='golden meadow from above (birds, the river, wind), crickets and a bee at the grass; '
             'muffled under the turf with the mole, a glint of gold and the Roman jar; deep stone and a slow fall through '
             'the years to a drip by the giant; the meadow full again for the end; harp and strings in D, low and still in '
             'deep time, the flute when we come back up')


def score():
    """Harp and strings in D, light: the meadow (Dadd9), down the layers (Bm7, Gmaj7) quieter, deep time a low held
    D and A with nothing on top, back on top resolved with the flute, holding to the end card."""
    s = MK.Score(seed=53)
    for t, d, ch in ((0.0, 7.6, [38, 50, 57, 64, 66]), (7.2, 6.0, [43, 55, 62, 66, 69]), (12.8, 5.0, [47, 59, 62, 66, 69]),
                     (17.6, 5.0, [43, 55, 59, 62, 66]), (22.2, 7.2, [26, 38, 45, 50]), (29.0, 10.9, [38, 50, 57, 62, 66, 69])):
        s.pad(t, d, ch, vel=0.42)
    harp = [(1.0, 62), (1.4, 66), (1.8, 69), (2.2, 74), (4.2, 69), (4.6, 74), (5.0, 76), (8.0, 67), (8.4, 71), (8.8, 74),
            (10.4, 71), (10.8, 74), (13.4, 66), (14.6, 62), (15.2, 66), (17.6, 67), (19.25, 62), (20.6, 59),
            (30.0, 62), (30.4, 66), (30.8, 69), (31.2, 74), (33.2, 69), (33.6, 74), (34.0, 78), (36.0, 74)]
    for t, n in harp:
        s.note('harp', n, t, ring=2.5, vel=0.36, pan=-0.2)
    for t, n, d in ((3.0, 74, 1.2), (4.4, 76, 1.4), (31.6, 78, 1.0), (32.8, 81, 1.4), (34.6, 78, 1.0), (35.8, 74, 3.0)):
        s.note('flute', n, t, dur=d, vel=0.42, pan=0.15)
    y = s.render(env=[(0, -3), (7, -2), (12.6, -3), (21.8, -5), (23, -7), (28.6, -7), (30, -1), (D, -2)])
    return y, {'engine': MK.engine(), 'voices': sorted(s.used), 'key': 'D',
               'turn': 'deep time, 22.4 to 29 s (the music thins to a low D and A)'}


if __name__ == '__main__':
    main()
