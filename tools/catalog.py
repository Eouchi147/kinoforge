#!/usr/bin/env python3
"""catalog.py: build studio-web/public/data/catalog.json, the one list of everything KINOFORGE has made.

    python3 tools/catalog.py            write studio-web/public/data/catalog.json
    python3 tools/catalog.py --check    exit 1 if the file on disk differs from what the repo says (ignores "generated")
    python3 tools/catalog.py --stdout   print it instead of writing

The catalog is the contract between the AI manual (docs/manual/) and the studio OS (studio-web/). It is built from the
repo, never typed by hand:
  - films: every tracked film.json under films/ (film folders), the director jobs in films/studio/ (brief.json,
    status.json), the code ads in ads/ (ad.json), the anthology prototypes in proto/ (gallery release);
  - styles: the house styles and the Cutaway art looks (films/styles/cutaway/art/<look>.py, films/cutaway/looks/),
    with their board images found in studio-web/public/looks/ (served at /looks/<name>.jpg);
  - workflows: the pages in docs/manual/workflows/ (the table WORKFLOWS below says how each is started);
  - music: the recordings in rc-render release `music` (table MUSIC).
What the repo cannot say (which release assets exist, Sam's verdicts, delivery state, the sound in one line) is in the
static tables below, taken from docs/LOG.md, docs/STATUS.md, docs/SOUL.md and the films' NOTES.md on 23 Oct 2026. When a
film is rendered, delivered or judged, update its row here (and the asset list), run this script, commit the JSON.

Deterministic: everything sorted, no clock except the top-level "generated" (SOURCE_DATE_EPOCH is honoured).
House style for every string: no em dash, no en dash, no three dots.
"""
import datetime, json, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(ROOT, 'studio-web', 'public', 'data', 'catalog.json')
RC, KF = 'Eouchi147/rc-render', 'Eouchi147/kinoforge'

# ---------------------------------------------------------------------------------------------- release assets (static)
# rc-render release `kino-films`, listed on 23 Oct 2026 (gh api repos/Eouchi147/rc-render/releases/tags/kino-films).
# For each film id: which of <id>.mp4, <id>-preview.mp4, <id>-poster.jpg, <id>-sheet.jpg exist ("v", "p", "o", "s").
KINO_FILMS = {
    'battle-map-agincourt': 'vpos', 'battle-map-ain-jalut': 'vps', 'battle-map-cannae': 'vps',
    'battle-map-gaugamela': 'vps', 'battle-map-hastings': 'vps', 'battle-map-hattin': 'vps',
    'battle-map-thermopylae': 'vps', 'battle-map-waterloo': 'vps',
    'cutaway-ad-drainage-v169': 'vps', 'cutaway-ad-drainage-v916': 'vps',
    'cutaway-agincourt-mud-A': 'vps', 'cutaway-agincourt-mud-B': 'vps',
    'cutaway-loop-seasons': 'vps',
    'cutaway-series-hidden-meadow': 'vpos', 'cutaway-series-river-time': 'vpos',
    'cutaway-series-sleeping-volcano': 'vpos', 'cutaway-series-under-the-city': 'vpos',
    'dark-corners-arabia-clay': 'vps', 'dark-corners-bamberg-kinetic': 'vps',
    'dark-corners-kleidion-lantern-road': 'vps', 'dark-corners-zong-lantern-road': 'vps',
    'style-cutaway-cinematic': 'vps', 'under-the-surface-venice': 'vps',
}
# kinoforge release `films` (the director pipeline's and NOOR's release), listed on 23 Oct 2026.
KF_FILMS = {'noor-descent-05-iqra': 'vpos', 'noor-descent-05-iqra-short': 'vpos', 'noor-juz-30-amma': 'vpos'}
# kinoforge release `ads`: <id>.mp4 and <id>-sheet.jpg for each code ad.
KF_ADS = {'unmissed-01': 'vs', 'unmissed-v1': 'vs', 'unmissed-v2': 'vs', 'unmissed-v3': 'vs', 'unmissed-v4': 'vs', 'unmissed-v5': 'vs'}
# kinoforge release `gallery`: <id>.mp4 and <id>.contact.jpg for each anthology prototype (13 Oct 2026).
# Width, height and seconds measured with ffprobe on the release files (23 Oct 2026).
GALLERY = {'p01-static': (1280, 720, 10), 'p02-ink-ember': (1280, 720, 10), 'p03-lantern-road': (1280, 720, 12),
           'p04-witness': (1280, 720, 6), 'p05-relic': (1280, 720, 10), 'p06-cel': (1280, 720, 10),
           'p07-ash-ascent': (1280, 720, 6), 'p08-two-chairs': (1280, 720, 12), 'p09-paper-kingdom': (1280, 720, 10),
           'p10-clay': (1280, 720, 6), 'p11-kinetic': (720, 1280, 8), 'p12-terrain': (1280, 720, 10),
           'p13-pixel-vigil': (1280, 720, 10), 'p15-moon-lesson': (1920, 1080, 62.5), 'p16-dragon-tale': (1920, 1080, 124)}

