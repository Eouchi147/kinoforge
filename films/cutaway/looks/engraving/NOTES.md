# engraving (Cutaway look board)

Look: a 19th-century encyclopaedia plate: sepia line hatching where every tone is a set of parallel lines as wide as the tone asks, the lines follow the forms (the soil layers themselves through an AOV of the strata coordinate, ground relief, foliage clumps), cross-hatched deep shadows, cream paper with foxing and fibres, a thin double plate border. Labels become ink on paper plates.

Art module: films/styles/cutaway/art/engraving.py with the shared helpers in films/styles/cutaway/art/_npr_lines.py (numpy only, no scipy).
How it renders: Cycles renders the passes (colour, albedo, normal, world position, depth, material and object index) of the
real scene, numpy turns them into the picture, then a one-sample pass draws the labels and title over it (crisp, set in code).

Log (23 Oct 2026, Sonnet builder): built and tuned on local pass dumps of frames 440 and 880 (hero) at 1280x720, 8 to 10 spp
on the 2-core chat box (about 110 to 250 s a frame there, mostly Cycles; the look's own numpy is 3 to 10 s). Runner stills and
final seconds per frame: see the section below once the runs are in.

Board frames: 440 (crane on the cut face) and 830 (hero; frame 768 of the brief is the dinosaur macro, the hero shot starts at frame 790).

Weak spots: hatching and paper are locked to the world or screen, so on a moving camera the chalk grain and paper texture stay
put on the screen (that is how paper behaves) but any screen-space noise can shimmer between frames; fine lines near the
size of a pixel can alias on far objects (they fade out below a minimum spacing); the grass and tree interiors are
simplified on purpose.

Project ideas where this look is the right choice:
1. A history channel, a heritage trust or an archaeology dig film (Roman layers, medieval site).
2. A publisher of illustrated history or a rare-book and map dealer (an animated plate for a social launch).
3. A museum or a law/finance firm with old roots that wants a serious, timeless look.
