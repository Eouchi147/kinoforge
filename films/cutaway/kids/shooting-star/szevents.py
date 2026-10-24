"""What is a shooting star? THE EVENT TABLE (no bpy, no numpy): every timed event of the picture, in film seconds, each
anchored to a beat of beats.json (beat name + seconds after that beat starts), so a re-timed beats.json re-times the
whole film (picture and sound). blender.py hands it to szworld.set_events(); audio/make_audio.py reads the same table.

The music (Grieg, Anitra's Dance, Musopen) is cut on its bar lines; one bar = 1.3065 s. Film time of a recording time r:
  r 0.00 to 3.60      film 0.00 to 3.60            (the introduction)
  r 5.18 to 30.05     film r - 1.58                (the theme; bars at 3.60 + 1.3065 k)
  r 88.84 to 120.19   film r - 61.68               (the plucked build, the peak at r 102.27 to 111.5 = film 40.59 to 49.82)
  r 226.06 to 237.3   film r - 168.86              (the dance's own ending: the chord at r 228.41 = film 59.55)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_BJ = json.load(open(os.path.join(HERE, 'beats.json')))
_T0 = {b['name']: float(b['t'][0]) for b in _BJ['beats']}
BAR = 1.3065


def E(beat, t):
    """(beat name, seconds after the beat starts) for the film second t."""
    return (beat, round(t - _T0[beat], 4))


EVENTS = {
    # ---- hook (0 to 4.91): dusk; the title; the camp comes to life; the snail looks up through its tiny telescope
    'snail_up0': E('hook', 0.6), 'snail_up1': E('hook', 1.6),
    'sun0': E('hook', 0.0), 'sun1': E('look', 8.0),
    # ---- look (4.91 to 8.82): the dance begins; a small streak zips by on the bar line 7.52 (a 0.9 s zip); everyone looks up
    'toast0': E('hook', 3.6), 'toast1': E('look', 8.8),
    'streak1_0': E('look', 7.52), 'streak1_1': E('look', 8.42), 'point0': E('look', 7.80), 'point1': E('notstar', 11.5),
    'owl0': E('look', 7.95), 'owl1': E('look', 8.6),
    # ---- not a star (8.82 to 12.74): the window opens on one bright star, a ring and two gold lines tie it to the sky
    'win0': E('notstar', 9.55), 'win1': E('notstar', 10.25), 'lens_star': E('notstar', 10.25),
    'tele0': E('notstar', 9.0), 'tele1': E('notstar', 9.9),
    # ---- far away (12.74 to 17.97): the star is a giant calm ball of fire; the window closes; she picks up a pebble
    'star_pulse': E('far', 13.3), 'win_close0': E('far', 15.45), 'win_close1': E('far', 16.05),
    'pebble0': E('far', 14.45), 'pebble1': E('far', 15.85), 'pebble2': E('far', 17.55),
    # ---- tiny rock (17.97 to 21.88): the window opens on a small brown rock tumbling in space, a matching pebble beside it
    'win2': E('rock', 18.25), 'win3': E('rock', 18.95), 'lens_rock': E('rock', 18.95), 'pebble_in': E('rock', 19.6),
    # ---- drifting (21.88 to 27.16): the rock drifts closer; accents on the bar lines 21.88, 23.19 and 24.50
    'acc0': E('drift', 21.88), 'acc1': E('drift', 23.19), 'acc2': E('drift', 24.50), 'air_in': E('drift', 26.0),
    # ---- the air (27.16 to 40.23): the window shows the layers of the air; the rock enters and glows orange, yellow, white
    'enter': E('air', 28.45), 'glow0': E('air', 30.0), 'glow1': E('air', 39.0), 'hold0': E('air', 31.0),
    'ring0': E('air', 29.0), 'sky_ring': E('air', 32.0),
    # ---- the streak (40.23 to 44.14): the rock rushes in on the full orchestra: the long streak across the sky
    'streak0': E('streak', 40.59), 'peak': E('streak', 41.90), 'streak1': E('streak', 44.00), 'label0': E('streak', 41.90),
    'label1': E('gone', 44.70), 'burn': E('streak', 41.90), 'gasp': E('streak', 41.70),
    # ---- gone (44.14 to 49.37): the trail fades, sparkles drift down and melt; the window closes; specks of dust glint
    'win_close2': E('gone', 46.0), 'win_close3': E('gone', 46.6), 'dust0': E('gone', 46.6), 'dust1': E('wish', 52.0),
    # ---- the wish (49.37 to 57.2): everyone closes their eyes; the snail's wish, a lettuce leaf, floats in and lands
    'wish0': E('wish', 49.7), 'wish1': E('wish', 54.4), 'leaf0': E('wish', 50.4), 'leaf1': E('wish', 53.9), 'munch0': E('wish', 54.2), 'munch1': E('wish', 56.8),
    # ---- the send-off (57.2 to 68.4): the dance's last bright chord (59.55), a breath of stillness (61.88 to 63.57), the plucked ending
    'cuddle0': E('send', 57.6), 'cuddle1': E('send', 59.4), 'chord': E('send', 59.55), 'hush0': E('send', 61.88), 'hush1': E('send', 63.57),
    'words_send': E('send', 61.88), 'last0': E('send', 66.60), 'last1': E('send', 67.50),
    # ---- names the shared words layer (szwords.py) reads for the clock and the label; the clock is never shown here
    'rw0': E('send', 68.4), 'rw1': E('send', 68.4), 'stack0': E('send', 68.4), 'stack1': E('send', 68.4), 'rain0': E('send', 68.4), 'erode1': E('send', 68.4),
}
BEAT_NAMES = {n: n for n in _T0}
