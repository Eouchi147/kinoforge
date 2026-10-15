"""judge.py — the studio's Eyes and Ears: independent multimodal reviewers on OpenRouter.

    python3 harness/review/judge.py eyes  STORY.md SHEET.jpg [SHEET2.jpg ...] --out findings.json
    python3 harness/review/judge.py ears  SCRIPT.json NARRATION.wav --out findings.json

Eyes: two vision models from different providers look at contact sheets against the rulebook's §0 (common sense) and
R-0-08 (polish). A finding counts as a blocker only when both judges raise it (or one judge rates it critical with a
concrete frame), which keeps false alarms from looping forever. Ears: an audio-capable model listens to the narration
against its script for repeated / missing words, pace, pauses, tone vs genre.
Models are picked live from OpenRouter's model list (best published intelligence index that accepts the senses needed).
Needs OPENROUTER_API_KEY in the environment.
"""
import sys, os, json, base64, urllib.request, time

API = 'https://openrouter.ai/api/v1'
RULES = """Rules (the studio's core rule, a blocker above all others):
1. Anatomy complete: every creature/person has every part its kind has, attached where it belongs; hidden parts only behind something visible.
2. Physics and contact: grounded things touch the ground; nothing floats/sinks/passes through solids without a story reason; consistent scale.
3. Motion matches facing: nobody moves backwards to where they face.
4. Story actions are seen: cause and effect of each beat are in frame and readable on a phone; key characters big enough at their key moment.
5. Continuity: props, costumes and states carry over between shots.
6. Nothing nonsensical or stray: no leftover pieces, extra limbs, meaningless shapes.
7. Polish: clean, smooth, harmonious; nothing harsh, scratchy, jagged or clunky unless the style intends it."""

FINDINGS = {'type': 'object', 'additionalProperties': False, 'required': ['findings', 'verdict'], 'properties': {
    'verdict': {'type': 'string', 'enum': ['pass', 'fix']},
    'findings': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False, 'required': ['frames', 'problem', 'rule', 'severity', 'fix'], 'properties': {
        'frames': {'type': 'string', 'description': 'frame numbers or tile labels'}, 'problem': {'type': 'string'}, 'rule': {'type': 'integer'},
        'severity': {'type': 'string', 'enum': ['critical', 'major', 'minor']}, 'fix': {'type': 'string', 'description': 'what to change, concretely'}}}}}}

def get(url, key=None):
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {key}'} if key else {})
    return json.load(urllib.request.urlopen(req, timeout=60))

def pick(modality, n=2, max_price=6.0):
    """Best models that accept `modality`, one per provider."""
    data = get(f'{API}/models')['data']
    ok = []
    for m in data:
        ins = m.get('architecture', {}).get('input_modalities', []) or []
        params = m.get('supported_parameters', []) or []
        price = float(m.get('pricing', {}).get('prompt') or 0) * 1e6
        score = ((m.get('benchmarks') or {}).get('artificial_analysis') or {}).get('intelligence_index')
        if modality in ins and ('structured_outputs' in params or 'response_format' in params) and not m.get('expiration_date') and ':' not in m['id'] and 0 < price <= max_price and score is not None:
            ok.append((score, m['id']))
    out, seen = [], set()
    for _, mid in sorted(ok, reverse=True):
        p = mid.split('/')[0]
        if p not in seen: out.append(mid); seen.add(p)
        if len(out) == n: break
    return out

