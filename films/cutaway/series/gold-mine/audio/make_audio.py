#!/usr/bin/env python3
"""Sound for The Gold Mine (20 s, 9:16, no music, no voice): real recordings only (BigSoundBank CC0, release sfx-bank;
sources in ../../SOUND.md). Every sound is something we see or feel.

    python3 films/cutaway/series/gold-mine/audio/make_audio.py   # writes audio/mix.m4a + mix.json (mix.wav local)

Story: a mountain at night; inside, lantern-lit tunnels, ladders, a cart rolling on rails, miners, a gold vein that
glints when a pick strikes. The sound: wind on the mountain and the night outside; inside, the mine's still air and
drips, a lantern's flame, a ladder's creak, the cart's squeal and rumble, and the pick striking rock, the last strike
the one that rings and lets the gold glint, held by the tunnel's echo.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import audio_kit as K  # noqa: E402

# Events (s): from the film's NOTES.md event table when it lands, else the README story.
EV = {
    'outside': (0.0, 4.0),    # the mountain at night
    'inside': 4.0,            # into the lantern-lit tunnels
    'ladder': [6.0, 6.7, 7.4],
    'cart': (8.5, 12.5),      # the cart rolls on rails
    'picks': [13.6, 14.6, 15.6],
    'glint': 16.6,            # the strike that reveals the gold
}


def main():
    m = K.Mix(seed=13)
    i0 = EV['inside']
    # outside: wind on the mountain and the night, fading as we go in
    m.bed('wind_plain', start=10, gain=-8, hp=80, t0=0, t1=i0 + 1.5, fi=0.8, fo=1.5)
    m.bed('campaign_night_1', start=5, gain=-14, hp=1500, t0=0, t1=i0 + 1.0, fi=0.8, fo=1.0)
    m.spot('owl_tawny', 1.4, gain=-20, p=-0.5, length=2.0, hp=300, fo=0.5, label='an owl on the mountain')
    # inside: the mine's air and drips, the lantern
    m.bed('cave_1', start=4, gain=-8, t0=i0 - 1.0, t1=20, fi=1.5, fo=1.0)
    m.bed('candle_sparkle_1', start=0, gain=-22, hp=300, p=0.2, t0=i0, t1=20, fi=1.0, fo=1.0)
    for k, t in enumerate(EV['ladder']):
        m.spot('squeaky_steps_1', t, gain=-16, p=-0.3, start=1.0 + 1.5 * k, length=0.7, fo=0.2, label='ladder rung')
    c0, c1 = EV['cart']
    m.spot('squeaky_barrow_4', c0, gain=-12, p=-0.6, start=2.0, length=c1 - c0, fi=0.6, fo=1.2, trim=False, label='cart wheels squeal')
    m.spot('steam_between_wagons', c0 + 0.2, gain=-14, p=-0.4, start=8.0, length=c1 - c0, lp=1500, fi=0.8, fo=1.2, trim=False,
           label='cart rumble on the rails')
    for k, t in enumerate(EV['picks']):
        m.spot('hammer_concrete', t, gain=-9, p=0.35, length=0.8, hp=100, fo=0.3, label='pick strikes rock')
        m.spot('fall_of_stone', t + 0.05, gain=-20, p=0.35, start=2.0 + 3.0 * k, length=0.9, fo=0.4, label='chips fall')
    m.spot('anvil_1', EV['glint'], gain=-15, p=0.35, length=2.5, lp=6000, fo=1.5, label='the ringing strike, the gold glints')
    m.spot('fall_of_stone', EV['glint'] + 0.08, gain=-16, p=0.35, start=8.0, length=1.4, fo=0.6, label='rock gives, the vein shows')
    m.room(rt60=1.4, wet=0.22, seed=17)
    m.master(HERE, notes='night wind and owl outside; cave air, drips, lantern; ladder, cart, pick strikes; the ringing strike at the glint')


if __name__ == '__main__':
    main()
