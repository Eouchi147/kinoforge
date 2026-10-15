// The director's conversation turn. The HEAD (strongest model) talks with Sam and decides; when it wants fresh material
// it asks the CREW (cheap strong models, in parallel) and curates what comes back. Every call has a timeout and a
// fallback chain; every cent is counted against the caps in lib/crew.json.
import { ask, fanOut, ledger, account } from '@/lib/agents';
import CREW from '@/lib/crew.json';
import { STYLES } from '@/lib/data';
export const maxDuration = 300;
export const dynamic = 'force-dynamic';

const S = (t) => ({ type: ['string', 'null'], description: t });
const BRIEF = {
  type: 'object', additionalProperties: false,
  required: ['title', 'channel', 'format', 'length_seconds', 'style', 'logline', 'beats', 'characters', 'narrator', 'moral', 'music_mood'],
  properties: {
    title: S('working title'),
    channel: { type: ['string', 'null'], enum: ['family', 'dark-corners', null] },
    format: { type: ['string', 'null'], enum: ['16:9', '9:16', null] },
    length_seconds: { type: ['number', 'null'] },
    style: { type: ['string', 'null'], enum: [...STYLES.map((s) => s.name), null] },
    logline: S('one sentence, under 25 words'),
    beats: { type: 'array', items: { type: 'string' } },
    characters: { type: 'array', items: { type: 'string' } },
    narrator: S('who narrates and how they sound, or "no narrator"'),
    moral: S('the closing line or takeaway, if any'),
    music_mood: S('instruments and mood'),
  },
};
const TURN = {
  type: 'object', additionalProperties: false, required: ['say', 'options', 'brief', 'ready', 'step_for_sam', 'crew'],
  properties: {
    say: { type: 'string', description: 'What you say to Sam: 1 to 3 short sentences, then at most ONE question.' },
    options: { type: 'array', items: { type: 'string' }, description: '2 to 4 tappable answers to your question (each under 8 words), or [].' },
    brief: BRIEF,
    ready: { type: 'boolean', description: 'true only when every brief field is filled and Sam has said to build it.' },
    step_for_sam: S('Only if Sam must do something outside this chat: the single next action as one imperative sentence. Otherwise null.'),
    crew: {
      type: 'object', additionalProperties: false, required: ['need', 'task'],
      description: 'Ask your crew for fresh material BEFORE answering, only when it would make this answer clearly better (new ideas, alternatives, a title list, beat variations). Otherwise need = "none".',
      properties: { need: { type: 'string', enum: ['none', 'ideas'] }, task: { type: ['string', 'null'], description: 'Exactly what the crew should produce, with the constraints from the brief.' } },
    },
  },
};
const IDEAS = {
  type: 'object', additionalProperties: false, required: ['ideas'],
  properties: { ideas: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['title', 'pitch', 'why'], properties: { title: { type: 'string' }, pitch: { type: 'string' }, why: { type: 'string' } } } } },
};

const STYLE_LIST = STYLES.map((s) => `${s.name} (${s.motion})`).join('; ');
const SYSTEM = `You are the Showrunner, head of KINOFORGE, Sam's animation studio. You lead a crew of AI writers and reviewers; you talk with Sam, decide, and own the quality of every film.
Channels: "family" (kid-friendly, enjoyable for adults, not "made for kids") and "dark-corners" (adult, dark storytelling; unsettling, never gratuitous).
Style packs (pick the one that serves the story): ${STYLE_LIST}.
How you talk:
- Plain words, no jargon, warm and decisive. At most 3 short sentences per turn, then ONE question with 2-4 tappable options. Never a list of questions.
- Lead with a concrete proposal, not a blank question.
- Keep the brief updated every turn: carry forward what is known, null for what is not.
- When the brief is complete, read the logline and beats back in two sentences and ask "Shall I build it?" with options ["Build it", "Change something"]. Set ready=true only after Sam says to build it.
Your crew: when fresh material would clearly improve your answer, set crew.need="ideas" with a precise task; you will get their drafts and then answer. Curate hard: keep only what is original and fits.
Hard rules:
- Common sense: everything on screen must make sense; complete bodies; nothing missing or stray. Polish: clean, smooth, harmonious.
- Every film has its own original story (YouTube's "inauthentic content" rule): nothing templated or mass-produced.
- No real people's likeness or voice, no existing characters or brands, nothing illegal. Kids' films stay kind and safe.
- A hook in the first 3 seconds, beats linked by "but" or "therefore", a clear ending image.
Reply only with the JSON object.`;

