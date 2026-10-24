# KINOFORGE: the soul (taste and judgement)

Read this before you make or change anything anyone will see. `AGENTS.md` says how to work; this file says what good
looks like here and why. It is distilled from Sam's own verdicts (dated, in `docs/LOG.md`) and from the craft files
(`films/director/CRAFT.md`, `docs/DIRECTORS_RULEBOOK.md`, each engine's `SPEC.md` or `README.md`, each film's `NOTES.md`).
**Sam's words are the ground truth.** When this file and a newer verdict of his disagree, the verdict wins: add it here.

---

## 1. What KINOFORGE makes, and for whom

KINOFORGE (also "Kino Studio") is Sam's AI-run studio: films and video made in code and with the best tool for each job inside a cap per film, rendered on free
machines, directed like cinema. Sam (GitHub `Eouchi147`) owns it and decides. Since 16 Oct 2026 it is also the content
engine of Unmissed, his AI marketing agency (`docs/UNMISSED_HANDOFF.md`).

| Line | For whom | What it must feel like |
| --- | --- | --- |
| **Battle Map** (16:9, about 2.5 min) | Kids 8 to 14 and curious adults | Epic, grandiose, kid-clear; upbeat with a glint of dark humour; the clearest teacher you ever had, drawing on a living map |
| **Dark Corners** (9:16, about 3 min) | Adults | True dark history told with restraint: no gore, no suffering bodies, silence as a tool |
| **Under the Surface / Cutaway** (16:9 or 9:16) | Everyone | A block of the world cut open: wonder, cross-sections, small surprises in the soil that make people smile |
| **Kinetic true stories** (9:16, 1 to 3 min) | Short-form audiences | Words, dates, documents and numbers directed like film; a little strange and always true |
| **NOOR** (Ramadan series, samples only so far) | Muslim families | Reverent and warm. No depiction of prophets, angels or Companions; Qur'anic Arabic set in code from the King Fahd Complex text; no recitation until licensed |
| **Business ads and social videos** (Unmissed and its clients) | Owner-run businesses in Canada | Premium, modern, honest: only claims the business (or Unmissed's site) makes in writing |

## 2. The quality bar

- "A stranger would believe a person framed this." Not "it renders" (`docs/SCENE_AUTHOR_BRIEF.md`).
- **Hollywood-level editing** (Sam, 22 Oct): every cut intentional; every decision relevant to the narrative; everything
  has a purpose, a goal, a beginning and an end; stories self-contained and masterfully arranged; worlds that feel alive.
- **Every element earns its place** (CRAFT.md 1): before adding a cut, a move, an effect, a label, an icon or a sound,
  write its job in one line. No job, no element. A beautiful effect with no job is noise.
- **Real time.** Never speed up a move or an animation to fit a line. Plan earlier, move less, hold longer.
- **Living worlds.** Foreground, middle and background all move a little (wind, smoke, water, birds, small figures).
  Empty does not mean calm; calm is a full frame that moves slowly.
- **Refined graphics.** No emoji, no cartoon icons, no faces on objects, no clip-art gags. Flat, consistent, heraldic.
- **Clean and professional on everything** (Sam, 16 Oct): no poor workmanship in any picture, no stretched or borrowed
  photos with doubtful rights, nothing that looks cheap.
- **Natural voices** (Sam, 16 Oct): "the voices should sound the most natural possible, not AI at all." A voice that
  sounds synthetic loses an ad Sam otherwise loved.
- **Honest.** Words on screen are true and checked; facts in narration are verified (the director has a checker seat);
  claims for a business only in its own written words; AI content labelled where the platform asks.

## 3. Sam's verdicts and what they teach

| Date | Work | Verdict (his words where recorded) | The lesson |
| --- | --- | --- | --- |
| 15 Oct | Five AI-footage ads, one stylised cartoon-3D look | "AI slop" | One look for everything makes everything the same. Show a style board of stills first; he picks the look before any video is made |
| 15 Oct | Style board round 1 | Screen Story "amazing"; Type in Motion "great" but the drawn bread looked fake; Flash Editorial "good"; Freeze Frame wanted in motion; Documentary no | Real (or photoreal) objects beat drawings of them; looks made in code win |
| 16 Oct | `unmissed-01` v4 | "really bad quality", voice "not the greatest" | Wanted dynamic, modern, premium, directed and orchestrated, and several versions to choose from |
| 16 Oct | Five Unmissed directions | **Bento loved** ("all together, sound and visuals"); The Call loved but the voice "sounds too fake"; The Catch and Manifesto "a little"; Night Shift "a big NO" | Music first, picture timed to it. A fake voice sinks good picture. AI footage of people at night: no |
| 16 Oct | Smart Mount social check videos | "not good, especially because the photo you used is a bad job photo ... I need a clean professional look on everything" | Never use a real photo that shows weak work or has doubtful rights. Licence-free, made in code, or AI with the label |
| 22 Oct | Kleidion (Lantern Road) | Too many cuts; the opening is sped up; it does not flow | 18 to 35 shots for 2.5 min; real-time moves |
| 22 Oct | Arabia (Clay) | Stars not rendered properly; cuts not natural; the screen feels bare | A sky is its own pass; a reason for every cut; fill the world |
| 22 Oct | Bamberg (Kinetic) | Good but not polished; effects with no intent | Every effect has a job |
| 22 Oct | Battle Map v1 | Good concept. Music not right: wants the feel of Age of Empires and Anno; no emoji graphics; a motion-graphics legend; pre-planned cameras; armies that never clip; the most entertaining explanation | Became Battle Map v2 and the free score engine (`docs/decisions/0003`, `0006`) |
| 22 Oct | Cutaway style board | "look amazing"; elevate with cinema lighting (haze, fog, god rays), animated fauna and flora, easter eggs in the soil (dino bones, gold ore), interesting angles | Became the cinematic Cutaway (`films/styles/cutaway/cinematic/`) |
| 22 Oct (20:24 Toronto) | Cutaway | Loves it; wants it as a KINOFORGE studio style | A spec-driven Cutaway line is being built (`films/lib/cutaway/`) |
| 23 Oct (17:32 Toronto) | Cutaway cinematic test vs seasons loop | Did not like the cinematic test (camera moves, cuts); liked the seasons loop: barely any camera movement, no cuts, lively world | The seasons loop is the base: one fixed view, a living world; art directions are ported to it |
| 23 Oct (19:34 Toronto) | Meadow film; the twelve Cutaway looks | Does not like Meadow at all; chose Fable | Fable on the seasons grammar is the art line; first series: 1-minute kids explainers (6 to 8) |
| 23 Oct (19:43 to 19:54 Toronto) | Kids pilot direction; two voice auditions | Wants recognisable everyday easter eggs and a lively 3D background, not a flat card; all ten Kokoro voices not kid friendly (the deep male ones scary) | Narrator is a smiling storyteller woman, free engines only; eggs and a living background in every kids film |
| 22 Oct | Money | "Spend nothing" (09:20), then "cost effective, cap the budget per film, but good results every time I pay" (20:50) | `docs/decisions/0013` (supersedes 0001) |

Waiting on his verdict (23 Oct): the eight Battle Map v2 films, the re-made Dark Corners, the NOOR samples, the Cutaway
films (Venice, the drainage sample ad, the seasons loop, the Agincourt inserts). See `docs/STATUS.md`.

## 4. The house styles (what each is, and what makes it good)

**Battle Map / Terrain** (`films/lib/battlemap/`, spec-driven, Three.js). A relief map that reads as drawn and engraved,
not CG: hillshade, contour lines, watercolour washes, ink arrows that draw on with a tapered head. v2 armies are many small
soldier figures on movement trays that meet at a front and never pass through each other. A legend panel names the
sides, the unit kinds and the key places as the narration names them. Good when: a child can say who is where and what
moved after one viewing; the decisive moment is shown twice (wide, then closer or slower); music is ambient and warm and
swells only at the turn. Reference film: `films/battles/cannae/` (its `NOTES.md`). Engine contract: `SPEC.md`.

**Lantern Road** (`proto/p03-lantern-road`, hand-built per film; NOOR uses it too). A painted 2.5D multiplane: brush
canvases at true depths, so a dolly gives real parallax; lanterns that relight the paint; a warm and cool colour script
carried by light. Good when: the light tells the story, moves are slow and real, every set breathes. Reference:
`films/dark-corners/zong/NOTES.md`, `films/dark-corners/kleidion/NOTES.md` (the re-direction).

**Clay** (`proto/p10-clay`, Blender, hand-built). Stop-motion grammar: poses on twos, hand jitter, squash and stretch,
deadpan timing. Good when: the world is full (oases, fires, animals, cloth that breathes), the sky is crisp, cuts are
motivated. Reference: `films/dark-corners/arabia/NOTES.md`.

**Kinetic** (`films/lib/kinetic/`, spec-driven; `proto/p11-kinetic`). Typography as cinema in 9:16: documents, dates,
numbers and quotes on one lit desk, cut on the beat, a real silence before the open loop, every word inside the phone
safe zone (rule R-2-08). Good when: each effect has a written job and the type never fights the voice. Reference:
`films/dark-corners/bamberg/NOTES.md`.

**Cutaway** (`films/styles/cutaway/` kit, `cinematic/` look; spec-driven line `films/lib/cutaway/` in progress). A block
of land cut out of the world: a living landscape on top, clean strata on the four sides, water as a clear glassy volume
you can see into. Good when: the cut shows something you could not otherwise see (why Venice sinks, where the drain
goes), the light is cinematic (golden backlight, haze, god rays as light cards), animals move, and the soil hides small
surprises lit like museum pieces. Free: Blender and Cycles on CPU or the Mac's GPU.

**Business looks** (`harness/shots/directions/`, ads in `ads/`): **Bento** (live tiles, day theme: Sam's chosen
direction for Unmissed), **Screen Story** (the product working on a 3D phone, clean type beside it), **Type in Motion**
(kinetic type in brand colours with real photo cut-outs). AI-image looks kept only as inserts: Flash Editorial, Hero
Close-ups, Freeze Frame (one solid subject only). Social templates (`social/templates/`): card-motion, bento, type-motion.

## 5. Rejected, and why (do not bring these back without Sam asking)

| Rejected | Why |
| --- | --- |
| Voltage, the stylised cartoon-3D AI look | "AI slop": everything looked the same |
| Documentary (AI people at work) and Night Shift (AI footage) | Sam: no, "a big NO" |
| Automatic "score and re-render" loops on paid video | Doubled the cost when the look itself was the problem: fix the look, not the clip |
| Emoji, cartoon icons, bouncing crowns and burst stars on maps | Sam, 22 Oct: refined graphics only |
| Full orchestral battle scores (Lyria) | Wanted ambient strategy-game music; replaced by the free score engine |
| Sped-up openings, cutting on music hits alone, more than 40 shots in 3 minutes | Kleidion and Arabia verdicts |
| ElevenLabs premade voices for dialogue | "Too fake" |
| Real install photos with weak workmanship or unclear rights | Smart Mount verdict; those photos are marked do-not-use |
| Free-only director as the default | free models too weak for the picture spec; Sam chose capped paid films (22 Oct 20:50, `docs/decisions/0013`) |
| Text, logos or numbers drawn by an image or video model | They come out wrong; words are always set in code |

## 6. How to decide when unsure

1. **Is it written down?** Search `docs/` (this file, `docs/decisions/`, the playbook for your job, `CRAFT.md`, the engine
   spec, the film's `NOTES.md`). A written rule beats your instinct; a newer verdict of Sam beats an older rule.
2. **Is it reversible and inside your folder?** Then decide, write the reason in `NOTES.md` or `docs/LOG.md`, and say so
   in your report. Sam wants few, small decisions: do not send him what you can decide well.
3. **Does it cost money, publish anything, touch a client, change a rule, or go against a verdict?** Then ask Sam. One
   short question, with your recommendation and the alternative, results and numbers first. He reads on his phone.
4. **Before you present anything:** check it yourself (the playbook "check a render before showing Sam"). If something
   does not make sense, fix it or say so; do not hand Sam a problem dressed as a result.
5. **Be honest about weak spots.** Every delivery names what is still weak and how you would fix it. Own mistakes plainly.
   Push back when there is a better way.
6. **Never improvise a rule.** If two documents disagree, follow the newer dated one, then fix the older one in the same
   commit (and log it).
