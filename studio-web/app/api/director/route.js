// The director's conversation turn. The HEAD (strongest model) talks with Sam and decides; when it wants fresh material
// it asks the CREW (cheap strong models, in parallel) and curates what comes back. Every call has a timeout and a
// fallback chain; every cent is counted against the caps in lib/crew.json.
import { ask, fanOut, ledger, account } from '@/lib/agents';
import CREW from '@/lib/crew.json';
import { guard } from '@/lib/gate';
export const maxDuration = 300;
export const dynamic = 'force-dynamic';

const S = (t) => ({ type: ['string', 'null'], description: t });
// The brief is exactly what the film pipeline reads (films/director/DESIGN.md, films/studio/<id>/brief.json).
const BRIEF = {
  type: 'object', additionalProperties: false,
  required: ['title', 'line', 'format', 'subject', 'angle', 'audience', 'tone', 'target_seconds', 'notes'],
  properties: {
    title: S('the film title; for a battle: "The Battle of X"'),
    line: { type: ['string', 'null'], enum: ['battle-map', 'kinetic', 'cutaway', null], description: 'the production line' },
    format: { type: ['string', 'null'], enum: ['16:9', '9:16', null], description: 'cutaway only: 16:9 (wide, YouTube) or 9:16 (vertical, Shorts and Reels); null for the other lines' },
    subject: S('what the film is about, one sentence with the real names, places and dates'),
    angle: S('the one idea or question the film is built around, one sentence'),
    audience: S('who it is for, a few words'),
    tone: S('how it feels, a few words'),
    target_seconds: { type: ['number', 'null'], description: 'battle-map 120 to 180, kinetic 60 to 180, cutaway 30 to 90' },
    notes: S('anything else Sam asked for that the writer must respect (a fact to include, a thing to avoid), or null'),
  },
};
const TURN = {
  type: 'object', additionalProperties: false, required: ['say', 'options', 'brief', 'ready', 'crew'],
  properties: {
    say: { type: 'string', description: 'What you say to Sam: 1 to 3 short sentences, then at most ONE question.' },
    options: { type: 'array', items: { type: 'string' }, description: '2 to 4 tappable answers to your question (each under 8 words), or [].' },
    brief: BRIEF,
    ready: { type: 'boolean', description: 'true only when every brief field is filled and Sam has said to build it.' },
    crew: {
      type: 'object', additionalProperties: false, required: ['need', 'task'],
      description: 'Ask your crew for fresh material BEFORE answering, only when it would make this answer clearly better (subject ideas, angles, titles). Otherwise need = "none".',
      properties: { need: { type: 'string', enum: ['none', 'ideas'] }, task: { type: ['string', 'null'], description: 'Exactly what the crew should produce, with the constraints from the brief.' } },
    },
  },
};
const IDEAS = {
  type: 'object', additionalProperties: false, required: ['ideas'],
  properties: { ideas: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['title', 'pitch', 'why'], properties: { title: { type: 'string' }, pitch: { type: 'string' }, why: { type: 'string' } } } } },
};

