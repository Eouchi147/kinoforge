"""free.py: free OpenRouter models for the director (free-only mode). Seats, robust JSON, rate limits, a full call log.

    python3 films/director/free.py films/studio/<id>      (on the runner: list the live free models, choose the seats,
                                                          write <job>/seats.json and status.json outputs.seats)

Seat choice: config.json `free_seats` has, per role (text: writer, checker, crew; code: spec drafts and repairs; vision:
eyes), an ordered preference list of capable free models (id prefixes or substrings), intersected with the live ':free'
list. Anything not on a list must clear a floor (at least `min_params_b` billions in its name, or a published
intelligence index of at least `min_iq`) and must not match the role's `exclude` patterns or `known_bad`. A model that
answers 403 (agentic harnesses only), 404 or keeps failing is benched for the rest of the job.
Calls: response_format json_schema where the model supports structured outputs, json_object where it supports
response_format, plain otherwise; the reply is parsed from fenced blocks, leading prose and trailing text; one repair
retry asks for the JSON only; 429s back off (8 s, 25 s) and then the next model is tried.
"""
import os, sys, json, re, time, threading, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
API = 'https://openrouter.ai/api/v1'
CFG = json.load(open(os.path.join(HERE, 'config.json')))
SEAT_ROLE = {'head': 'text', 'deputy': 'text', 'crew': 'text', 'free': 'text', 'ears': 'text', 'writer': 'text', 'checker': 'text',
             'coder': 'code', 'coder2': 'code', 'repair': 'code', 'eyes': 'vision'}
BENCH = {}          # model -> reason (for this process)
FAILS = {}          # model -> failed calls
COOL = {}           # model -> time until which it is skipped (rate limited three times in a row)
MIN_TOKENS = 8000   # free calls cost nothing: room for reasoning models to think and still answer
CALLS = []          # every attempt: model, seat, label, status, seconds, note
_lock = threading.Lock(); _market = None


def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)
def key(): return os.environ.get('OPENROUTER_API_KEY', '')


def market(refresh=False):
    """Live free models: {id: {id, ctx, mods, params, created, iq, size_b}} (empty when OpenRouter cannot be reached)."""
    global _market
    if _market is not None and not refresh: return _market
    out = {}
    try:
        data = json.load(urllib.request.urlopen(urllib.request.Request(f'{API}/models'), timeout=30))['data']
        for m in data:
            mid = m['id']
            if not mid.endswith(':free') or m.get('expiration_date'): continue
            out[mid] = {'id': mid, 'name': m.get('name', ''), 'ctx': m.get('context_length') or 0,
                        'mods': (m.get('architecture') or {}).get('input_modalities') or ['text'], 'params': m.get('supported_parameters') or [],
                        'created': m.get('created', 0), 'iq': ((m.get('benchmarks') or {}).get('artificial_analysis') or {}).get('intelligence_index'),
                        'size_b': size_b(mid + ' ' + m.get('name', ''))}
    except Exception as e:
        log('free models: the list could not be read:', str(e)[:200])
    _market = out
    return out


def size_b(s):
    """Parameter count in billions from a model id or name ('120b', '235b-a22b' -> 235, '1.2t' -> 1200), else None."""
    s = s.lower(); m = re.findall(r'(?<![a-z0-9.])(\d+(?:\.\d+)?)([bt])(?![a-z])', s)
    if not m: return None
    return max(float(n) * (1000 if u == 't' else 1) for n, u in m)


def _match(mid, pat): return mid.startswith(pat) or pat in mid


