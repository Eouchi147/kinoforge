# V3 The Call: hear the product work (target 20 to 23 s)

Read `ads/UNMISSED_DIRECTION.md` first.

**Idea.** No narrator. You hear a real-sounding late-night call between a customer and the AI front desk of an invented
restaurant, and you read it as huge kinetic captions, word by word, exactly on time (`audio/dialogue.json` has every word's
start and end). It proves the product instead of describing it. Then the music opens up and three supers land on the beat.

**Look.** Night palette, mostly typographic. Captions: Instrument Sans 650, 110 to 140 px, two lines at most, centred
slightly above middle; the word being spoken is full white, already-spoken words ink2, upcoming words not yet shown.
AI words in #79b4ff tint, caller words in white. Each word pops in at its start time (scale 1.08 to 1 over 4 frames, slight
upward drift). Speaker indicator above the captions: the AI is a glowing ring orb (the logo ring, pulsing with the voice
level), the caller a simple soft white circle with initials "JM"; the active one is lit, the other dims.
Top-left chip during the call: "Saffron Hearth Kitchen" and "AI front desk" with a live timer "0:07".
Bottom-left small mono: "Demo with an invented business".

**Structure.**
1. 0 to about 1.6 s: black, a phone rings twice (sfx ring on two beats); "21:47" mono and a ringing icon pulse.
   The ring is "answered" (click) and the call UI fades up.
2. The dialogue, lines placed back to back with natural gaps (about 0.25 to 0.4 s; the caller's reply may overlap a hair).
   On "Done." a booking card slams in under the captions: calendar tick, "Saturday 12:00, catering for 40, booked".
3. When the call ends (a soft hang-up click), the music opens up (place the music so its opening-up lands right here:
   use `music_offset` to shift the score). Three supers, one per beat, full-frame, huge:
   "Answered at 9:47 PM." / "Booked on the call." / "In your business's name."
4. End card on a downbeat (ring draws, node pops with impact, "Unmissed", tagline, AI line). No voice on the end card.

**Sound.** Dialogue on top, music very low under the call (-14 dB) then up to about -5 dB when it opens (use a gain
automation: place two music segments or fade; simplest: duck_ratio 6 so the call keeps it down). sfx ring, click, check on the
booking card, impact on the logo.
