#!/usr/bin/env python3
"""Sound for Under the City (20 s, no music, no voice): real recordings only (BigSoundBank CC0, release sfx-bank;
sources in ../../SOUND.md). City sounds are this place's nature; everything is diegetic.

    python3 films/cutaway/series/under-the-city/audio/make_audio.py   # writes audio/mix.m4a + mix.json (mix.wav local)

Story: a dusk street on top (lamps, a bus); the camera sinks through pipes, cables, a sewer with a rat, a metro train
roaring past in its tunnel, Roman ruins, then dinosaur bones at the bottom. The sound sinks with the camera: the
street closes over us (filtered, then gone), water in the pipes and the sewer, a rat's squeak, the metro as the one
loud moment, then the stillness of old stone, drips, and at the bottom almost nothing: the train's rumble far above.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import audio_kit as K  # noqa: E402

# Events (s): from the film's NOTES.md event table when it lands, else the README story.
EV = {
    'street': (0.0, 4.5),     # dusk street, lamps, a bus passes
    'bus': 1.6,
    'pipes': (4.5, 7.5),      # pipes and cables
    'sewer': (7.0, 10.0),     # the sewer and its rat
    'rat': 8.4,
    'metro': (10.0, 13.2),    # the train roars past in its tunnel (peak about 11.4)
    'ruins': (13.2, 16.5),    # Roman ruins
    'bones': (16.5, 20.0),    # dinosaur bones at the bottom
}


def main():
    m = K.Mix(seed=5)
    s0, s1 = EV['street']
    # the street at dusk, closing over us as we sink (lowpass by layering a dark copy under a fading bright one)
    m.bed('paris_by_night', start=8, gain=-6, t0=0, t1=s1 + 1.5, fi=0.8, fo=2.0, env=[(0, 0), (s1 - 0.5, 0), (s1 + 1.5, -30)])
    m.bed('paris_by_night', start=8, gain=-10, lp=500, t0=s1 - 1.0, t1=EV['pipes'][1] + 0.5, fi=1.0, fo=2.0)
    m.spot('london_bus', EV['bus'], gain=-6, p=-0.3, start=35.5, length=5.0, fi=0.8, fo=1.5, trim=False, label='bus passes')
    # water in the pipes and the sewer
    m.bed('sewer_1', start=2, gain=-7, lp=2500, t0=EV['pipes'][0], t1=EV['sewer'][1] + 0.5, fi=1.5, fo=1.5,
          env=[(EV['pipes'][0], -8), (EV['sewer'][0], 0), (EV['sewer'][1], 0)])
    m.bed('drops_2', start=0, gain=-16, t0=EV['sewer'][0], t1=EV['ruins'][1], fi=1.0, fo=1.5)
    m.spot('mouse_screams', EV['rat'], gain=-18, p=0.45, start=0, length=0.6, hp=1500, fo=0.15, label='rat squeaks')
    # the metro: the one loud moment
    m0, m1 = EV['metro']
    m.spot('train_passage_1', m0 - 0.6, gain=-3, start=2.0, length=m1 - m0 + 2.5, fi=1.0, fo=1.6, trim=False, label='metro passes')
    # old stone: the cave's air, drips, then at the bottom almost nothing but the train far above
    m.bed('cave_2', start=3, gain=-3, t0=EV['ruins'][0] - 1.0, t1=20, fi=2.0, fo=1.0, env=[(EV['ruins'][0], 0), (EV['bones'][0], -3), (20, -6)])
    m.spot('drops_3', EV['ruins'][0] + 0.9, gain=-14, p=-0.4, length=1.5, label='drip in the ruins')
    m.spot('drops_4', EV['bones'][0] + 1.3, gain=-16, p=0.3, length=1.5, label='drip by the bones')
    m.spot('metro_paris_1', EV['bones'][0] - 0.2, gain=-16, start=40, length=3.6, lp=180, fi=1.0, fo=1.5, trim=False,
           label='a train far above')
    m.master(HERE, notes='street at dusk and a bus, water in pipes and sewer, a rat, the metro, cave stillness and drips')


if __name__ == '__main__':
    main()
