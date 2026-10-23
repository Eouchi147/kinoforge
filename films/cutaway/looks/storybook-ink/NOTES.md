# storybook-ink (Cutaway look board)

Look: a children's picture book: ink outlines of varied weight, watercolor washes that pool at the lines and slide off them, warm paper showing through, light pencil hatching in the shadows, slightly desaturated warm colour. Sky is a wet-in-wet wash, grass is a smooth green band, glass water a teal wash.

Art module: films/styles/cutaway/art/storybook-ink.py with the shared helpers in films/styles/cutaway/art/_npr_lines.py (numpy only, no scipy).
How it renders: Cycles renders the passes (colour, albedo, normal, world position, depth, material and object index) of the
real scene, numpy turns them into the picture, then a one-sample pass draws the labels and title over it (crisp, set in code).

Log (23 Oct 2026, builder): built and tuned on local pass dumps of frames 440 and 880 (hero) at 1280x720, 8 to 10 spp
on the 2-core chat box (about 110 to 250 s a frame there, mostly Cycles; the look's own numpy is 3 to 10 s). Runner stills and
final seconds per frame: see the section below once the runs are in.

Board frames: 440 (crane on the cut face) and 830 (hero; frame 768 of the brief is the dinosaur macro, the hero shot starts at frame 790).

Weak spots: hatching and paper are locked to the world or screen, so on a moving camera the chalk grain and paper texture stay
put on the screen (that is how paper behaves) but any screen-space noise can shimmer between frames; fine lines near the
size of a pixel can alias on far objects (they fade out below a minimum spacing); the grass and tree interiors are
simplified on purpose.

Project ideas where this look is the right choice:
1. A children's book publisher or a parenting brand explaining nature or the body to kids (how a seed grows, what lives under a garden).
2. A museum or science centre family trail: 'what is under our feet' panels and short films.
3. A school or library reading-week film where the story is told over a soft, hand-made picture.

Measured (23 Oct 2026):
- Runner (rc-render stills.yml, 640x360, 8 spp, frames 440 and 830 in parallel jobs): storybook-ink r2 (tag looks-storybook-ink-r2) both
  jobs done in about 87 s including about 60 s of setup, so about 25 s a frame. Before volumes were left out of the capture
  (haze and light-shaft objects are hidden during the capture render) frame 440 took 19 minutes on the runner, frame 830 about 80 s.
- Local 2-core chat box, 1280x720, 8 spp: Cycles capture about 50 s (hero) to 110 s (frame 440); the look's numpy 2 to 7 s; the label
  pass about 1 s. Runner stills run for storybook-ink only (r1 = tags looks-storybook-ink-r1, run 40025708724; r2 = run 40028913182);
  the other three were checked locally and on the seasons loop (KF_ART=<name>, 360x640) because the coordinator asked to skip waiting.
- Same Cycles scene and samples as the reference, minus the volumes; the full-size time is the Mac lane's (about 15 s a frame).
- Works on the line engine (meadow) and, through _adapter.py, on the seasons loop (the material names of both are classified).
- The frame to judge the hero is 830 (frame 768 is the dinosaur macro).
