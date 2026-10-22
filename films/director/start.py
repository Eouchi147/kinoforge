"""start.py: open (or resume) a director job on the runner, and close a failed one.

    python3 films/director/start.py films/studio/<id> [--from resume|script|sound|spec|render|reflect] [--push]
    python3 films/director/start.py films/studio/<id> --failed "<message>" [--log <url>]

Opening: checks the brief (fields, line available, cap), the key and its credit, decides fresh or resume, clears the
outputs of the stages that must run again, sets status.json to queued and commits. Prints `render=true|false` for
$GITHUB_OUTPUT. A push of a brief whose approved_at differs from the one in status.json starts fresh; otherwise every
stage whose outputs exist is skipped (re-running a failed job does not pay twice).
"""
import os, sys, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

STAGE_FILES = {   # what each stage makes (cleared when the job restarts from that stage or an earlier one)
    'script': ['script.json', 'ad.json'],
    'sound': ['audio', 'cues.json', 'film.json', 'index.html', 'prep.log'],
    'spec': ['cand', 'check', 'spec.js', 'spec_log.json'],
    'render': [], 'reflect': ['reflect.json'],
}
ORDER = ['script', 'sound', 'spec', 'render', 'reflect']


def check_brief(d):
    b = json.load(open(os.path.join(d, 'brief.json'))); probs = []
    for k in ('title', 'subject'):
        if not str(b.get(k) or '').strip(): probs.append(f'{k} is missing')
    ln = b.get('line') or C.DEFAULTS['line']
    try: C.line(ln)
    except ValueError as e: probs.append(str(e))
    try:
        cap = float(b.get('cap_usd') or C.DEFAULTS['cap_usd'])
        if not 0.3 <= cap <= 5: probs.append(f'cap_usd {cap} is outside 0.30 to 5.00')
        ts = float(b.get('target_seconds') or C.DEFAULTS['target_seconds'])
        if not 45 <= ts <= 240: probs.append(f'target_seconds {ts} is outside 45 to 240')
    except (TypeError, ValueError): probs.append('cap_usd and target_seconds must be numbers')
    if b.get('id') and b['id'] != os.path.basename(d): probs.append(f'id {b["id"]!r} does not match the folder {os.path.basename(d)!r}')
    return b, probs


def clear(d, stages):
    for s in stages:
        for f in STAGE_FILES[s]:
            p = os.path.join(d, f)
            if os.path.isdir(p): shutil.rmtree(p)
            elif os.path.exists(p): os.remove(p)


def open_job(d, frm, push):
    b, probs = check_brief(d)
    if probs:
        C.set_status(d, 'script', 'failed', 'The brief cannot start: ' + '; '.join(probs)); return None
    if not os.environ.get('OPENROUTER_API_KEY'):
        C.set_status(d, 'script', 'failed', 'The OPENROUTER_API_KEY secret is missing on GitHub.'); return None
    acc = C.agents.account()
    if not C.FREE_ONLY and acc and acc.get('remaining') is not None and acc['remaining'] < 0.25:
        C.set_status(d, 'script', 'failed', f'The OpenRouter key has only ${acc["remaining"]:.2f} left; add credit or raise its limit.'); return None
    st = C.read_status(d)
    fresh = push and st.get('approved_at') != b.get('approved_at')
    if fresh or frm == 'script':
        keep = {'brief.json'} | ({'ledger.json'} if not fresh else set())
        for f in os.listdir(d):
            if f in keep: continue
            p = os.path.join(d, f); shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
        st = {}
    elif frm in ORDER:
        clear(d, ORDER[ORDER.index(frm):])
    done_render = (st.get('stages') or {}).get('render', {}).get('state') == 'done'
    render = not done_render or frm in ('script', 'sound', 'spec', 'render') or fresh
    mark = {'script': 'script.json', 'sound': 'cues.json', 'spec': 'spec.js'}
    first = next((s for s in ['script', 'sound', 'spec'] if not os.path.exists(os.path.join(d, mark[s]))), 'render')
    note = ('fresh job' if fresh or not st else f'resuming at {first}') + ('; free models and free tools only' if C.FREE_ONLY else '')
    C.set_status(d, first if first != 'render' else 'render', 'queued',
                 f'On the runner ({note}); key credit left: ' + (f'${acc["remaining"]:.2f}' if acc and acc.get('remaining') is not None else 'unknown') + '.')
    return render


if __name__ == '__main__':
    d = os.path.abspath(sys.argv[1].rstrip('/')); a = sys.argv[2:]
    if '--failed' in a:
        msg = a[a.index('--failed') + 1]; st = C.read_status(d); stage = st.get('stage') or 'script'
        logu = a[a.index('--log') + 1] if '--log' in a else None
        prev = st.get('message') or ''
        if (st.get('state') == 'failed'): msg = prev   # the stage already said why
        C.set_status(d, stage, 'failed', msg, outputs={'log': logu} if logu else None); sys.exit(0)
    frm = a[a.index('--from') + 1] if '--from' in a else 'resume'
    r = open_job(d, frm, '--push' in a)
    if r is None: sys.exit(1)
    print(f'render={"true" if r else "false"}')
    b = json.load(open(os.path.join(d, 'brief.json')))
    print(f'sound={"false" if os.path.exists(os.path.join(d, "cues.json")) else "true"}')
    v = (b.get('voice') or C.DEFAULTS['voice']).split('|')[0]
    print(f'tts={v if v in ("chatterbox", "kokoro") else ("chatterbox" if C.FREE_ONLY else "paid")}')
