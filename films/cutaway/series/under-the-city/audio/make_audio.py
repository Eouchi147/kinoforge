#!/usr/bin/env python3
"""Sound for Under the City (20 s, no music, no voice): real recordings only (BigSoundBank CC0, release sfx-bank;
sources in ../../SOUND.md). City sounds are this place's nature; everything is diegetic.

    python3 films/cutaway/series/under-the-city/audio/make_audio.py   # writes audio/mix.m4a + mix.json (mix.wav local)

Story: a dusk street on top; the camera sinks through pipes, the sewer with its rat, the metro tunnel as a train rushes
past, old bricks, a Roman floor, a T. rex at the bottom; then the whole block at nightfall. The sound sinks with the
camera: the street closes over us, water in the pipes and the sewer, the rat, the metro as the one loud moment, then
stillness and drips in old stone, near silence by the skull, and the city faintly back for the wide end.
Event times: the "Events for the sound designer" table in ../NOTES.md (23 Oct, first build).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import audio_kit as K  # noqa: E402
import music_kit as MK  # noqa: E402

EV = {
    'street': (0.0, 4.5),          # dusk street; the bus left to right in the near lane
    'bus_centre': 2.4,
    'descent': 4.5,                # the street closes over us
    'pipes': (4.5, 7.0),
    'drips': [6.7, 8.4, 10.1],
    'rat_in': (6.9, 7.9),          # scurry in
    'squeak': 8.4,
    'sewer': (7.0, 10.3),
    'rumble': 9.6,                 # the train is coming
    'rat_bolt': (10.0, 10.5),
    'train_centre': 10.74,         # nose at frame centre, left to right
    'bricks': 12.4,                # a trickle of grit
    'roman': 13.9,                 # a slow drip in stone
    'skull': (14.8, 15.5),         # near silence
    'wide': 15.5,                  # the whole block: the city faintly back
    'train2_centre': 18.1,         # second train below, right to left, far
}


def score():
    """Warm pad with a distant pulse in A minor: dusk (Am9), down through the pipes (Fmaj7) and the sewer (Dm9) with a
    soft low pulse, the metro as the turn (E sus, the swell at 10.7 s), stillness by the bones, and the city at
    nightfall resolved in C major; a soft harp in the middle register stands in for an electric piano."""
    s = MK.Score(seed=37)
    for t, d, ch in ((0.0, 4.9, [45, 52, 59, 60, 64]), (4.4, 4.2, [41, 53, 57, 60, 64]), (8.3, 3.2, [38, 50, 57, 60, 64]),
                     (11.2, 4.4, [40, 52, 57, 59, 64]), (15.4, 4.6, [36, 48, 55, 59, 64, 67])):
        s.pad(t, d, ch, vel=0.45, att=2.0)
    for k in range(9):
        s.note('cello_pizz', 45, 4.7 + 1.15 * k, ring=1.4, vel=0.32, gain=-5, pan=0.0)
    for t, m in ((0.6, 64), (1.5, 67), (2.5, 72), (3.6, 71), (16.0, 67), (16.8, 71), (17.7, 74), (18.6, 72)):
        s.note('harp', m, t, ring=3.0, vel=0.35, pan=0.15)
    y = s.render(env=[(0, -3), (4.5, -3), (9.6, -2), (10.8, 1), (12.4, -4), (14.8, -9), (15.6, -3), (20, -3)], lp=6500)
    return y, {'engine': MK.engine(), 'voices': sorted(s.used), 'key': 'A minor to C', 'turn': 'the metro, 10.74 s'}


def main():
    m = K.Mix(seed=5)
    d = EV['descent']; w = EV['wide']
    # the street at dusk (traffic far off, a few birds), closing over us as we sink, faintly back for the wide end
    m.bed('paris_by_night', start=8, gain=-7, t0=0, t1=d + 1.5, fi=0.8, fo=1.5, env=[(0, 0), (d - 0.3, 0), (d + 1.5, -30)])
    m.bed('paris_by_night', start=8, gain=-12, lp=450, t0=d - 1.0, t1=7.5, fi=1.0, fo=1.5)
    m.bed('evening_birds', start=33, gain=-16, hp=1200, t0=0, t1=d + 0.5, fi=0.6, fo=1.0)
    m.spot('london_bus', EV['bus_centre'] - 2.2, gain=-7, sweep=(-0.7, 0.7), start=36.3, length=4.6, fi=0.6, fo=1.2,
           trim=False, label='bus passes left to right')
    m.spot('steam_hiss_1', 0.3, gain=-24, p=0.25, length=4.0, lp=2500, fi=0.8, fo=1.5, trim=False, label='manhole steam')
    # pipes and the sewer: running water, drips, the rat
    p0, p1 = EV['pipes']; s0, s1 = EV['sewer']
    m.bed('sewer_1', start=2, gain=-8, lp=2500, t0=p0, t1=s1 + 0.6, fi=1.2, fo=0.8,
          env=[(p0, -6), (s0, 0), (s1, 0)])
    for k, t in enumerate(EV['drips']):
        m.spot('drops_4', t, gain=-12, p=(-0.3, 0.2, -0.1)[k], start=2.0 * k, length=0.9, fo=0.3, label='drip into the sewer')
    r0, r1 = EV['rat_in']
    for k, t in enumerate([r0 + 0.12 * i for i in range(int((r1 - r0) / 0.12))]):
        m.spot('pencil_2', t, gain=-30, p=-0.2 + 0.05 * k, start=0.3 + 0.37 * k, length=0.07, hp=2500, fo=0.02, label='rat claws')
    m.spot('mouse_screams', EV['squeak'], gain=-20, p=0.1, start=0, length=0.5, hp=1500, fo=0.12, label='rat squeaks')
    b0, b1 = EV['rat_bolt']
    for k, t in enumerate([b0 + 0.08 * i for i in range(6)]):
        m.spot('pencil_2', t, gain=-28, p=0.1 - 0.15 * k, start=2.0 + 0.29 * k, length=0.06, hp=2500, fo=0.02, label='rat bolts')
    # the metro: the far rumble from 9.6, the roar peaks with the nose at centre, then away (left to right)
    tc = EV['train_centre']
    m.spot('train_passage_1', tc - 2.0, gain=-3, sweep=(-0.6, 0.6), start=2.5, length=4.6, fi=1.0, fo=1.6, trim=False,
           label='metro roars past')
    m.spot('train_passage_1', EV['rumble'], gain=-14, start=1.0, length=1.6, lp=200, fi=0.8, fo=0.6, trim=False,
           label='rumble before the train')
    # old stone: stillness, grit, a slow drip, near silence by the skull
    m.bed('cave_2', start=3, gain=-4, t0=11.3, t1=20, fi=1.5, fo=1.0, env=[(11.3, 0), (EV['skull'][0], -4), (w, -6), (20, -10)])
    m.spot('fall_of_stone', EV['bricks'], gain=-24, p=0.3, start=12.0, length=1.2, hp=1500, fo=0.5, label='a trickle of grit')
    m.spot('drops_3', EV['roman'], gain=-14, p=-0.3, length=1.4, fo=0.6, label='slow drip on the Roman floor')
    # the wide end: the city faintly back on top, the second train far below (right to left)
    m.bed('paris_by_night', start=40, gain=-16, lp=1800, t0=w - 0.2, t1=20, fi=1.5, fo=1.0)
    m.spot('london_bus', w, gain=-22, lp=1500, sweep=(-0.6, 0.0), start=36.3, length=4.5, fi=1.0, fo=1.0, trim=False,
           label='faint bus on top')
    m.spot('train_passage_1', EV['train2_centre'] - 2.0, gain=-15, lp=350, sweep=(0.5, -0.5), start=2.5, length=3.6, fi=1.0,
           fo=1.2, trim=False, label='second train far below')
    m.room(rt60=0.9, wet=0.12, seed=23)
    y, info = score()
    m.music(y, under=10.0, info=info)
    m.master(HERE, notes='street at dusk with a bus and steam, water in pipes and sewer, drips, the rat, the metro, '
                         'stillness in old stone, the city faintly back with a far train')


if __name__ == '__main__':
    main()