# ---------------------------------------------------------------------------------------------- per film facts (static)
# status: delivered (Sam has it: on his Mac or the link sent), rendered (a finished file exists, not sent on its own),
# in-progress (being made now), draft (folder exists, never rendered or stopped). date: the day (UTC) of the current
# version's render or delivery. Sources: docs/LOG.md and docs/STATUS.md lines of that date.
BM_SOUND = 'ElevenLabs narration (brian), free procedural score (films/lib/score), final mix by remux.yml at -14.2 LUFS'
BM_MADE = ['Battle Map engine v2 (films/lib/battlemap, Three.js)', 'Chromium frame renderer (harness/render.cjs)',
           'free score engine (films/lib/score)', 'rc-render films.yml', 'rc-render remux.yml']
DC_SOUND = 'original Dark Corners narration, score and mix (rc-render release dark-films), kept unchanged'
CW_MADE = ['Blender 5.2 bpy, Cycles', 'Cutaway kit (films/styles/cutaway/cutaway.py)']
SERIES_SOUND = 'no voice: BigSoundBank CC0 recordings timed to the picture (release sfx-bank) under a quiet VSCO-2 score, -16 LUFS'
SERIES_MADE = CW_MADE + ['cinematic extras (films/styles/cutaway/cinematic/extras.py)', 'sfx kit (films/cutaway/series/audio_kit.py, music_kit.py)']
FILMS = {
    'battle-map-cannae': dict(status='delivered', date='2026-10-22', sound=BM_SOUND, made=BM_MADE,
        summary='Hannibal encircles a Roman army twice its size, 216 BC; the Battle Map v2 reference film (9 scenes, 26 shots).'),
    'battle-map-hastings': dict(status='delivered', date='2026-10-22', sound=BM_SOUND, made=BM_MADE,
        summary='Harold against William at Hastings, 1066, on Battle Map v2 (8 scenes, 30 shots).'),
    'battle-map-agincourt': dict(status='delivered', date='2026-10-23', sound=BM_SOUND, made=BM_MADE + ['two Cutaway mud inserts laid by films.yml'],
        summary='Henry V wins at Agincourt, 1415, on Battle Map v2 with two Cutaway inserts of the mud (9 scenes, 29 shots).'),
    'battle-map-waterloo': dict(status='delivered', date='2026-10-22', sound=BM_SOUND, made=BM_MADE,
        summary='Wellington, Blucher and Napoleon at Waterloo, 1815: hollow squares and artillery (9 scenes, 28 shots).'),
    'battle-map-thermopylae': dict(status='delivered', date='2026-10-22', sound=BM_SOUND, made=BM_MADE,
        summary='The pass and the hidden path at Thermopylae, 480 BC (9 scenes, 32 shots).'),
    'battle-map-gaugamela': dict(status='delivered', date='2026-10-22', sound=BM_SOUND, made=BM_MADE,
        summary='Alexander against Darius at Gaugamela, 331 BC, scythed chariots and the gap (9 scenes, 27 shots).'),
    'battle-map-hattin': dict(status='delivered', date='2026-10-22', sound=BM_SOUND, made=BM_MADE,
        summary='Saladin traps the crusader army at the Horns of Hattin, 1187: thirst, brush fire (9 scenes, 28 shots).'),
    'battle-map-ain-jalut': dict(status='delivered', date='2026-10-22', sound=BM_SOUND, made=BM_MADE,
        summary='The Mamluks stop the Mongols at Ain Jalut, 1260, with a feigned retreat (9 scenes, 23 shots).'),
    'dark-corners-bamberg-kinetic': dict(status='delivered', date='2026-10-22', sound=DC_SOUND,
        made=['Kinetic engine (films/lib/kinetic, web canvas)', 'Chromium frame renderer (harness/render.cjs)', 'rc-render films.yml'],
        summary='The Bamberg witch trials in eight movements on one candle-lit desk: documents, dates and numbers in motion.'),
    'dark-corners-zong-lantern-road': dict(status='delivered', date='2026-10-22', sound=DC_SOUND,
        made=['Lantern Road (hand-built 2.5D painted multiplane, web)', 'Chromium frame renderer (harness/render.cjs)', 'rc-render films.yml'],
        summary='The Zong, 1781: the ship called Care, told as a lantern-lit painted fable.'),
    'dark-corners-kleidion-lantern-road': dict(status='delivered', date='2026-10-22', sound=DC_SOUND,
        made=['Lantern Road (hand-built 2.5D painted multiplane, web)', 'Chromium frame renderer (harness/render.cjs)', 'rc-render films.yml'],
        summary='Kleidion, 1014, re-directed after Sam\'s notes: 9 scenes and 29 shots, an opening in real time.'),
    'dark-corners-arabia-clay': dict(status='delivered', date='2026-10-22', sound=DC_SOUND,
        made=['Blender 5.2 bpy, Cycles (Clay, hand-built)', 'rc-render films.yml'],
        summary='A desert story in Clay, re-directed: pin-hole stars in their own pass, 31 shots in 9 scenes, a fuller camp.'),
    'noor-juz-30-amma': dict(status='delivered', date='2026-10-23',
        sound='Chatterbox narration on the runner, free procedural score (noor-sound.yml)',
        made=['Lantern Road (web)', 'Amiri Quran type set in code', 'kinoforge noor-sound.yml', 'kinoforge films-render.yml'],
        summary='NOOR Ramadan sample, Tonight\'s Juz, Night 30: seven painted sets, teaching graphics, no person shown.'),
    'noor-descent-05-iqra': dict(status='delivered', date='2026-10-23',
        sound='Chatterbox narration on the runner, free procedural score (noor-sound.yml)',
        made=['Lantern Road (web)', 'Amiri Quran type set in code', 'kinoforge noor-sound.yml', 'kinoforge films-render.yml'],
        summary='NOOR Ramadan sample, The Descent, Night 5: Iqra; mountain, cave and sky, light only, no figure drawn.'),
    'noor-descent-05-iqra-short': dict(status='delivered', date='2026-10-22',
        sound='cut from the Iqra film\'s mix by make_short.py',
        made=['Lantern Road (web)', 'kinoforge films-render.yml'],
        summary='The 9:16 short cut from the Iqra sample, the same sets reframed.'),
    'under-the-surface-venice': dict(status='delivered', date='2026-10-23',
        sound='Kokoro narration (bm_george), harp, pizzicato and flute from the free score engine, -14.1 LUFS (sound.yml)',
        made=CW_MADE + ['overlay.py words set in code', 'kinoforge sound.yml', 'rc-render films.yml'],
        summary='Why Venice Sinks: 23 shots in 8 scenes through the lagoon, the wooden piles and the MOSE gates, in section.'),
    'cutaway-loop-seasons': dict(status='delivered', date='2026-10-22',
        sound='soft ambience and a short loopable score, an exact 12 s loop in picture and sound',
        made=CW_MADE + ['rc-render films.yml'],
        summary='One pond block through four seasons, one fixed view, no cuts, a living world: the Cutaway base (Sam, 23 Oct).'),
    'cutaway-ad-drainage-v169': dict(status='delivered', date='2026-10-23',
        sound='free score engine only, words on screen, -14.2 LUFS',
        made=CW_MADE + ['Inter Tight words set in code', 'rc-render films.yml'],
        summary='Sample trade ad for an invented drainage business (marked Sample): the drain laid under a soggy yard, 16:9.'),
    'cutaway-ad-drainage-v916': dict(status='delivered', date='2026-10-23',
        sound='free score engine only, words on screen, -14.2 LUFS',
        made=CW_MADE + ['Inter Tight words set in code', 'rc-render films.yml'],
        summary='The same sample drainage ad in 9:16, words inside the phone safe box (rule R-2-08).'),
    'cutaway-agincourt-mud-A': dict(status='rendered', date='2026-10-23', sound='none of its own: laid over the Agincourt film, which carries the mix',
        made=CW_MADE + ['rc-render films.yml'],
        summary='Agincourt insert A: the rain-soaked field and the stakes in section, frames 1375 to 1727 of the battle film.'),
    'cutaway-agincourt-mud-B': dict(status='rendered', date='2026-10-23', sound='none of its own: laid over the Agincourt film, which carries the mix',
        made=CW_MADE + ['rc-render films.yml'],
        summary='Agincourt insert B: knights sinking to the knee at the cut face, crows, frames 2081 to 2420.'),
    'style-cutaway-cinematic': dict(status='delivered', date='2026-10-23', sound='silent',
        made=CW_MADE + ['cinematic extras (films/styles/cutaway/cinematic/extras.py)', 'rc-render films.yml'],
        summary='The cinematic Cutaway test: golden backlight, mist, animals, ten buried surprises, five camera angles.'),
    'cutaway-line-meadow': dict(status='in-progress', date='2026-10-23',
        sound='no voice: CC0 recordings timed to the cue words, harp, strings and flute in D thinning to a low drone, -16 LUFS',
        made=CW_MADE + ['Cutaway line (films/lib/cutaway: spec.json as data)', 'Mac lane (Metal, Samsung X5 drive)'],
        summary='What Lies Under a Meadow, the Cutaway line\'s example: river, village, mill and ten finds in the soil layers.'),
    'cutaway-series-river-time': dict(status='delivered', date='2026-10-23', sound=SERIES_SOUND, made=SERIES_MADE + ['rc-render films.yml'],
        summary='A stream cuts down through the layers over ages until a canyon stands; today, a hiker on the rim.'),
    'cutaway-series-under-the-city': dict(status='delivered', date='2026-10-23', sound=SERIES_SOUND, made=SERIES_MADE + ['rc-render films.yml'],
        summary='From a dusk street down through pipes, a sewer, a metro train and Roman ruins to dinosaur bones.'),
    'cutaway-series-hidden-meadow': dict(status='delivered', date='2026-10-23', sound=SERIES_SOUND, made=SERIES_MADE + ['rc-render films.yml'],
        summary='A spring meadow over a warren, an ant nest, a mole and a fox den; a hawk\'s shadow sends the rabbits under.'),
    'cutaway-series-reef-and-wreck': dict(status='delivered', date='2026-10-23', sound=SERIES_SOUND, made=SERIES_MADE + ['Mac lane (Metal)'],
        summary='A small island cut through the sea: light rays, a reef, fish, a turtle, a sunken ship with a chest, a diver.'),
    'cutaway-series-gold-mine': dict(status='delivered', date='2026-10-23', sound=SERIES_SOUND, made=SERIES_MADE + ['Mac lane (Metal)'],
        summary='A mountain at night: lantern-lit tunnels, ladders, a cart on rails, miners, a gold vein that rings when struck.'),
    'cutaway-series-sleeping-volcano': dict(status='delivered', date='2026-10-23', sound=SERIES_SOUND, made=SERIES_MADE + ['rc-render films.yml'],
        summary='A green island over a glowing magma chamber; birds lift, smoke, then a gentle eruption at dusk.'),
    'style-cutaway-test': dict(status='draft', date='2026-10-22', sound='none',
        made=CW_MADE, summary='The kit\'s 8 s motion test folder; never rendered (the cinematic version came first).'),
    'kinetic-demo': dict(status='draft', date=None, sound='the Zong mix (Dark Corners)', series='Director examples',
        title='Kinetic line example: The Ship Called Care',
        made=['Kinetic engine (films/lib/kinetic)'],
        summary='The director\'s example film for the kinetic line (films/director/lines.json); not a release.'),
    'salamis': dict(status='in-progress', date='2026-10-23', sound='Chatterbox narration and the procedural score (free day, 22 Oct), 119 s',
        made=['director pipeline (film.yml)', 'Battle Map engine v2'],
        summary='First director film: script and sound done; stopped at the picture spec, waits for credit to run as the first paid film.'),
    'battle-of-tours': dict(status='draft', date='2026-10-22', sound='script and sound done before the stop',
        made=['director pipeline (film.yml)'],
        summary='Paid director test job, cancelled at 09:20 on 22 Oct by the no-spend order after US$0.36.'),
    'great-emu-war': dict(status='draft', date='2026-10-22', sound='not made',
        made=['director pipeline (film.yml)'],
        summary='Slate film for the kinetic line; stopped at the script stage by the free models\' daily limit.'),
}
VERDICTS = {
    'style-cutaway-cinematic': 'Sam, 23 Oct 17:32: did not like the cinematic test (camera moves, cuts).',
    'cutaway-loop-seasons': 'Sam, 23 Oct 17:32: liked it, barely any camera movement, no cuts, a lively world; the seasons loop is the base.',
    'unmissed-v5': 'Sam, 16 Oct: loved, sound and visuals; the chosen direction for Unmissed.',
    'unmissed-v3': 'Sam, 16 Oct: loved, but the voice sounds too fake.',
    'unmissed-v2': 'Sam, 16 Oct: "a little".',
    'unmissed-v1': 'Sam, 16 Oct: "a little".',
    'unmissed-v4': 'Sam, 16 Oct: "a big NO".',
    'unmissed-01': 'Sam, 16 Oct: "really bad quality", the voice "not the greatest".',
}
# The code ads (ads/<id>/ad.json; release `ads` in kinoforge). Titles and voices from docs/LOG.md, 16 Oct 2026.
ADS = {
    'unmissed-01': ('Unmissed ad, first version (v4)', 27.6, 'ElevenLabs voice, Lyria score, synthesised interface sounds, -14 LUFS'),
    'unmissed-v1': ('Unmissed direction 1: Manifesto', None, 'Lyria score, ElevenLabs voice (roger), -14 LUFS'),
    'unmissed-v2': ('Unmissed direction 2: The Catch (3D)', None, 'Lyria score, ElevenLabs voice (river), -14 LUFS'),
    'unmissed-v3': ('Unmissed direction 3: The Call', None, 'Lyria score (delayed 3 bars), ElevenLabs dialogue with Whisper word times, -14 LUFS'),
    'unmissed-v4': ('Unmissed direction 4: Night Shift (AI footage)', None, 'Lyria score, ElevenLabs voice (eric), -14 LUFS'),
    'unmissed-v5': ('Unmissed direction 5: Bento', None, 'Lyria score cut on whole bars, ElevenLabs voice (jessica), -14 LUFS'),
}
PROTO = {   # names from studio-web/lib/data.js and docs/LOG.md (13 to 14 Oct 2026)
    'p01-static': 'Static', 'p02-ink-ember': 'Ink Ember', 'p03-lantern-road': 'Lantern Road', 'p04-witness': 'Witness',
    'p05-relic': 'Relic', 'p06-cel': 'Cel', 'p07-ash-ascent': 'Ash Ascent', 'p08-two-chairs': 'Two Chairs',
    'p09-paper-kingdom': 'Paper Kingdom', 'p10-clay': 'Clay', 'p11-kinetic': 'Kinetic', 'p12-terrain': 'Terrain',
    'p13-pixel-vigil': 'Pixel Vigil', 'p15-moon-lesson': 'Why the Moon Changes Shape (pilot)',
    'p16-dragon-tale': 'The Dragon Who Couldn\'t Fly (pilot)',
}
STYLE_OF = {'terrain': 'battle-map', 'kinetic': 'kinetic', 'lantern-road': 'lantern-road', 'clay': 'clay', 'cutaway': 'cutaway'}

