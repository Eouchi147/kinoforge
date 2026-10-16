# V5 Bento: bright product-launch grid (target 16 to 18 s)

Read `ads/UNMISSED_DIRECTION.md` first.

**Idea.** An Apple-style product film in the site's day theme. A bento grid of tiles, each showing one part of the service
working in a tiny live UI. The camera glides across a big grid, punching into each tile on its beat, then pulls back to reveal
the whole system, which collapses into the ring logo. Bright, optimistic, quick.

**Look.** Day palette. Tiles: white surfaces, radius 40 px, soft layered shadows (0 30px 60px -30px rgba(23,43,99,.25)),
one accent each (#2456c9 family). Tile labels in Instrument Sans 650, 44 to 72 px; micro UI inside at real legible sizes.
The grid lives on a large plane (about 3200 x 2000) and the "camera" is a CSS transform on it (translate + scale + slight
rotateX for depth). Background #f4f6fa with a very soft blue radial glow.

**Tiles** (each with its own micro animation that plays when the camera arrives):
1. Calls: an incoming call card, the answer button presses itself, timer starts, "Answered" tick.
2. Leads: three lead cards slide into a pipeline column, the top one moves to "Booked".
3. Reviews: a text bubble "Would you leave us a Google review?" sends, a "Sent" tick (no stars or ratings).
4. Website: a mini premium website for the invented restaurant (`/ads/unmissed-01/media/bread-oven.jpg` as hero), scrolling.
5. Google profile: a profile card with "Open until 11 pm" and Call / Directions / Menu buttons.
6. Run for you: a checklist ticking itself: "Built for you", "Run for you", "Paid monthly".
Label "Demo with an invented business" bottom-left, small.

**Structure (VO lines from `audio/vo.json`, cuts on `audio/music.json` beats).**
1. Build (first beats): tiles flip up into place across the grid one per half-beat, camera far out, then a fast glide in.
2. Camera punches into Calls on VO "Calls, answered." then whips (motion blur) to Leads on "Leads, followed up.", then
   Reviews on "Reviews, asked for.", then Website + Google profile together on "A website that looks the part."
3. On the music's stop: the camera pulls all the way back to the whole bento; VO "All built for you, and run for you." with
   tile 6 ticking.
4. Final hit: tiles collapse toward the centre (staggered, with motion blur) and the ring logo draws where they meet;
   VO "Unmissed. A premium presence. An AI front desk." End card on the day palette (ink text), small AI line.

**Sound.** Music -5 dB, duck_ratio 2.5 (keep it bright). sfx: pop on each tile flip (quiet), whoosh on camera whips,
check on ticks, impact on the logo.
