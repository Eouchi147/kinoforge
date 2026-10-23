#!/usr/bin/env python3
"""Sound for The Hidden Meadow (20 s, 9:16, no music, no voice): real recordings only (BigSoundBank CC0, release
sfx-bank; sources in ../../SOUND.md). Every sound is something we see or feel; rabbits and foxes are silent here.

    python3 films/cutaway/series/hidden-meadow/audio/make_audio.py   # writes audio/mix.m4a + mix.json (mix.wav local)

Story (blender.py, 23 Oct): a spring meadow in morning light, bees, rabbits grazing (meadow 0 to 6 s); the camera cranes
down the cut face past the warren, a mole digging, a fox den with cubs, the ant nest (below 6 to 12.5 s); a hawk's
shadow reaches the block (12.7 s), the rabbits look up (13.25 s) and bolt (13.45 s), arrive safe in the warren (15.3 s),
calm returns (16.4 s) and the camera pulls back to the whole block.
The sound: birdsong, crickets and bees above; under the soil the meadow is muffled and close sounds take over (the
mole's earth, the ants' tiny scratching); when the shadow comes the birds and crickets stop (silence is the warning),
wings pass, the rabbits' soft thumps as they run and land in the warren; then the meadow breathes again.
Event times: blender.py constants (T_SHADOW, T_ALARM, T_GO, T_SAFE, T_CALM) and its shot list; NOTES.md table when it lands.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import numpy as np
import audio_kit as K  # noqa: E402
import music_kit as MK  # noqa: E402

EV = {
    'meadow': (0.0, 6.0),
    'bees': [1.5, 4.0],            # bees cross close to camera, one near 2.6 s
    'below': (6.0, 12.5),          # cut below: everything above muffles, a close earthy tone
    'mole': (6.0, 11.0),           # paw strokes about 2.2 a second
    'cub_lands': [6.68, 9.28, 11.88],
    'ants': (7.5, 12.5),
    'hush': 12.5,                  # the shadow reaches the block: birdsong stops
    'wings': [13.08, 13.70],       # two slow wing beats overhead (13.08 to 14.32)
    'bolt': [13.45, 13.63],        # rabbits bolt: quick thumps on turf
    'drop': [13.86, 14.07],        # into the burrow mouth: a soft scuffle
    'gust': 14.0,
    'arrive': [15.10, 15.38],      # in chamber A: a muffled scrabble, then stillness
    'calm': 16.4,                  # birdsong returns, the bed swells gently to the end
}


def main():
    m = K.Mix(seed=7)
    b0, b1 = EV['below']; hu = EV['hush']; cm = EV['calm']
    top = [(0, 0), (b0 - 0.15, 0), (b0 + 0.4, -40), (b1 - 0.15, -40), (b1 + 0.1, -8), (hu + 0.3, -45),
           (cm - 0.2, -45), (cm + 1.6, 0), (20, 1)]
    m.bed('birds_waking_3', start=60, gain=-6, hp=300, t0=0, t1=20, fi=0.8, fo=1.5, env=top)
    m.bed('field_cricket', start=3, gain=-19, hp=2500, t0=0, t1=20, fi=1.0, fo=1.5, env=top)
    m.bed('wind_plain', start=40, gain=-24, hp=200, t0=0, t1=20, fi=1.0, fo=1.5, env=top)
    for k, t in enumerate(EV['bees']):
        m.spot(('bumblebee_1', 'bumblebee_2')[k], t, gain=-14 - 3 * k, sweep=((0.6, -0.4), (-0.5, 0.3))[k], start=1.0, length=2.4,
               fi=0.5, fo=0.8, trim=False, label='a bee crosses close')
    # below: the meadow muffled above, a close earthy tone, the mole, the cubs, the ants
    m.bed('birds_waking_3', start=60, gain=-5, lp=600, t0=b0 - 0.2, t1=b1 + 0.2, fi=0.3, fo=0.4)
    m.bed('countryside', start=24, gain=-2, lp=700, t0=b0 - 0.2, t1=b1 + 0.2, fi=0.3, fo=0.4)
    m0, m1 = EV['mole']
    for k, t in enumerate(np.arange(m0 + 0.2, m1, 1 / 2.2)):
        m.spot('steps_mud', t, gain=-25 + 2 * (k % 2), p=0.4, start=0.5 + 0.43 * (k % 18), length=0.2, lp=2500, fo=0.08,
               label='the mole digs (paw strokes)')
    for k, t in enumerate((7.3, 9.6)):
        m.spot('dig_shovel', t, gain=-19, p=0.4, start=3.0 + 4.0 * k, length=0.6, lp=2200, fo=0.2, label='a dirt trickle')
    for k, t in enumerate(EV['cub_lands']):
        m.spot('steps_mud', t, gain=-20, p=0.25, start=6.0 + 0.9 * k, length=0.25, lp=800, fo=0.1, label='a fox cub lands on straw')
        m.spot('cloth', t + 0.03, gain=-28, p=0.25, start=2.0 + 2.0 * k, length=0.35, hp=800, fo=0.15, label='straw rustles')
    a0, a1 = EV['ants']
    m.spot('steps_mud', a0, gain=-22, p=-0.3, length=a1 - a0, hp=3000, fi=0.6, fo=0.5, trim=False, label='ants scratching')
    # the hawk: the hush, two slow wing beats, the rabbits bolt and drop, a gust, a muffled scrabble, stillness
    for k, t in enumerate(EV['wings']):
        m.spot(('flight_pigeon', 'flight_bird_1')[k], t, gain=-11, sweep=(-0.5 + 0.5 * k, 0.5 * k), speed=0.7, lp=3000, length=1.2,
               fo=0.5, label='slow wing beat overhead')
    for k, t in enumerate(EV['bolt']):
        m.spot('steps_mud', t, gain=-17, p=(-0.1, 0.1)[k], start=1.5 + 1.1 * k, length=0.22, lp=1200, fo=0.08, label='a rabbit bolts')
    for k, t in enumerate(EV['drop']):
        m.spot('dig_shovel', t, gain=-20, p=(-0.1, 0.1)[k], start=12.0 + 4 * k, length=0.4, lp=2500, fo=0.15, label='into the burrow')
    m.spot('wind_plain', EV['gust'] - 0.3, gain=-16, hp=150, start=50, length=1.6, fi=0.5, fo=0.9, trim=False, label='a gust as the shadow passes')
    for k, t in enumerate(EV['arrive']):
        m.spot('steps_mud', t, gain=-22, p=(-0.15, 0.1)[k], start=6.2 + 1.2 * k, length=0.25, lp=600, fo=0.1, label='safe in the warren')
    y, info = score()
    m.music(y, under=10.0, info=info)
    m.master(HERE, notes='birdsong, crickets and bees above; below, muffled, the mole, the fox cubs and the ants; a hush, two '
                         'slow wing beats, the rabbits run and land; the meadow breathes again; flute and pizzicato that fall '
                         'silent for the hawk')


def score():
    """Flute and pizzicato, light, in G: the meadow (Gadd9) with a skipping pizzicato and a flute phrase, the homes
    below (Em7, Cmaj7) quieter, then the music stops with the birds when the hawk's shadow comes (only a low D held),
    and returns resolved (G) with the flute when calm comes back."""
    s = MK.Score(seed=41)
    for t, d, ch in ((0.0, 6.4, [43, 55, 62, 69, 71]), (6.0, 3.6, [40, 52, 59, 62, 67]), (9.2, 3.6, [36, 48, 55, 59, 64]),
                     (12.4, 4.4, [38, 50]), (16.2, 3.8, [43, 55, 62, 67, 71, 74])):
        s.pad(t, d, ch, vel=0.42)
    for t, m in ((1.2, 67), (1.5, 71), (1.8, 74), (3.0, 72), (3.3, 71), (4.5, 67), (4.8, 71), (7.1, 64), (8.0, 67),
                 (10.0, 64), (11.0, 62), (17.0, 71), (17.3, 74), (17.6, 79)):
        s.note('pizz', m, t, ring=1.2, vel=0.38, pan=-0.25)
    for t, m, d in ((2.3, 74, 1.1), (3.6, 76, 0.8), (4.6, 79, 1.5), (16.8, 74, 0.8), (17.8, 78, 0.7), (18.5, 79, 1.3)):
        s.note('flute', m, t, dur=d, vel=0.45, pan=0.15)
    y = s.render(env=[(0, -2), (6, -4), (12.2, -4), (12.6, -16), (16.2, -16), (17.2, -1), (20, -2)])
    return y, {'engine': MK.engine(), 'voices': sorted(s.used), 'key': 'G', 'turn': 'the hawk, 12.7 to 16.4 s (the music falls away)'}


if __name__ == '__main__':
    main()
