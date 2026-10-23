#!/usr/bin/env python3
"""Sound for The Gold Mine (20 s, 9:16, no music, no voice): real recordings only (BigSoundBank CC0, release sfx-bank;
sources in ../../SOUND.md). Every sound is something we see or feel.

    python3 films/cutaway/series/gold-mine/audio/make_audio.py   # writes audio/mix.m4a + mix.json (mix.wav local)

Story (blender.py, 23 Oct): a miner walks into the mine at night (night 0 to 6 s); inside, the work goes on as the camera
cranes down the face (descent 6 to 14 s): the ore cart rolls, a climber goes down the ladder, two diggers swing, until
the deepest miner's pick strikes the gold vein in a burst of sparks; the ring of it wakes the bats, which burst out of
the cavern and pour out of the mine entrance across the moon (flight 14 to 20 s).
The sound: wind, crickets and an owl on the mountain, the miner's steps; inside, the mine's air and drips, the cart's
squeal, a ladder creaking, far pick ticks, three blows (the last one rings), bats waking, then the flight into the night.
Event times: blender.py constants (STRIKES, T_BATS, T_OUT, the cart and ladder windows); NOTES.md table when it lands.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import audio_kit as K  # noqa: E402

EV = {
    'night': (0.0, 6.0),
    'walk': (0.6, 5.4),            # the miner walks into the mine
    'inside': 6.0,                 # descent shot: the cut face, inside
    'cart': (1.5, 10.5),           # the cart rolls down the top gallery (heard once we are on the face)
    'ladder': (5.6, 12.6),         # the climber goes down (18 rungs)
    'diggers': ((0.3, 1.15), (0.85, 1.4)),   # middle gallery: first blow, period
    'strikes': (8.6, 9.8, 11.0),   # the gold miner's blows; the last finds the gold (sparks, flash)
    'bats_wake': 11.45,
    'bats_out': 14.15,             # flight shot: bats pour out of the entrance across the moon
}


def main():
    m = K.Mix(seed=13)
    n0, n1 = EV['night']; i0 = EV['inside']; out = EV['bats_out']
    # the mountain at night: wind, crickets, an owl; back outside for the flight
    night_env = [(0, 0), (i0 - 0.4, 0), (i0 + 0.8, -30), (out - 0.6, -30), (out + 0.2, -3), (20, -3)]
    m.bed('wind_plain', start=10, gain=-9, hp=80, t0=0, t1=20, fi=0.8, fo=1.0, env=night_env)
    m.bed('campaign_night_1', start=5, gain=-15, hp=1500, t0=0, t1=20, fi=0.8, fo=1.0, env=night_env)
    m.spot('owl_tawny', 1.2, gain=-21, p=-0.5, length=2.0, hp=300, fo=0.5, label='an owl on the mountain')
    w0, w1 = EV['walk']
    for k in range(int((w1 - w0) / 0.55)):
        m.spot('steps_gravel_1', w0 + 0.55 * k, gain=-22 + 0.4 * k, p=0.15, start=0.4 + 0.55 * k, length=0.45, hp=150, fo=0.12,
               label='the miner walks in')
    # inside: the mine's air, drips, lanterns
    m.bed('cave_1', start=4, gain=-7, t0=i0 - 0.6, t1=out + 0.6, fi=1.0, fo=0.8)
    m.bed('candle_sparkle_2', start=3, gain=-24, hp=400, p=0.2, t0=i0, t1=out, fi=1.0, fo=0.6)
    c1 = EV['cart'][1]
    m.spot('squeaky_barrow_4', i0 - 0.3, gain=-14, sweep=(-0.4, 0.1), start=2.0, length=c1 - i0 + 0.3, fi=0.5, fo=0.6, trim=False,
           send=-6, label='cart wheels squeal')
    m.spot('steam_between_wagons', i0 - 0.3, gain=-17, lp=1200, sweep=(-0.4, 0.1), start=8.0, length=c1 - i0 + 0.3, fi=0.6, fo=0.6,
           trim=False, label='cart rumble on the rails')
    l0, l1 = EV['ladder']
    for k in range(6):
        t = max(i0 + 0.2, l0) + k * (l1 - max(i0 + 0.2, l0)) / 6
        m.spot('squeaky_steps_1', t, gain=-21, p=0.05, start=1.0 + 2.3 * k, length=0.5, fo=0.15, send=-8, label='ladder rung creaks')
    for t0, per in EV['diggers']:
        for t in [t0 + k * per for k in range(40)]:
            if 7.0 < t < 12.4:
                m.spot('hammer_concrete', t, gain=-27, p=-0.35, lp=2500, length=0.4, fo=0.2, send=-4, label='diggers far off')
    # the gold miner: two blows on rock, the third rings and throws sparks
    for k, t in enumerate(EV['strikes']):
        m.spot('hammer_concrete', t, gain=-11 + 2 * k, p=0.3, length=0.8, hp=100, fo=0.3, send=-4, label='pick strikes rock')
        m.spot('fall_of_stone', t + 0.04, gain=-21, p=0.3, start=2.0 + 3.0 * k, length=0.8, fo=0.4, label='chips fall')
    tg = EV['strikes'][-1]
    m.spot('anvil_1', tg, gain=-13, p=0.3, length=2.4, lp=7000, fo=1.6, send=-2, label='the strike rings: gold')
    m.spot('fire_foley', tg + 0.02, gain=-14, p=0.3, start=8.0, length=0.9, hp=1500, fo=0.5, label='sparks')
    # the bats wake, then pour out across the moon
    b = EV['bats_wake']
    m.spot('bats', b, gain=-18, p=0.2, start=0.0, length=out - b + 0.4, hp=800, fi=0.4, fo=0.3, trim=False, send=-6,
           label='bats wake in the cavern')
    m.spot('flight_bird_1', b + 0.5, gain=-20, p=0.25, length=2.0, send=-6, label='wings in the cavern')
    m.spot('flight_pigeon', b + 1.4, gain=-18, p=0.0, length=2.0, send=-6, label='wings in the cavern')
    m.spot('bats', out, gain=-14, sweep=(-0.3, 0.5), start=9.0, length=20 - out, hp=800, fi=0.3, fo=2.0, trim=False,
           label='bats pour out across the moon')
    for k, t in enumerate((out + 0.05, out + 0.45, out + 0.9, out + 1.6)):
        m.spot(('flight_pigeon', 'flight_bird_1', 'flight_bird_2', 'flight_pigeon')[k], t, gain=-13 - 2 * k,
               p=(-0.3, 0.2, 0.5, 0.0)[k], length=2.0, label='wings rush out')
    m.room(rt60=1.6, wet=0.5, seed=17)
    m.master(HERE, notes='night wind, crickets, owl and the miner\'s steps; cave air and lanterns; cart, ladder, far diggers; '
                         'three blows, the last rings with sparks; bats wake and pour out across the moon')


if __name__ == '__main__':
    main()
