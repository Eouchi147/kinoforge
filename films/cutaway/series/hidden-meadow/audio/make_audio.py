#!/usr/bin/env python3
"""Sound for The Hidden Meadow (20 s, 9:16, no music, no voice): real recordings only (BigSoundBank CC0, release
sfx-bank; sources in ../../SOUND.md). Every sound is something we see or feel; rabbits are silent.

    python3 films/cutaway/series/hidden-meadow/audio/make_audio.py   # writes audio/mix.m4a + mix.json (mix.wav local)

Story: a spring meadow; below, a rabbit warren, an ant nest busy with ants, a mole digging, a fox den with cubs; a
hawk's shadow crosses and the rabbits dive underground. The sound: birdsong, crickets and a bee above; under the
soil the meadow is muffled and close sounds take over (the mole's earth, the ants' tiny scratching); when the hawk's
shadow crosses the birds stop (silence is the warning), wings pass, the rabbits' soft thumps as they dive; then the
meadow breathes again.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import audio_kit as K  # noqa: E402

# Events (s): from the film's NOTES.md event table when it lands, else the README story.
EV = {
    'meadow': (0.0, 5.0),     # spring meadow above
    'bee': 2.6,
    'below': (5.0, 12.5),     # warren, ants, mole, fox den
    'mole': [7.2, 7.9, 8.5],
    'ants': (9.0, 11.0),
    'hawk': 13.0,             # the shadow crosses (birds stop just before)
    'dive': [13.9, 14.3, 14.6],
    'calm': 16.5,             # the meadow breathes again
}


def main():
    m = K.Mix(seed=7)
    b0, b1 = EV['below']; hk = EV['hawk']
    # the meadow above: open (bright) up top, muffled under the soil, silent when the hawk crosses
    birds_env = [(0, 0), (b0 - 0.3, 0), (b0 + 0.7, -12), (b1, -10), (hk - 0.8, -10), (hk - 0.3, -40), (EV['calm'] - 0.4, -40),
                 (EV['calm'] + 1.2, -2), (20, 0)]
    m.bed('birds_waking_3', start=60, gain=-6, hp=300, t0=0, t1=20, fi=0.8, fo=1.0, env=birds_env)
    m.bed('birds_waking_3', start=60, gain=-12, lp=700, t0=b0 - 0.5, t1=b1 + 0.5, fi=1.0, fo=1.0)   # heard through soil
    m.bed('field_cricket', start=3, gain=-18, hp=2500, t0=0, t1=20, fi=1.0, fo=1.0,
          env=[(0, 0), (b0, 0), (b0 + 0.8, -10), (hk - 0.5, -10), (hk, -40), (EV['calm'], -40), (EV['calm'] + 1.5, 0), (20, 0)])
    m.spot('bumblebee_1', EV['bee'], gain=-15, p=0.4, start=1.0, length=2.6, fi=0.6, fo=0.8, trim=False, label='bumblebee')
    # under the soil: the mole's earth, the ants
    for k, t in enumerate(EV['mole']):
        m.spot('dig_shovel', t, gain=-14, p=-0.25, start=3.0 + 4.0 * k, length=0.6, lp=2500, fo=0.2, label='mole digs')
    a0, a1 = EV['ants']
    m.spot('steps_mud', a0, gain=-26, p=0.3, length=a1 - a0, hp=2500, fi=0.4, fo=0.6, trim=False, label='ants (tiny scratching)')
    # the hawk: the meadow falls silent, a wing passes, rabbits dive
    m.spot('flight_bird_1', hk, gain=-12, p=-0.5, length=2.5, hp=150, fo=0.5, label='hawk wings pass')
    for k, t in enumerate(EV['dive']):
        m.spot('steps_mud', t, gain=-16, p=(-0.2, 0.15, 0.35)[k], start=1.5 + 2.5 * k, length=0.35, lp=900, fo=0.12, label='rabbit dives')
    m.master(HERE, notes='birdsong, crickets and a bee above; muffled below with the mole and ants; silence and wings for the hawk')


if __name__ == '__main__':
    main()