# ---------------------------------------------------------------------------------------------- styles (static facts)
HOUSE = [
    dict(id='cutaway', name='Cutaway', engine='films/styles/cutaway/cutaway.py',
         summary='A block of land cut out of the world: a living landscape on top, clean strata on the cut faces, clear water, surprises in the soil.',
         best_for='what lies under the surface: cities, digs, geology, nature, how things work underground; ads for trades',
         start=dict(line='cutaway', format='16:9', look=None), board_films=['cutaway-loop-seasons'], board_looks=['reference', 'board-meadow']),
    dict(id='cutaway-seasons', name='Cutaway seasons loop', engine='films/cutaway/loops/seasons/blender.py', recipe='cutaway-seasons-loop',
         summary='The Cutaway base grammar since 23 Oct: one fixed view, no cuts, a living world changing through the seasons.',
         best_for='social loops, ambient and music films, brand loops; every art look is ported onto it',
         start=dict(line=None, format='9:16', look=None), board_films=['cutaway-loop-seasons'], board_looks=['seasons-base']),
    dict(id='cutaway-cinematic', name='Cutaway cinematic', engine='films/styles/cutaway/cinematic/extras.py',
         summary='The kit with cinema light, mist, animals and buried surprises, shot with moving cameras and cuts; Sam did not like the test.',
         best_for='set pieces inside another film (the Agincourt inserts) and explainers that need many angles',
         start=dict(line=None, format='16:9', look=None), board_films=['style-cutaway-cinematic'], board_looks=[]),
    dict(id='battle-map', name='Battle Map', engine='films/lib/battlemap',
         summary='A 3D relief map that reads as drawn and engraved, armies as soldier figures on trays, ink arrows, a legend, labels in code.',
         best_for='battles, campaigns, journeys, expeditions: anything about places and movement',
         start=dict(line='battle-map', format='16:9', look=None), board_films=['battle-map-cannae'], board_looks=[]),
    dict(id='kinetic', name='Kinetic', engine='films/lib/kinetic',
         summary='Words, dates, numbers and documents in motion on one lit desk, restrained and adult, every word inside the phone safe box.',
         best_for='true stories told through words and documents: history, science, ideas',
         start=dict(line='kinetic', format='9:16', look=None), board_films=['dark-corners-bamberg-kinetic'], board_looks=[]),
    dict(id='lantern-road', name='Lantern Road', engine='proto/p03-lantern-road',
         summary='Painterly storybook sets at true depths (a 2.5D multiplane), lanterns that relight the paint, slow real moves.',
         best_for='dark history told as a fable; NOOR (reverent, no figures)',
         start=dict(line=None, format='9:16', look=None), board_films=['dark-corners-zong-lantern-road'], board_looks=[]),
    dict(id='clay', name='Clay', engine='proto/p10-clay',
         summary='Thumb-sized clay figures and handmade sets in Blender, poses on twos, deadpan timing.',
         best_for='intimate human stories',
         start=dict(line=None, format='9:16', look=None), board_films=['dark-corners-arabia-clay'], board_looks=[]),
]
LOOKS = {   # summary: the art module's docstring; best_for: the look's NOTES.md "project ideas" (films/cutaway/looks/<look>/)
    'fable': ('Fable', 'A mid-century storybook painting in gouache: jewel palette, painted sky and sun halos, tall decorative trees.',
              'children\'s and family brands, museums and parks, terroir and luxury hospitality; the Fable music film'),
    'night-glow': ('Night glow', 'The block at night, alive with light: stars, a pale moon, glowing roots, finds that burn warm.',
                   'natural history museums and science centres, night events and gaming, sleep and calm apps'),
    'stained-glass': ('Stained glass', 'A leaded Art Nouveau window (secular, no figures): jewel panes held by dark lead lines.',
                      'heritage and craft brands, wineries and terroir food, cultural seasons and festivals'),
    'papercraft': ('Papercraft', 'Layered cut paper under a desk lamp: posterised card colours, torn-edged strata sheets, drop shadows.',
                   'children\'s book publishers and museum exhibits, craft brands, schools and science channels'),
    'claymation': ('Claymation', 'Plasticine stop-motion: every material clay with lumps, thumb prints and tool marks.',
                   'family, kids, toy and food brands, museum and children\'s TV explainers, mascot shorts'),
    'pixel': ('Pixel', 'A 16-bit game diorama: rendered small, Bayer dither, a fixed 32-colour palette, scaled up crisp.',
              'game studios and indie launches, retro-gaming and developer brands, educational games'),
    'risograph': ('Risograph', 'A riso print in three spot inks (fluorescent pink, teal, yellow) through coarse halftone screens.',
                  'posters, album and festival art, cultural institutions, craft food and drink'),
    'storybook-ink': ('Storybook ink', 'A children\'s picture book: ink lines over a soft, hand-made picture.',
                      'children\'s publishers and parenting brands, museum family trails, school and library films'),
    'blueprint': ('Blueprint', 'An engineering drawing: cyanotype blue, drafting grid, hatched soil symbols, depth ruler and dimensions.',
                  'civil, geotechnical and drilling firms, infrastructure start-ups, engineering schools'),
    'chalkboard': ('Chalkboard', 'The cutaway drawn in chalk on a slate board: dusty white outlines, a few coloured sticks, smudged layers.',
                   'teachers and course brands, museum education, soil-testing and garden businesses'),
    'engraving': ('Engraving', 'A 19th-century encyclopaedia plate: sepia copperplate hatching on cream paper that follows the forms.',
                  'history channels and heritage trusts, illustrated history publishers, firms with old roots'),
    'flat-vector': ('Flat vector', 'The Cutaway as a 2D web film: flat shapes and clean labels, renders in minutes in Chromium.',
                    'weekly explainer series, trade and local business ads in both formats, data and infographic pieces'),
}

