# Little Big Questions: real recordings and real sound effects (research, 23 Oct 2026)

Question: which real orchestral recordings (not MIDI, not sample libraries) can the six silent 60 s films use on YouTube, in
companion videos and in client work, for free; and which free, commercially usable sound-effect sources fit a kids' storybook film.

Confidence key: high = I read the page itself; medium = secondary page, mirror, or a label I could not cross-check;
low = search snippet, memory, or inference. LAWYER = needs a lawyer or an accountant before money or a client is involved.

---

## 0. Answer first

Top pick for the FOSSIL film: Mozart, The Magic Flute Overture, Musopen recording (Czech National Symphony Orchestra, 2012, 6:45).
Why: it is the only candidate that has all of these at once: (1) a modern digital orchestral recording with a dedicated
public-domain or CC label that I could read (IMSLP "Public Domain (dedicated)", Internet Archive "Public Domain Mark 1.0");
(2) a built-in magic moment (three solemn chords, then a hush) that can carry the bone-to-stone transformation; (3) a playful
whispering fugato that builds to a bright full-orchestra tutti, which is the dig, the build and the joyful find; (4) the
composer died 1791, so no composition question anywhere. Second: Grieg, Morning Mood (same project, CC BY 3.0 on IMSLP, credit
Musopen), for the quiet "deep time dawn" and the gentle sad beat. Third, only if the licence is confirmed: the Commons
recording of Saint-Saens "Fossiles" (it is literally the movement called Fossils, about 1:20 of xylophone bones) and the 1925
Stokowski "Danse macabre" (xylophone bones, public domain by date).

The honest limits (read before relying on any time range):
- I could NOT open Wikimedia Commons file pages, Musopen recording lists or download any audio from this session (hosts blocked, see section 1).
  So every licence below comes from IMSLP, Internet Archive, OpenGameArt or official pages that I could read; Commons-only claims are marked.
- I could not listen to or measure any file. Every time range in section 4 is an ESTIMATE from the known structure of the work,
  scaled to the duration printed on IMSLP. A cue-sheet pass on the real file (ffprobe plus onset and energy analysis on a runner)
  must fix each cut point to the frame before picture lock.
- No qualifying real recording exists (that I could find) of: The Sorcerer's Apprentice, Flight of the Bumblebee, a modern
  Nutcracker, Night on Bald Mountain (without ShareAlike), Debussy orchestral, Haydn Surprise, Strauss waltzes, Offenbach, a clean Vivaldi.

---

## 1. How this was checked, and what was blocked

- curl from this session reaches only api.github.com. commons.wikimedia.org, upload.wikimedia.org, archive.org, musopen.org,
  freesound.org, kenney.nl, pixabay.com and sonniss.com all failed at connect (proxy policy; the status call confirmed the proxy is on).
  I did not route around the block (the proxy README says report, do not circumvent). Source: /root/.ccr/README.md.
- WebFetch could read: IMSLP, archive.org item pages, opengameart.org, bigsoundbank.com, the Sonniss licence page, the Pixabay licence
  summary, YouTube Help, Wikipedia article pages, the Library of Congress. It could NOT read any Wikimedia Commons or Wikipedia
  "File:" page (url_not_found), so no Commons licence template was seen by me this session.
- The earlier brief (docs/research/CUTAWAY_USES_AND_MUSIC_2026-10.md) read some Commons files through the mirror c.enwp.org, and
  rc-render run 40023819924 recorded the Commons licence JSON for the Borodin file ("Public domain", Copyrighted False). I re-use
  only what that doc or `docs/manual/sound/music-fetch.md` states.
- Not done: no audio was downloaded, nothing was listened to, no file was measured. The fix is in section 7 (dispatch `music-fetch.yml`
  for the Commons titles listed there, then run a cue-sheet pass).

---

## 2. Rules applied

Licence classes accepted: public domain (PD) by date or by dedication, CC0, Public Domain Mark, CC BY (credit line in the description and end card).
Rejected: any NC; any ND (a 60 s excerpt cut to picture is an edit); any ShareAlike (SA).

Why SA is rejected for a film soundtrack: CC treats music set to moving images as an adaptation, and SA then asks for the combined
work to be SA. That is my reading of the CC position, not checked on the CC site in this session (confidence medium). LAWYER if anyone wants to rely on SA.
The EFF Open Audio License (used for the Seattle Youth Symphony Carnival on IMSLP) has the same share-alike rule: a new work containing or
derived from a licensed work "must itself be licensed as a whole under the terms of this license"; IMSLP also calls it outdated.
Source: https://imslp.org/wiki/IMSLP:EFF_Open_Audio_License (read; confidence high).

