"""common.py: shared helpers for the director pipeline (films/director/*.py).

A job is a folder films/studio/<id>/ holding brief.json (from the web studio) and everything the pipeline makes.
status.json is the contract with the web studio: {id, title, line, stage, state, message, usd, cap_usd, outputs,
stages, approved_at, run_url, updated_at}. Every paid call goes through the job's Ledger (ledger.json) against
brief.cap_usd. Commits happen only when KF_COMMIT=1 (set on the runners), so local runs and tests never push.
"""
import os, sys, json, re, time, random, subprocess, glob, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'harness', 'director'))
sys.path.insert(0, os.path.join(ROOT, 'harness', 'shots'))
import agents  # noqa: E402  (seats, Ledger, ask, OverBudget, AllFailed)
from agents import Ledger, OverBudget, AllFailed  # noqa: E402,F401

STAGES = ['script', 'sound', 'spec', 'check', 'eyes', 'render', 'reflect', 'done']
CONFIG = json.load(open(os.path.join(HERE, 'config.json')))
FREE_ONLY = os.environ.get('KF_FREE_ONLY', '1' if CONFIG.get('free_only', True) else '0') != '0'
DEFAULTS = {'target_seconds': 150, 'cap_usd': 1.5, 'voice': CONFIG.get('free_voice', 'chatterbox') if FREE_ONLY else 'elevenlabs/eleven-v4|brian',
            'line': 'battle-map'}
RELEASE = 'films'


def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)


def now():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def rel(p):
    return os.path.relpath(p, ROOT)


# ------------------------------------------------------------------ lines (production lines are config)
def lines_config():
    return {k: v for k, v in json.load(open(os.path.join(HERE, 'lines.json'))).items() if not k.startswith('_')}


def discover_examples(engine):
    """Hand-made film folders whose index.html loads the engine and that have a spec.js and cues.json. Director jobs
    (folders with a brief.json) are never examples: their quality is not proven by a person."""
    out = []
    for idx in sorted(glob.glob(os.path.join(ROOT, 'films', '**', 'index.html'), recursive=True)):
        d = os.path.dirname(idx)
        if '/films/lib/' in d + '/' or os.path.exists(os.path.join(d, 'brief.json')) or os.path.basename(d).startswith('_'): continue
        if not (os.path.exists(os.path.join(d, 'spec.js')) and os.path.exists(os.path.join(d, 'cues.json'))): continue
        if '/' + engine.strip('/') + '/' in open(idx).read(): out.append(rel(d))
    return out


def line(name):
    """The line's config with resolved example folders; raises if the line is not available yet."""
    cfg = lines_config()
    if name not in cfg: raise ValueError(f'unknown line {name!r} (known: {", ".join(cfg)})')
    L = dict(cfg[name]); L['name'] = name
    if not os.path.exists(os.path.join(ROOT, L['spec_md'])):
        raise ValueError(f'line {name!r} is not available yet: {L["spec_md"]} does not exist')
    ex = [e for e in (L.get('examples') or []) if os.path.exists(os.path.join(ROOT, e, 'spec.js'))]
    if len(ex) < 2 and not L.get('examples_fixed'):
        ex += [e for e in discover_examples(L['engine']) if e not in ex]
    L['examples'] = ex[:2]
    if not L['examples']: raise ValueError(f'line {name!r} has no example films with a spec.js')
    return L


def available_lines():
    out = []
    for k in lines_config():
        try: line(k); out.append(k)
        except ValueError: pass
    return out


# ------------------------------------------------------------------ the job
class Job:
    def __init__(self, d):
        self.dir = os.path.abspath(d.rstrip('/'))
        self.id = os.path.basename(self.dir)
        b = json.load(open(self.p('brief.json')))
        self.brief = {**DEFAULTS, **{k: v for k, v in b.items() if v not in (None, '')}}
        self.brief['id'] = self.id
        self.brief['target_seconds'] = float(self.brief['target_seconds'])
        self.brief['cap_usd'] = float(self.brief['cap_usd'])
        self.line = line(self.brief['line'])
        self.ledger = Ledger(self.brief['cap_usd'], self.p('ledger.json'))

    def p(self, *a): return os.path.join(self.dir, *a)
    def has(self, *a): return os.path.exists(self.p(*a))
    def read(self, name, default=None):
        return json.load(open(self.p(name))) if self.has(name) else default
    def write(self, name, data):
        os.makedirs(os.path.dirname(self.p(name)), exist_ok=True)
        json.dump(data, open(self.p(name), 'w'), indent=1, ensure_ascii=False)


def read_status(d):
    p = os.path.join(d, 'status.json')
    return json.load(open(p)) if os.path.exists(p) else {}