def chain(role, mk=None, n=8):
    """The ordered free models for a role: the preference list first (in its order), then anything that clears the floor."""
    mk = market() if mk is None else mk; R = CFG['free_seats'][role]; bad = CFG['free_seats'].get('known_bad', [])
    need = ['image'] if role == 'vision' else []
    def ok(m):
        if m['id'] in BENCH or any(_match(m['id'], b) for b in bad): return False
        if any(x not in m['mods'] for x in need): return False
        return not any(re.search(x, m['id']) for x in R.get('exclude', []))
    out = []
    for pat in R['prefer']:
        hits = sorted((m for m in mk.values() if _match(m['id'], pat) and ok(m) and m['id'] not in out),
                      key=lambda m: (-(m['size_b'] or 0), -m['created']))
        out += [m['id'] for m in hits]
    floor = [m for m in mk.values() if m['id'] not in out and ok(m) and ((m['size_b'] or 0) >= CFG['free_seats'].get('min_params_b', 30)
             or (m['iq'] or 0) >= CFG['free_seats'].get('min_iq', 40))]
    out += [m['id'] for m in sorted(floor, key=lambda m: (-(m['iq'] or 0), -(m['size_b'] or 0), -m['created']))]
    if not mk:   # offline (tests, or the list failed): the known good ones
        out = [x for x in R.get('offline', []) if x not in BENCH]
    return out[:n]


def seat_chain(seat):
    """The role's models, the ones cooling down after rate limits moved to the end."""
    ms = chain(SEAT_ROLE.get(seat, 'text')); now = time.time()
    return [m for m in ms if COOL.get(m, 0) <= now] + [m for m in ms if COOL.get(m, 0) > now]


# ------------------------------------------------------------------ JSON from any reply
def parse_json(text, required=()):
    """The JSON object in a reply: fenced blocks first, then every '{' from the left; the largest object that has the required
    keys wins. Raises ValueError with what was seen."""
    t = str(text or ''); cands = re.findall(r'```(?:json|JSON)?\s*\n?(.*?)```', t, re.S) + [t]
    dec = json.JSONDecoder(); best = None
    for c in cands:
        for i in [k for k, ch in enumerate(c) if ch == '{'][:400]:
            try: obj, end = dec.raw_decode(c, i)
            except ValueError: continue
            if isinstance(obj, dict) and all(k in obj for k in required):
                if best is None or len(json.dumps(obj)) > len(json.dumps(best)): best = obj
        if best is not None: return best
    raise ValueError('no JSON object with ' + (', '.join(required) or 'any keys') + ' in the reply: ' + repr(t[:160]))


def _post(body, timeout):
    req = urllib.request.Request(f'{API}/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Authorization': f'Bearer {key()}', 'Content-Type': 'application/json', 'X-Title': 'KINOFORGE director (free)'})
    return json.load(urllib.request.urlopen(req, timeout=timeout))


class Stop(Exception): pass
class DailyLimit(Stop): pass


