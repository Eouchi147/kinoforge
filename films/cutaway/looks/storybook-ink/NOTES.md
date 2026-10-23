# storybook-ink (Cutaway look board)

Look: a children's picture book: ink outlines of varied weight, watercolor washes that pool at the lines and slide off them, warm paper showing through, light pencil hatching in the shadows, slightly desaturated warm colour. Sky is a wet-in-wet wash, grass is a smooth green band, glass water a teal wash.

Art module: films/styles/cutaway/art/storybook-ink.py with the shared helpers in films/styles/cutaway/art/_npr_lines.py (numpy only, no scipy).
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
1. A children's book publisher or a parenting brand explaining nature or the body to kids (how a seed grows, what lives under a garden).
2. A museum or science centre family trail: 'what is under our feet' panels and short films.
3. A school or library reading-week film where the story is told over a soft, hand-made picture.
