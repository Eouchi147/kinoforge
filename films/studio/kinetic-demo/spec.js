// Kinetic demo: the Zong episode ("The Ship Called Care", Dark Corners) re-told from a spec alone: no hand-written scenes.
// Every word on screen is in the narration (cues.json) or is a label for it. No bodies, no water, no ship drawn: words and objects only.
// Colour script: dark card + cream type (narration) | cold paper (records, the insurance, the court) | one warm parchment page (the price).
// ONE accent mark in the film: "CARE." in the last line.
export default {
  series: 'DARK CORNERS',
  title: ['The Ship', 'Called Care'],
  accent: '#cf3b2e',
  look: { vignette: 0.30, grain: 0.045 },
  cards: [
    // ---- the promise (0 to 14.7)
    { type: 'slam', at: 0, kicker: 'IN', text: '1781', on: 'o1.1781,', dateline: 'A BRITISH SLAVE SHIP' },
    { type: 'statement', at: 'o1.ran', text: ['^RAN SHORT OF', '!!WATER', 'IN THE CARIBBEAN.'] },
    { type: 'statement', line: 'o2', text: ['^WHAT ITS CREW', '!DID NEXT'] },
    { type: 'statement', at: 'o2.ended', text: ['^ENDED UP IN', '+A LONDON', '!!COURT'] },
    { type: 'record', at: 'o2.as', bg: 'paper', header: 'LONDON COURT', pos: 'upper', lines: ['^AS AN', '!!INSURANCE', '!!CLAIM.'] },
    { type: 'statement', line: 'o3', pos: 'upper', text: ["EVERYTHING YOU'RE ABOUT TO HEAR", '+REALLY', '!!HAPPENED.'] },
    { type: 'title', at: 14.85, on: 15.1 },

    // ---- the ship (17.4 to 41.5)
    { type: 'statement', line: 'x1', text: ['^THE SHIP WAS CALLED', '!!THE ZONG.'] },
    { type: 'statement', at: 'x1.It', text: ['^IT HAD BEEN TAKEN', '+FROM THE DUTCH,', '^WHO NAMED IT', '!!ZORG.'] },
    { type: 'statement', at: 'x1.In', text: ['^IN DUTCH,', 'THAT WORD MEANS', '!!CARE.'] },
    { type: 'count', line: 'x2', kicker: 'ON BOARD WERE', to: 17, on: 'x2.board', settle: 'x2.seventeen+0.3', label: 'CREW' },
    { type: 'count', at: 'x2.and', kicker: 'AND ABOUT', to: 440, on: 'x2.about', settle: 'x2.forty+0.4', label: ['AFRICAN', 'CAPTIVES.'] },
    { type: 'statement', at: 'x2.Twice', text: ['!!TWICE', 'WHAT A SHIP', 'THAT SIZE CARRIED.'] },
    { type: 'stamp', line: 'x4', doc: { header: 'INSURANCE', lines: ['EVERY CAPTIVE'] }, word: 'INSURED', on: 'x4.insured', angle: -6 },
    { type: 'slam', at: 'x4.Thirty', text: '£30', on: 'x4.Thirty', dateline: 'THIRTY POUNDS EACH' },

    // ---- the voyage (42.4 to 57.9): one map card, text steps on the cue words
    { type: 'map', line: 'm1', until: 'm2.And', grid: 'sea', seed: 4, gridOn: 42.4, gridDur: 3.2, zoom: [['m1', 1.0], ['m2.And', 1.16]], focus: [0.5, 0.5],
      nodes: {
        jam: { x: 0.56, y: 0.54, label: 'JAMAICA', on: 'm1.Jamaica.', big: true },
        jam2: { x: 0.56, y: 0.54, kind: 'none', label: 'ANOTHER ISLAND', side: 'below', on: 'm1.another' },
      },
      routes: [
        { points: [[0.06, 0.74], [0.28, 0.66], [0.47, 0.6]], on: 'm1.In', until: 'm1.Jamaica.>', ease: 'linear' },
        { points: [[0.47, 0.6], [0.66, 0.64], [0.99, 0.7]], on: 'm1.And', until: 'm2.downwind.>', ease: 'linear', dash: true },
      ],
      steps: [
        { at: 'm1', text: ['^IN LATE NOVEMBER,', 'THEY SAW', '!!JAMAICA.'] },
        { at: 'm1.The', text: ['^THE CAPTAIN THOUGHT', 'IT WAS', '!ANOTHER ISLAND.'] },
        { at: 'm1.And', text: ['^AND SAILED', '!!RIGHT PAST IT.'] },
        { at: 'm2', text: ['^BY THE TIME', '!THEY KNEW,'] },
        { at: 'm2.they#1', text: ['^HUNDREDS OF MILES', '!!DOWNWIND.'] },
      ] },
    { type: 'statement', at: 'm2.And', text: ['^AND THE WATER', '+WAS RUNNING', '!!LOW.'] },

    // ---- the rule (58 to 70)
    { type: 'statement', line: 'm3', bg: 'paper', text: ['^THE INSURANCE HAD A', '!!RULE.'] },
    { type: 'list', at: 'm3.Captives', bg: 'paper', title: 'THE INSURANCE RULE', pos: 'upper',
      items: [{ txt: "DIED OF SICKNESS: THE OWNERS' LOSS", mark: 'cross' }, { txt: 'THROWN OVERBOARD TO SAVE THE SHIP: THE INSURERS PAID', mark: 'tick' }] },

    // ---- the night (70.4 to 84)
    { type: 'statement', line: 'd1', pos: 'upper', text: ['^ON THE NIGHT OF', '+NOVEMBER', { kind: 'huge', txt: '29', on: 'd1.twenty-ninth,' }] },
    { type: 'statement', at: 'd1.the#2', text: ['^THE CREW', '!!DECIDED.'] },
    { type: 'count', line: 'd2', to: 54, on: 'd2.fifty-four', settle: 'd2.people,', label: 'PEOPLE' },
    { type: 'statement', at: 'd2.women', text: ['^WOMEN AND', '!!CHILDREN', '^FIRST'] },
    { type: 'statement', at: 'd2.were', text: ['^WERE FORCED', '!!INTO THE SEA.'] },
    { type: 'count', line: 'd3', kicker: 'TWO DAYS LATER', to: 42, on: 'd3.later,', settle: 'd3.forty-two+0.3', label: 'MEN.' },

    // ---- the rain (84 to 99)
    { type: 'statement', line: 'r1', text: ['^THEN IT', '!!RAINED.'] },
    { type: 'count', at: 'r1.They', kicker: 'THEY FILLED', to: 6, on: 'r1.filled', settle: 'r1.six+0.25', label: ['CASKS', 'WITH WATER.'] },
    { type: 'statement', line: 'r2', text: ['^AND THEY', '!!KEPT GOING.'] },
    { type: 'count', line: 'r3', to: 26, on: 'r3.twenty-six', settle: 'r3.twenty-six+0.6', label: 'MORE.' },
    { type: 'statement', at: 'r3.were', text: ['^WERE THROWN IN', '^WITH THEIR HANDS', '!!CHAINED.'] },
    { type: 'count', at: 'r3.Ten', to: 10, on: 'r3.Ten', settle: 'r3.Ten+0.5', label: ['OTHERS', 'JUMPED.'] },
    { type: 'statement', at: 'r3.They', text: ['^THEY CHOSE', '+THE SEA', '^OVER', '!!THE CHAINS.'] },

    // ---- the rope (99.7 to 106)
    { type: 'statement', line: 'p1', text: ['^ONE MAN,', '+THROWN OVERBOARD,'] },
    { type: 'statement', at: 'p1.caught', text: ['^CAUGHT A', '!!ROPE.'], deco: { kind: 'rope', on: 'p1.rope', x: 0.86, len: 0.5 } },
    { type: 'statement', at: 'p1.And', text: ['^AND CLIMBED', '+BACK', '!!ABOARD.'], deco: { kind: 'rope', on: 'p1.rope', x: 0.86, len: 0.5 } },

    // ---- Jamaica again (106.6 to 116)
    { type: 'statement', line: 'a1', text: ['^THREE WEEKS', '!!LATER,'] },
    { type: 'map', at: 'a1.the', until: 'a1.Two', grid: 'sea', seed: 4, gridOn: 40, zoom: 1.16, focus: [0.5, 0.5],
      nodes: { jam: { x: 0.56, y: 0.54, label: 'JAMAICA', on: 'a1.Jamaica.', big: true } },
      routes: [{ points: [[0.06, 0.74], [0.28, 0.66], [0.52, 0.56]], on: 'a1.the', until: 'a1.Jamaica.', ease: 'linear' }],
      text: ['^THE ZONG REACHED', '!!JAMAICA.'] },
    { type: 'count', at: 'a1.Two', to: 208, on: 'a1.Two', settle: 'a1.eight+0.5', label: ['CAPTIVES', 'WERE ALIVE.'] },
    { type: 'statement', at: 'a1.They', text: ['^THEY WERE', '!!SOLD.'] },

    // ---- the claim and the court (116 to 131)
    { type: 'record', line: 'c1', bg: 'paper', header: 'INSURANCE CLAIM', pos: 'upper', lines: ['THE OWNERS CLAIMED THE INSURANCE', '+FOR THE PEOPLE THEY', '!!HAD DROWNED.'] },
    { type: 'stamp', line: 'c2', doc: { header: 'LONDON', date: 'MARCH 1783', lines: ['A JURY AGREED WITH THE OWNERS.'] }, word: 'AGREED', on: 'c2.agreed', angle: -5 },
    { type: 'statement', line: 'c3', text: ['^THEIR LAWYER', '^TOLD THE COURT:'] },
    { type: 'quote', at: 'c3.It', text: 'It is the case of throwing over goods.', size: 'big' },

    // ---- Equiano and Sharp (131 to 146)
    { type: 'map', line: 'e1', until: 'e2', grid: 'graticule', seed: 2, gridOn: 131.2, zoom: 1.1, focus: [0.5, 0.5],
      nodes: { eq: { x: 0.24, y: 0.50, label: 'EQUIANO', on: 'e1.Equiano', big: true, side: 'above' }, sh: { x: 0.62, y: 0.56, label: 'SHARP', on: 'e1.Granville', big: true, side: 'above' } },
      edges: [{ from: 'eq', to: 'sh', on: 'e1.story', dur: 1.1 }],
      steps: [
        { at: 'e1', text: ['^BUT A MAN NAMED', '!!OLAUDAH', '!!EQUIANO'] },
        { at: 'e1.He', text: ['^HE HAD ONCE BEEN', '!!ENSLAVED', '+HIMSELF.'] },
        { at: 'e1.He#1', text: ['^HE TOOK THE STORY', '^TO A CAMPAIGNER,'] },
        { at: 'e1.Granville', text: ['!GRANVILLE', '!!SHARP.'] },
      ] },
    { type: 'record', line: 'e2', bg: 'paper', header: 'GRANVILLE SHARP', pos: 'upper', lines: ['WANTED THE CREW TRIED FOR', '!!MURDER.'] },

    // ---- the judge (146.6 to 161)
    { type: 'statement', line: 'j1', text: ['^THE JUDGE ORDERED', '!A NEW TRIAL.'] },
    { type: 'statement', at: 'j1.Because', text: ['^BECAUSE OF', '!!THE RAIN.'] },
    { type: 'record', at: 'j1.After', bg: 'paper', header: 'THE JUDGE', pos: 'upper', lines: ['AFTER THE RAIN, HE SAID, THERE SEEMED TO BE', '!!NO NEED.'] },
    { type: 'statement', line: 'j2', text: ['^THAT TRIAL', '!!NEVER', '+HAPPENED.'] },
    { type: 'strike', at: 'j2.No', text: ['^NO ONE WAS EVER', 'CHARGED WITH', '!MURDER.'], strikeOn: 'j2.murder.>+0.15' },

    // ---- the price (161.8 to 176)
    { type: 'statement', line: 'f1', text: ["^THE CAPTIVES' NAMES", '^WERE NEVER', '!!WRITTEN DOWN.'] },
    { type: 'letter', at: 'f1.Only', bg: 'parchment', text: 'Only their price.', size: 'big', pos: 'upper' },
    { type: 'statement', line: 'f2', text: ['^CAMPAIGNERS KEPT', '+TELLING THE', '!!STORY'] },
    { type: 'statement', at: 'f2.until', text: ['^UNTIL BRITAIN ENDED', '+ITS SLAVE TRADE,'] },
    { type: 'slam', at: 'f2.in', kicker: 'IN', text: '1807', on: 'f2.1807.' },
    { type: 'statement', line: 'f3', accent: true, text: ['^A SHIP WHOSE', '^NAME MEANT', '!!CARE.'] },
    { type: 'end' },
  ],
};