def call(model, messages, ledger, seat, label, max_tokens, timeout, response_format=None):
    """One reply from one free model, with 429 back-off. Returns (text, usage). Raises Stop for a charge or a 402."""
    for wait in (0, 20):   # every request counts against the key's free daily quota (1000): one wait, then the next model
        if wait: time.sleep(wait)
        body = {'model': model, 'max_tokens': max_tokens, 'messages': messages, 'usage': {'include': True}}
        if response_format: body['response_format'] = response_format
        t0 = time.time()
        try:
            j = _post(body, timeout)
            u = j.get('usage') or {}; cost = float(u.get('cost') or 0)
            msg = (j.get('choices') or [{}])[0].get('message') or {}
            text = msg.get('content') or ''
            if not text.strip() and msg.get('reasoning'): text = msg['reasoning']   # some models leave the answer in the reasoning
            fin = (j.get('choices') or [{}])[0].get('finish_reason')
            ledger.add(seat=seat, model=j.get('model', model), task=label, usd=round(cost, 6), s=round(time.time() - t0, 1), ok=bool(text.strip()),
                       note=fin if fin != 'stop' else None, tok_in=u.get('prompt_tokens'), tok_out=u.get('completion_tokens'))
            CALLS.append({'model': model, 'seat': seat, 'label': label, 'status': 200, 's': round(time.time() - t0, 1), 'finish': fin, 'chars': len(text)})
            if cost > 0: raise Stop(f'free-only mode: {model} charged US${cost:.4f}; stopped')
            if 'error' in j and not text: raise RuntimeError(str(j['error'])[:200])
            if fin == 'length' and not text.strip(): raise RuntimeError('reply cut at max_tokens before any answer')
            return text, fin
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors='ignore')[:300]
            CALLS.append({'model': model, 'seat': seat, 'label': label, 'status': e.code, 's': round(time.time() - t0, 1), 'note': msg[:160]})
            if e.code == 402: raise Stop('OpenRouter answered 402 (no credit): stopped')
            if e.code == 429:
                if re.search(r'per-day|per day|daily', msg, re.I): raise DailyLimit(f'the free models daily limit of this OpenRouter key is reached ({msg[:160]}); it resets at 00:00 UTC')
                log(f'  {model}: 429 rate limited, waiting ({msg[:140]})'); continue
            if e.code == 400 and re.search(r'max_tokens|maximum|context', msg, re.I) and max_tokens > 8000:
                max_tokens = 8000 if max_tokens <= 16000 else 16000; log(f'  {model}: 400 on the length, retrying with max_tokens {max_tokens}'); continue
            if e.code in (400,) and response_format: raise BadFormat(msg)
            if e.code in (401, 403, 404): bench(model, f'{e.code} {msg[:120]}')
            raise RuntimeError(f'{e.code} {msg[:200]}')
    COOL[model] = time.time() + 300
    raise RuntimeError('429 rate limited twice (skipped for 5 minutes)')


class BadFormat(Exception): pass


def bench(model, why):
    with _lock:
        if model not in BENCH: BENCH[model] = why; log(f'  benched {model}: {why[:160]}')


def _ask(seat, messages, schema, ledger, name='reply', max_tokens=2000, validate=None, only=None, label='', timeout=None, **_):
    """One JSON object from a free model of the seat's role. Returns (data, model)."""
    models = [only] if only else seat_chain(seat)
    if not models: raise RuntimeError(f'no free model for the seat {seat}')
    mk = market(); req = list(schema.get('required', [])); errors = []; max_tokens = max(max_tokens, MIN_TOKENS)
    timeout = timeout or 240
    for model in models:
        if model in BENCH: continue
        params = (mk.get(model) or {}).get('params', [])
        modes = []
        if 'structured_outputs' in params: modes.append({'type': 'json_schema', 'json_schema': {'name': name, 'strict': True, 'schema': schema}})
        if 'response_format' in params: modes.append({'type': 'json_object'})
        modes.append(None)
        hint = {'role': 'system', 'content': 'Reply with ONE JSON object only (no prose, no code fences) matching this JSON schema:\n' + json.dumps(schema)}
        msgs = messages + [hint]
        for rf in modes:
            try:
                text, fin = call(model, msgs, ledger, seat, label, max_tokens, timeout, rf)
                try: data = parse_json(text, req)
                except ValueError as e:   # one repair retry: the JSON only
                    log(f'  {model}: {str(e)[:160]}; asking for the JSON only')
                    more = min(32000, max_tokens * 2) if fin == 'length' else max_tokens   # a cut reply gets twice the room
                    text2, _ = call(model, msgs + [{'role': 'assistant', 'content': text[:6000]},
                                                    {'role': 'user', 'content': 'That reply was not the complete JSON object. Reply again with the JSON object only, '
                                                     'exactly matching the schema, starting with { and ending with }; keep every reason to one short sentence.'}],
                                    ledger, seat, label + ' (json retry)', more, timeout, rf)
                    data = parse_json(text2, req)
                problem = validate(data) if validate else None
                if problem: raise ValueError(problem)
                log(f'  {label}: {model} ok')
                return data, model
            except Stop: raise
            except BadFormat as e: errors.append(f'{model}: response_format refused'); continue
            except Exception as e:
                errors.append(f'{model}: {str(e)[:180]}'); log(f'  {label}: {model} failed: {str(e)[:200]}')
                FAILS[model] = FAILS.get(model, 0) + 1
                if FAILS[model] >= 2 and '429' not in str(e): bench(model, 'failed twice: ' + str(e)[:100])
                break
    raise RuntimeError(' | '.join(errors[-6:]) or 'no free model answered')


