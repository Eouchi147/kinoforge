# KINOFORGE research brief (23 Oct 2026)

Two tasks: (1) legally usable classical recordings for a 60-120 s film, (2) market figures for a cutaway-diorama animation style.

## How this was checked (read first)

- The session proxy blocks (HTTP 403 on CONNECT) commons.wikimedia.org, upload.wikimedia.org, archive.org, musopen.org, marineband.marines.mil, en.wikipedia.org, api.openverse.org when called with curl. No HEAD or download test was possible on any audio file. Nothing below is "download verified".
- Pages were read as text through the WebFetch tool (works only for URLs that came up in search results). Several pages (Commons file pages, Musopen, Columbia library, Wikipedia via redirect) could not be fetched; I used Commons mirrors (c.enwp.org, download.osmand.net), IMSLP (which lists licence lines per recording), Project Gutenberg, and Marine Band pages instead.
- Direct file URLs were NOT confirmed except where the page itself printed a path (Gutenberg). Where I give a pattern it is labelled "unverified pattern".
- Legal items flagged for a lawyer are marked LAWYER.

---

# PART 1. Recordings

## 1.0 Rules I applied, with evidence

- IMSLP rows labelled "Public Domain - Non-PD US" are NOT usable: they are 1950s-60s recordings that are public domain only in some countries (EU style), still protected in the US. Example: Dukas / Peer Gynt / Borodin Otterloo, Solti, Munch, Ansermet, Bernstein 1960 entries. Source: https://imslp.org/wiki/L%27apprenti_sorcier_(Dukas%2C_Paul) , https://imslp.org/wiki/The_Nutcracker,_suite,_Op.71a_(Tchaikovsky,_Pyotr_Ilyich) (confidence high that the label says this; high that they are unsuitable for a worldwide monetised film).
- NC / ND / SA licences excluded: DuPage Symphony (CC BY-NC-ND 3.0 or NC-SA) on Nutcracker, Steppes, Prince Igor; Skidmore Night on Bald Mountain (CC BY-SA 3.0, ShareAlike would pull the film into SA); Rami Bar-Niv Clair de Lune (NC-ND). Sources: IMSLP pages above and https://imslp.org/wiki/Night_on_Bald_Mountain_(Mussorgsky,_Modest) , https://imslp.org/wiki/Suite_bergamasque_(Debussy%2C_Claude).
- US recordings of 1925 entered the US public domain on 1 Jan 2026 (the Music Modernization Act schedule); 1927 recordings do not until 1 Jan 2028 (my arithmetic from the 1925 fact; the sources only state the 1925 fact). Sources: https://blog.archive.org/public-domain-day-2026/ , https://lib.cua.edu/wordpress/newsevents/27531/ (confidence high for 1925, medium for the 1927 inference).
- Composer status: Tchaikovsky, Rimsky-Korsakov, Borodin, Grieg, Saint-Saens, Debussy, Dukas, Glazunov, Satie are long out of copyright (assumption from death dates, general knowledge, not source-checked here). Ketelbey (d. 1959) is NOT clean worldwide: life+50 in Canada gave PD in 2010, but life+70 in UK/EU runs to end of 2029 (my reasoning, no source fetched; LAWYER). I did not research Ketelbey recordings.
- LAWYER: (a) "public domain worldwide" for US-government band recordings: 17 USC 105 puts them in the public domain in the US; foreign treatment is not something I confirmed. (b) Canadian and EU term for 1920s sound recordings (I expect expired, not confirmed with a source). (c) Whether a CC BY credit line in the film description is enough for your platforms.

## 1.1 Ranked shortlist (best first)

Ranking = sound quality, exotic/magical feel, clear structure for picture. Durations are from the source pages.

