import { chat } from '@/lib/openrouter';
import { STYLES } from '@/lib/data';
export const maxDuration = 60;

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
const SCHEMA = {
  type: 'object', additionalProperties: false, required: ['say', 'options', 'brief', 'ready', 'step_for_sam'],
  properties: {
    say: { type: 'string', description: 'What you say to Sam: 1 to 3 short sentences, then at most ONE question.' },
    options: { type: 'array', items: { type: 'string' }, description: '2 to 4 tappable answers to your question (each under 7 words), or [] if none.' },
    brief: BRIEF,
    ready: { type: 'boolean', description: 'true only when every brief field is filled and Sam has said to build it.' },
    step_for_sam: S('If Sam must do something outside this chat, the single next action in one imperative sentence; otherwise null.'),
  },
};

const SYSTEM = `You are the Showrunner of KINOFORGE, Sam's animation studio. You talk with Sam to find the film he wants, then the studio builds it.
Channels: "family" (kid-friendly, enjoyable for adults, not "made for kids") and "dark-corners" (adult, dark storytelling).
Style packs (pick the one that serves the story): ${STYLES.map((s) => `${s.name} (${s.motion})`).join('; ')}.
How you talk:
- Plain words, no jargon. At most 3 short sentences per turn, then ONE question with 2-4 tappable options. Never a list of questions.
- Lead with a proposal, not a blank question: suggest something concrete and let Sam react.
- Keep the brief updated every turn: carry forward what is known, null for what is not.
- When the brief is complete, read the logline and beats back in two sentences and ask "Shall I build it?" with options ["Build it", "Change something"]. Set ready=true only after Sam says to build it.
Hard rules (the studio's rulebook):
- Common sense: everything on screen must make sense; complete bodies; nothing missing or stray. Polish: clean, smooth, harmonious.
- Every film has its own original story (YouTube's "inauthentic content" rule): no templates, nothing that feels mass-produced.
- No real people's likeness or voice, no existing characters or brands, nothing illegal. Kids' films stay kind and safe.
- A hook in the first 3 seconds, beats linked by "but" or "therefore", a clear ending image.
Reply only with the JSON object.`;

// Free models sometimes return internal tokens ("choose_concept") or stray shapes; keep only what Sam should see.
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

export async function POST(req) {
  const { messages = [], brief = null } = await req.json();
  const convo = [{ role: 'system', content: SYSTEM }];
  if (brief) convo.push({ role: 'system', content: 'Current brief: ' + JSON.stringify(brief) });
  for (const m of messages.slice(-24)) convo.push({ role: m.role, content: m.content });
  if (!messages.length) convo.push({ role: 'user', content: 'Hi. Greet me in one line and pitch three different film ideas as options: one family, one Dark Corners, one surprising.' });
  try {
    const { data, model } = await chat({ messages: convo, schema: SCHEMA, name: 'director_turn' });
    return Response.json({ ...clean(data), model });
  } catch (e) {
    const code = e.code || 'error';
    return Response.json({ error: e.message, code }, { status: code === 'no-key' ? 409 : 502 });
  }
}

// GET = a health check of the director (the opening turn), used to verify the model chain after changes.
export async function GET() {
  const t0 = Date.now();
  try {
    const convo = [{ role: 'system', content: SYSTEM }, { role: 'user', content: 'Hi. Greet me in one line and pitch three different film ideas as options: one family, one Dark Corners, one surprising.' }];
    const { data, model } = await chat({ messages: convo, schema: SCHEMA, name: 'director_turn' });
    return Response.json({ ok: true, ms: Date.now() - t0, model, data: clean(data) });
  } catch (e) { return Response.json({ ok: false, ms: Date.now() - t0, code: e.code, error: e.message }, { status: 502 }); }
}
