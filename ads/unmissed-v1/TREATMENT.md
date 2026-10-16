# V1 Manifesto: kinetic typography, music-led (target 14 to 16 s)

Read `ads/UNMISSED_DIRECTION.md` first.

**Idea.** The problem in four cold lines, then the drop, then the answer fired one word per beat. The music does the
talking; the voice only signs off. Think Nike or Apple kinetic-type spots: huge condensed type, hard cuts, colour slams.

**Look.** Night palette. Instrument Sans 700 at width 75% (condensed) for the slams, 300 to 420 px, tracking -0.04 em.
Small labels in JetBrains Mono. Accent colour fields (#2f7df6 full frame) and one or two white flash frames on the drop.

**Structure (beats from `audio/music.json`; find the drop = `biggest_rise_s`, snap to the nearest beat).**
Before the drop (tense, sparse, the type small-to-medium and cold, lots of black):
1. "9:47 PM" in mono, a ticking second hand or blinking colon; a tiny phone glyph vibrating.
2. "The phone rings." Concentric ring pulses expand behind the words on each beat.
3. "Nobody picks up." The words drop out of focus and slide down; a red missed-call dot.
4. "They call the next place." Words whip off-frame to the right; a riser into the drop.
The drop (beat 0 of the loud section): one white flash frame, then "Not anymore." huge, #2f7df6 on black, scale punch, camera shake 3 frames.
After the drop, one word per beat, each with its own composition (alternate black / blue / white fields, change size and position):
5. "Answered." 6. "Booked." 7. "Texted back." 8. "Followed up." 9. "Review asked."
Each word carries a tiny proof glyph drawn in code (call handset with a tick, calendar tick, speech bubble, arrow, star outline).
10. "Day and night." (sun/moon swap), 11. "In your name." (2 beats each).
End card on a downbeat: the ring draws in one beat, the node pops on the next with an impact; "Unmissed" slams; tagline types in.
Voice (cast in prep): line 0 "Unmissed." on the logo slam; line 1 the tagline right after.

**Sound.** sfx: tick on the clock, ring on line 2, impact on the drop and on the logo, whoosh on the whip. Music gain about -4 dB,
gentle ducking under the two voice lines only (duck_ratio 2).
