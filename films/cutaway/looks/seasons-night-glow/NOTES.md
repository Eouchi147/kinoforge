# Look board: the seasons loop in `night-glow`

23 Oct 2026: the seasons loop (films/cutaway/loops/seasons, 12 s, 9:16, one fixed high three-quarter view, a 3 degree
sway, no cuts) dressed with the art direction `night-glow` (films/styles/cutaway/art/night-glow.py) through the kit adapter
(films/styles/cutaway/art/_adapter.py). This folder is made by `python3 films/cutaway/looks/make_seasons.py night-glow`:
blender.py names the look (module global KF_ART_NAME, nothing set in the environment) and runs the loop's own
blender.py; film.json is the loop's (720x1280 rendered, 1080x1920 delivered, 288 frames), without audio.

Board frames: 40 (spring: blossom), 100 (summer), 180 (autumn), 260 (winter: full snow and ice; snow cover peaks from 10.5 to 11.15 s,
so frame 230 at 9.6 s is still mostly autumn ground). Local checks: 270x480, 8 samples, this 2-core chat machine
(stills in the coordinator's report). Cost: see films/cutaway/looks/night-glow/NOTES.md, section "On the seasons loop".
