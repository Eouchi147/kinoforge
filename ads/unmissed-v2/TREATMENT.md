# V2 The Catch: 3D glass ring in dark space (target 17 to 19 s)

Read `ads/UNMISSED_DIRECTION.md` first.

**Idea.** The site's hero, "the catch", as a film. Notifications (calls, messages, leads) stream through deep space toward
camera. Some slip past into the dark: the gaps. Then the glass ring forms and catches every one; they orbit it and are
absorbed; the ring becomes the logo. Apple-keynote calm, luxurious, cinematic depth.

**Build.** Three.js (`/harness/node_modules/three/build/three.module.js` via an import map, addons under
`/harness/node_modules/three/examples/jsm/`). Renderer with `preserveDrawingBuffer: true`, exponential fog in #05070f,
ACES tone mapping, UnrealBloomPass (strength about 0.8). Deterministic: everything from `t`, seeded randomness.
Cards: rounded-rectangle planes with canvas textures (dark glass card #0b1122 at 90% opacity, 1 px #79b4ff edge, icon, title
and one line: "Incoming call, 21:47", "New message: table for 6 tonight?", "New lead: catering for 40", "Missed call, 18:32",
"New enquiry from your website"). The ring: a torus (radius about 3, tube 0.12) with MeshPhysicalMaterial (transmission or a
fresnel glow shader), rim-lit in #2f7df6 to #79b4ff, a small emissive sphere node at one o'clock. Keep the WebGL scene light
enough for SwiftShader (low poly counts, one bloom pass); final text is HTML over the canvas (crisp).

**Structure (time to `audio/music.json` beats and `audio/vo.json` durations).**
1. Black, then cards begin streaming from far z, slow at first. VO "Calls." / "Messages." / "Leads." each on a beat, and
   the matching card type surges forward on its word. Camera drifts and slightly orbits.
2. "Some slip through the gaps." Several cards veer off past the camera edges and fade into darkness. Big thin type
   overlays briefly: "the gaps." (lowercase, ink3) then gone.
3. On the music's rise: the glass ring materialises (the hair-thin circle draws, then the glass body and glow bloom in),
   VO "Unmissed answers every one, day and night." Every card now bends its path into the ring, orbits once, flashes and is
   absorbed. Camera pushes through to frame the ring head-on.
4. The ring flattens and scales into the 2D logo position; HTML end card: "Unmissed", the tagline as VO reads it, the AI line.

**Sound.** sfx: soft whoosh as cards pass camera, chime when the ring forms, small pops when cards are absorbed (quiet),
impact under the logo. Music gain about -7 dB, duck_ratio 3.
