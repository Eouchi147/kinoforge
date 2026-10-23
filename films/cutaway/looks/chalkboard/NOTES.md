# chalkboard (Cutaway look board)

Look: chalk on a slate blackboard: dusty white outlines, soil layers rubbed in with yellow, pink and pale blue chalk (hatching smudged with a finger), each find in its own coloured stick, water in blue wavy lines, grainy broken strokes, old eraser swipes and dust, a slim wooden frame, label plates in Archivo.

Art module: films/styles/cutaway/art/chalkboard.py with the shared helpers in films/styles/cutaway/art/_npr_lines.py (numpy only, no scipy).
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
1. A teacher, a tutoring brand or an online course explaining geology, history of land or a science topic.
2. A museum education department: a gallery talk film or an activity sheet that feels like a lesson.
3. A farm, garden or soil-testing business: 'what is in your soil' explainers for customers.

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
