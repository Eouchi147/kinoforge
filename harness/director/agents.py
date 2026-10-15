"""agents.py — the director's agent core for the build pipeline (mirror of studio-web/lib/agents.js).

Seats (head, deputy, crew, eyes, ears, free) are filled live from OpenRouter: the highest published intelligence inside
each seat's price ceiling and abilities, one model per provider, then the seat's `prefer` list as backups. Every call
has a timeout and falls through the chain; every cent goes into a Ledger that refuses calls past the film's cap.
Caps and seats: studio-web/lib/crew.json.
"""
import os, json, time, threading, urllib.request, urllib.error, concurrent.futures as cf

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CREW = json.load(open(os.path.join(ROOT, 'studio-web', 'lib', 'crew.json')))
API = 'https://openrouter.ai/api/v1'
KEY = os.environ.get('OPENROUTER_API_KEY', '')
_market = None


class OverBudget(Exception): pass
class AllFailed(Exception): pass


def _get(url, auth=False, timeout=30):
    h = {'Authorization': f'Bearer {KEY}'} if auth else {}
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout))


def market():
    global _market
    if _market is None:
        try:
            out = {}
            for m in _get(f'{API}/models')['data']:
                if m.get('expiration_date') or m['id'].startswith('openrouter/'): continue
                p = m.get('supported_parameters') or []
                out[m['id']] = {'id': m['id'], 'iq': ((m.get('benchmarks') or {}).get('artificial_analysis') or {}).get('intelligence_index'),
                                'in': float(m.get('pricing', {}).get('prompt') or 0) * 1e6, 'out': float(m.get('pricing', {}).get('completion') or 0) * 1e6,
                                'mods': (m.get('architecture') or {}).get('input_modalities') or [], 'json': 'structured_outputs' in p, 'created': m.get('created', 0)}
            _market = out
        except Exception:
            _market = {}
    return _market


def seat(name):
    s = CREW['seats'][name]; mk = market()
    if not mk: return list(s['prefer'])
    def fits(m):
        if not all(n in m['mods'] for n in s['needs']): return False
        if s.get('free'): return m['id'].endswith(':free')
        return ':' not in m['id'] and 0 < m['in'] <= s['max_in'] and m['out'] <= s['max_out']
    ranked = sorted((m for m in mk.values() if fits(m) and m['iq'] is not None), key=lambda m: (-m['iq'], -m['created']))
    out, seen = [], set()
    for m in ranked:
        p = m['id'].split('/')[0]
        if p not in seen: out.append(m['id']); seen.add(p)
        if len(out) == s['n']: break
    for mid in s['prefer']:
        if mid in mk and mid not in out and len(out) < s['n'] + 1: out.append(mid)
    return out or list(s['prefer'])


def account():
    try:
        d = _get(f'{API}/key', auth=True)['data']
        return {'usage': d.get('usage'), 'today': d.get('usage_daily'), 'remaining': d.get('limit_remaining')}
    except Exception:
        return None


class Ledger:
    """Every call, its seat, model, cost and time. Refuses a call whose worst case would pass the cap."""
    def __init__(self, cap, path=None):
        self.cap, self.path, self.calls, self.total, self.lock = cap, path, [], 0.0, threading.Lock()
        if path and os.path.exists(path):
            old = json.load(open(path)); self.calls = old.get('calls', []); self.total = old.get('total', 0.0)

    def room(self, worst): return self.total + worst <= self.cap
    def add(self, **c):
        with self.lock:
            self.calls.append(c); self.total += c.get('usd', 0) or 0; self.save()
    def save(self):
        if self.path:
            by = {}
            for c in self.calls: by[c['seat']] = round(by.get(c['seat'], 0) + (c.get('usd') or 0), 5)
            json.dump({'cap': self.cap, 'total': round(self.total, 5), 'by_seat': by, 'calls': self.calls}, open(self.path, 'w'), indent=1)


def parse_json(text):
    dec = json.JSONDecoder(); t = str(text or ''); i = t.find('{')
    while i != -1:
        try: return dec.raw_decode(t, i)[0]
        except ValueError: i = t.find('{', i + 1)
    raise ValueError('no JSON object in the reply')