def set_status(d, stage, state, message='', outputs=None, commit=True, extra_paths=()):
    """Write status.json (and commit it with the stage's files when KF_COMMIT=1)."""
    d = os.path.abspath(d); s = read_status(d)
    b = json.load(open(os.path.join(d, 'brief.json')))
    led = os.path.join(d, 'ledger.json'); usd = json.load(open(led)).get('total', 0) if os.path.exists(led) else 0
    st = s.get('stages') or {}
    cur = st.get(stage) or {}
    if state == 'running' and cur.get('state') != 'running': cur = {'state': 'running', 'started_at': now()}
    else: cur = {**cur, 'state': state}
    if state in ('done', 'failed', 'skipped'): cur['ended_at'] = now()
    cur['usd'] = round(usd, 4); st[stage] = cur
    run_url = None
    if os.environ.get('GITHUB_RUN_ID'):
        run_url = f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ.get('GITHUB_REPOSITORY')}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
    s.update({'id': os.path.basename(d), 'title': b.get('title'), 'line': b.get('line', DEFAULTS['line']), 'stage': stage, 'state': state,
              'message': message, 'usd': round(usd, 4), 'cap_usd': float(b.get('cap_usd') or DEFAULTS['cap_usd']),
              'outputs': {**(s.get('outputs') or {}), **(outputs or {})}, 'stages': st, 'approved_at': b.get('approved_at'),
              'run_url': run_url or s.get('run_url'), 'updated_at': now()})
    json.dump(s, open(os.path.join(d, 'status.json'), 'w'), indent=1, ensure_ascii=False)
    log(f'[status] {stage} {state}: {message} (${usd:.3f})')
    if commit: git_commit([d] + list(extra_paths), f'film {os.path.basename(d)}: {stage} {state}')
    return s


def git_commit(paths, msg):
    if os.environ.get('KF_COMMIT') != '1': return False
    g = lambda *a, check=True: subprocess.run(['git', *a], cwd=ROOT, capture_output=True, text=True, check=check)
    ps = [rel(p) for p in paths]
    g('add', '-A', '--', *ps)
    if g('diff', '--cached', '--quiet', '--', *ps, check=False).returncode == 0: return False
    g('commit', '-q', '-m', msg, '--', *ps)   # only these paths, whatever else is staged
    for k in range(8):
        r = g('pull', '-q', '--rebase', '--autostash', check=False)
        if r.returncode == 0 and g('push', '-q', check=False).returncode == 0: return True
        if r.returncode != 0: g('rebase', '--abort', check=False)
        time.sleep(3 + random.random() * 6)
    raise RuntimeError('could not push after 8 tries: ' + msg)


# ------------------------------------------------------------------ models
class PaidRefused(Exception): pass


def is_free(model): return bool(model) and model.endswith(':free')


def free_chain(seat_name, n=6):
    """Free models (id ends in ':free') that have the seat's input abilities, best published intelligence first, one per
    provider first, then the crew's `free` prefer list. Used for every seat in free-only mode."""
    needs = agents.CREW['seats'].get(seat_name, {}).get('needs', ['text']); mk = agents.market()
    ok = [m for m in mk.values() if is_free(m['id']) and all(x in m['mods'] for x in needs)]
    ranked = sorted(ok, key=lambda m: (m['iq'] is None, -(m['iq'] or 0), -m['created']))
    out, seen = [], set()
    for m in ranked:
        p = provider(m['id'])
        if p not in seen: out.append(m['id']); seen.add(p)
    for m in ranked:
        if m['id'] not in out: out.append(m['id'])
    for m in agents.CREW['seats']['free']['prefer']:
        if m not in out and (not mk or (m in mk and all(x in mk[m]['mods'] for x in needs))): out.append(m)
    return out[:n]


def _guard_free(model, ledger, before):
    if FREE_ONLY and ledger.total > before + 1e-9:
        raise OverBudget(f'free-only mode: {model} charged US${ledger.total - before:.4f}; stopped')


def ask(seat_name, messages, schema, ledger, only=None, **kw):
    """JSON replies (strict schema), through the seat's chain and the ledger. Free-only mode: free models only, two passes
    (free models are rate limited), any paid model refused, any charge stops the job."""
    if not FREE_ONLY: return agents.ask(seat_name, messages, schema, ledger, only=only, **kw)
    if only and not is_free(only): raise PaidRefused(f'free-only mode: {only} is not a free model')
    chain = [only] if only else free_chain(seat_name); errors = []
    for attempt in range(2):
        for m in chain:
            before = ledger.total
            try:
                r = agents.ask(seat_name, messages, schema, ledger, only=m, **kw); _guard_free(m, ledger, before); return r
            except OverBudget: raise
            except Exception as e: errors.append(f'{m}: {str(e)[:160]}')
        if attempt == 0: time.sleep(20)
    raise AllFailed(' | '.join(errors[-8:]))


def seat_models(name):
    return free_chain(name) if FREE_ONLY else agents.seat(name)


def provider(model):
    return (model or '').split('/')[0]


