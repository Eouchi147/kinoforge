# V4 Night Shift: cinematic, real-looking footage (target 20 to 22 s)

Read `ads/UNMISSED_DIRECTION.md` first.

**Idea.** A short film. An invented neighbourhood restaurant after closing: empty, rain on the windows, a phone lights up on
the counter. "You closed at nine. Your customers didn't." The AI front desk answers in the restaurant's name and books the
job. Morning light. Intimate, slow, premium; the opposite of the Manifesto.

**Footage** (AI, photoreal, no people; 4 s clips at 1080p in `media/`, stills as backup):
`ns-1-move` empty room, rain window, slow push-in. `ns-2-move` phone on the counter lighting up. `ns-3-move` rain drops and
city bokeh. `ns-4-move` dawn, sunbeams and dust. Still `ns-5.jpg` the kitchen pass (use a slow code push-in).

**Look.** 2.39:1 letterbox bars (the film frame), a teal-amber grade (CSS filters on the video layer are fine), grain in post.
Type: small and elegant, never shouting: Instrument Sans 500, 44 to 64 px, tracking -0.01 em, lower-left or centred in the
lower third, white at 92%. UI overlays drawn in code as dark glass cards (blur, 1 px #79b4ff edge), anchored in the shot
with a slight parallax: "21:47" and "Incoming call" near the phone; then "Answered by your AI front desk"; then on the kitchen
shot "Booked: catering for 40, Saturday 12:00".

**Structure (cut on the slow beats of `audio/music.json`, voice lines from `audio/vo.json`).**
1. ns-1 push-in (about 4 s). VO "You closed at nine."
2. ns-3 rain (about 2.5 s). VO "Your customers didn't."
3. ns-2 phone lights up (4 s). VO "At nine forty-seven, someone called." UI card "Incoming call, 21:47" appears with the glow.
4. Hold on the phone as the card flips to "Answered by your AI front desk"; cut to ns-5 kitchen pass (about 3 s) with
   "Booked: catering for 40, Saturday 12:00". VO "Your AI front desk answered. In your name. And booked them in." spans both.
5. ns-4 dawn (4 s) as the music swells. No words, just light.
6. End card fades up from the dawn shot into the night palette: logo draws, VO "Unmissed." then the tagline.

**Sound.** Music -8 dB, duck_ratio 3. sfx: a soft phone buzz could be the ring kind at low level on the phone shot, a chime
when the card flips to answered, impact (soft) under the logo.
