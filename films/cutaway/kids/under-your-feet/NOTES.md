# Who lives under your feet? (Little Big Questions, film "under-your-feet")

A SILENT 74 s story for children aged 6 to 8: Fable look, one fixed view of one lifted slice (a park lawn with a big tree), a 2 degree
sway, no cuts. We follow ONE periodical cicada nymph from egg to its big day while the busy neighbours of the soil go about their
day and the seasons turn on top. Facts: `docs/research/KIDS_FACTS_2026-10.md` section 2.1 (binding). Words are set in code (never drawn).
Music: Mozart, The Marriage of Figaro overture (Czech National Symphony Orchestra, Musopen; CC0 1.0 on the Wikimedia Commons page).

## Beats (beats.json is the source of truth; blender.py T(**seconds) anchors every event to a beat)
| Time | Beat | Picture | Words | Music moment |
| --- | --- | --- | --- | --- |
| 0 to 5.2 | hook | summer park on top, shoes crossing the lawn, a bike on the tree, a picnic; a pale egg on a twig glints | WHO LIVES UNDER YOUR FEET? | hushed scurrying strings: many small feet |
| 5.2 to 8.7 | scurry | the egg cracks, the nymph tumbles, walks to the hole, dives in and digs down the cut face | none | the whisper grows to the burst |
| 8.7 to 14.25 | reveal | the tunnels glow open; worms, ant town, mole, grubs pop in; roots start to drink; the nymph reaches its root and sips | A HIDDEN WORLD! | FIRST TUTTI BURST at 8.75 |
| 14.25 to 22.15 | meet | the label points at the nymph; ants haul the sandwich crumb; the mole tunnels on; one slow year (four seasons) on top | CICADA! (the label on the nymph) | the lilting second theme |
| 22.15 to 27.6 | years | a pocket watch races; seven more years of seasons whirl by; the nymph grows | 17 YEARS | the racing tutti at 22.15, cross-fade at 26.1 to 27.6 |
| 27.6 to 34.0 | stir | spring warmth creeps down the face; nymphs let go of the roots and gather at the shaft | ALL TOGETHER! | cello and violin build |
| 34.0 to 43.6 | emerge | five cicadas pop out of the lawn, birds lift off, the kids look, the dog barks; they march to the tree | none | FINALE TUTTI at 34.0 (rec 202.9) |
| 43.6 to 55.55 | climb | they climb the trunk past the bike and the kite | none | tutti, accent at 43.6 |
| 55.55 to 59.7 | split | the old skins split, pale soft cicadas ease out, wings pump up | none | accent at 55.55 |
| 59.7 to 68.05 | sing | wings snap open in a golden flash, rings and notes pour out, kids and dog dance, the sun turns to gold | none | BIGGEST CLIMAX: the coda at 59.7, final chord at 68.05 |
| 68.05 to 74 | send | calm gold; a girl lies with her ear to the grass, the snail waves, soft hum | WHO IS DOWN THERE RIGHT NOW? | final cadence and its decay, then a quiet tail |

Each word is on screen for at least 2.5 s. The key word label CICADA! sits on the nymph (14.6 to 17.9 s).

## Files
`blender.py` (scene, camera, seasons, the T(**seconds) event table), `szworld.py` (heights, beats clock, the years and seasons, shared places),
`szpark.py` (lawn, big tree, park props, kids, dog, playground, snail), `szunder.py` (cut face: roots, tunnels, rooms, worms, ants, mole, grubs, easter
eggs), `szcic.py` (the cicada thread: egg, nymph, the climb, the skin, the adult, the song), `szback.py` (the world behind), `szwords.py` and `szui.py`
and `fonts/` (copied unchanged from the fossil film: captions, clock, label), `szgeo.py` and `szmats.py` (copied). `audio/make_audio.py` builds the sound.

## Easter eggs and the joke
- THE JOKE: an ant hauls a sandwich crumb much bigger than itself from the lawn down the shaft into its pantry, again every 14 s (first arrival at 20.5 s).
- Under the lawn: a lost marble, a coin, a lost key, a buried treasure box, a toy car in the right wall, pebbles. On the lawn: a garden-gnome-like figure with a red hat, a kite stuck in the tree,
  a bike, a teddy, the snail on a dock leaf (waves at 69.5 s, bows at the end).

## The years (honest)
The film shows SEVEN turns of the seasons (one slow year, then six in a race) next to the words 17 YEARS. The fact is 13 or 17 years (checked); the film shows the passing, not a count.
The egg on a twig, the tumble, the shell on the trunk and the golden rings and notes are story from general knowledge of cicada life; the research notes do not source a "song" claim for children, so
no sentence about the song is put in the words.

## Weak spots (named on purpose)
- Nobody has listened to the sound; the cicada song is a field cricket chorus (a stand-in, see SOUND.md).
- The kids and creatures are small stylised figures with no faces; the mole reads as a dark blue blob.
- The title caption covers the tree crown at the start (about 5 s).
- The adult cicadas are small on the trunk against a big crown; the rings and the gold flash carry the climax.
- Playground (swing, slide) sits at the right edge and is cut by the frame.
- Machine speed: only low-resolution local frames were checked before the push; real stills from rc-render `stills.yml` were read after.

## Checks
`bash tools/verify.sh` (all gates pass). Sound: `python3 films/cutaway/kids/under-your-feet/audio/make_audio.py` (-16.1 LUFS, -1.9 dBTP).
