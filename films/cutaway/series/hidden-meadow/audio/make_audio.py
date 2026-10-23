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
import audio_kit as K  # noqa: E402
import music_kit as MK  # noqa: E402

EV = {
    'meadow': (0.0, 6.0),
    'bees': [1.4, 4.2],
    'below': (6.0, 12.5),          # crane down: warren, mole, fox den, ants
    'mole': [7.9, 8.5, 9.2],
    'ants': (10.9, 12.4),
    'shadow': 12.7,                # the hawk's shadow reaches the block (passes to about 14.6)
    'go': 13.45,                   # the rabbits bolt
    'run': [13.5, 13.75, 14.0, 14.3],
    'safe': 15.3,                  # they land in the warren
    'calm': 16.4,
}


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
    y = s.render(env=[(0, -2), (6, -4), (12.4, -4), (12.8, -16), (16.0, -16), (17.0, -1), (20, -2)])
    return y, {'engine': MK.engine(), 'voices': sorted(s.used), 'key': 'G', 'turn': 'the hawk, 12.7 to 16.4 s (the music falls away)'}


def main():
    m = K.Mix(seed=7)
    b0, b1 = EV['below']; sh = EV['shadow']; cm = EV['calm']
    top = [(0, 0), (b0 - 0.3, 0), (b0 + 0.7, -40), (b1 - 0.4, -40), (b1, -6), (sh - 0.1, -6), (sh + 0.4, -45),
           (cm - 0.2, -45), (cm + 1.6, 0), (20, 0)]
    m.bed('birds_waking_3', start=60, gain=-6, hp=300, t0=0, t1=20, fi=0.8, fo=1.0, env=top)
    m.bed('field_cricket', start=3, gain=-19, hp=2500, t0=0, t1=20, fi=1.0, fo=1.0, env=top)
    for k, t in enumerate(EV['bees']):
        m.spot(('bumblebee_1', 'bumblebee_2')[k], t, gain=-15, sweep=((0.6, -0.2), (-0.5, 0.3))[k], start=1.0, length=2.4,
               fi=0.5, fo=0.8, trim=False, label='a bee crosses')
    # under the soil: the meadow muffled above, the mole's earth, the ants
    m.bed('birds_waking_3', start=60, gain=-5, lp=600, t0=b0 - 0.5, t1=b1 + 0.3, fi=0.8, fo=0.6)
    m.bed('countryside', start=24, gain=-2, lp=700, t0=b0 - 0.5, t1=b1 + 0.3, fi=0.8, fo=0.6)
    m.bed('field_cricket', start=3, gain=-22, lp=1500, t0=b0 - 0.5, t1=b1 + 0.3, fi=0.8, fo=0.6)
    for k, t in enumerate(EV['mole']):
        m.spot('dig_shovel', t, gain=-7, p=-0.2, start=3.0 + 4.0 * k, length=0.6, lp=2200, fo=0.2, label='the mole digs')
    a0, a1 = EV['ants']
    m.spot('steps_mud', a0, gain=-17, p=0.3, length=a1 - a0, hp=3000, fi=0.4, fo=0.5, trim=False, label='ants scratching')
    # the hawk: everything stops, wings pass, the rabbits run and land in the warren
    m.spot('flight_bird_1', sh + 0.2, gain=-12, sweep=(-0.6, 0.6), length=2.4, hp=150, fo=0.6, label='hawk wings pass over')
    for k, t in enumerate(EV['run']):
        m.spot('steps_mud', t, gain=-18 - k, p=-0.1 * k, start=1.5 + 1.1 * k, length=0.25, lp=900, fo=0.1, label='rabbits bolt')
    for k, t in enumerate((EV['safe'] - 0.15, EV['safe'] + 0.1)):
        m.spot('steps_mud', t, gain=-20, p=(-0.15, 0.1)[k], start=6.2 + 1.2 * k, length=0.25, lp=600, fo=0.1, label='safe in the warren')
    y, info = score()
    m.music(y, under=10.0, info=info)
    m.master(HERE, notes='birdsong, crickets and bees above; muffled below with the mole and the ants; silence and wings for '
                         'the hawk, the rabbits run; the meadow breathes again')


if __name__ == '__main__':
    main()