### 1. Borodin, In the Steppes of Central Asia. Czech National Symphony Orchestra (Musopen Kickstarter, recorded 2012). BEST FIT
- Source page (IMSLP, shows licence and length): https://imslp.org/wiki/In_the_Steppes_of_Central_Asia_(Borodin%2C_Aleksandr)
- File: PMLP03599-AlexanderBorodin-InTheSteppesOfCentralAsia.mp3, 10.19 MB, 7:38. Publisher line "Palo Alto: Musopen, 2012." Uploaded to IMSLP 2021/9/7, 1,034 downloads.
- Licence line on IMSLP: "Creative Commons Zero 1.0". Confidence: medium-high (IMSLP uploader label; I could not see the Musopen page).
- Lossless: Wikimedia Commons Category:Musopen lists "Borodin - In the Steppes of Central Asia (Musopen Symphony).flac" and "Alexander Borodin - In The Steppes Of Central Asia.ogg": https://download.osmand.net/wiki/Category:Musopen (mirror of Commons; confidence medium; I did not read the file description or licence template for these two). Direct URL: not confirmed. Unverified pattern: https://commons.wikimedia.org/wiki/Special:FilePath/Borodin_-_In_the_Steppes_of_Central_Asia_(Musopen_Symphony).flac
- Era/quality: modern digital orchestral, expected stereo. Quality not listened to.
- Fit: exotic (Central Asian caravan, Russian and "Eastern" themes), a built-in story (caravan approaches, passes, fades), very quiet ending. 7:38 is too long; plan a 100-120 s cut or edit/loop. Cutting is simple because the piece is a slow arch.
- Conflict to resolve: Wikipedia says the Musopen 2012 recordings were made by the Czech Philharmonic (https://en.wikipedia.org/wiki/Musopen); IMSLP says Czech National Symphony Orchestra. Credit "Musopen" and verify the orchestra name on the Musopen page before the credits.

### 2. Grieg, Peer Gynt Suite No. 1 (Morning Mood 3:53, Death of Ase 4:38, Anitra's Dance 4:04, In the Hall of the Mountain King 2:38). Czech National Symphony Orchestra / Musopen, 2012
- Source page: https://imslp.org/wiki/Peer_Gynt_Suite_No.1%2C_Op.46_(Grieg%2C_Edvard)
- Licence line on IMSLP: "Creative Commons Attribution 3.0" (so credit is required). "Lossless files are also available" per the page. Uploaded 2012/8/17. Confidence: medium (IMSLP says CC BY 3.0 here but CC0 for the Steppes from the same project; the two labels disagree, so check the Musopen page; either is acceptable, treat as CC BY and credit).
- Fit: Anitra's Dance (4:04, Arabian flavour, strings and triangle) and Morning Mood (sunrise arc) suit a poetic picture; Mountain King (2:38) builds from whisper to chaos and is the easiest to sync, but is 2:38 and too frantic for a gentle storybook mood. Excerpt to 90-120 s possible for Anitra's Dance and Mountain King.
- Same project also recorded (Commons Category:Musopen, Seattle Star article list): Mendelssohn Hebrides, Smetana Vltava, Rimsky-Korsakov Russian Easter Overture. Source for the list: https://www.seattlestar.net/2012/08/musopen-sets-music-free/ (confidence medium; says "internationally renowned orchestra", unnamed).

### 3. Saint-Saens, Orient et Occident, Op. 25 (grand march for band). US Marine Band, cond. John Bourgeois, 1990
- Source page: https://imslp.org/wiki/Orient_et_occident,_Op.25_(Saint-Saëns,_Camille)
- File PMLP59071-orient et occident.mp3, 10.65 MB, 11:38. Publisher: "Marine Band Showcase: Volume 2, Washington, DC: United States Marine Band, 1990". IMSLP licence line: "Public Domain". Uploaded 2010/8/26.
- Marine Band source: Showcase Volume Two track list (Saint-Saens Orient et Occident, Opus 25 is track 3), page says "This recording is no longer available" so the original Marine Band download may be gone: https://www.marineband.marines.mil/Audio-Resources/Educational-Series/Marine-Band-Showcase-Volume-Two/ . The page has no rights statement. Confidence on PD: medium. Basis is that it is a US Marine Band work (see Commons licence text for another Marine Band file below). LAWYER for outside the US.
- Fit: title and music contrast Orient and Occident, march structure is clear, but band sound, 11:38 long, a march pulse is not "storybook". Rank 3 because the exotic idea is explicit.
- Evidence that Marine Band recordings are treated as public domain on Commons: "As a work of the U.S. federal government, it is in the public domain." (Sousa High School Cadets file) https://c.enwp.org/wiki/File:Sousa_The_High_School_Cadets_United_States_Marine_Band.ogg . That file: Ogg Vorbis 430 kbps, 7.9 MB, 2:34. Direct URL not shown.
- The Marine Band pages for Overtures, Bicentennial Disc 5 and Live in Concert list orchestral and band works (Berlioz, Verdi, Milhaud, Vaughan Williams etc.) but none of the exotic list you named (no Nutcracker, Scheherazade, Peer Gynt, Danse Macabre found). Source: https://www.marineband.marines.mil/Audio-Resources/Educational-Series/Overtures/ , .../The-Bicentennial-Collection-Disc-5/ , .../Marine-Band-Albums/Live-in-Concert/ . These pages carry no copyright statement; a PDF titled "Sousa Marches Public Domain letter" exists on the Marine Band site but could not be fetched. The Marine Band audio page says recordings are "not for sale" and for educational/public-affairs use (https://www.marineband.marines.mil/Audio-Resources/Patriotic-Favorites): not a licence restriction I can confirm, but note it. LAWYER if you use the band route for a commercial film.
- Also note: band transcriptions can carry a living arranger's copyright (e.g. Gordon Jacob, Schuller transcriptions on Live in Concert). Orient et Occident was written for band by Saint-Saens (my knowledge; not source-checked).
- I found no US Navy Band, Air Force Band or Army Band classical-exotic recording with a checked licence. The Army Band 1812 Overture on Commons (16:29) is a verified US-soldier work: https://download.osmand.net/wiki/File:1812_Overture.ogg (not exotic).

### 4. Tchaikovsky, Nutcracker: Waltz of the Flowers (Valse des fleurs). Israel J. Hochman / Emerson International Symphony Orchestra, Emerson Phonograph Co., 1919
- Source page: https://imslp.org/wiki/The_Nutcracker,_suite,_Op.71a_(Tchaikovsky,_Pyotr_Ilyich)
- File PMLP3607-ValseFleur-Emer.flac, uploaded 2024/7/29, licence line "Public Domain" (no "Non-PD US" qualifier). Duration not printed on the page. Recorded around Oct 1919.
- Why usable: a 1919 US recording is pre-1923, so public domain in the US (Music Modernization Act; see 1.0) and old enough for EU/Canada (my inference; LAWYER).
- Quality: acoustic-horn era, mono, heavy surface noise, narrow band. Fit: the best-known "magical" piece I could clear, but a 1919 78 rpm sound may not match a polished storybook look. Treat as a texture choice.
- There is no clean modern Nutcracker. Modern Nutcracker recordings on IMSLP: DuPage (CC BY-NC-ND), piano by Kolodin (CC BY-SA 4.0, ShareAlike), Hernandez (NC), Eastern Wind Symphony wind band (CC BY-SA 4.0). None meet your rule.

### 5. Rimsky-Korsakov, Scheherazade extracts Pt. 1. American Concert Orchestra, recorded 28 April 1925 (Project Gutenberg Sound)
- Source page: https://gutenberg.org/ebooks/10179 . Rights line: "Public domain in the USA." File: /files/10179/10179-m/10179-m-001.mp3, 3.3 MB (duration not printed; at a typical 128 kbps that would be roughly 3.5 min, my estimate). Direct file URL printed on the page: https://www.gutenberg.org/files/10179/10179-m/10179-m-001.mp3 (path from the page; not fetched).
- Rights caution: US public domain only from 1 Jan 2026 and only if first published in 1925 (the page gives a recording date, not a publication date). If it was first released in 1926, it is protected in the US until 2027. Confidence: medium-low. Check the Gutenberg readme (https://www.gutenberg.org/files/10181/10181-m/10181-m-readme.txt is the pattern for 10181; use 10179) before use. LAWYER.
- Quality: 1925 electrical recording, mono, noisy, compressed MP3 (probably transferred from 78). Fit: exactly the exotic-fairytale subject, arguably the best theme for storybook animation; sound is the weakness. 
- Not usable: Gutenberg Clair de Lune, Hotel Commodore Ensemble, recorded 21 July 1927 (https://www.gutenberg.org/ebooks/10181 says "Public domain in the USA"): a 1927 recording is not in the US public domain until 2028 by the schedule above, so I would NOT trust that label. Confidence: medium.

### 6. Satie, Gymnopedie No. 1. Daria Baiocchi, piano, 2021
- Source page: https://imslp.org/wiki/3_Gymnop%C3%A9dies_(Satie%2C_Erik)
- Licence line: "Creative Commons Zero 1.0". File PMLP4215-Satie Gymnope-die n.1 DariaBaiocchi.mp3, 3:11, uploaded 2021/8/16. Digital modern piano. Confidence: medium-high.
- Fit: hypnotic, dreamy, simple repeating structure with two alternating sections (easy to hold a slow single scene; hard to sync hit-points). Not exotic by itself. Good for a quiet 90-120 s excerpt.

### 7. Saint-Saens, The Swan (Le cygne). Matilda Colliard, cello; Stefano Ligoratti, piano (live)
- Source page: https://imslp.org/wiki/Le_carnaval_des_animaux_(Saint-Sa%C3%ABns%2C_Camille)
- File PMLP06099-Le_Cygne.mp3, 2:38, publisher Milan: Classica Viva, uploaded 2015/7/14. Licence line: "Creative Commons Attribution 4.0". Credit required. Confidence: medium-high.
- Fit: poetic, one long arc, well sized for a 2:38 film; live recording, not exotic.
- Not usable from the same page: Philharmonia/Dervaux (marked Non-PD US), Seattle Youth Symphony Carnival of the Animals (licence line "EFF Open Audio License", 22:52, amateur youth ensemble; I did not verify that licence allows commercial use or whether it needs credit; skip unless checked).

### 8. Glazunov, Chant du menestrel, Op. 71 (Musopen)
- Source: https://c.enwp.org/wiki/File:Alexander_Glazunov_-_chant_du_menestrel,_op._71.ogg (Commons mirror). Licence text: "released into the public domain by its author, Musopen. This applies worldwide." Duration 3:52, Ogg Vorbis 145 kbps, 4 MB. Performer not stated; Musopen requests in-line attribution. Direct URL not shown. Confidence: medium (it also matches Musopen's attribution request: credit Musopen).
- Fit: lyrical, medieval/orientalist feel; weaker structure for sync.

### 9. Other Musopen items on Commons (not read in detail)
- Saint-Saens, Introduction et Rondo capriccioso; Bizet, Carmen Prelude; Grieg Piano Concerto movements (Adagio read: 6:21, "released into the public domain by its author, Musopen", https://c.enwp.org/wiki/File:Edvard_Grieg_-_piano_concerto_in_a_minor,_op._16_-_ii._adagio.ogg ). Full list of 476 files was only partly readable (200 shown): https://download.osmand.net/wiki/Category:Musopen . No Scheherazade, Nutcracker, Sorcerer's Apprentice, Danse Macabre, Clair de Lune in the part I could read; the remaining 276 files and the "Musopen Kickstarter Project" (144 files) and "Set Chopin Free" (155 files) subcategories were not listed.

## 1.2 Not found as clean (so you do not waste time)
- Scheherazade, Flight of the Bumblebee, Danse Macabre, Sorcerer's Apprentice, Carnival Aquarium, Arabian Dance, Polovtsian Dances, Ravel: I found NO modern recording with a clean licence in the sources reachable. The IMSLP lists for Dukas, Prince Igor and Danse Macabre carry only Non-PD US, NC or SA entries. (Danse Macabre IMSLP page did not come up in search.)
- Debussy Clair de Lune: only piano CC BY/CC BY-NC-ND/NC items; the ones that qualify (CC BY 4.0) are Paul De Bra accordions, clarinet and sax-quartet versions on https://imslp.org/wiki/Suite_bergamasque_(Debussy%2C_Claude) . Not a classic piano sound.

## 1.3 Recommendation
- Primary: Borodin In the Steppes (Czech NSO/Musopen, CC0 label) cut to 100-120 s, lossless from Commons if the file page confirms the licence. Secondary: Peer Gynt "Anitra's Dance" or "Morning Mood" (CC BY 3.0, credit Musopen). Tertiary, for texture: 1919 Valse des fleurs or 1925 Scheherazade extract, only after a lawyer check.
- Before production: open each Commons/Musopen page in a browser and copy the licence text into the film's docs; run HEAD/GET on the final file URL from a machine with network access (my sandbox could not).
- For KINOFORGE docs: record the exact licence text, source URL and retrieval date per file, add a credits line ("Music: <piece>, <orchestra>, via Musopen, CC BY 3.0").

---

# PART 2. Market figures for a cutaway-diorama style

Confidence legend: high = official or primary; medium = published dataset with method; low = vendor blog, unsourced, or AI-summary.

## 2.1 YouTube CPM / RPM

Definitions: CPM = what advertisers pay per 1,000 ad impressions; RPM = creator revenue per 1,000 views, after YouTube's cut.

| Niche | Figure | Source | Confidence |
|---|---|---|---|
| Education and Science (one combined bucket, includes history-type explainers) | Median RPM $10.22 (P25 to P75: $2.31 to $19.50); median Studio CPM $5.91; monetised playback 77% | AIR Media-Tech, 300 channels, 3,595 channel-months, May 2025 to May 2026: https://air.io/en/air-data-findings/which-youtube-niche-makes-the-most-money-in-2026-ranked-by-real-rpm-and-cpm and https://air.io/en/air-data-findings/how-much-does-youtube-really-pay-in-2026-real-rpm-data-from-300-channels | medium (AIR's client base, medians; huge spread) |
| Kids and Teens | Median RPM $0.33 (P25 to P75: $0.16 to $0.88); median Studio CPM $1.59; monetised playback only 32% | same AIR pages | medium |
| Music (nearest proxy for relaxing/ambient) | Median RPM $2.28; Studio CPM $4.05 | same AIR page (45 channels) | medium; no ambient-specific figure found |
| Entertainment | Median RPM $2.43 | same | medium |
| All niches | Median RPM $2.30 | same | medium |
| Education / how-to | CPM $6 to $15 | vidIQ, 17 Apr 2026: https://vidiq.com/blog/post/how-much-does-youtube-pay-per-view/ (no data source named) | low-medium |
| Kids / family / music | CPM $1 to $4 | same vidIQ | low-medium |
| Made for Kids videos | CPM $1 to $7; educational and toy content $4 to $7; generic animation/nursery $1 to $3 | vidIQ, updated 24 Apr 2026: https://vidiq.com/blog/post/make-money-kids-youtube-channel/ | low |
| Made for Kids revenue effect | No official percentage; industry estimates of 50% to 90%+ lower than comparable general content are unconfirmed | https://www.makeinfluence.com/en/academy/youtubes-made-for-kids-coppa-classification-what-it-does-to-ad-revenue | low |
| Shorts | RPM about $0.03 to $0.10 per 1,000 views (its own summary line says $0.01 to $0.06, internal conflict); creators keep 45% | vidIQ, updated 28 May 2026: https://vidiq.com/blog/post/youtube-shorts-monetization/ | low-medium |
| Shorts | $0.01 to $0.07 per 1,000 views | vidIQ 17 Apr 2026 (page above) | low-medium |
| Shorts | "consistently under $0.20" vs $3 to $6+ for long-form in same niches (Digiday interviews) | https://influencermarketinghub.com/youtube-shorts-rpm/ (updated 30 Oct 2025) | low-medium |
| History | NO sourced niche figure found. Only a planning model: Shorts 10 to 25 cents RPM, "YouTube does not publish a history or military RPM table" | https://saturaai.com/history-military-youtube-shorts-rpm | low |
| Relaxing/ambient/sleep | NO RPM found. OutlierKit says music "playback RPM is among YouTube's lowest"; estimated monthly channel revenue Lofi Girl $3K to $17K, Soothing Relaxation $4K to $23K, Sleepless Historian $2K to $9K (estimates, not actuals) | https://alpha.outlierkit.com/resources/youtube-music-channel-growth-strategy/ (updated 27 Sep 2026) | low |

Made for Kids limits (official). Not available on Made for Kids watch pages: targeted ads, comments, channel memberships, Super Chat and Super Stickers, merchandise and ticket sales, donation buttons, end screens and cards, notifications, save to playlist. "Ads still may appear" (contextual only). Source: https://support.google.com/youtube/answer/9632097?hl=en-GB . Confidence high. Other pages disagree with each other on which features are unaffected (vidIQ says merch off-platform is unaffected; that is about off-platform merch, not consistent with YouTube's own merch shelf rule), so rely on the YouTube page.

Takeaway (my reading, not a source): science/education is the only niche with RPM in the double digits at the median, but the spread is 8x between the bottom and top quartile; Kids is about 30x lower than Education & Science at the median.

## 2.2 What businesses pay (all vendor blogs: expect upward bias)

| Item | Price | Source | Confidence |
|---|---|---|---|
| 2D animated explainer, freelancer or small studio | $3,000 to $8,000 per finished minute | Pixune (studio), updated 17 Jun 2026: https://pixune.com/blog/animated-explainer-video-cost/ | low |
| 2D, established studio | $5,000 to $15,000 per minute | same | low |
| 3D animation, established studio | $15,000 to $30,000+ per minute | same | low |
| Template or AI platforms | about $50 to $500 per video | same | low |
| 2D animation | $5,000 to $20,000 per minute; 3D $8,000 to $25,000+ per minute; explainer $3,000 to $25,000 per video | DesignRush, updated 13 Apr 2026: https://www.designrush.com/agency/video-production/trends/cost-of-video-production | low-medium |
| Per-minute by tier (freelancer / mid studio / agency) | $1,000 to $5,000 / $5,000 to $15,000 / $15,000 to $50,000+ (Vidico, May 2026); overall $5,000 to $50,000+ per finished minute, mid-tier about $10,000 (b2w.tv, Aug 2026) | quoted in https://framesixty.com/how-much-does-3d-animation-cost/ (10 Sep 2026) | low |
| 3D product animation | $5,000 to $50,000+; budget $5,000 to $7,000, mid $7,000 to $15,000, premium (incl. exploded views) $15,000 to $50,000+ | Vidico, 26 Jun 2026: https://vidico.com/news/product-video-cost/ | low |
| Technical animation with exploded views (closest to "cutaway") | $20,000 to $50,000+; product feature animation $10,000 to $25,000; 30 s exploded view animation $20,000 to $50,000+ | Just Animations, May 2026, as quoted at https://framesixty.com/how-much-does-3d-animation-cost/ | low |
| Architectural stills | residential interior $250 to $2,000; exterior $400 to $2,800; commercial exterior $800 to $10,000+; floor plan $250 to $1,500 | MyArchitectAI, updated 19 Aug 2026: https://myarchitectai.com/blog/3d-architectural-rendering-cost | low |
| Architectural animation | $4,000 to $12,000 per minute | same | low |
| Animated product demo (SaaS) | $1,500 to $15,000; most B2B SaaS spends $2,500 to $5,000 for 2 to 3 min | Vidico (page above) | low |

Not found: a price for "cutaway/section" rendering specifically. The nearest are the "exploded view" and "section" lines above (my reading). Medical animation (Pixozone, Oct 2025, as quoted by Framesixty): short social clips $800 to $2,000; 2 to 4 min pharma explainers $2,000 to $8,000 (low).

Gap: these prices come from sellers; I found no buyer-side survey. AI-assisted production (your model) would sit under the "template/AI" row on price, not the studio row; do not quote studio prices as your achievable price without a client test.

## 2.3 Licensing and other income

Stock footage
- Shutterstock video royalty: 15% to 40% across six levels; level 1 = up to 10 licenses a year (article dated May 2020, rates effective June 2020; may have changed): https://www.mystockphoto.org/shutterstock-updates-royalty-rates/ (low-medium, old).
- Pond5 50% standard, 60% exclusive; Shutterstock 15% to 40% (20% to 45% exclusive); example: a 4K wildlife clip priced $499 sold 8 times in 2025 for $3,992 sales and $1,996 royalty; generic subscription downloads about $0.31 on Shutterstock: https://www.earnifyhub.com/blog/pond5-vs-shutterstock-video-earnings (Feb 2026, no method: low).
- Average single-clip 4K commercial price on pay-per-clip platforms $79 (range $50 to $200); only 4.8% of contributors earn over $2,000/month: https://voxbooster.com/blog/stock-footage-statistics-2026 (Aug 2026, scope excludes animation, low).
- Per-clip returns have "crashed" at Pond5; Adobe's free-collection pay was $8 per selected clip: https://brutallyhonestmicrostock.com/2026/06/15/microstock-hamster-wheel-more-files-fewer-sales-lower-real-returns-data-analysis-from-2019-2026/ (one contributor's data, low).
- NOT found: any rate card specific to animated clips. Stock video marketplaces are a weak income line per these sources.

Educational licensing
- Boclips (licenses video to ed-tech): median buyer pays $33,400 a year; Library priced per video with bulk discounts (that is what buyers pay Boclips, not what creators get): https://www.vendr.com/marketplace/boclips (date not stated, low).
- LearningMole sells licences by single-platform, enterprise, API, territory-limited, annual and renewable, price on enquiry: https://learningmole.com/educational-video-licensing-learningmole-content/ (medium that this model exists; no price).
- Not found: per-video prices from schools or museums. Not found: museum commission rates. Gap.

Print on demand (art prints and posters)
- Printful average profit margin about 56%, up to 75% for framed art prints, lowest 32% (tote bags); you set the price; no royalty model. Society6 default artist margin 10% on paid plans: https://www.printful.com/blog/comparing-artist-profit-on-society6-vs-printful (7 Aug 2024, Printful is a seller: low-medium). Redbubble not covered.

Children's picture books (Amazon KDP)
- Ebook: 70% royalty for $2.99 to $12.99 list price (less $0.15/MB delivery cost) else 35%; paperback and hardcover: 60% at $9.99+ (50% below) minus printing; premium colour printing $1.00 + $0.065 per page, so 100 pages cost $7.50, minimum list $12.50, a $14.99 list yields $1.49 royalty. Source: https://cartmango.com/kdp-royalties/ (13 Sep 2026; third-party summary of KDP terms; medium). A 32-page colour picture book cost is not given in that source; by its formula it would be about $3.08 (my calculation, check KDP's calculator).

Memberships
- Patreon: new creators after 4 Aug 2025 pay a standard 10% platform fee, plus payment processing 2.9% + $0.30 per payment over $3 (US cards), payout fees extra: https://support.patreon.com/hc/en-us/articles/11111747095181-Creator-fees (official, high).

## 2.4 Businesses built on a recognisable illustrated style

1. Kurzgesagt (flat-vector science explainers, Munich)
- 25.6M subscribers; team about 70; €2.97M from Open Philanthropy (Mar 2022); US$570k Gates grant (2015); Jan 2023 statement: 65% of income from viewers (merch, Patreon, AdSense), 24% from sponsorships and grants. Source: https://en.wikipedia.org/wiki/Kurzgesagt (medium; Wikipedia relays company statements).
- Fuller 2015 to 2022 breakdown: shop 40%, YouTube ads 13%, commercial sponsors 12%, institutional sponsors 10%, Patreon 9%, paid agency work 9% (stopped 2022), German public broadcasting 7%; 60+ full-time staff in 2023: https://opentools.ai/youtube-summary/how-we-make-money-on-youtube-with-20m-subs and https://videohighlight.com/v/1x-i9z617z4 (both AI summaries of Kurzgesagt's video, consistent with each other, original video not checked: low-medium).
- Third-party revenue guess $5M to $10M a year, no sources: https://becomeviral.com/blog/kurzgesagt-case-study (low; do not quote).
- Read-across (my reading): ad revenue is the minor part (13%); the shop is the largest part (40%); client/agency work was a real earner (9%) until they dropped it.
2. DK "Stephen Biesty's Incredible Cross-Sections" (the print origin of the cross-section look): first published 1992, "more than a million copies sold", RRP £14.99: https://dk.com/uk/book/9780241379783-stephen-biestys-incredible-cross-sections (publisher statement: medium-high for the claim as a claim).
3. MinutePhysics and MinuteEarth (hand-drawn whiteboard explainers, Neptune Studios): MinutePhysics 5.94M subs (Jan 2026), MinuteEarth 3.24M; on Nebula; no revenue disclosed: https://en.wikipedia.org/wiki/MinutePhysics (medium).
4. OverSimplified (illustrated history): 9.6M subs; estimated $38K to $211K a month including sponsors, one upload in over a year as of 30 Jul 2026; the revenue is an OutlierKit estimate: https://outlierkit.com/channel/oversimplified (subs: medium; revenue: low).
5. TED-Ed Animation: 22.4M subs: https://air.io/en/trending/10-most-popular-animation-channels-on-youtube-in-2026 (medium).

## 2.5 Reading across (my judgement, not sourced)
- Highest-RPM niche is education/science, the lowest is kids; kids also loses ads personalisation, comments, memberships and merch. If the style goes to kids, do it as books and licensing, not YouTube ads.
- Paid client work looks stronger than ad revenue for a small studio: even Kurzgesagt got 9% from agency work; but all prices above come from sellers.
- No evidence found of any single "cutaway" price band; test with 2 to 3 real quotes.

## 2.6 Gaps and things to check
- No history-specific or ambient-specific RPM from a dataset.
- No buyer-side prices; no museum or school licence rates; no animated-clip stock rates.
- Kurzgesagt breakdown comes via AI transcript summaries; verify against the original video.
- Nothing here is legal, tax or accounting advice. Platform fees and MFK rules change; re-check before pricing.