const SYSTEM = `You are the Director of KINOFORGE, Sam's film studio. Sam tells you a subject, any subject; you turn it into a short explainer film the studio builds by itself and hands back finished. You talk, decide and own the quality.
The studio has three production lines. Pick the one that serves the subject:
- "battle-map": 16:9 landscape, about 2.5 minutes (120 to 180 s). An animated 3D relief map with unit blocks, arrows that draw on and labels that pop in. Best for battles, campaigns, journeys, expeditions, migrations: anything about places and movement. Tone: upbeat, a glint of dark humour, clear enough for a child (kid-safe words). Examples already made: Cannae, Hastings, Agincourt, Waterloo, Thermopylae, Gaugamela, Hattin, Ain Jalut.
- "kinetic": 9:16 vertical, about 1 to 3 minutes (60 to 180 s). Words, dates, numbers, documents and quotes set in motion. Best for anything told through language and facts: history, science, true stories, ideas. Tone: plain, restrained, adult by default. Example already made: A Hundred Thousand Good Nights (the Bamberg witch trials).
- "cutaway": a block of land cut out of the world, built in Blender: a living landscape on top (trees, water, houses, animals), the layers underneath cut clean like a diagram, with surprises buried at their depth (fossils, treasure, ruins, tunnels), golden light and fog. 16:9 or 9:16 (ask which: wide for YouTube, vertical for Shorts and Reels), 30 to 90 seconds (longer films take many hours to render on free machines). Best for what lies under the surface: geology, archaeology, cities on water, mines and tunnels, how things work underground, nature through the seasons. Tone: warm, curious, kid-clear. Examples: Why Venice Sinks, Four Seasons Over One Block, What Lies Under a Meadow.
Not available yet: clay, paper, lantern-road or other hand-built looks, characters, real-footage shots. If Sam wants one, say so in one sentence and offer the closest line.
The brief you fill (carry it forward every turn, null for what is not decided): title, line, format (cutaway only), subject, angle, audience, tone, target_seconds, notes (optional extras from Sam). The narrator is the studio's series voice; do not discuss voices.
How you talk:
- Plain words, warm, decisive. At most 3 short sentences, then ONE question with 2 to 4 tappable options. Never a list of questions.
- Lead with a proposal, not a blank question. As soon as Sam names a subject, propose the line, the angle, the tone and the length yourself in the same turn and let him correct you. Two or three turns should be enough.
- Facts matter: the script's every claim is checked by a second model, but help it by choosing a clear, well-documented angle. Never invent facts yourself; if you are unsure of something, say so.
- When the brief is complete, read it back in two sentences (title, line, length, angle) and ask "Shall I build it?" with options ["Build it", "Change something"]. Set ready=true only after Sam says to build it.
- A film runs on GitHub machines with the best model for each job, inside a hard money cap Sam sets (default US$2; a 2.5 minute film usually costs about US$1 to 1.50). It passes a fact check and picture checks before it is rendered; if it cannot pass inside the cap it stops and nothing is rendered. A Cutaway film takes a few hours to render. Sam watches the stages and nothing is published without him.
Hard rules: no real person's likeness or voice, nothing illegal, no gore for its own sake; sensitive history is handled with restraint. No em dashes or en dashes, no "..." anywhere.
Reply only with the JSON object.`;

function clean(d = {}) {
  return {
    say: typeof d.say === 'string' ? d.say.trim() : '',
    options: Array.isArray(d.options) ? d.options.filter((o) => typeof o === 'string' && o.trim()).map((o) => o.trim().slice(0, 60)).slice(0, 4) : [],
    brief: d.brief && typeof d.brief === 'object' ? d.brief : null,
    ready: d.ready === true,
  };
}
const FIELDS = ['title', 'line', 'format', 'subject', 'angle', 'audience', 'tone', 'target_seconds', 'notes'];
const LINES = ['battle-map', 'kinetic', 'cutaway'];
const dashless = (s) => typeof s === 'string' ? s.replace(/[\u2013\u2014]/g, ',').replace(/\.{3,}|\u2026/g, '') : s;
// Keep what is already decided: a weaker model must not wipe the brief by answering null.
function merge(prev, next) {
  const out = {};
  for (const k of FIELDS) {
    const v = next?.[k], keep = prev?.[k] ?? null;
    out[k] = v === null || v === undefined || v === '' ? keep : dashless(v);
  }
  if (!LINES.includes(out.line)) out.line = LINES.includes(prev?.line) ? prev.line : null;
  out.format = out.line === 'cutaway' ? (['16:9', '9:16'].includes(out.format) ? out.format : ['16:9', '9:16'].includes(prev?.format) ? prev.format : '16:9') : null;
  out.target_seconds = Number.isFinite(Number(out.target_seconds)) && out.target_seconds !== null ? Math.round(Number(out.target_seconds)) : null;
  return out;
}
const complete = (b) => ['title', 'line', 'subject', 'angle', 'audience', 'tone', 'target_seconds'].every((k) => b?.[k]);
const validTurn = (d) => (typeof d?.say !== 'string' || d.say.trim().length < 2) ? 'empty reply' : null;
const short = (id) => (id || '').split('/').pop().replace(/:free$/, ' (free)');

// Which seat leads this turn: the head, unless money is short. The free seat is also the automatic last link of
// every chain (lib/agents.js), so a dead key, a 402 or a timeout never ends the conversation.
async function leadSeat() {
  const a = await account();
  if (a?.remaining != null && a.remaining < 0.05) return { seat: 'free', why: 'credit' };
  if (a?.today != null && a.today >= CREW.caps.day_usd) return { seat: 'crew', why: 'day' };
  if (a?.remaining != null && a.remaining < CREW.caps.reserve_usd) return { seat: 'deputy', why: null };
  return { seat: 'head', why: null };
}

