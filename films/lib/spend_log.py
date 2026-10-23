"""spend_log.py: one line in the film's ledger.json for every paid call and every render, so tools/spend.py can show
what each video cost without anyone typing a number.

The rule (docs/manual/system/money-and-keys.md, "Spend per video"): any code that pays for a call or renders a film
writes one line here, in the film's own folder, the moment it knows the cost. Paid calls go under "calls" (the same
shape the director's Ledger writes, so old and new ledgers read alike); renders go under "renders".

    import sys; sys.path.insert(0, 'films/lib'); import spend_log
    usd, basis = spend_log.cost_from_usage(reply.get('usage'), price_in=3e-6, price_out=15e-6)
    spend_log.call('films/battles/cannae', seat='voice', model='elevenlabs/eleven-v4', task='vo brian 0',
                   usd=usd, basis=basis, seconds=3.7, ok=True)
    spend_log.render('films/cutaway/series/gold-mine', where='mac', seconds=2825.8, frames=480, note='10 jobs, 1280x720')
    spend_log.render('films/battles/cannae', where='github', run_id=39798701933, repo='Eouchi147/rc-render',
                     workflow='films.yml')

Command line (for a step in a workflow or a by-hand render):
    python3 films/lib/spend_log.py call   <folder> <seat> <model> <task> <usd> <measured|estimated> [seconds] [note]
    python3 films/lib/spend_log.py render <folder> <github|mac> <seconds> [run id] [note]

basis: "measured" when the provider reported the cost (OpenRouter usage.cost), "estimated" when our code priced it
(characters times a rate, tokens times a list price, a fallback). A failed call that still cost money is written with
ok=False and its cost. Every line is stamped with the UTC time ("at"), so spend is dated to the minute.
Writes are atomic (a temporary file, then a rename) and locked, so parallel calls in one job never lose a line.
No key is read or written here, ever.
"""
import datetime, fcntl, hashlib, json, os, sys, tempfile

BASES = ('measured', 'estimated')
WHERE = ('github', 'mac')


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def cost_from_usage(usage, price_in=None, price_out=None):
    """(usd, basis) from an OpenRouter usage block: its own cost when present (measured), else tokens times the list
    prices given (estimated), else (0.0, 'estimated') so the gap is visible instead of hidden."""
    u = usage or {}
    if u.get('cost') is not None: return round(float(u['cost']), 6), 'measured'
    if price_in is not None and price_out is not None:
        return round((u.get('prompt_tokens') or 0) * price_in + (u.get('completion_tokens') or 0) * price_out, 6), 'estimated'
    return 0.0, 'estimated'


def _update(folder, fn):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, 'ledger.json')
    key = hashlib.sha1(os.path.abspath(path).encode()).hexdigest()[:16]
    with open(os.path.join(tempfile.gettempdir(), f'kf-ledger-{key}.lock'), 'w') as lock:   # outside the repo
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            led = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {}
        except ValueError:
            raise SystemExit(f'spend_log: {path} is not valid JSON; fix it by hand before writing more lines')
        led.setdefault('cap', None); led.setdefault('calls', [])
        fn(led)
        by = {}
        for c in led['calls']: by[c.get('seat') or 'other'] = round(by.get(c.get('seat') or 'other', 0) + (c.get('usd') or 0), 6)
        led['total'] = round(sum(c.get('usd') or 0 for c in led['calls']), 6); led['by_seat'] = by
        out = {k: led[k] for k in ('cap', 'total', 'by_seat', 'calls')}
        out.update({k: v for k, v in led.items() if k not in out})
        fd, tmp = tempfile.mkstemp(dir=folder, prefix='.ledger.', suffix='.json')
        with os.fdopen(fd, 'w', encoding='utf-8') as f: json.dump(out, f, indent=1, ensure_ascii=False); f.write('\n')
        os.replace(tmp, path)
    return path


def call(folder, seat, model, task, usd, basis, seconds=None, ok=True, note=None, cap=None, **extra):
    """One paid call. usd is what it cost (0 for a free model); basis is "measured" or "estimated"."""
    if basis not in BASES: raise ValueError(f'basis must be one of {BASES}')
    line = {'seat': seat, 'model': model, 'task': task, 'usd': round(float(usd or 0), 6), 's': seconds, 'ok': bool(ok),
            'note': note, 'basis': basis, 'at': now(), **extra}

    def add(led):
        if cap is not None: led['cap'] = cap
        led['calls'].append(line)
    return _update(folder, add)


def render(folder, where, seconds=None, run_id=None, repo=None, workflow=None, frames=None, note=None, **extra):
    """One render: on GitHub runners (give run_id: tools/spend.py fetches the job minutes) or on the Mac lane (give the
    seconds, and job=<the lane's job name> so a later CSV export of the job logs is not counted twice)."""
    if where not in WHERE: raise ValueError(f'where must be one of {WHERE}')
    line = {'where': where, 'at': now(), 'seconds': seconds, 'run_id': int(run_id) if run_id else None, 'repo': repo,
            'workflow': workflow, 'frames': frames, 'note': note, **extra}

    def add(led):
        led.setdefault('renders', []).append({k: v for k, v in line.items() if v is not None})
    return _update(folder, add)


def main(argv):
    if len(argv) >= 7 and argv[0] == 'call':
        _, folder, seat, model, task, usd, basis, *rest = argv
        print(call(folder, seat, model, task, float(usd), basis, seconds=float(rest[0]) if rest else None, note=rest[1] if len(rest) > 1 else None))
        return 0
    if len(argv) >= 4 and argv[0] == 'render':
        _, folder, where, seconds, *rest = argv
        print(render(folder, where, seconds=float(seconds), run_id=rest[0] if rest and rest[0].isdigit() else None,
                     note=rest[-1] if rest and not rest[-1].isdigit() else None))
        return 0
    print('Command line' + __doc__.split('Command line')[1].split('basis:')[0].rstrip())
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