def ask(model, content, key, schema, name):
    body = {'model': model, 'messages': [{'role': 'user', 'content': content}], 'max_tokens': 3000,
            'response_format': {'type': 'json_schema', 'json_schema': {'name': name, 'strict': True, 'schema': schema}}, 'provider': {'require_parameters': True}}
    req = urllib.request.Request(f'{API}/chat/completions', data=json.dumps(body).encode(), headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json', 'X-Title': 'KINOFORGE judge'})
    for attempt in range(3):
        try:
            j = json.load(urllib.request.urlopen(req, timeout=300)); return json.loads(j['choices'][0]['message']['content']), j.get('model', model)
        except Exception as e:
            err = e; time.sleep(5 * (attempt + 1))
    raise err

def b64(path, mime): return f'data:{mime};base64,' + base64.b64encode(open(path, 'rb').read()).decode()

def eyes(story_path, sheets, key):
    story = open(story_path).read()
    prompt = (f'You are an independent reviewer for an animated film. You have NOT seen it being made. Find anything on screen that breaks common sense or polish.\n'
              f'Each tile is labelled with its frame number (24 fps). Style notes and story:\n{story}\n\n{RULES}\n\n'
              'Report only real problems, concretely (frames, what is wrong, which rule, severity, and the fix). Do not report things that are only unclear because of sampling. verdict = "fix" if any critical or major finding.')
    content = [{'type': 'text', 'text': prompt}] + [{'type': 'image_url', 'image_url': {'url': b64(s, 'image/jpeg')}} for s in sheets]
    models = pick('image'); reports = []
    for m in models:
        r, used = ask(m, content, key, FINDINGS, 'eyes_review'); r['model'] = used; reports.append(r)
    # consensus: a blocker needs two judges, or one critical
    blockers = []
    for i, r in enumerate(reports):
        for f in r['findings']:
            if f['severity'] == 'minor': continue
            others = [o for j, o in enumerate(reports) if j != i]
            agreed = any(any(g['rule'] == f['rule'] and g['severity'] != 'minor' and set(_frames(g['frames'])) & set(_frames(f['frames'])) for g in o['findings']) for o in others)
            if agreed or f['severity'] == 'critical': blockers.append(dict(f, judge=r['model'], agreed=agreed))
    return {'judges': reports, 'blockers': blockers, 'verdict': 'fix' if blockers else 'pass'}

def _frames(s):
    import re
    return [int(x) for x in re.findall(r'\d+', str(s))] or [-1]

EARS = {'type': 'object', 'additionalProperties': False, 'required': ['findings', 'verdict', 'tone_fit'], 'properties': {
    'verdict': {'type': 'string', 'enum': ['pass', 'fix']}, 'tone_fit': {'type': 'string', 'description': 'one sentence: does the delivery fit the genre and the picture?'},
    'findings': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False, 'required': ['line', 'at_s', 'problem', 'severity'], 'properties': {
        'line': {'type': 'string'}, 'at_s': {'type': 'number'}, 'problem': {'type': 'string'}, 'severity': {'type': 'string', 'enum': ['critical', 'major', 'minor']}}}}}}

def ears(script_path, wav, key):
    script = json.load(open(script_path))
    lines = '\n'.join(f"{l['id']} @ {l['start']}s: {l['text']}" + (f"  [direction: {l['tone']}]" if l.get('tone') else '') for l in script['lines'])
    prompt = (f"Listen to this narration for a {script.get('profile', 'narrated')} film. Script with start times and direction:\n{lines}\n\n"
              'Report every repeated, skipped or extra word, any unnatural pause or slowdown, mispronunciation, robotic or wrong-emotion delivery, and anything that does not fit the direction. verdict = "fix" if any major/critical.')
    content = [{'type': 'text', 'text': prompt}, {'type': 'input_audio', 'input_audio': {'data': base64.b64encode(open(wav, 'rb').read()).decode(), 'format': 'wav'}}]
    m = pick('audio', n=1)[0]; r, used = ask(m, content, key, EARS, 'ears_review'); r['model'] = used; return r

if __name__ == '__main__':
    key = os.environ.get('OPENROUTER_API_KEY')
    if not key: sys.exit('OPENROUTER_API_KEY is not set')
    mode, args = sys.argv[1], [a for a in sys.argv[2:] if not a.startswith('--')]
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
    if out in args: args.remove(out)
    res = eyes(args[0], args[1:], key) if mode == 'eyes' else ears(args[0], args[1], key)
    s = json.dumps(res, indent=1); print(s)
    if out: open(out, 'w').write(s)
