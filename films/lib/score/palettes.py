"""palettes.py: the musical data of the score engine (modes, moods, palettes). No code, only choices.

A palette is the sound of an era and a place; a mood is a stage of the story. The engine combines them.
Sam's brief (CRAFT.md section 8): ambient, warm, living strategy-game music in the manner of Age of Empires and Anno,
not a full score: warm pads, plucked and bowed strings, soft hand drums, a solo instrument for the place and era,
long evolving chords; it swells only at the turn of the battle, settles after, and sits under the voice.
"""

TONIC_PC = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
            'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}

# scales as semitones above the tonic
MODES = {
    'dorian': [0, 2, 3, 5, 7, 9, 10],
    'aeolian': [0, 2, 3, 5, 7, 8, 10],
    'phrygian': [0, 1, 3, 5, 7, 8, 10],
    'hijaz': [0, 1, 4, 5, 7, 8, 10],          # Middle Eastern (phrygian dominant)
    'ionian': [0, 2, 4, 5, 7, 9, 11],
    'mixolydian': [0, 2, 4, 5, 7, 9, 10],
    'minor_pent': [0, 3, 5, 7, 10],            # Central Asian colour
}

# chord roots (semitones above the tonic) by role, per mode. Every root belongs to the mode, so the harmony stays modal.
MENUS = {
    'dorian':     dict(stable=[0, 10, 5, 0, 7], curious=[0, 5, 10, 2, 7, 3], tense=[0, 3, 7, 10, 2], pre=[7, 2], peak=[10, 5], lift=[0, 5]),
    'aeolian':    dict(stable=[0, 8, 10, 0, 5], curious=[0, 8, 5, 10, 3], tense=[0, 5, 7, 3, 8], pre=[7, 5], peak=[8, 3], lift=[0, 5]),
    'phrygian':   dict(stable=[0, 1, 0, 10, 8], curious=[0, 8, 10, 5, 3], tense=[0, 1, 5, 8, 7], pre=[1, 7], peak=[8, 1], lift=[0, 8]),
    'hijaz':      dict(stable=[0, 0, 10, 5, 7], curious=[0, 5, 10, 7, 8], tense=[0, 1, 5, 8, 7], pre=[1, 7], peak=[8, 10], lift=[0, 5]),
    'ionian':     dict(stable=[0, 5, 0, 7, 9], curious=[0, 5, 9, 2, 7], tense=[9, 2, 7, 4, 0], pre=[7, 4], peak=[5, 9], lift=[0, 5]),
    'mixolydian': dict(stable=[0, 10, 5, 0, 7], curious=[0, 5, 10, 2, 7], tense=[0, 10, 7, 2], pre=[7, 2], peak=[10, 5], lift=[0, 5]),
    'minor_pent': dict(stable=[0, 10, 7, 0, 5], curious=[0, 5, 10, 7], tense=[0, 3, 7, 10], pre=[7, 5], peak=[10, 5], lift=[0, 7]),
}

# the six stages of the story. Each curve value is (at the start of the section, towards its end).
#   I      overall intensity 0..1 (pad level, how many voices, brightness)       perc   hand drums 0..1
#   bright filter opening 0..1                                                    chord  seconds one chord lasts
#   pluck  seconds between plucked events (min, max)                              rest   seconds of silence between solo phrases
#   notes  notes per solo phrase (min, max)                                       dur    solo note lengths to pick from
#   reg    solo register: centre (MIDI) offset from the palette's solo centre
MOODS = {
    'calm':      dict(I=(.21, .23), perc=(0, 0), bright=(.22, .30), chord=(15, 20), pluck=(2.8, 4.6), rest=(6, 11), notes=(3, 5), dur=[1.8, 2.4, 3.2, 4.2], reg=0, pad=1.0),
    'curious':   dict(I=(.34, .44), perc=(0, 0), bright=(.38, .50), chord=(11, 15), pluck=(1.2, 2.4), rest=(3.5, 7), notes=(4, 7), dur=[0.9, 1.3, 1.8, 2.6], reg=1, pad=1.0),
    'tension':   dict(I=(.44, .58), perc=(.45, .80), bright=(.42, .56), chord=(8.5, 11), pluck=(0.5, 0.5), rest=(7, 11), notes=(2, 4), dur=[1.6, 2.2, 3.2], reg=-4, pad=1.0),
    'turn':      dict(I=(1.0, .66), perc=(1.0, .72), bright=(1.0, .72), chord=(7.5, 9.5), pluck=(0.5, 0.9), rest=(2.5, 5), notes=(3, 5), dur=[1.2, 1.8, 2.8], reg=5, pad=1.0),
    'triumph':   dict(I=(.74, .58), perc=(.40, 0.0), bright=(.82, .62), chord=(10, 13), pluck=(0.55, 1.1), rest=(3, 6), notes=(4, 6), dur=[1.0, 1.5, 2.2, 3.4], reg=3, pad=1.0),
    'aftermath': dict(I=(.20, .13), perc=(0, 0), bright=(.24, .18), chord=(16, 22), pluck=(4.5, 7.5), rest=(8, 14), notes=(2, 4), dur=[2.4, 3.2, 4.6], reg=-1, pad=1.0),
}