# ---------------------------------------------------------------------------------------------- workflows and music
WORKFLOWS = [   # id, name, summary, page under docs/manual/workflows/, how it is started
    ('render-film', 'Render a film on runners', 'Any film folder rendered in parallel parts on free runners, joined with its own sound.',
     'render-film-on-runners.md', 'rc-render films.yml (REST dispatch: film, parts, ref)'),
    ('check-stills', 'Check stills', 'Full-quality single frames of a film folder on free runners, before any full render.',
     'check-stills.md', 'rc-render stills.yml (REST dispatch: film, frames, tag, w, h, samples, per_job, ref)'),
    ('mac-lane', 'Render on the Mac lane', 'Blender films on Sam\'s M4 GPU from his Samsung X5 drive, about 7 runners\' worth.',
     'render-on-the-mac.md', 'a job JSON in KINOFORGE/render/mac-jobs/ on the drive; lane started by harness/mac/go.py in Blender'),
    ('remux', 'Remux sound', 'New sound on a finished film without re-rendering the picture.',
     'remux-sound.md', 'rc-render remux.yml (REST dispatch: film, ref)'),
    ('chain', 'Follow-up chains', 'A render that waits for other renders, checked every 15 minutes on GitHub.',
     'follow-up-chains.md', 'a rule line in rc-render .github/workflows/chain.yml (cron, or REST dispatch)'),
    ('music-fetch', 'Fetch music', 'A public domain or CC0 recording from Wikimedia Commons with its licence record.',
     'fetch-music.md', 'rc-render music-fetch.yml (REST dispatch: file, name)'),
    ('sfx-bank', 'Build the sound bank', 'The BigSoundBank CC0 recordings as one checked archive with loudness.',
     'build-the-sound-bank.md', 'rc-render sfx-bank.yml (REST dispatch, no inputs)'),
    ('narration-score', 'Narration and score', 'Free narration (Kokoro or Chatterbox), the procedural score and the mix for a film folder.',
     'narration-and-score.md', 'kinoforge sound.yml or noor-sound.yml (REST dispatch)'),
    ('director', 'Director pipeline', 'An approved brief in, a checked and rendered film out, inside a hard money cap.',
     'director-pipeline.md', 'push films/studio/<id>/brief.json, or kinoforge film.yml (REST dispatch: job, from)'),
    ('web-build', 'Web studio build button', 'The studio\'s "Build this film" commits the brief that starts the director.',
     'web-studio-build.md', 'button in the web studio (POST /api/build)'),
    ('social', 'Social videos', 'Phone-format batch videos from code templates, one runner per video (lane paused).',
     'social.md', 'kinoforge social.yml (REST dispatch: batch, only)'),
    ('ads', 'Code ads', 'Business ads built in code, music first: prep then render (lane paused).',
     'ads.md', 'kinoforge codead.yml (REST dispatch: ad, mode)'),
    ('boards-pieces', 'Style boards and AI footage', 'Paid AI stills and clips for a style board, and the AI-footage shot factory.',
     'style-boards-and-ai-footage.md', 'kinoforge board.yml and piece.yml (REST dispatch; Sam\'s go per job)'),
    ('legacy', 'Legacy lanes', 'The 13 to 16 Oct lanes kept for history: gallery, showcase, voice, finish, director.yml, motion, smoke.',
     'legacy-lanes.md', 'see the page; not used for new work'),
]
MUSIC = [
    dict(id='borodin-steppes-musopen', title='Borodin, In the Steppes of Central Asia (Musopen Symphony)',
         source='https://commons.wikimedia.org/wiki/File:Borodin_-_In_the_Steppes_of_Central_Asia_(Musopen_Symphony).flac',
         licence='Public domain (Wikimedia Commons record in borodin-steppes-musopen.licence.json)',
         asset=dict(repo=RC, release='music', name='borodin-steppes-musopen.flac')),
]