def _cached(messages, model):
    if not (model.startswith('anthropic/') or model.startswith('google/')): return messages
    out = []
    for k, m in enumerate(messages):
        if k == 0 and m['role'] == 'system' and isinstance(m['content'], str):
            out.append({'role': 'system', 'content': [{'type': 'text', 'text': m['content'], 'cache_control': {'type': 'ephemeral'}}]})
        else: out.append(m)
    return out


def ask(seat_name, messages, schema, ledger, name='reply', max_tokens=2000, validate=None, only=None, allow_free=False, label=''):
    """Ask a seat for one JSON object matching `schema`. Falls through the seat's chain (and the free seat if allowed)."""
    mk = market()
    chain = [(seat_name, only, False)] if only else [(seat_name, m, False) for m in seat(seat_name)]
    if allow_free and not only: chain += [('free', m, False) for m in seat('free')]
    in_tok = len(json.dumps(messages)) // 3.5
    errors = []; k = 0
    while k < len(chain):
        seat_used, model, loose = chain[k]; k += 1
        m = mk.get(model) or {'in': 0, 'out': 0, 'json': True}
        worst = (in_tok * m['in'] + max_tokens * m['out']) / 1e6
        if not ledger.room(worst): errors.append(f'{model}: over the cap'); continue
        strict = m.get('json', True) and not loose
        msgs = _cached(messages, model)
        if not strict: msgs = msgs + [{'role': 'system', 'content': 'Reply with ONE JSON object only (no prose, no code fences) matching this JSON schema:\n' + json.dumps(schema)}]
        body = {'model': model, 'max_tokens': max_tokens, 'messages': msgs, 'usage': {'include': True}}
        if strict: body['response_format'] = {'type': 'json_schema', 'json_schema': {'name': name, 'strict': True, 'schema': schema}}
        req = urllib.request.Request(f'{API}/chat/completions', data=json.dumps(body).encode(),
                                     headers={'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json', 'X-Title': 'KINOFORGE director'})
        t0 = time.time()
        try:
            j = json.load(urllib.request.urlopen(req, timeout=CREW['seats'][seat_used].get('timeout_s', 60) * 3))   # no web time limit here
            u = j.get('usage') or {}
            cost = float(u.get('cost') if u.get('cost') is not None else (u.get('prompt_tokens', in_tok) * m['in'] + u.get('completion_tokens', max_tokens) * m['out']) / 1e6)
            data = parse_json(j['choices'][0]['message']['content'])
            problem = validate(data) if validate else None
            ledger.add(seat=seat_used, model=j.get('model', model), task=label, usd=round(cost, 6), s=round(time.time() - t0, 1), ok=not problem, note=problem)
            if problem: errors.append(f'{model}: {problem}'); continue
            return data, model          # the requested id: stable for retries; the ledger keeps the served one
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors='ignore')[:200]; errors.append(f'{model}: {e.code} {msg}')
            ledger.add(seat=seat_used, model=model, task=label, usd=0, s=round(time.time() - t0, 1), ok=False, note=f'{e.code}')
            if e.code == 402: raise OverBudget('OpenRouter key limit reached')
            if e.code == 400 and strict: chain.insert(k, (seat_used, model, True))
            if e.code == 429: time.sleep(15)
        except Exception as e:
            errors.append(f'{model}: {type(e).__name__} {e}'[:200])
            ledger.add(seat=seat_used, model=model, task=label, usd=0, s=round(time.time() - t0, 1), ok=False, note=type(e).__name__)
    if any('over the cap' in e for e in errors) and len(errors) == sum('over the cap' in e for e in errors):
        raise OverBudget('the film cap would be passed')
    raise AllFailed(' | '.join(errors))


def fan_out(seat_name, n, messages, schema, ledger, **kw):
    """The same task to n different models of a seat, in parallel. Returns [(data, model)] for every draft that came back."""
    models = seat(seat_name)[:n]
    with cf.ThreadPoolExecutor(n) as ex:
        futs = [ex.submit(ask, seat_name, messages, schema, ledger, only=m, **kw) for m in models]
        out = []
        for f in futs:
            try: out.append(f.result())
            except OverBudget: raise
            except Exception: pass
    if not out:   # every crew model failed: one more try down the full chain, free models included
        out.append(ask(seat_name, messages, schema, ledger, allow_free=True, **kw))
    return out