US recording dates (assumption carried from the earlier brief, arithmetic from the Music Modernization Act schedule): recordings first published in
1925 or earlier are US public domain as of 1 Jan 2026; 1926 recordings follow on 1 Jan 2027; 1927 on 1 Jan 2028. The Library of Congress National
Jukebox rights text confirms only the pre-1923 step on 1 Jan 2022 and the later steps in general terms
(https://www.loc.gov/item/jukebox-11207, read; confidence high for that statement, medium for my extension to 1925).
IMSLP rows tagged "Public Domain - Non-PD US" are NOT usable (1950s and 60s commercial recordings, still protected in the US).

US government bands: works of US federal employees are not protected in the US (17 USC 105). Outside the US this is a LAWYER question.
A band playing a copyrighted ARRANGEMENT is a second question (the arrangement is its own copyright).

### Compositions: any still in copyright? (death dates from general knowledge, NOT source-checked here; confidence high on dates, medium on conclusions)

| Composer | Died | US | Canada | EU/UK (life + 70) | Note |
|---|---|---|---|---|---|
| Mozart, Grieg, Mendelssohn, Smetana, Borodin, Tchaikovsky, Rimsky-Korsakov, Saint-Saens, Debussy | 1791 to 1921 | PD | PD | PD | none |
| Holst (The Planets) | 1934 | PD (published 1921) | PD | PD since 2005 | band transcriptions may be separate copyrights |
| Dukas | 1935 | PD | PD | PD since 2006 | no clean recording anyway |
| Glazunov | 1936 | PD | PD | PD | |
| Ravel | 1937 | PD | PD | PD | |
| Grainger (Children's March on the Marine Band disc) | 1961 | PD if published before 1931 | PD (life + 50 ended 2011) | IN COPYRIGHT to end of 2031 | YouTube is global; EU claims or blocks possible |
| Ketelbey | 1959 | PD | PD | IN COPYRIGHT to end of 2029 | skip |

Conclusion: every piece proposed below is out of copyright as a composition in Canada, the US and the EU. The only live risks are (a) band or other arrangements
and (b) the recording rights, which is what the licence evidence below is for. LAWYER for (a) and for the Canada term for 1920s sound recordings.

---

## 3. Recordings that qualify (catalogue)

Credit rule for every Musopen item: credit "Musopen" in the description even where a page says no attribution is needed. The labels disagree between
IMSLP pages for the same 2012 project (CC0, "Public Domain (dedicated)", CC BY 3.0; the Internet Archive collection says "Public Domain Mark 1.0").
Treat all as CC BY 3.0 and credit. Orchestra name conflict: IMSLP says Czech National Symphony Orchestra, Wikipedia says the Czech Philharmonic was commissioned
(https://en.wikipedia.org/wiki/Musopen, read). Credit "Musopen" and avoid naming the orchestra until the Musopen page is read in a browser.

Archive for the whole 2012 set: https://archive.org/details/MusopenCollectionAsFlac (read; "Public Domain Mark 1.0"; FLAC 32 bit; 145 files in 37 folders;
the folder names are listed on the page and the directory https://archive.org/download/MusopenCollectionAsFlac shows the folders). It contains Peer Gynt Suite 1,
Vltava, Hebrides, the Italian and Scottish symphonies, Magic Flute Overture, Marriage of Figaro, Russian Easter Overture, Egmont, Coriolan, Borodin Steppes, Mozart 40,
Brahms, Beethoven 3, Tchaikovsky 6, plus quartets and sonatas. It does NOT contain Carnival, Nutcracker, Midsummer Night's Dream, Sorcerer's Apprentice or Planets.
A second, smaller copy: https://archive.org/details/musopen-dvd-in-lossless-flac-format (24 bit FLAC for 39 files incl. Peer Gynt, Hebrides, Magic Flute, Figaro; "Public Domain Mark 1.0"; read).
The Musopen blog confirms the project, names the pieces and says "the beauty of public domain music": https://musopen.org/blog/news/2/musopen-kickstarter-project-1-complete (read; it names no licence; confidence medium).

| ID | Work, performer | Length | Licence evidence (URL, what it says) | Conf. |
|---|---|---|---|---|
| R1 | Mozart, Magic Flute Overture, Czech National SO / Musopen 2012 | 6:45 | https://imslp.org/wiki/Die_Zauberfl%C3%B6te,_K.620_(Mozart,_Wolfgang_Amadeus) : "Public Domain (dedicated)", uploaded 2012/8/17. IA set above: PDM 1.0 | high (IMSLP read) |
| R2 | Mozart, Marriage of Figaro Overture, same | 4:05 | https://imslp.org/wiki/Le_nozze_di_Figaro,_K.492_(Mozart,_Wolfgang_Amadeus) : "Public Domain (dedicated)" | high |
| R3 | Grieg, Peer Gynt Suite 1, same: Morning Mood 3:53, Death of Aase 4:38, Anitra's Dance 4:04, Mountain King 2:38 | see left | https://imslp.org/wiki/Peer_Gynt_Suite_No.1%2C_Op.46_(Grieg%2C_Edvard) : "Creative Commons Attribution 3.0" (credit Musopen) | high |
| R4 | Smetana, Vltava (The Moldau), Musopen Symphony | 12:51 | https://imslp.org/wiki/Vltava%2C_JB_1%3A112%2F2_(Smetana%2C_Bed%C5%99ich) : "Creative Commons Zero 1.0", uploaded 2018/8/15, file PMLP85117-Smetana-Vltava.mp3 29.61 MB, "lossless file also available" | high for the label; medium that it is the same take as the 2012 IA folder `Smetana_Vltava` |
| R5 | Mendelssohn, Hebrides Overture, Czech NSO / Musopen | 11:27 | https://imslp.org/wiki/Die_Hebriden,_Op.26_(Mendelssohn,_Felix) : "Creative Commons Attribution 3.0". Do NOT use the Munich student recording on the same page (CC BY-SA 4.0) | high |
| R6 | Mendelssohn, Italian Symphony IV Saltarello, Czech NSO / Musopen | 6:12 (movement) | https://imslp.org/wiki/Symphony_No.4,_Op.90_(Mendelssohn,_Felix) : "Creative Commons Attribution 3.0". Same page: Munich (SA) and the 1950s Columbia and London rows are not usable | high |
| R7 | Borodin, In the Steppes of Central Asia, Musopen 2012 | 7:38 | already fetched on 23 Oct (run 40023819924): Commons record "Public domain", Copyrighted False, AttributionRequired false. IMSLP says CC0. See `docs/manual/sound/music-fetch.md` | high |
| R8 | Saint-Saens, Danse macabre, Philadelphia Orchestra / Stokowski, recorded 29 Apr 1925, Victor 6505 (matrix CVE-27929 and CVE-27930), early electrical | 6:54 (two sides joined) | https://archive.org/details/PhiladelphiaSymphonyOrchestra-DanseMacabre : uploader label "CC0 1.0 Universal", recording date 4/29/1925, uploaded 2012-03-09 by sabinelr. The PD basis is the date (1925 or earlier = US PD from 1 Jan 2026), not the uploader's label. Another copy of side 2: https://archive.org/details/78_danse-macabre-dance-of-death_philadelphia-symphony-orchestra-saint-sens-leopold_gbia0335078b (Victrola 6505-B, publication 1925, 3:12). The DAHR matrix page https://adp.library.ucsb.edu/index.php/matrix/detail/800001920/CVE-27930-Danse_macabre_op._40 could not be fetched, so the first-release date is not independently confirmed | medium (release date unconfirmed; LAWYER for Canada and EU) |
| R9 | Holst, The Planets (incomplete: no Saturn, no Neptune), US Air Force Heritage of America Band | n/a | https://opengameart.org/content/holst-the-planets-suite : licence "CC0", "free of all known copyright restrictions", uploader says "the quality is not the best", submitted 13 Apr 2015, 37.3 MB zip. A comment says the full suite is at https://archive.org/details/Holst-ThePlanets (could not be fetched) | medium (band arrangement copyright unknown; LAWYER) |
| R10 | Holst, The Planets, London Symphony Orchestra, Holst conducting, Columbia "1923": whole suite 44:41, and a Saturn restoration 7:05 | see left | https://imslp.org/wiki/The_Planets,_Op.32_%28Holst,_Gustav%29 : "Public Domain" (no "Non-PD US" tag). CONFLICT: a 44:41 whole suite looks like the 1926 electrical set, which would not be US PD until 1 Jan 2027; the page says 1923 | low until the real publication date is checked |
| R11 | Saint-Saens, Carnival of the Animals, movements as separate .ogg on Commons: 04 Tortues, 05 L'Elephant, 06 Kangourous, 07 Aquarium, 09 Coucou, 10 Voliere, 11 Pianistes, 12 Fossiles, 13 Le cygne, 14 Final, plus a complete "Camille Saint-Saens - The Carnival of the Animals.ogg" | Fossiles about 1:20 (my knowledge) | File names read from https://c.enwp.org/wiki/Category:Le_Carnaval_des_animaux (read; the category holds 72 files; performers NOT named). The Commons file pages could not be opened. Likely source (INFERENCE, not verified): the Seattle Youth Symphony / Vilem Sokol recording on IMSLP, labelled "EFF Open Audio License" (share-alike, see section 2) | low: NOT usable until the Commons licence template is read |
| R12 | Saint-Saens, The Swan, Matilda Colliard (cello) and Stefano Ligoratti (piano), live, Milan: Classica Viva | 2:38 | https://imslp.org/wiki/Le_carnaval_des_animaux_(Saint-Sa%C3%ABns%2C_Camille) : "Creative Commons Attribution 4.0" | high |
| R13 | Tchaikovsky, Valse des fleurs, Emerson Orchestra / Hochman, Emerson Phonograph, 1919 | 3:28 | https://imslp.org/wiki/The_Nutcracker,_suite,_Op.71a_(Tchaikovsky,_Pyotr_Ilyich) : "Public Domain" (also in the earlier brief). Acoustic horn sound | medium (quality weak) |
| R14 | US Marine Band Showcase Volume Two (Grainger Children's March, Saint-Saens Orient et Occident, Bach/Knox, Beethoven) | n/a | https://www.marineband.marines.mil/Audio-Resources/Educational-Series/Marine-Band-Showcase-Volume-Two/ : download links on tracks 1 to 4 and 6, NO rights statement on the page | medium; Grainger is in EU copyright |
| R15 | US Navy Band, "Light Cavalry Overture and other WARHORSES" (2005) | 3 files online | https://archive.org/details/LightCavalryOvertureAndOtherWarhorses : "Public Domain Mark 1.0"; only Liszt Hungarian Rhapsody 2, Weber Oberon and Rossini Italian Girl are online. The liner notes list Dukas, The Sorcerer's Apprentice on the CD, but it is NOT one of the 3 online files | high for the 3 files; Sorcerer's Apprentice not available |

### Looked at and rejected (so nobody re-checks)

| Item | Why | Source |
|---|---|---|
| Vivaldi Four Seasons, John Harrison and Wichita State Chamber Players (live 2000) | CC BY-SA (share-alike) | https://freemusicarchive.org/music/John_Harrison_with_the_Wichita_State_University_Chamber_Players/The_Four_Seasons_Vivaldi (read) |
| Seattle Youth Symphony Carnival (22:52) | EFF Open Audio License = share-alike | IMSLP Carnival page (read) |
| DuPage Nutcracker, University of Chicago Danse macabre and Vltava | CC BY-NC-ND | IMSLP pages (read) |
| Munich Hochschulsymphonieorchester Hebrides and Saltarello | CC BY-SA 4.0 | IMSLP pages (read) |
| Dukas Sorcerer's Apprentice (Munch, Solti, Ansermet, Fiedler, Toscanini 1929) | all "Non-PD US" | https://imslp.org/wiki/L%27apprenti_sorcier_(Dukas%2C_Paul) (read) |
| Bumblebee | only Stern/Columbia 1963, "Non-PD US" | https://imslp.org/wiki/Flight_of_the_Bumblebee_(Rimsky-Korsakov,_Nikolay) (read) |
| Midsummer Night's Dream | IMSLP lists 0 recordings | https://imslp.org/wiki/A_Midsummer_Night%27s_Dream,_Op.61_(Mendelssohn,_Felix) (read) |
| Debussy Children's Corner | piano only, NC-ND or Non-PD US (no orchestral Caplet or Busser recording) | https://imslp.org/wiki/Children%27s_Corner_%28Debussy%2C_Claude%29 (read) |
| Kevin MacLeod "Classical Sampler" Sugar Plum Fairy (CC BY 3.0, 1:59) | the page does not say how it was made; I believe it is synthesized (assumption, low); it fails the "real recording" brief | https://freemusicarchive.org/music/Kevin_MacLeod/Classical_Sampler/Dance_of_the_Sugar_Plum_Fairy/ (read) |
| Commons "PDP-CH" series (e.g. National Symphony Orchestra of London, Stanford Robinson, Decca K1142 Sugar Plum Fairy) | a Swiss public-domain tag on a 78 of the 1930s or later; US status unknown; not read | search result title only (low) |
| Das Orchester Tsumugi (Japan), Saltarello 6:01 | CC BY 3.0 but an amateur orchestra; not explored further | IMSLP Symphony 4 page (read) |

---

## 4. Per film (Fossil first)

All time ranges are ESTIMATES (see section 0). "Phrases" lists the musical events to cut picture to, in order; confirm on the file.
Where I write "est. m:ss" the figure is scaled from the IMSLP length and the known shape of the work. One first choice per film so the six films do not all sound alike.

### 4.1 FOSSIL (dinosaurs, deep time, a magical bone-to-stone moment, a joyful find)

The film needs wonder and warmth, a magic beat, a build, and a bright reveal.

1. FIRST CHOICE: R1, Mozart Magic Flute Overture (6:45, Musopen).
   - Phrases (from the score structure, est.): three solemn chords at 0:00 (bone to stone: land the transformation on the third chord); a hushed Adagio of winds and brass (est. 0:00 to 1:05) ending on a general pause; the Allegro starts pianissimo in the violins (est. 1:05) and enters instrument by instrument (a whispering dig), building to the first full-orchestra tutti (est. 1:40 to 1:50) = the find; the three chords return mid-piece (est. 3:30); the final coda (est. last 12 s) = the button.
   - Suggested excerpt, about 70 s: 0:00 to 0:14 (chords and first phrase), splice at the Adagio's pause to the Allegro entry est. 1:05 to 1:50 (45 s), then hard cut to the final tutti est. 6:33 to 6:45. The Adagio pause and the Allegro entry are natural joints; confirm on the file.
   - Mood fit: magic and wonder yes; "gentle sad" is weak (the intro is solemn, not sad).
2. SECOND: R3-I, Grieg Morning Mood (3:53, Musopen, CC BY 3.0, credit Musopen). For the opening "deep time dawn" and the quiet sad beat when the bone becomes stone.
   - Phrases (est.): solo flute theme (0:00 to 0:30); oboe answer (0:30 to 1:00); the theme steps up a key (est. 1:00 to 1:10, "sun lifts"); string build (1:10 to 1:45); radiant full-orchestra statement (est. 1:45 to 2:15) = the joyful reveal; long calm fade with flute and oboe echoes (2:15 to 3:53).
   - Suggested excerpt, 90 s: est. 0:35 to 2:05. Mood fit: warm and wondering yes; playful no.
3. IF CLEARED: Saint-Saens "Fossiles" (R11), the ideal subject match: xylophone "rattling bones", a Danse macabre quote, Au clair de la lune, and short enough (my knowledge, about 1:20) to need no cutting. Not usable until the Commons file page shows a licence we can use (CC0, PD or CC BY). If it turns out to be the Seattle/EFF recording (share-alike), skip it.
   FALLBACK for the same bones idea: R8, Stokowski Danse macabre 1925 (6:54). Phrases (est.): twelve harp strokes (midnight) at 0:00; the solo violin enters est. 0:25; the waltz; the xylophone bones episode mid-piece (est. 3:00 to 3:40, check); the oboe cockcrow near the end (est. last 40 s) = dawn. Excerpt, 60 to 80 s: the xylophone episode plus the cockcrow. Sound: 1925 electrical, narrow band, surface noise. Skeletons and death are the theme; for ages 6 to 8 it is Halloween-playful, not scary, but it is a taste call for Sam.
4. GENTLE SAD MOMENT (an insert, not a whole film): R12 The Swan, CC BY 4.0, 2:38 (credit "Matilda Colliard and Stefano Ligoratti, Classica Viva, CC BY 4.0"). Live recording, so audience noise is possible (not checked).
5. Texture options, weaker: R10 Holst Saturn (deep time, "Bringer of Old Age"; date unresolved, see R10); R7 Borodin Steppes (CC0, slow).

### 4.2 VOLCANO (rumble, build, eruption, then calm)

1. FIRST CHOICE: R3-IV, Grieg In the Hall of the Mountain King (2:38). One continuous accelerando from a whisper to a crash: rumble to eruption is built in.
   Phrases (est.): creeping pizzicato theme at pianissimo (0:00 to 0:40); each repeat gets louder and faster (0:40 to 1:50); the last run into the final crash (est. 2:20 to 2:30); a beat of silence; the last chord (2:38). Excerpt about 85 s: 0:00 to 0:40, splice to 1:50 to 2:38. Kids' fit: playful-ominous; the end is comic chaos, not horror.
2. R6, Mendelssohn Italian Symphony, Saltarello (6:12): a fast Italian dance in A minor with a rolling triplet drive; Italy = Vesuvius. Excerpt 0:00 to 1:30 (est.); keep it for a hot, busy second act.
3. Do not use Night on Bald Mountain (only SA recordings, and too scary) or Holst Mars (no clean orchestral file, too martial).

### 4.3 RAIN (cloud, first drops, stream, river, sun back)

1. FIRST CHOICE: R4, Vltava (CC0, 12:51). It opens with two rippling flute and clarinet lines that read as the first drops of two springs, then joins into the great river theme.
   Phrases (est., scaled to 12:51): two springs (0:00 to 1:30); the river theme in the strings and oboe (est. 1:30 to 3:00); a forest hunt (horns) and a village wedding polka (est. 3:00 to 6:00); moonlight nymphs (est. 6:00 to 8:00); the rapids (est. 8:30 to 10:00); the river broadens in a major key (est. 10:30 to 11:30); quiet end.
   Excerpt about 75 s: 0:00 to 0:55 (drops to stream), splice to the broad major-key river est. 10:35 to 10:55 for the joyful reveal. The cue-sheet pass must find the real splice points.
2. R3-I, Morning Mood, for the "rain stops, sun returns" end beat (same estimates as 4.1).
3. R5, Hebrides opening, if the rain is a storm at sea (see 4.4).

### 4.4 DEEP SEA (descent, strange lights, a wonder reveal, return)

1. FIRST CHOICE: R5, Mendelssohn Hebrides (CC BY 3.0, 11:27, credit Musopen). The first bars are a rolling wave motif in low strings.
   Phrases (my knowledge of the score, est.): rolling wave motif (0:00 to 0:30); first swell (0:30 to 1:30); the warm cello and bassoon second theme (est. 1:45 to 2:30) = a creature appears; stormy development (est. 4:00 to 6:30); calm clarinet coda (est. last 1:30) = return to the surface.
   Excerpt about 80 s: 0:00 to 0:30, splice to est. 1:45 to 2:35.
2. R4 Vltava, moonlight section (est. 6:00 to 8:00): muted strings, flutes and harp, a shimmering "water spirits at night" mood; a good bioluminescence bed, 90 s. If R4 is used for Rain, keep this section for Shooting Star and use Hebrides here.
3. R11 "Aquarium" (Commons, about 2:20 in the usual recording): the obvious title, but the licence is unverified, see R11.
4. Holst Neptune would be ideal; it is absent from the CC0 band set (the uploader says Saturn and Neptune are missing). The Holst LSO set is not cleared (R10).

### 4.5 SHOOTING STAR (night sky, a streak, wonder, a wish)

1. FIRST CHOICE: R3-III, Grieg Anitra's Dance (4:04, CC BY 3.0). Light strings with a triangle: a twinkling, dancing sparkle; easy to cut to short phrases.
   Phrases (est.): a lilting string melody (0:00 to 0:30); a repeat with fuller texture (0:30 to 1:20); a gentle rise to a tutti (est. 1:50); a soft close. Excerpt 60 to 80 s: 0:00 to 1:20.
2. R4 Vltava moonlight (est. 6:00 to 8:00), the "night magic" section (see 4.4).
3. R9 Holst Planets, USAF Heritage of America Band, CC0: Venus (calm) or Uranus (the Magician, playful and strange) or Mercury (fast flicker). Only the movement tags (Mars, Venus, Mercury, Uranus) are known to me; band sound is thinner than an orchestra. Check the zip's COPYING file and the arrangement credit first. LAWYER if used in client work.
4. R13 Valse des fleurs 1919 for sparkle and a nod to the Nutcracker, if a vintage sound is a deliberate choice.

### 4.6 UNDER YOUR FEET (animals under the ground, burrows, roots, worms)

1. FIRST CHOICE: R2, Mozart Marriage of Figaro Overture (4:05, Musopen). A hushed, scurrying string and bassoon opening that sounds like many small feet in tunnels, then a bright burst: the hidden world revealed. Phrases (est.): scurrying whisper (0:00 to 0:12); first tutti burst (est. 0:12); lilting second theme (est. 0:40 to 1:20); a repeat; the coda (last 20 s). Excerpt 60 to 70 s: 0:00 to 1:05. Playful and bright; not warm or sad.
2. R3-IV, the Mountain King (a literal underground kingdom of small creatures when only the quiet first half is used): 0:00 to 1:10 (est.). Do not use if it is already the Volcano film.
3. R7, Borodin Steppes (CC0, 7:38): a slow, warm bed for roots and soil; low energy, no playfulness.

### 4.7 Series view (first choices, all different)

| Film | First choice | Credit needed |
|---|---|---|
| Fossil | R1 Magic Flute Overture | Musopen (credit anyway) |
| Volcano | R3-IV Mountain King | Musopen, CC BY 3.0 |
| Rain | R4 Vltava | Musopen (CC0, credit anyway) |
| Deep sea | R5 Hebrides | Musopen, CC BY 3.0 |
| Shooting star | R3-III Anitra's Dance | Musopen, CC BY 3.0 |
| Under your feet | R2 Figaro Overture | Musopen (credit anyway) |

Suggested credit line: "Music: Wolfgang Amadeus Mozart, The Magic Flute Overture, recorded by Musopen (public domain / CC BY 3.0 / CC0), via the Internet Archive and IMSLP." One line per film; keep the evidence packet from section 6.

---

## 5. Sound effects

### 5.1 BigSoundBank (CC0): new ids beyond the 197 already in the bank

Licence: https://bigsoundbank.com/licence.html (read): "Creative Commons CC0 1.0 Universal", also WTFPL and a public-domain dedication; "Use, including for commercial purposes"; attribution not required;
"Nothing is mandatory" (confidence high). The bank CSV (release sfx-bank, `sfx-bank.csv`, read) already holds, among others, whoosh s1795 to s1802 (partial), splash s1519 and s1529, bubbles s0150 and s1074,
candle sparkle s1278 and s1279, music-box winder s1674, steps s0495 s0510 s0165 s0606, bumblebee s1000 s1001, bird flight s2891 s2892, pencil, paper and cloth. The list below is what the bank LACKS for kids' films.
IDs come from the category and search pages (high confidence that id and title match; the per-sound licence is the site licence). Durations are as listed.

| Need | ids and titles (duration) |
|---|---|
| Soft boings (a harp imitating a cartoon bounce) | s2277 Boing cartoon #1 (3 s), s2278 #2 (3 s), s2279 #3, s2280 #4, s2281 #5, s2282 #6, s2283 #7 (2 s), s2284 #8 (2 s). Category page: https://bigsoundbank.com/search?CatID=TOON |
| Cartoon bops ("Planted cartoon", French title "plante cartoon"; listen first, I only have titles) | s1950 to s1960 (#1 to #11), 2 to 4 s |
| Pops and plops | s0274 Wine stopper #1, s1719 #3, s1720 #4, s0211 and s0648 Champagne cork, s0547 s1619 s1860 Cap cider, s1261 Suction cup on plastic, s1262 on window, s0928 Sucker, s1244 s1245 s1246 Straw suction, s0183 Water bubble #2 |
| Squeaks and toy sounds | s0879 Squeaker toy #2, s3331 to s3338 Couinement jouet #1 to #8 (1 to 3 s), s0364 Coin-coin (toy duck), s0427 Pouet of a toy, s0366 Bird song 2 (toy), s0371 Rattle, s0633 Metal slinky (12 s), s1827 to s1832 pneumatic horn (1 to 2 s) |
| Chimes, sparkles, magic | s2079 to s2086 Chimes "Dream" #1 to #8 (2 to 3 s), s2087 to s2091 Chimes "Butterfly" #1 to #5 (3 to 6 s), s2687 Cluster chimes (3:47 bed), s0040 Dreamcatcher (7 s), s0920 Glockenspiel (20 s), s1688 Triangle #2 (8 s), s3067 Metallophone (4 s), s1109 s1110 s2553 s2554 Tibetan bowl, s0230 Sparkling water (14 s) |
| Soft footsteps | s0181 barefoot on wooden stairs (10 s), s0373 slipper on floor (10 s), s1253 steps in the grass slow (24 s), s0854 steps in short grass (31 s), s0137 and s2889 feet in leaves, s1301 steps on twigs, s0839 feet on pebbles, s1843 running in tall grass, s1836 s1837 s1839 jumps (1 to 2 s), s3363 and s0208 snow |
| Munching and crunching | s1113 Apple crunched #1 (14 s), s1114 #2 (8 s), s0407 Eat a rusk (14 s), s1594 Raw carrot crunched (13 s), s1432 Eating potato chips #2 (18 s), s0185 Rat nibbling (35 s), s1244 Straw suction (slurp) |
| Brushes (digging, dusting a fossil) | s1961 Brush (14 s), s1106 Brush on wood, s1107 Brush on concrete (20 s, closest to a brush on rock), s1856 Horsehair brush, s0163 Straw broom, s0024 Broom, s0718 Toothbrush (comic) |
| Splashes | s1519 s1520 s1521 big (4 to 8 s), s1529 to s1534 small (2 to 3 s), s0192 Swirl in the water, s0507 Small cascade, s1522 Flowing water, s0563 Liquid flowing over the soil |
| Whooshes and flaps | s0572 Whoosh #1 (11 s), s0573 #2 (13 s), s1798 #10, s0128 Sword through the air, s2032 Boomerang pass, s2893 s2894 Flight bird #3 and #4, s0840 and s0476 pigeon, s0797 Bumblebee against a window |

DO NOT USE (the sound contains a copyrighted tune, even though the recording is CC0): s3535 Harry Potter Theme on Carillon; s0465 "White Christmas" Music Box. s0417 Mallard duck plush and s0416 Plush music box play unnamed tunes: identify the tune first.
Whole catalogue: https://bigsoundbank.com/categories.html (110 categories, e.g. CARTOON 32, TOYS 44, FOOTSTEPS 75, FOOD & DRINK 142, MUSICAL 227, WATER 125; read).
Not browsed: pages 2 to 6 of MUSICAL, 2 to 4 of FOOD, FOOTSTEPS and WATER (only the first 40 of each category were read). Searches "sparkle" and "giggle" returned no kid voices.

### 5.2 Other free sources

| Source | Licence evidence | Verdict | Conf. |
|---|---|---|---|
| Sonniss #GameAudioGDC bundles | https://sonniss.com/gdc-bundle-license/ (read): personal and commercial projects, unlimited projects, no attribution, may modify, may redistribute; you may not sell the effects as they come or modify them to claim authorship; the page does not mention Content ID or AI training. GDC 2026: 7.47 GB, 17 vendors, released 16 Mar 2026, download at gdc.sonniss.com (https://rekkerd.org/sonniss-releases-gdc-2026-game-audio-bundle/, read). A third-party page says licence "version 2.0, effective 27 August 2026" with a ban on AI training and on giving away sounds as sound effects (https://tryslicemedia.com/podcast-tools/sonniss, read, secondary) | Best professional source: real recordings by pro sound designers. Save the licence PDF as it stands on the day of download. Do not use it to train or fine-tune any model. | high for the main licence, low-medium for the v2.0 detail |
| Pixabay sound effects | https://pixabay.com/en/service/license/ (read): free use, no attribution needed, modification allowed; no standalone sale or distribution; no recognisable trademarks; "only the full Content License is legally binding"; Content ID not mentioned | Usable; quality mixed (user uploads, may be synthesized). Prefer sounds that are clearly recordings; keep a screenshot per sound. | medium |
| Kenney audio | https://opengameart.org/content/interface-sounds (read): CC0, 100 OGG files, credit "not mandatory"; a secondary list gives Impact Sounds 130, RPG Audio 50, UI Audio 50 (https://gtstu.com/?p=5011, read, secondary) | Clean CC0 but mostly UI blips and impacts; little that is kid-playful. | high (Interface), medium (the rest) |
| OpenGameArt CC0 | https://opengameart.org/content/cc0-sounds-library (ETTiNGRiNDER, CC0, 54 packs: magic spells, kitchen, footsteps, water; real or synthesized not stated); https://opengameart.org/content/pop-sounds (cogitollc, CC0, 10 files made on an iPhone SE, so real); https://opengameart.org/content/baby-animals-sounds-pack (CC0 but built from nine freesound clips with unchecked licences) | Pop sounds: fine. Baby animals: skip until the nine freesound licences are checked (some may be CC BY or NC). | medium |
| Freesound, CC0 filter only | freesound.org not fetchable here; a secondary page says the CC0 filter gives no-attribution sounds and CC BY needs credit (https://gtstu.com/?p=5011) | Usable with the CC0 filter; record the sound id and a screenshot of the licence per sound. I give no ids because I could not browse it. | low |
| Mixkit | https://mixkit.co/llm-info/ (read): Free License allows commercial use with no attribution, but items cannot be resold unaltered, and a separate "Restricted" licence is personal-only | Usable per item; check each item's licence badge. The full text at mixkit.co/license/ was not read. | medium |
| Morphonaut "Cartoon Comic Sound Pack" on itch.io | https://morphonaut.itch.io/cartoon-comic-sound-pack : surfaced in a search; licence NOT read | Unverified, skip until read. | low |

Not recommended, from memory and NOT checked this session (low): BBC Sound Effects archive (non-commercial licence), Orange Free Sounds (NC).

---

## 6. YouTube Content ID and public-domain classical recordings

What the evidence shows (thin; I found no study with frequencies):
- A public-domain COMPOSITION does not make a RECORDING public domain, and anyone can register a copy of a public-domain recording in Content ID through a distributor.
  Source: TunePocket (sells royalty-free music, so biased; single case study): https://www.tunepocket.com/youtube-copyright-claim-public-domain/ and https://www.tunepocket.com/public-domain-music-safety-tips/ (both read; confidence low to medium).
- One documented case with Musopen: a 2016 forum post. A video using a Musopen Mozart oboe concerto was claimed by "Adshare" (publishing); the video was monetised with revenue sharing; the outcome was not reported.
  https://yttalk.com/threads/copyright-claim-on-classical-music-from-a-public-domain-site.204501/ (read; confidence medium that it happened, low that it is typical). The poster could not name the performer, which weakened the dispute.
- Musopen's own FAQ says public-domain works are free "for any purpose, even if sold for profit", but it "cannot guarantee that every upload is" public domain, and it says nothing about Content ID.
  https://musopen.org/faq/ (read; high).
- I found NO source saying Content ID is known to flag the specific 2012 Musopen orchestra recordings. Treat the risk as real but unquantified (unknown).
- Historic recordings (R8, R13) carry a different risk (assumption, low): labels re-release and remaster 1920s recordings and may fingerprint them.

How creators handle a claim (YouTube Help, read; confidence high): dispute with a reason; the claimant has 30 days to respond; they can release, reinstate, let it lapse, or file a copyright removal request (a valid one creates a strike);
an appeal gives the claimant 7 days; a counter-notification is possible after a removal request; a dispute cannot be cancelled; repeated abusive disputes are penalised.
https://support.google.com/youtube/answer/2797454?hl=en&co=GENIE.Platform%3DAndroid
Dispute steps (TunePocket, low-medium): choose "Public domain", confirm ownership, write a specific rationale with source URL and date.

Practical plan (my recommendation, not a source):
1. Evidence packet per film, saved in the film's NOTES.md: for each recording the exact page URL, retrieval date, licence text copied, performer, recording date, and a screenshot. For R8 add the recording date (29 Apr 1925) and the first-issue date from a discography.
2. Upload as Unlisted first and read the Studio "Copyright" status before going Public. A claim on an unlisted video costs nothing.
3. Put the credit line, the licence and the source link in the description so a human reviewer sees the basis.
4. Prefer the Musopen 2012 set and the Internet Archive PDM item over anything pulled from a streaming service.
5. If a claim appears, dispute with the packet. A claim can still mute or block a video in some countries even where ad revenue is small (Made for Kids pays little, see the earlier brief), so do not let one sit.
6. LAWYER: if a client's channel carries the film, agree in writing who handles a claim.

---

## 7. Gaps and next steps

| Gap | Fix |
|---|---|
| No Commons licence record seen for any Commons-only file | Dispatch `music-fetch.yml` (Sam's own workflow) for these titles; each run saves a `.licence.json`. Titles are copied from search-result page titles and may need a re-check: `Grieg_-_Peer_Gynt_Suite_No._1,_Op._46_-_I._Morning_Mood_(Musopen_Symphony).flac`; `Grieg_-_Peer_Gynt_Suite_No._1,_Op._46_-_IV._In_the_Hall_of_the_Mountain_King_(Musopen_Symphony).flac`; `Mendelssohn_-_Hebrides_Overture,_Op._26_(Musopen_Symphony).flac`; `Mozart_-_Magic_Flute_Overture.ogg`; `Mozart,_The_Marriage_of_Figaro_(overture).ogg`; `Saint-Saens_-_The_Carnival_of_the_Animals_-_12_Fossiles.ogg`; `Saint-Saens_-_The_Carnival_of_the_Animals_-_07_Aquarium.ogg`; `PhiladelphiaSymphonyOrchestra-DanseMacabre.ogg`; `Felix_Mendelssohn_-_symphony_no._4_in_a_major_'italian',_op._90_-_iv._saltarello.ogg`. The Anitra's Dance and Vltava Commons titles were not surfaced. |
| The full-quality Musopen FLACs live on archive.org, which the chat sandbox cannot reach | Ask Sam before adding a runner workflow for archive.org (folders `Greig_PeerGynt`, `Mozart_MagicFluteOverture`, `Mozart_MarriageOfFigaro`, `Mendelssohn_Hebrides`, `Mendelssohn_ItalianSymphony`, `Smetana_Vltava` under https://archive.org/download/MusopenCollectionAsFlac/). File names inside the folders were not read. |
| All cut points are estimates | Cue-sheet job on a runner: ffprobe for exact durations, then an energy and onset analysis (librosa or ffmpeg ebur128) to print bar-start times and the loudest 8 s windows for each piece; add the table to each film's NOTES.md. |
| No listening test | Someone must listen. I could not judge orchestral quality. |
| R10 Holst date | Check the real first-issue date of the LSO set (1923 acoustic vs 1926 electrical) before use; LAWYER if the answer is 1926. |
| R9 and R14 band arrangements | Find the arranger credit (Planets zip COPYING file; Marine Band liner notes). If the arrangement is a living arranger's work, do not use. LAWYER. |
| R11 Carnival of the Animals (Fossiles, Aquarium, Elephant, Final) | Read the Commons licence template. If "Open Audio License" or CC BY-SA, skip. Otherwise Fossiles becomes the top Fossil pick. |
| No clean Sorcerer's Apprentice, Bumblebee, modern Nutcracker, Bald Mountain, Haydn Surprise, Strauss, Offenbach, Debussy orchestral | None exists in the sources I could read. Next-best: check the Navy Band's own download page (navyband.navy.mil) for the Dukas track, which I could not reach; or commission a recording. |
| Freesound and Pixabay inventories | Not browsed; pick specific ids later with a browser. |
| Canada and EU terms for 1925 sound recordings, "public domain worldwide" for US-government bands, whether a CC BY credit in the description is enough | LAWYER (same open items as the earlier brief). |

---

## Sources checked (read this session unless marked)

IMSLP: Carnival of the Animals; Vltava; Danse macabre; Peer Gynt Suite 1; Nutcracker Suite; Magic Flute; Marriage of Figaro; Hebrides; Symphony 4 (Mendelssohn); The Planets; Children's Corner; Midsummer Night's Dream; Flight of the Bumblebee; Dukas; Strauss album; EFF Open Audio License page.
Internet Archive: MusopenCollectionAsFlac; musopen-dvd-in-lossless-flac-format; PhiladelphiaSymphonyOrchestra-DanseMacabre; two 78 rpm Danse macabre sides; Navy Band Warhorses; Seattle Youth Symphony video item; Netfocus Carnival item; Dukas upload (no licence).
Other: Musopen blog and FAQ; Wikipedia (Musopen, Carnival, Danse macabre, Open Audio License, Navy Band); c.enwp.org Carnival category; OpenGameArt (Planets, Interface sounds, CC0 library, pop sounds, baby animals); BigSoundBank (licence, categories, TOON, TOY, SWSH, FOOD, FEET, MUSC, WATR, WING, searches); Sonniss licence and Rekkerd; Pixabay licence; Mixkit; Free Music Archive (Vivaldi, MacLeod); Marine Band Showcase page; Library of Congress Jukebox item; YouTube Help; yttalk; TunePocket (2 pages).
NOT readable: Wikimedia Commons file and category pages, Wikipedia File pages, Musopen recording lists (JavaScript), freesound.org, archive.org folder listings, DAHR, archive.org/details/Holst-ThePlanets.