# ---------------------------------------------------------------------------------------------- helpers
def tracked(*paths):
    try:
        out = subprocess.run(['git', 'ls-files', '-z', '--', *paths], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        files = [p for p in out.split('\0') if p]
    except Exception:   # not a git checkout: walk the folders
        files = []
        for base in paths:
            for d, _, fs in os.walk(os.path.join(ROOT, base)):
                files += [os.path.relpath(os.path.join(d, f), ROOT) for f in fs]
    return sorted(p for p in files if os.path.isfile(os.path.join(ROOT, p)))


def load(p):
    with open(os.path.join(ROOT, p), encoding='utf-8') as f: return json.load(f)


def first_existing(cands):
    for c in cands:
        if os.path.exists(os.path.join(ROOT, c)): return c
    return cands[0]


def asset(repo, release, name): return {'repo': repo, 'release': release, 'name': name}


def media(fid):
    """video, preview, poster for a film id from the static release tables and the committed posters."""
    local = f'/posters/{fid}.jpg' if os.path.exists(os.path.join(ROOT, 'studio-web', 'public', 'posters', fid + '.jpg')) else None
    for table, repo, rel in ((KINO_FILMS, RC, 'kino-films'), (KF_FILMS, KF, 'films')):
        if fid in table:
            h = table[fid]
            poster = local or (asset(repo, rel, f'{fid}-poster.jpg') if 'o' in h else asset(repo, rel, f'{fid}-sheet.jpg') if 's' in h else None)
            return (asset(repo, rel, f'{fid}.mp4') if 'v' in h else None,
                    asset(repo, rel, f'{fid}-preview.mp4') if 'p' in h else None, poster)
    return None, None, local


def fmt(w, h): return '9:16' if (h or 0) > (w or 0) else '16:9'


def recipe(fid, folder, extra=()):
    """The film's own page if it exists, else a series page that covers it (extra), else the expected film page."""
    base = os.path.basename(folder.rstrip('/'))
    pair = re.sub(r'-(A|B|v169|v916)$', '', fid)   # one page may cover both inserts or both formats
    own = [f'docs/manual/films/{fid}.md', f'docs/manual/films/{base}.md'] + ([f'docs/manual/films/{pair}.md'] if pair != fid else [])
    hit = first_existing(own + list(extra))
    return hit if os.path.exists(os.path.join(ROOT, hit)) else own[0]


def film_row(fid, title, series, style, w, h, duration, folder, made_default=None):
    s = FILMS.get(fid, {})
    video, preview, poster = media(fid)
    return {
        'id': fid, 'title': s.get('title') or title, 'series': s.get('series') or series, 'style': style, 'look': s.get('look'), 'format': fmt(w, h),
        'duration_s': round(float(duration), 2) if duration else None, 'folder': folder,
        'status': s.get('status') or ('rendered' if video else 'draft'),
        'video': video, 'preview': preview, 'poster': poster,
        'sound': s.get('sound') or 'not recorded', 'made_with': s.get('made') or made_default or [],
        'recipe': recipe(fid, folder), 'summary': s.get('summary') or 'not recorded',
        'verdict': VERDICTS.get(fid), 'date': s.get('date'),
    }


# ---------------------------------------------------------------------------------------------- builders
SKIP = ('films/director/tests/', 'films/cutaway/looks/', 'films/styles/cutaway/stills/')


def films():
    rows, seen = [], set()
    for p in tracked('films'):
        if not p.endswith('/film.json') or p.startswith(SKIP) or '/_' in p: continue
        m = load(p); folder = os.path.dirname(p); fid = m['id']
        if fid in seen: continue
        seen.add(fid)
        style = STYLE_OF.get((m.get('style') or '').lower(), (m.get('style') or '').lower() or None)
        title = m.get('title') or fid
        if folder.startswith('films/studio/') and os.path.exists(os.path.join(ROOT, folder, 'brief.json')):
            title = load(os.path.join(folder, 'brief.json')).get('title') or title
        rows.append(film_row(fid, title, m.get('series') or 'not recorded', style, m.get('w') or m.get('render_w'),
                             m.get('h') or m.get('render_h'), m.get('duration'), folder))
    # director jobs that never got a film.json (stopped early)
    for p in tracked('films/studio'):
        if not p.endswith('/brief.json') or '/_' in p: continue
        b = load(p); folder = os.path.dirname(p); fid = b.get('id') or os.path.basename(folder)
        if fid in seen: continue
        seen.add(fid)
        line = b.get('line') or 'battle-map'
        w, h = (1080, 1920) if line == 'kinetic' or b.get('format') == '9:16' else (1920, 1080)
        rows.append(film_row(fid, b.get('title') or fid, {'kinetic': 'Kinetic', 'battle-map': 'Battle Map', 'cutaway': 'Cutaway'}.get(line, 'Studio'),
                             line, w, h, b.get('target_seconds'), folder))
    # code ads (release `ads`)
    for fid, (title, dur, sound) in sorted(ADS.items()):
        folder = f'ads/{fid}'
        if not os.path.exists(os.path.join(ROOT, folder, 'ad.json')): continue
        a = load(os.path.join(folder, 'ad.json')); h = KF_ADS.get(fid, '')
        row = film_row(fid, title, 'Unmissed ads', 'business', a.get('w', 1920), a.get('h', 1080), dur or a.get('duration'), folder,
                       ['code ad (ads/lib/motion.js, harness/dom-render.cjs)', 'kinoforge codead.yml'])
        row.update(status='delivered', date='2026-10-16', sound=sound, recipe=recipe(fid, folder, ['docs/manual/styles/business-ads.md']),
                   video=asset(KF, 'ads', f'{fid}.mp4') if 'v' in h else None, preview=None,
                   poster=asset(KF, 'ads', f'{fid}-sheet.jpg') if 's' in h else None,
                   summary='Unmissed ad direction built in code, music first; shown to Sam on the page "Unmissed Ad Directions".' if fid != 'unmissed-01'
                   else 'The first Unmissed ad built in code (AI front desk offer), fourth revision delivered to Sam.')
        rows.append(row)
    # anthology prototypes (release `gallery`)
    for fid, (w, h, dur) in sorted(GALLERY.items()):
        folder = f'proto/{fid}'
        if not os.path.isdir(os.path.join(ROOT, folder)): continue
        row = film_row(fid, PROTO.get(fid, fid), 'Anthology prototypes', fid.split('-', 1)[1], w, h, dur, folder,
                       ['proto scene (web or Blender)', 'kinoforge render.yml'])
        row.update(status='rendered', date='2026-10-13', video=asset(KF, 'gallery', f'{fid}.mp4'), preview=None,
                   recipe=recipe(fid, folder, ['docs/manual/styles/anthology-prototypes.md']),
                   poster=asset(KF, 'gallery', f'{fid}.contact.jpg'), sound='not recorded',
                   summary='Anthology style prototype rendered by render.yml to the gallery release; the origin of a house style or a pilot.')
        rows.append(row)
    return sorted(rows, key=lambda r: (r['series'], r['id']))


def boards(prefix):
    d = os.path.join(ROOT, 'studio-web', 'public', 'looks')
    if not os.path.isdir(d): return []
    pat = re.compile('^' + re.escape(prefix) + r'-(\d+)\.jpg$')
    names = [n for n in os.listdir(d) if pat.match(n)]
    return [f'/looks/{n}' for n in sorted(names, key=lambda n: int(pat.match(n).group(1)))]


def styles():
    rows = []
    for s in HOUSE:
        board = []
        for fid in s['board_films']:
            _, _, poster = media(fid)
            h = KINO_FILMS.get(fid, '')
            if poster: board.append(poster)
            if 's' in h and not (isinstance(poster, dict) and poster['name'].endswith('-sheet.jpg')):
                board.append(asset(RC, 'kino-films', f'{fid}-sheet.jpg'))
        for lk in s['board_looks']: board += boards(lk)
        rows.append({'id': s['id'], 'name': s['name'], 'family': 'house', 'summary': s['summary'], 'best_for': s['best_for'],
                     'engine': s['engine'], 'recipe': first_existing([f'docs/manual/styles/{s.get("recipe", s["id"])}.md', f'docs/manual/styles/{s["id"]}.md']),
                     'board': board, 'start': s['start']})
    for look, (name, summary, best) in sorted(LOOKS.items()):
        engine = f'films/cutaway/looks/{look}/index.html' if look == 'flat-vector' else f'films/styles/cutaway/art/{look}.py'
        rows.append({'id': f'cutaway-{look}', 'name': name, 'family': 'cutaway-look', 'summary': summary, 'best_for': best,
                     'engine': engine,
                     'recipe': first_existing([f'docs/manual/styles/cutaway-art-{look}.md', f'docs/manual/styles/cutaway-{look}.md',
                                               f'docs/manual/styles/cutaway-look-{look}.md']),
                     'board': boards(look) + boards(f'seasons-{look}'),
                     'start': {'line': None if look == 'flat-vector' else 'cutaway', 'format': '16:9', 'look': look}})
    return rows


def workflows():
    return [{'id': i, 'name': n, 'summary': s, 'doc': f'docs/manual/workflows/{d}', 'run': r} for i, n, s, d, r in WORKFLOWS]


def build():
    epoch = os.environ.get('SOURCE_DATE_EPOCH')
    now = datetime.datetime.fromtimestamp(int(epoch), datetime.timezone.utc) if epoch else datetime.datetime.now(datetime.timezone.utc)
    return {'generated': now.strftime('%Y-%m-%dT%H:%M:%SZ'), 'films': films(), 'styles': styles(),
            'workflows': workflows(), 'music': sorted(MUSIC, key=lambda m: m['id'])}


BAD = re.compile('[–—…]|\\.\\.\\.')


def main(argv):
    cat = build()
    text = json.dumps(cat, indent=1, ensure_ascii=False) + '\n'
    bad = [m.group(0) for m in BAD.finditer(text)]
    if bad: print(f'catalog: house style broken ({len(bad)} dash or three dots in the words); fix the table rows'); return 1
    if '--stdout' in argv: sys.stdout.write(text); return 0
    if '--check' in argv:
        old = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else {}
        same = {k: v for k, v in old.items() if k != 'generated'} == {k: v for k, v in cat.items() if k != 'generated'}
        print('catalog: up to date' if same else 'catalog: out of date, run python3 tools/catalog.py'); return 0 if same else 1
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f: f.write(text)
    by = {}
    for r in cat['films']: by[r['status']] = by.get(r['status'], 0) + 1
    print(f"catalog: {len(cat['films'])} films ({', '.join(f'{k} {v}' for k, v in sorted(by.items()))}), "
          f"{len(cat['styles'])} styles, {len(cat['workflows'])} workflows, {len(cat['music'])} music -> {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
