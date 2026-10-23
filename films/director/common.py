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
FREE_ONLY = os.environ.get('KF_FREE_ONLY', '1' if CONFIG.get('free_only', False) else '0') != '0'
DEFAULTS = {'target_seconds': 150, 'cap_usd': CONFIG.get('default_cap_usd', 2.0),
            'voice': CONFIG.get('free_voice', 'chatterbox') if FREE_ONLY else CONFIG.get('paid_voice', 'elevenlabs/eleven-v4|brian'), 'line': 'battle-map'}
CAP_RANGE = CONFIG.get('cap_range_usd', [0.5, 5.0])
GATES = CONFIG.get('gates', {})
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
        self.brief['cap_usd'] = min(CAP_RANGE[1], max(CAP_RANGE[0], float(self.brief['cap_usd'])))
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
    if state == 'running' and cur.get('state') != 'running': cur = {'state': 'running', 'started_at': now(), 'usd_start': round(usd, 4)}
    else: cur = {**cur, 'state': state}
    if state in ('done', 'failed', 'skipped'): cur['ended_at'] = now()
    cur['usd'] = round(usd, 4)                                          # the job's total when this stage last reported
    cur['spent'] = round(usd - cur.get('usd_start', usd), 4)            # what this stage cost
    st[stage] = cur
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


def free_chain(seat_name, n=8):
    """Free models for a seat (films/director/free.py: curated per role, intersected with the live ':free' list)."""
    import free
    return free.seat_chain(seat_name)[:n]


def _guard_free(model, ledger, before):
    if FREE_ONLY and ledger.total > before + 1e-9:
        raise OverBudget(f'free-only mode: {model} charged US${ledger.total - before:.4f}; stopped')


# ------------------------------------------------------------------ paid seats (by role) and the hard cap
PAID = {k: v for k, v in CONFIG.get('paid_seats', {}).items() if not k.startswith('_')}
_PENDING = {}; _BOOK = __import__('threading').Lock()
UNKNOWN_PRICE = {'in': 5.0, 'out': 25.0}   # US$ per million tokens, assumed for a model the live list does not price


def role_models(role):
    """The configured models for a role that exist on OpenRouter right now (all of them when the list cannot be read)."""
    if role not in PAID: return agents.seat(role)
    mk = agents.market(); ms = PAID[role]['models']
    live = [m for m in ms if not mk or m in mk]
    return live or ms


def price(model):
    m = (agents.market() or {}).get(model)
    return {'in': m['in'], 'out': m['out']} if m else dict(UNKNOWN_PRICE)


def worst_cost(model, messages, max_tokens):
    p = price(model); in_tok = len(json.dumps(messages)) / 3.5
    return (in_tok * p['in'] + max_tokens * p['out']) / 1e6


def book(ledger, usd):
    """Reserve a call's worst case against the cap (parallel calls included). False when it would pass the cap."""
    with _BOOK:
        k = id(ledger); pend = _PENDING.get(k, 0.0)
        if ledger.total + pend + usd > ledger.cap + 1e-9: return False
        _PENDING[k] = pend + usd; return True


def unbook(ledger, usd):
    with _BOOK: _PENDING[id(ledger)] = max(0.0, _PENDING.get(id(ledger), 0.0) - usd)


def _paid_ask(name, messages, schema, ledger, only=None, **kw):
    cfg = PAID.get(name); seat = cfg['seat'] if cfg else name
    chain = [only] if only else role_models(name)
    mt = kw.get('max_tokens', 2000); errors = []
    for m in chain:
        w = worst_cost(m, messages, mt)
        if not book(ledger, w): errors.append(f'{m}: would pass the cap (worst case US${w:.3f})'); continue
        try: return agents.ask(seat, messages, schema, ledger, only=m, **kw)
        except OverBudget: raise
        except AllFailed as e: errors.append(str(e)[:240])
        finally: unbook(ledger, w)
    if errors and all('pass the cap' in e or 'over the cap' in e for e in errors):
        raise OverBudget(f'the film cap US${ledger.cap:.2f} would be passed (spent US${ledger.total:.2f})')
    raise AllFailed(' | '.join(errors))


def ask(seat_name, messages, schema, ledger, only=None, **kw):
    """JSON replies (strict schema), through the seat's chain and the ledger. Free-only mode: films/director/free.py (curated
    free models, robust JSON, 429 back-off, a paid model refused, any charge stops the job)."""
    if not FREE_ONLY: kw.pop('allow_free', None); return _paid_ask(seat_name, messages, schema, ledger, only=only, **kw)
    if only and not is_free(only): raise PaidRefused(f'free-only mode: {only} is not a free model')
    import free
    kw.pop('allow_free', None)
    try: return free.ask(seat_name, messages, schema, ledger, only=only, **kw)
    except free.Stop as e: raise OverBudget(str(e))
    except RuntimeError as e: raise AllFailed(str(e))


def seat_models(name):
    return free_chain(name) if FREE_ONLY else role_models(name)


def provider(model):
    return (model or '').split('/')[0]


def complete(seat_name, messages, ledger, max_tokens=24000, only=None, label='', validate=None):
    """A plain-text reply (for code), through the seat's chain and the ledger. Returns (text, model)."""
    if FREE_ONLY:
        if only and not is_free(only): raise PaidRefused(f'free-only mode: {only} is not a free model')
        import free
        try: return free.complete(seat_name, messages, ledger, max_tokens=max_tokens, only=only, label=label, validate=validate)
        except free.Stop as e: raise OverBudget(str(e))
        except RuntimeError as e: raise AllFailed(str(e))
    if FREE_ONLY and only and not is_free(only): raise PaidRefused(f'free-only mode: {only} is not a free model')
    mk = agents.market(); chain = [only] if only else seat_models(seat_name)
    crew_seat = PAID.get(seat_name, {}).get('seat', seat_name)
    if FREE_ONLY: chain = [m for m in chain if is_free(m)] * 2   # two passes: free models are rate limited
    in_tok = len(json.dumps(messages)) // 3.5; errors = []
    timeout = max(600, agents.CREW['seats'].get(crew_seat, {}).get('timeout_s', 60) * 1.5)   # long code replies
    for model in chain:
        m = mk.get(model) or dict(UNKNOWN_PRICE)
        worst = (in_tok * m['in'] + max_tokens * m['out']) / 1e6
        if not book(ledger, worst): errors.append(f'{model}: over the cap (worst case US${worst:.3f})'); continue
        try:
            got = _complete_one(model, messages, ledger, seat_name, max_tokens, label, validate, timeout, in_tok, m, errors)
        finally: unbook(ledger, worst)
        if got: return got
    if errors and all('over the cap' in e for e in errors): raise OverBudget(f'the film cap US${ledger.cap:.2f} would be passed (spent US${ledger.total:.2f})')
    raise AllFailed(' | '.join(errors))


def _complete_one(model, messages, ledger, seat_name, max_tokens, label, validate, timeout, in_tok, m, errors):
    """One plain-text call; (text, model) or None (the reason is appended to errors)."""
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
        if problem: errors.append(f'{model}: {problem}'); return None
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
    return None


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