function clean(d = {}) {
  const sentence = (s) => typeof s === 'string' && / /.test(s.trim()) && s.trim().length > 15 ? s.trim() : null;
  return {
    say: typeof d.say === 'string' ? d.say.trim() : '',
    options: Array.isArray(d.options) ? d.options.filter((o) => typeof o === 'string' && o.trim()).slice(0, 4) : [],
    brief: d.brief && typeof d.brief === 'object' ? d.brief : null,
    ready: d.ready === true,
    step_for_sam: sentence(d.step_for_sam),
  };
}
const validTurn = (d) => (typeof d?.say !== 'string' || d.say.trim().length < 2) ? 'empty reply' : null;
const short = (id) => (id || '').split('/').pop().replace(/:free$/, ' (free)');

// Which seat leads this turn: the head, unless money is short.
async function leadSeat() {
  const a = await account();
  if (a?.remaining != null && a.remaining < 0.05) return { seat: 'free', note: 'Your OpenRouter limit is used up, so a free model is answering.' };
  if (a?.today != null && a.today >= CREW.caps.day_usd) return { seat: 'crew', note: 'Today’s spending cap is reached, so a cheaper model is answering.' };
  if (a?.remaining != null && a.remaining < CREW.caps.reserve_usd) return { seat: 'deputy', note: null };
  return { seat: 'head', note: null };
}

async function turn(messages, brief) {
  const t0 = Date.now(), deadline = t0 + 110e3, book = ledger(CREW.caps.turn_usd);
  const lead = await leadSeat();
  const convo = [{ role: 'system', content: SYSTEM }];
  if (brief) convo.push({ role: 'system', content: 'Current brief: ' + JSON.stringify(brief) });
  for (const m of messages.slice(-24)) convo.push({ role: m.role, content: m.content });
  const opening = !messages.length;
  let crewNote = null, crewModels = [];

  // The opening turn always uses the crew: several cheap models pitch in parallel, the head curates the best three.
  const crewTask = opening ? 'Pitch 3 original short animated films (60 to 120 seconds) for KINOFORGE: one for the family channel, one for Dark Corners, one surprising. Each: a title, a one-sentence pitch with a visual hook, and why it would work as animation.' : null;
  const runCrew = async (task) => {
    const drafts = await fanOut('crew', 3, {
      messages: [{ role: 'system', content: `You are a writer on the KINOFORGE crew. Be original: no fairy-tale templates, no existing characters or brands, no real people. Style packs available: ${STYLE_LIST}.` },
        ...(brief ? [{ role: 'system', content: 'Brief so far: ' + JSON.stringify(brief) }] : []), { role: 'user', content: task }],
      schema: IDEAS, name: 'crew_ideas', maxTokens: 900, deadline: Math.min(deadline, Date.now() + 40e3), book,
    });
    crewModels = drafts.map((d) => d.model);
    return drafts.flatMap((d) => d.data.ideas || []);
  };

  if (opening) {
    const ideas = await runCrew(crewTask);
    convo.push({ role: 'user', content: 'Hi. Greet me in one line and offer three film ideas as options: one family, one Dark Corners, one surprising.' });
    if (ideas.length) crewNote = { role: 'system', content: `Your crew drafted ${ideas.length} pitches. Pick or improve the three strongest; options must be short (under 8 words each), the pitches themselves go in "say" only if short:\n` + JSON.stringify(ideas) };
  }
  let r = await ask(lead.seat, { messages: crewNote ? [...convo, crewNote] : convo, schema: TURN, name: 'director_turn', maxTokens: 1400, deadline, book, validate: validTurn });

  // The head asked for crew material: one round, then it answers with the drafts in hand.
  if (!opening && r.data?.crew?.need === 'ideas' && r.data.crew.task && deadline - Date.now() > 50e3) {
    const ideas = await runCrew(r.data.crew.task);
    if (ideas.length) {
      const note = { role: 'system', content: `Your crew answered "${r.data.crew.task}" with:\n${JSON.stringify(ideas)}\nNow answer Sam. Set crew.need to "none".` };
      r = await ask(lead.seat, { messages: [...convo, note], schema: TURN, name: 'director_turn', maxTokens: 1400, deadline, book, validate: validTurn }).catch(() => r);
    }
  }
  return {
    ...clean(r.data),
    director: { head: short(r.model), seat: r.seat, crew: crewModels.map(short), usd: +book.total.toFixed(4), ms: Date.now() - t0, note: lead.note, calls: book.calls },
  };
}

export async function POST(req) {
  const { messages = [], brief = null } = await req.json();
  if (!process.env.OPENROUTER_API_KEY) return Response.json({ error: 'no key', code: 'no-key' }, { status: 409 });
  try { return Response.json(await turn(messages, brief)); }
  catch (e) { return Response.json({ error: e.message, code: e.code || 'error' }, { status: 502 }); }
}

// GET = health check: runs the real opening turn (crew pitches, head curates) and reports models, time and cost.
export async function GET() {
  try { const t = await turn([], null); return Response.json({ ok: true, ...t }); }
  catch (e) { return Response.json({ ok: false, code: e.code, error: e.message }, { status: 502 }); }
}
