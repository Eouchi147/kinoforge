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
    'owl': 2.0,
    'walk': (0.6, 5.4),            # the miner walks across the gravel yard into the entrance
    'inside': 6.0,                 # cut inside the mountain
    'cart': (1.5, 10.5),           # the cart rolls along the top gallery (muffled until 6.0); a clunk when it stops
    'ladder': (5.6, 12.6),         # a rung about every 0.39 s
    'diggers': ([6.05, 7.2, 8.35, 9.5, 10.65, 11.8, 12.95], [6.45, 7.85, 9.25, 10.65, 12.05, 13.45]),
    'strikes': (8.6, 9.8, 11.0),   # the gold miner's blows; the last finds the gold (sparks, flash)
    'shiver': 11.0,                # the bats shiver on the ceiling
    'bats_wake': 11.45,            # they drop and burst toward the camera
    'lens': 12.9,                  # they pass the lens (12.5 to 13.5)
    'outside': 14.0,               # cut outside: the wind returns
    'bats_out': (14.15, 17.9),     # 34 bats pour out of the entrance, thinning
}


def main():
    m = K.Mix(seed=13)
    i0 = EV['inside']; o0 = EV['outside']; b0, b1 = EV['bats_out']
    # the mountain at night: wind in the pines, crickets, an owl; back outside for the flight
    night_env = [(0, 0), (i0 - 0.15, 0), (i0 + 0.5, -32), (o0 - 0.15, -32), (o0 + 0.4, -2), (20, 0)]
    m.bed('wind_plain', start=10, gain=-9, hp=80, t0=0, t1=20, fi=0.8, fo=1.2, env=night_env)
    m.bed('campaign_night_1', start=5, gain=-16, hp=1500, t0=0, t1=20, fi=0.8, fo=1.2,
          env=[(0, 0), (i0 - 0.15, 0), (i0 + 0.5, -32), (o0, -32), (15.0, -8), (20, 0)])
    m.spot('owl_tawny', EV['owl'], gain=-21, p=-0.5, length=2.0, hp=300, fo=0.5, label='an owl on the mountain')
    w0, w1 = EV['walk']
    for k in range(int((w1 - w0) / 0.55)):
        m.spot('steps_gravel_1', w0 + 0.55 * k, gain=-22 + 0.4 * k, p=0.15, start=0.4 + 0.55 * k, length=0.45, hp=150, fo=0.12,
               label='the miner walks in')
    m.spot('squeaky_steps_1', 2.3, gain=-30, p=0.15, start=13.0, length=0.4, hp=900, fo=0.1, label='the lantern handle creaks')
    # inside: the mine's air, drips every 1 to 2 s, lanterns
    m.bed('cave_1', start=4, gain=-7, t0=i0 - 0.15, t1=o0 + 0.5, fi=0.3, fo=0.6)
    m.bed('candle_sparkle_2', start=3, gain=-25, hp=400, p=0.2, t0=i0, t1=o0, fi=1.0, fo=0.5)
    for k, t in enumerate((6.7, 8.1, 9.3, 10.9, 12.4, 13.6)):
        m.spot('drops_1', t, gain=-19, p=(-0.5, 0.4, -0.2, 0.5, -0.4, 0.2)[k], start=(0, 3, 5, 7, 11, 13)[k], length=0.7, fo=0.3,
               send=-3, label='a drip')
    c0, c1 = EV['cart']
    m.spot('squeaky_barrow_4', c0, gain=-14, sweep=(-0.4, 0.1), start=2.0, length=c1 - c0, fi=0.5, fo=0.25, trim=False, send=-6,
           lp=None, label='cart wheels on the rails')
    m.spot('steam_between_wagons', c0, gain=-16, lp=1200, sweep=(-0.4, 0.1), start=6.0, length=c1 - c0, fi=0.6, fo=0.25,
           trim=False, label='cart rumble')
    m.spot('iron_bar_fall_2', c1 - 0.02, gain=-20, p=0.1, length=0.9, lp=2500, fo=0.4, send=-4, label='the cart stops: a clunk')
    l0, l1 = EV['ladder']
    for k in range(9):
        t = l0 + 0.78 * k
        m.spot('squeaky_steps_1', t, gain=-23 - (t < i0) * 10, p=0.05, start=1.0 + 2.3 * k % 26, length=0.45, fo=0.15, send=-8,
               label='ladder creaks')
    for far, times in enumerate(EV['diggers']):
        for t in times:
            m.spot('hammer_concrete', t, gain=-24 - 4 * far, p=-0.35 + 0.15 * far, lp=3000 - 800 * far, length=0.4, fo=0.2, send=-3,
                   label='diggers\' picks')
    # the gold miner: two blows on quartz, the third rings and throws sparks
    for k, t in enumerate(EV['strikes']):
        m.spot('hammer_concrete', t, gain=-11 + 2 * k, p=0.3, length=0.8, hp=100, fo=0.3, send=-4, label='pick strikes quartz')
        if k < 2:
            m.spot('anvil_1', t + 0.005, gain=-30, p=0.3, length=0.25, hp=1500, lp=9000, fo=0.1, send=-2, label='bright click')
    tg = EV['strikes'][-1]
    m.spot('anvil_1', tg + 0.005, gain=-12, p=0.3, length=2.4, lp=8000, fo=1.6, send=-2, label='the strike rings: gold')
    m.spot('fire_foley', tg + 0.02, gain=-15, p=0.3, start=8.0, length=0.9, hp=1500, fo=0.5, label='sparks')
    m.spot('fall_of_stone', tg + 0.06, gain=-22, p=0.3, start=8.0, length=0.9, hp=300, fo=0.4, label='a scatter of chips')
    # the bats: a shiver, the burst toward the lens, the flight out across the moon
    m.spot('cloth', EV['shiver'], gain=-20, p=0.2, length=0.5, hp=1500, fi=0.1, fo=0.2, trim=False, label='bats shiver')
    bw = EV['bats_wake']
    m.spot('bats', bw, gain=-16, p=0.2, start=0.0, length=o0 - bw + 0.2, hp=800, fi=0.2, fo=0.3, trim=False, send=-6,
           label='bats squeak as they drop')
    for k, t in enumerate((bw + 0.05, bw + 0.4, bw + 0.8, bw + 1.3)):
        m.spot(('flight_pigeon', 'flight_bird_1', 'flight_bird_2', 'flight_pigeon')[k], t, gain=-15 - k, p=(-0.2, 0.3, 0.0, -0.3)[k],
               length=1.8, send=-6, label='wings burst')
    m.spot('whoosh_4', EV['lens'] - 0.3, gain=-12, sweep=(-0.5, 0.5), length=1.0, label='bats pass the lens')
    m.spot('bats', b0, gain=-14, sweep=(-0.3, 0.5), start=9.0, length=20 - b0, hp=800, fi=0.3, fo=2.5, trim=False,
           label='bats pour out toward the moon')
    for k, t in enumerate([b0 + 0.05 + 0.42 * j for j in range(9)]):
        m.spot(('flight_pigeon', 'flight_bird_1', 'flight_bird_2')[k % 3], t, gain=-12 - 1.6 * k, p=(-0.3, 0.2, 0.5)[k % 3] * (1 - k / 10),
               length=1.6, label='dense wing flutter, thinning')
    m.room(rt60=1.6, wet=0.5, seed=17)
    m.master(HERE, notes='night wind, crickets, owl and the miner\'s steps; cave air, drips, lanterns; cart, ladder, diggers; '
                         'three blows, the last rings with sparks; bats shiver, burst past the lens and pour out toward the moon')


if __name__ == '__main__':
    main()