# one bar of eight steps for each hand-drum pattern: (drum, importance 0..1). Importance sets how much intensity a step
# needs before it plays: 1 = the pulse itself, .6 = answers, .3 = ghost notes that only appear near the turn.
PATTERNS = {
    'frame':   [('doum', 1.0), None, ('tek', .3), None, ('doum', .8), ('tek', .35), None, ('tek', .3)],              # bendir: low, high, low
    'tabor':   [('tabor', 1.0), None, ('tek', .4), None, ('tabor', .85), None, ('tek', .4), ('tek', .3)],            # dry, medieval
    'darbuka': [('doum', 1.0), ('tek', .35), None, ('tek', .6), ('doum', .8), None, ('tek', .6), None],             # maqsum: doum tek . tek doum . tek
    'march':   [('tom', 1.0), None, None, ('brush', .35), ('tom', .75), None, ('brush', .5), ('brush', .3)],        # muted, a distant drum corps
    'steppe':  [('tom', 1.0), None, ('tek', .4), ('tek', .35), ('tom', .9), None, ('tek', .4), ('tek', .35)],       # horse-like gallop for Central Asia
}

# samples: name -> (folders under the VSCO root, synthetic fallback kind, playable range as MIDI lo, hi)
INSTRUMENTS = {
    'cello':       (['Strings/Cello Section/susvib'], 'bass', (36, 72)),
    'viola':       (['Strings/Viola Section/susvib'], 'pad', (48, 84)),
    'violin':      (['Strings/Violin Section/susVib'], 'pad', (55, 88)),
    'harp':        (['Strings/Harp'], 'lyre', (30, 100)),
    'pizz':        (['Strings/Violin Section/Pizz'], 'lute', (55, 86)),
    'flute':       (['Woodwinds/Flute/susvib', 'Woodwinds/Flute/expvib'], 'flute', (60, 92)),
    'clarinet':    (['Woodwinds/Clarinet/susLong'], 'reed', (50, 88)),
    'bassoon':     (['Woodwinds/Bassoon/sus'], 'reed', (36, 70)),
    'solo_violin': (['Strings/Solo Violin/Arco Vib'], 'bowed', (55, 92)),
}

# Palettes: era and place. 'solo' lists (instrument, weight); 'pluck' is the plucked voice, either a sampled name or
# 'synth:<kind>' for Karplus-Strong (lute, oud, lyre). 'centre' is the middle of the solo register (MIDI).
PALETTES = {
    'ancient_med': dict(
        label='Ancient Mediterranean (Greek, Roman, Carthaginian)', key='D', mode='dorian', tempo=62,
        solo=[('flute', 1.0)], centre=71, pluck=['harp', 'synth:lyre'], pluck_weights=[0.7, 0.3], drums='frame', rt60=3.4,
        glide=0.10, fifth_drone=False, pluck_pan=-0.25, solo_pan=0.12, bass='cello', mids=['viola', 'cello'], highs=['violin']),
    'medieval_europe': dict(
        label='Medieval Europe (Normans, English, crusaders)', key='G', mode='dorian', tempo=76,
        solo=[('solo_violin', 0.55), ('flute', 0.45)], centre=67, pluck=['synth:lute', 'harp'], pluck_weights=[0.65, 0.35], drums='tabor', rt60=3.0,
        glide=0.0, fifth_drone=True, pluck_pan=-0.3, solo_pan=0.1, bass='cello', mids=['viola', 'cello'], highs=['violin']),
    'middle_east_central_asia': dict(
        label='Middle East and Central Asia (Persian, Arab, Mamluk, Mongol)', key='D', mode='hijaz', tempo=72,
        solo=[('flute', 1.0)], centre=69, pluck=['synth:oud'], pluck_weights=[1.0], drums='darbuka', rt60=3.2,
        glide=0.45, fifth_drone=True, pluck_pan=-0.3, solo_pan=0.15, bass='cello', mids=['viola', 'cello'], highs=['violin']),
    'early_modern_europe': dict(
        label='Early modern Europe (Napoleonic)', key='D', mode='aeolian', tempo=84,
        solo=[('clarinet', 0.7), ('bassoon', 0.3)], centre=64, pluck=['harp', 'pizz'], pluck_weights=[0.6, 0.4], drums='march', rt60=3.0,
        glide=0.0, fifth_drone=False, pluck_pan=-0.25, solo_pan=0.12, bass='cello', mids=['viola', 'violin'], highs=['violin']),
}
ALIASES = {'ancient': 'ancient_med', 'greek': 'ancient_med', 'roman': 'ancient_med', 'medieval': 'medieval_europe',
           'middle_east': 'middle_east_central_asia', 'central_asia': 'middle_east_central_asia', 'persian': 'middle_east_central_asia',
           'early_modern': 'early_modern_europe', 'napoleonic': 'early_modern_europe'}