def _complete(seat, messages, ledger, max_tokens=24000, only=None, label='', validate=None, timeout=900):
    """Plain text (code) from a free model of the seat's role. Returns (text, model)."""
    models = [only] if only else seat_chain(seat); errors = []
    for model in models:
        if model in BENCH: continue
        try:
            text, fin = call(model, messages, ledger, seat, label, max_tokens, timeout)
            problem = 'reply cut at max_tokens' if fin == 'length' else (validate(text) if validate else None)
            if problem: raise ValueError(problem)
            return text, model
        except Stop: raise
        except Exception as e:
            errors.append(f'{model}: {str(e)[:180]}'); log(f'  {label}: {model} failed: {str(e)[:200]}')
    raise RuntimeError(' | '.join(errors[-6:]) or 'no free model answered')


BUSY = re.compile(r'429|503|overloaded|rate limit|temporarily', re.I)


def _patient(fn, *a, **kw):
    """Every model busy (429, 503): wait 60, 120, 240 s and go down the list again before giving up."""
    for wait in (0, 90, 240):
        if wait:
            log(f'  every free model is busy; waiting {wait} s'); time.sleep(wait)
            for m in list(COOL): COOL.pop(m, None)
        try: return fn(*a, **kw)
        except Stop: raise
        except RuntimeError as e:
            if not BUSY.search(str(e)) or wait == 240: raise


def ask(*a, **kw):
    """One JSON object from a free model of the seat's role (patient with busy models). Returns (data, model)."""
    return _patient(_ask, *a, **kw)


def complete(*a, **kw):
    """Plain text (code) from a free model of the seat's role (patient with busy models). Returns (text, model)."""
    return _patient(_complete, *a, **kw)


def choose():
    """The seats for this job: role -> ordered models, plus the live free list (for the log)."""
    mk = market(refresh=True)
    return {'free_models': sorted(mk), 'count': len(mk), 'roles': {r: chain(r, mk) for r in ('text', 'code', 'vision')}}


if __name__ == '__main__':
    import common as C
    d = sys.argv[1].rstrip('/'); res = choose(); mk = market()
    log(f'{res["count"]} free models live on OpenRouter:')
    for mid in res['free_models']:
        m = mk[mid]; log(f'  {mid}  ctx {m["ctx"]}  size {m["size_b"]}  iq {m["iq"]}  in {",".join(m["mods"])}  '
                         f'{"schema" if "structured_outputs" in m["params"] else ("json" if "response_format" in m["params"] else "plain")}')
    for r, ms in res['roles'].items(): log(f'seat role {r}: ' + ', '.join(ms))
    json.dump({'at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), **res,
               'models': {k: {x: mk[k][x] for x in ('ctx', 'size_b', 'iq', 'mods')} | {'params': [p for p in mk[k]['params'] if p in ('structured_outputs', 'response_format', 'tools', 'reasoning')]} for k in res['free_models']}},
              open(os.path.join(d, 'seats.json'), 'w'), indent=1)
    if os.path.exists(os.path.join(d, 'brief.json')):
        st = C.read_status(d)
        C.set_status(d, st.get('stage') or 'script', st.get('state') or 'queued', st.get('message') or 'Seats chosen.',
                     outputs={'seats': {'writer_and_checker': res['roles']['text'][:4], 'coder': res['roles']['code'][:4], 'eyes': res['roles']['vision'][:3]}})
    if not res['roles']['text']: sys.exit('no capable free text model is live: the job cannot run free')