async function turn(messages, prior) {
  const t0 = Date.now(), deadline = t0 + 110e3, book = ledger(CREW.caps.turn_usd);
  const lead = await leadSeat();
  const convo = [{ role: 'system', content: SYSTEM }];
  if (prior) convo.push({ role: 'system', content: 'Current brief: ' + JSON.stringify(prior) });
  for (const m of messages.slice(-24)) convo.push({ role: m.role, content: String(m.content || '').slice(0, 4000) });
  const opening = !messages.length;
  let crewNote = null, crewModels = [];

  const runCrew = async (task) => {
    const drafts = await fanOut('crew', 3, {
      messages: [{ role: 'system', content: 'You are a writer on the KINOFORGE crew. Be specific and truthful: real, well-documented subjects with a clear angle. No real people\'s voices, nothing illegal. The studio makes three kinds of film: "battle-map" (animated relief map of a battle, campaign or journey, 16:9, about 2.5 min), "kinetic" (words, dates and documents in motion, 9:16, 1 to 3 min) and "cutaway" (a block of land cut open: life on top, layers and buried surprises underneath, 16:9 or 9:16, 30 to 90 s).' },
        ...(prior ? [{ role: 'system', content: 'Brief so far: ' + JSON.stringify(prior) }] : []), { role: 'user', content: task }],
      schema: IDEAS, name: 'crew_ideas', maxTokens: 900, deadline: Math.min(deadline, Date.now() + 40e3), book,
    });
    crewModels = drafts.map((d) => d.model);
    return drafts.flatMap((d) => d.data.ideas || []);
  };

  if (opening) {
    // Skip the crew when money is short: the free seat alone must open the conversation quickly.
    const ideas = lead.seat === 'free' ? [] : await runCrew('Pitch 3 film subjects for the studio: one battle or journey for battle-map, one dark true story for kinetic, one surprising science or ideas subject for kinetic. Each: a title, a one-sentence pitch with the real names and dates, and why it works on that line.');
    convo.push({ role: 'user', content: 'Hi. Greet me in one line, say you can make a film about any subject, and offer three subjects as options (under 8 words each).' });
    if (ideas.length) crewNote = { role: 'system', content: `Your crew drafted ${ideas.length} pitches. Pick or improve the three strongest as options; keep "say" short:\n` + JSON.stringify(ideas) };
  }
  let r = await ask(lead.seat, { messages: crewNote ? [...convo, crewNote] : convo, schema: TURN, name: 'director_turn', maxTokens: 1400, deadline, book, validate: validTurn });

  // The lead asked for crew material: one round, then it answers with the drafts in hand.
  if (!opening && r.seat !== 'free' && r.data?.crew?.need === 'ideas' && r.data.crew.task && deadline - Date.now() > 50e3) {
    const ideas = await runCrew(r.data.crew.task);
    if (ideas.length) {
      const note = { role: 'system', content: `Your crew answered "${r.data.crew.task}" with:\n${JSON.stringify(ideas)}\nNow answer Sam. Set crew.need to "none".` };
      r = await ask(lead.seat, { messages: [...convo, note], schema: TURN, name: 'director_turn', maxTokens: 1400, deadline, book, validate: validTurn }).catch(() => r);
    }
  }
  const d = clean(r.data), brief = merge(prior, d.brief);
  const fallback = r.seat === 'free';
  return {
    say: dashless(d.say), options: d.options.map(dashless), brief, ready: d.ready && complete(brief),
    director: {
      head: short(r.model), seat: r.seat, crew: crewModels.map(short), usd: +book.total.toFixed(4), ms: Date.now() - t0, calls: book.calls,
      fallback, reason: fallback ? (lead.why === 'credit' ? 'credit' : 'busy') : null,
      note: fallback ? (lead.why === 'credit' ? 'The studio key is out of credit, so a free model is answering.' : 'The usual models did not answer, so a free model is answering.') : lead.why === 'day' ? 'Today’s spending cap is reached, so a cheaper model is answering.' : null,
    },
  };
}

export async function POST(req) {
  const locked = guard(req); if (locked) return locked;   // every turn spends OpenRouter credit
  const { messages = [], brief = null } = await req.json().catch(() => ({}));
  if (!process.env.OPENROUTER_API_KEY) return Response.json({ error: 'no key', code: 'no-key' }, { status: 409 });
  try { return Response.json(await turn(messages, brief)); }
  catch (e) { return Response.json({ error: e.message, code: e.code || 'error' }, { status: 502 }); }
}

// GET = health check: runs the real opening turn and reports models, time and cost.
export async function GET(req) {
  const locked = guard(req); if (locked) return locked;
  try { const t = await turn([], null); return Response.json({ ok: true, ...t }); }
  catch (e) { return Response.json({ ok: false, code: e.code, error: e.message }, { status: 502 }); }
}
