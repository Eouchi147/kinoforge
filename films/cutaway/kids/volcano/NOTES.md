# Volcano film (Little Big Questions): the picture

23 Oct 2026. A silent 72.3 s story (Sam 20:09: no narration; real orchestral music and real sound effects carry it; a few
big words set in code) for children aged 6 to 8: HOW IS A VOLCANO BORN? Music: Grieg, In the Hall of the Mountain King
(Musopen Symphony, public domain, Commons), four cuts on rests of the music (see `beats.json` music block and `SOUND.md`).
Source of truth: `beats.json` (11 beats). Facts: `docs/research/KIDS_FACTS_2026-10.md` 1.2 and 1.2.1. Fable Cutaway look on the
"lifted slice" grammar of the fossil film (`../fossil/NOTES.md`): one fixed view, a 2 degree sway, no cuts. 16:9, rendered
1280x720, delivered 1920x1080, 24 fps, 1735 frames.

## The story the picture tells
A young volcano island, cut through its axis and lifted a little above its hole (a column of sea). The front face is the cross
section: layers of old lava, a crack, the magma chamber. Magma is lighter than the rock round it, so it rises; it finds the
crack; gas bubbles in it swell like a shaken fizzy drink (the bottle on the beach is the visual explanation); it bursts out of
the TOP (the bottle pops its cap at the same moment) and is lava; the lava slides to the sea, steams, and cools into new rock;
each eruption adds a layer; the mountain grows; plants find a home and the rock slowly becomes soil; the older green islands
round it, and Hawaii, were built the same way.

## Beats (beats.json times) and the event table
| Beat | Time (s) | Picture | Words |
| --- | --- | --- | --- |
| hook | 0 to 4.9 | the island is small and low, mostly under the sea; the beach ball rolls in (0.4 to 2.4); a dolphin hops | HOW IS A VOLCANO BORN? |
| magma | 4.9 to 8.5 | the chamber glows; a gold ribbon ties MAGMA to it | MAGMA |
| rises | 8.5 to 20.5 | glowing blobs lift off the chamber and the magma front creeps up the crack | none |
| gas | 20.5 to 31.39 | bubbles swell as they rise; the bottle is shaken; the slice trembles; the cap strains | none |
| erupt | 31.39 to 35.0 | the orchestra's big entrance: cap pop, a fountain of lava from the top, foam, the cap lands on the sandcastle | LAVA |
| flows | 35.0 to 42.3 | lava slides down to the sea, steam, it darkens into new rock | NEW ROCK |
| layers | 42.3 to 48.3 | the clock spins; eruptions on the hits 43.35, 44.31, 47.28, 48.22 each add a layer | LAYER BY LAYER |
| growth | 48.3 to 58.5 | hits 51.15, 52.09, 53.04, then the biggest on the final crash 56.82 | none |
| rest | 58.5 to 66.0 | the crack cools; green from the beach up; soil forms | none |
| islands | 66.0 to 69.0 | a gold ring round each older island in turn, then ours | HAWAII |
| send | 69.0 to 72.3 | the snail on its surfboard waves; the closing question | IS THE GROUND UNDER YOUR FEET REALLY STILL? |

Every event is one entry of `EVENTS` at the top of `blender.py` (beat, fraction); `szworld.set_events` turns it into seconds
(`W.B.<event>`) and `audio/make_audio.py` reads the same table, so a re-timed beat re-times picture and sound together.

## How the island is made (szworld.py)
`h_final(x, y)` is the finished island: a cone on a flat beach ring. `wgt(x, y)` says where the nine layers' material sits
(more near the summit); `off(t) * wgt` is subtracted for the layers not yet laid, so the island starts low (`INIT`) and each
eruption raises it by one layer (`TH`). The cut face's bands are `sd_wall` (depth below the surface, parallel to it), so the
bands of old lava follow the cone's shape. Everything is a pure function of t: the harness can render any frame alone.
Files: `szworld.py` (numbers, island, layers, magma level, flows, light), `szmats.py`, `szgeo.py` (rigid parts),
`szvolc.py` (cut face, flows, fountains, sea of the slice, bottle and sandcastle), `szlife.py` (plants, palms, gulls, dolphins,
boat, easter eggs, snail), `szback.py` (sea to the horizon, far islands, clouds, rings), `szwords.py` and `szui.py` (captions,
clock, label; the upgraded graphics of 402eb95), `blender.py` (event table, build, frame).

## Easter eggs and the joke
Obvious: the beach ball (rolls in, hops at every eruption), the sandcastle with its flag, bucket and spade, the fizzy-drink
bottle (a shaken bottle is the explanation of gas pushing magma), the snail on a surfboard (the series mascot: it pops into
its shell for the big whoosh, peeks out, and waves at the end). Hidden: flip-flops and a snorkel with mask on the sand, small
fish in the sea band of the cut face, dolphins, a sailing boat, far volcano islands with their own smoke. The visual joke: the
bottle's cap flies off at the eruption and lands on top of the sandcastle like a roof.

## Limits (honest)
- Checked locally at 320x180 and 640x360 only (4 to 5 samples); the real 1280x720 look comes from the runner stills.
- The slice shows a cartoon of an island volcano, not a scientific model: nine layers stand for nine eruptions; real
  eruptions are far apart in time (the clock says so), and the film never shows anyone in danger.
- Sound is built and measured, not heard (see `SOUND.md`).