def complete(seat_name, messages, ledger, max_tokens=24000, only=None, label='', validate=None):
    """A plain-text reply (for code), through the seat's chain and the ledger. Returns (text, model)."""
    if FREE_ONLY and only and not is_free(only): raise PaidRefused(f'free-only mode: {only} is not a free model')
    mk = agents.market(); chain = [only] if only else seat_models(seat_name)
    if FREE_ONLY: chain = [m for m in chain if is_free(m)] * 2   # two passes: free models are rate limited
    in_tok = len(json.dumps(messages)) // 3.5; errors = []
    timeout = max(600, agents.CREW['seats'][seat_name].get('timeout_s', 60) * 1.5)   # long code replies
    for model in chain:
        m = mk.get(model) or {'in': 0, 'out': 0}
        worst = (in_tok * m['in'] + max_tokens * m['out']) / 1e6
        if not ledger.room(worst): errors.append(f'{model}: over the cap'); continue
        body = {'model': model, 'max_tokens': max_tokens, 'messages': agents._cached(messages, model), 'usage': {'include': True}}
        req = urllib.request.Request(f'{agents.API}/chat/completions', data=json.dumps(body).encode(),
                                     headers={'Authorization': f'Bearer {agents.KEY}', 'Content-Type': 'application/json', 'X-Title': 'KINOFORGE director'})
        t0 = time.time()
        try:
            j = json.load(urllib.request.urlopen(req, timeout=timeout))
            u = j.get('usage') or {}
            cost = float(u.get('cost') if u.get('cost') is not None else (u.get('prompt_tokens', in_tok) * m['in'] + u.get('completion_tokens', max_tokens) * m['out']) / 1e6)
            text = (j['choices'][0]['message'].get('content') or '')
            fin = j['choices'][0].get('finish_reason')
            problem = 'empty reply' if not text.strip() else ('reply cut at max_tokens' if fin == 'length' else None)
            if not problem and validate: problem = validate(text)
            ledger.add(seat=seat_name, model=j.get('model', model), task=label, usd=round(cost, 6), s=round(time.time() - t0, 1), ok=not problem, note=problem,
                       tok_in=u.get('prompt_tokens'), tok_out=u.get('completion_tokens'))
            if FREE_ONLY and cost > 0: raise OverBudget(f'free-only mode: {model} charged US${cost:.4f}; stopped')
            if problem: errors.append(f'{model}: {problem}'); continue
            return text, model
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors='ignore')[:200]; errors.append(f'{model}: {e.code} {msg}')
            ledger.add(seat=seat_name, model=model, task=label, usd=0, s=round(time.time() - t0, 1), ok=False, note=f'{e.code}')
            if e.code == 402: raise OverBudget('OpenRouter key limit reached (HTTP 402)')
            if e.code == 429: time.sleep(15)
        except OverBudget: raise
        except Exception as e:
            errors.append(f'{model}: {type(e).__name__} {e}'[:200])
            ledger.add(seat=seat_name, model=model, task=label, usd=0, s=round(time.time() - t0, 1), ok=False, note=type(e).__name__)
    if errors and all('over the cap' in e for e in errors): raise OverBudget('the film cap would be passed')
    raise AllFailed(' | '.join(errors))


def code_block(text):
    """The JS module in a reply: the largest fenced block, or the whole reply if it already looks like a module."""
    blocks = re.findall(r'```(?:js|javascript|mjs)?[ \t]*\n(.*?)```', text, re.S)
    if blocks: return max(blocks, key=len).strip() + '\n'
    t = text.strip()
    if t.startswith('```'): t = re.sub(r'^```\w*\n?', '', t)   # an unclosed fence (cut reply)
    return t.strip() + '\n'


def craft():
    """CRAFT.md: Sam's verdicts and the house rules of direction and editing (read by the writer, coder and eyes seats)."""
    p = os.path.join(HERE, 'CRAFT.md')
    return open(p).read() if os.path.exists(p) else ''


# ------------------------------------------------------------------ house rules for words
KID_UNSAFE = re.compile(r'\b(blood\w*|bloody|gore|gory|guts|behead\w*|decapitat\w*|disembowel\w*|torture\w*|rape\w*|corpses?|mutilat\w*|slaughter\w*|massacre\w*|butcher\w*|impale\w*|severed|entrails)\b', re.I)
URL = re.compile(r'(https?://|www\.)\S+', re.I)


def house_clean(text):
    """Fix what code can fix: dashes, ellipses, double spaces. Returns (text, [fixes])."""
    fixes = []; t = text
    if re.search(r'[—–]', t):
        t = re.sub(r'(\d)\s*[–—]\s*(\d)', r'\1 to \2', t)
        t = re.sub(r'\s*[—–]\s*', ', ', t); fixes.append('dash replaced')
    if '...' in t or '…' in t:
        t = re.sub(r'\s*(\.\.\.|…)\s*', '. ', t).replace('. .', '.'); fixes.append('ellipsis replaced')
    t = re.sub(r'\s+([,.!?;:])', r'\1', t); t = re.sub(r',\s*,', ',', t); t = re.sub(r'\s{2,}', ' ', t).strip()
    t = re.sub(r'^[,\s]+', '', t)
    return t, fixes


def house_problems(text, kid_safe):
    p = []
    if re.search(r'[—–]', text): p.append('contains an em or en dash')
    if '...' in text or '…' in text: p.append('contains "..."')
    if URL.search(text): p.append('contains a URL')
    if kid_safe:
        bad = sorted(set(w.lower() for w in KID_UNSAFE.findall(text)))
        if bad: p.append('not kid-safe: ' + ', '.join(bad))
    return p
