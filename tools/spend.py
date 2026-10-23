#!/usr/bin/env python3
"""spend.py: build studio-web/public/data/spend.json, what every video cost, line by line, honest to the cent.

    python3 tools/spend.py                 write studio-web/public/data/spend.json (offline: the repo and data/spend/ only)
    python3 tools/spend.py --check         exit 1 if the file on disk differs from what the repo says (ignores "generated")
    python3 tools/spend.py --stdout        print it instead of writing
    python3 tools/spend.py --fetch-runs    first ask GitHub (gh api, read only) for every run id below that is not yet in
                                           data/spend/runs.json, and pick up the <film id>-run.json records that rc-render
                                           films.yml and remux.yml upload to release kino-films; then build
    python3 tools/spend.py --refresh-runs  the same, re-asking for every run (a run that was still going is stored again)

What it reads (nothing is typed by hand except the tables marked "static" below, each with its source):
  - paid calls: every tracked ledger.json (films/**, ads/*, boards/*, pieces/*): seat, model, task, usd, seconds, ok, note.
    Each line gets a basis: "measured" (the provider's own usage cost), "estimated" (priced by our code: speech from the
    characters sent, a fallback price, note "estimated"), or "not flagged" (old code that booked a list price when the
    provider sent no cost and did not record which it was). A call is dated by the commit that first recorded it.
  - director jobs: films/studio/<id>/status.json (cap, spend per stage, the run) next to their ledger;
  - the log: sentences of docs/LOG.md with US$ and a film's name. Never added on top of a ledger (shown as a cross-check);
    counted only when the film has no ledger and the sentence names that film alone;
  - GitHub Actions: job times of the runs named in docs/LOG.md, docs/manual/films/ and status.json (table RUNS), stored
    in data/spend/runs.json by --fetch-runs so the build is offline and repeatable; free on public repos, shown with what
    they would be worth at GitHub's list price;
  - the Mac lane: data/spend/mac-lane-jobs.csv (one row per job log), with an electricity estimate (RATES).
Deterministic: everything sorted, no clock except the top-level "generated" (SOURCE_DATE_EPOCH is honoured).
House style for every string: no em dash, no en dash, no three dots (the build fails otherwise).
"""
import collections, csv, datetime, json, math, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(ROOT, 'studio-web', 'public', 'data', 'spend.json')
CATALOG = os.path.join(ROOT, 'studio-web', 'public', 'data', 'catalog.json')
RUNS_FILE = os.path.join(ROOT, 'data', 'spend', 'runs.json')
MAC_CSV = os.path.join(ROOT, 'data', 'spend', 'mac-lane-jobs.csv')
RC, KF = 'Eouchi147/rc-render', 'Eouchi147/kinoforge'

# ---------------------------------------------------------------------------------------------- rates (static, cited)
RATES = {
    'runner_usd_per_min': {
        'value': 0.006, 'unit': 'US$ per minute',
        'what': 'GitHub Actions list price of a standard Linux 2-core x64 runner (SKU actions_linux), the price the same '
                'runs-on: ubuntu-24.04 jobs would pay in a private repo. Public repos run them free (on a 4-core machine). '
                'GitHub rounds each job up to the next whole minute.',
        'source': 'GitHub Docs, Actions runner pricing (docs.github.com/en/billing/reference/actions-runner-pricing), read '
                  'on 23 Oct 2026 from the docs source (github/docs, content/billing/reference/actions-runner-pricing.md '
                  'and data/reusables/billing/actions-standard-runner-prices.md at commit d67ced7 of 13 Oct 2026); the same '
                  'page lists Linux 4-core at US$0.012 a minute.',
        'verified': True},
    'mac_watts': {
        'value': 30, 'unit': 'W at the wall while rendering',
        'what': 'MacBook Air (M4) rendering in Blender (Metal GPU, fanless). Assumed, not measured: 30 W is the rating of the '
                'smallest power adapter Apple ships with it, a round upper figure for a sustained render on mains.',
        'source': 'not looked up: support.apple.com was not reachable from the session that built this (23 Oct 2026). '
                  'Measure it once with a plug meter or "sudo powermetrics" and update this line.',
        'verified': False},
    'kwh_cad': {
        'value': 0.20, 'unit': 'CA$ per kWh',
        'what': 'Ontario residential electricity, all in (energy, delivery, regulatory). Assumed round figure.',
        'source': 'not looked up: oeb.ca was not reachable from the session that built this (23 Oct 2026). Check the '
                  'Ontario Energy Board rates page and a recent hydro bill, then update this line.',
        'verified': False},
}

# ---------------------------------------------------------------------------------------------- runs (static, sourced)
# Every GitHub Actions run id written down in docs/LOG.md, docs/manual/films/*.md or a director status.json (searched
# 23 Oct 2026), with the film it belongs to. A run that is not a film's goes to OTHER by its key.
RUNS = {
    39790691570: ('rc-render', 'dark-corners-bamberg-kinetic', 'films.yml render (polish pass; text overprint found)', 'docs/LOG.md 22 Oct; docs/manual/films/dark-corners-bamberg-kinetic.md'),
    39800373137: ('rc-render', 'dark-corners-bamberg-kinetic', 'films.yml render (final)', 'docs/LOG.md 22 Oct; docs/manual/films/dark-corners-bamberg-kinetic.md'),
    39797513657: ('rc-render', 'dark-corners-kleidion-lantern-road', 'films.yml render', 'docs/LOG.md 22 Oct; docs/manual/films/dark-corners-kleidion-lantern-road.md'),
    39810673282: ('rc-render', 'dark-corners-arabia-clay', 'films.yml render (24 parts)', 'docs/LOG.md 22 Oct; docs/manual/films/dark-corners-arabia-clay.md'),
    39798701933: ('rc-render', 'battle-map-cannae', 'films.yml render (v2)', 'docs/LOG.md 22 Oct; docs/manual/films/battle-map-cannae.md'),
    39817058161: ('rc-render', 'battle-map-cannae', 'remux.yml (final score)', 'docs/LOG.md 22 Oct; docs/manual/films/battle-map-cannae.md'),
    39900294683: ('rc-render', 'battle-map-agincourt', 'films.yml render (v2, insert B missing)', 'docs/LOG.md 23 Oct; docs/manual/films/battle-map-agincourt.md'),
    39908562175: ('rc-render', 'battle-map-agincourt', 'films.yml render (v2, both inserts)', 'docs/LOG.md 23 Oct; docs/manual/films/battle-map-agincourt.md'),
    39880127743: ('rc-render', 'cutaway-line-meadow', 'stills.yml check stills r1 (8 frames)', 'docs/LOG.md 23 Oct; docs/manual/films/cutaway-line-meadow.md'),
    39884546069: ('rc-render', 'cutaway-line-meadow', 'stills.yml check stills r2 (3 frames)', 'docs/LOG.md 23 Oct; docs/manual/films/cutaway-line-meadow.md'),
    39894366759: ('rc-render', 'cutaway-series-river-time', 'films.yml render', 'docs/LOG.md 23 Oct; docs/manual/films/cutaway-series-river-time.md'),
    39895728062: ('rc-render', 'cutaway-series-sleeping-volcano', 'films.yml render', 'docs/LOG.md 23 Oct; docs/manual/films/cutaway-series-sleeping-volcano.md'),
    39896034330: ('rc-render', 'cutaway-series-under-the-city', 'films.yml render', 'docs/LOG.md 23 Oct; docs/manual/films/cutaway-series-under-the-city.md'),
    39896254752: ('rc-render', 'cutaway-series-hidden-meadow', 'films.yml render', 'docs/LOG.md 23 Oct; docs/manual/films/cutaway-series-hidden-meadow.md'),
    39822483930: ('kinoforge', 'noor-descent-05-iqra', 'films-render.yml render (part 11 hung 4.5 h, re-run)', 'docs/LOG.md 22 Oct; docs/manual/films/noor-descent-05-iqra.md'),
    39784277702: ('kinoforge', 'battle-of-tours', 'film.yml director job (cancelled)', 'films/studio/battle-of-tours/status.json'),
    39817396473: ('kinoforge', 'great-emu-war', 'film.yml director job (stopped at the script)', 'films/studio/great-emu-war/status.json'),
    39877596998: ('kinoforge', 'salamis', 'film.yml director job (resume, stopped before any call)', 'films/studio/salamis/status.json; docs/LOG.md 23 Oct'),
    39890165805: ('rc-render', 'shared-sound-bank', 'sfx-bank.yml (the CC0 sound bank the Cutaway series share)', 'docs/LOG.md 23 Oct; docs/manual/sound/sfx-bank.md'),
}

# ---------------------------------------------------------------------------------------------- paid work (static)
BOARDS_OF = {'unmissed-v4': ['boards/unmissed-night', 'boards/unmissed-night-clips']}   # docs/manual/films/unmissed-v4.md
OTHER_KINDS = {   # ledger folders that are not a video in the library: their own entries, counted in the studio total
    'boards': ('board', 'Style board (AI stills and clips)'),
    'pieces': ('piece', 'AI-footage piece (15 Oct, not in the library)'),
    'films/showcase': ('showcase', 'Showcase film agent (15 Oct, every film failed)'),
}
OTHER_TITLES = {'shared-sound-bank': 'Shared: the CC0 sound bank (sfx-bank)', 'mac-look-boards': 'Mac lane: look boards',
                'mac-lane-checks': 'Mac lane: drive and lane checks'}

# Log names: how docs/LOG.md names each film (matched as whole words, case as written). Ids and folders always match.
ALIASES = {
    'battle-map-cannae': ['Cannae'], 'battle-map-hastings': ['Hastings'], 'battle-map-agincourt': ['Agincourt'],
    'battle-map-waterloo': ['Waterloo'], 'battle-map-thermopylae': ['Thermopylae'], 'battle-map-gaugamela': ['Gaugamela'],
    'battle-map-hattin': ['Hattin'], 'battle-map-ain-jalut': ['Ain Jalut'], 'battle-of-tours': ['Battle of Tours'],
    'salamis': ['Salamis'], 'great-emu-war': ['Great Emu War'],
    'cutaway-agincourt-mud-A': ['insert A'], 'cutaway-agincourt-mud-B': ['insert B'],
    'dark-corners-arabia-clay': ['Arabia'], 'dark-corners-bamberg-kinetic': ['Bamberg'],
    'dark-corners-kleidion-lantern-road': ['Kleidion'], 'dark-corners-zong-lantern-road': ['Zong'],
    'noor-descent-05-iqra': ['Iqra'], 'noor-juz-30-amma': ['Juz Amma', 'Amma'],
    'cutaway-line-meadow': ['What Lies Under a Meadow'], 'cutaway-loop-seasons': ['seasons loop', 'Seasons loop'],
    'cutaway-series-gold-mine': ['Gold Mine'], 'cutaway-series-hidden-meadow': ['Hidden Meadow'],
    'cutaway-series-reef-and-wreck': ['Reef and Wreck'], 'cutaway-series-river-time': ['River Through Time'],
    'cutaway-series-sleeping-volcano': ['Sleeping Volcano'], 'cutaway-series-under-the-city': ['Under the City'],
    'cutaway-ad-drainage-v169': ['drainage ad'], 'cutaway-ad-drainage-v916': ['drainage ad'],
    'under-the-surface-venice': ['Venice'], 'style-cutaway-cinematic': ['cinematic test'],
    'unmissed-v1': ['Manifesto'], 'unmissed-v2': ['The Catch'], 'unmissed-v3': ['The Call'], 'unmissed-v4': ['Night Shift'],
    'unmissed-v5': ['Bento'],
}

# Mac lane folders that are a film's (the rest: look boards and lane checks, see mac())
MAC_FILM = {'films/cutaway/meadow': 'cutaway-line-meadow', 'films/cutaway/venice': 'under-the-surface-venice',
            'films/cutaway/loops/seasons': 'cutaway-loop-seasons'}

# ---------------------------------------------------------------------------------------------- helpers
BAD = re.compile('[–—…]|\\.\\.\\.')


def clean(s):
    """House style for words that come from records (task labels, error notes): no dashes, no three dots."""
    s = str(s)
    s = re.sub(r'\.\.\.+|…', '.', s)
    return re.sub(r'\s*[–—]\s*', ', ', s)


def r6(x): return round(float(x or 0) + 0.0, 6)


def sh(args):
    try: return subprocess.run(args, cwd=ROOT, capture_output=True, text=True).stdout
    except Exception: return ''


def tracked(*paths):
    out = sh(['git', 'ls-files', '-z', '--', *paths])
    files = [p for p in out.split('\0') if p]
    if not files:
        for base in paths:
            for d, _, fs in os.walk(os.path.join(ROOT, base)):
                files += [os.path.relpath(os.path.join(d, f), ROOT) for f in fs]
    return sorted(p for p in files if os.path.isfile(os.path.join(ROOT, p)))


def load(p, default=None):
    try:
        with open(os.path.join(ROOT, p), encoding='utf-8') as f: return json.load(f)
    except (OSError, ValueError): return default


def month(d): return d[:7] if d else None


def vendor(model):
    m = (model or '').lower()
    if m.endswith(':free'): return 'Free models (US$0)'
    if m.startswith('elevenlabs/'): return 'ElevenLabs voice'
    if m.startswith('google/lyria'): return 'Google Lyria music'
    if m.startswith('google/veo'): return 'Google Veo video'
    if m.startswith('google/') and ('image' in m or 'nano-banana' in m): return 'Google Gemini images'
    if m.startswith('google/'): return 'Google Gemini'
    if m.startswith('bytedance-seed/'): return 'ByteDance Seedream images'
    if m.startswith('anthropic/'): return 'Anthropic Claude'
    if m.startswith('xiaomi/'): return 'Xiaomi MiMo'
    if m.startswith('z-ai/'): return 'Z.ai GLM'
    if m.startswith('openai/'): return 'OpenAI'
    return (m.split('/')[0] or 'not recorded').capitalize()


UNREAD = ('ValueError', 'KeyError')   # agents.ask and scene_agent book US$0 when a reply arrives but cannot be parsed


def basis(c):
    """measured, estimated or unflagged, and why (see the module docstring)."""
    note, seat, model = c.get('note'), c.get('seat'), (c.get('model') or '')
    if model.endswith(':free'): return 'measured', 'free model: nothing to pay'
    if c.get('basis') in ('measured', 'estimated'):   # written by films/lib/spend_log.py
        return c['basis'], 'the provider reported this cost' if c['basis'] == 'measured' else 'priced by our code' + (f" ({c['note']})" if c.get('note') else '')
    if c.get('ok') is False and not (c.get('usd') or 0):
        if note in UNREAD: return 'measured', 'a reply came back but could not be read; the code booked US$0 (the provider may have charged a little)'
        return 'measured', 'the call failed before a reply; nothing was charged'
    if isinstance(note, str) and 'estimated' in note:
        return 'estimated', 'priced from the characters sent (the speech call returns no cost)' if 'characters' in note else 'a fallback price: the provider sent no cost'
    if seat == 'voice' and (model.startswith('elevenlabs/') or str(c.get('task', '')).startswith('vo ')):
        return 'estimated', 'priced from the characters sent (the speech call returns no cost)'
    if note == 'reported': return 'measured', 'the provider reported this cost'
    if seat in ('video', 'music') and 'note' not in c and (c.get('usd') or 0) > 0:
        return 'unflagged', 'the 15 Oct code booked a list price when the provider sent no cost and did not record which this is'
    return 'measured', 'the provider reported this cost (usage.cost)'


# ---------------------------------------------------------------------------------------------- ledgers
def dated_calls(path):
    """[(call, date)] for the ledger at `path`: each call dated (YYYY-MM-DD) by the commit that first recorded it.
    Calls not committed yet get None."""
    final = (load(path) or {}).get('calls') or []
    hist = sh(['git', 'log', '--reverse', '--format=%H %cs', '--', path]).split('\n')
    seen = collections.Counter(); queue = collections.defaultdict(list)
    for line in hist:
        if not line.strip(): continue
        h, d = line.split()
        try: calls = json.loads(sh(['git', 'show', f'{h}:{path}']) or '{}').get('calls') or []
        except ValueError: continue
        now = collections.Counter(json.dumps(c, sort_keys=True) for c in calls)
        for k, n in now.items():
            while seen[k] < n: queue[k].append(d); seen[k] += 1
    used = collections.Counter(); out = []
    for c in final:
        k = json.dumps(c, sort_keys=True); i = used[k]; used[k] += 1
        out.append((c, queue[k][i] if i < len(queue[k]) else None))
    return out


def ledger_lines(path, part=None):
    led = load(path) or {}
    lines = []
    for c, d in dated_calls(path):
        b, why = basis(c); usd = r6(c.get('usd'))
        flags = []
        if c.get('ok') is False and usd > 0: flags.append('failed but charged')
        if c.get('ok') is False and usd == 0 and c.get('note') in UNREAD and not str(c.get('model', '')).endswith(':free'): flags.append('reply unreadable, booked at US$0')
        elif c.get('ok') is False and usd == 0: flags.append('failed, nothing charged')
        if c.get('ok') is not False and usd == 0 and not str(c.get('model', '')).endswith(':free'): flags.append('no cost reported, recorded as US$0')
        lines.append({'kind': 'paid', 'source': path, 'part': part, 'seat': c.get('seat') or 'not recorded', 'model': c.get('model') or 'not recorded',
                      'vendor': vendor(c.get('model')), 'task': clean(c.get('task') or 'not recorded'), 'usd': usd, 'basis': b, 'basis_why': why,
                      'ok': c.get('ok') is not False, 'note': clean(c['note']) if c.get('note') not in (None, 'reported') else None,
                      'seconds': c.get('s'), 'date': (c.get('at') or '')[:10] or d, 'flags': flags})
    return led, lines


def stages_spent(stages):
    """Spend per director stage. Newer status.json files carry "spent" per stage; older ones only a running total
    ("usd"), so the stage's spend is the difference from the stage before it."""
    out, run = [], 0.0
    for k, v in stages.items():
        if 'spent' in v: spent, how = r6(v['spent']), 'status.json "spent"'
        else: spent, how = r6(max(0.0, (v.get('usd') or 0) - run)), 'difference of the running totals in status.json'
        run = max(run, float(v.get('usd') or 0))
        out.append({'stage': k, 'state': v.get('state'), 'spent_usd': spent, 'running_usd': r6(v.get('usd')), 'how': how,
                    'started': v.get('started_at'), 'ended': v.get('ended_at')})
    return out


def paid_summary(lines):
    s = collections.Counter()
    for l in lines:
        s[l['basis']] += l['usd']; s['total'] += l['usd']
        if 'failed but charged' in l['flags']: s['failed'] += l['usd']
    return {'usd': r6(s['total']), 'measured_usd': r6(s['measured']), 'estimated_usd': r6(s['estimated']),
            'unflagged_usd': r6(s['unflagged']), 'failed_charged_usd': r6(s['failed']), 'calls': len(lines),
            'failed_calls': sum(1 for l in lines if not l['ok'])}


# ---------------------------------------------------------------------------------------------- the log
LOG_HEAD = re.compile(r'^## (\d{1,2}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{4})\s*$')
MONTHS = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()
AMOUNT = re.compile(r'(about |around |~)?US\$(\d+(?:\.\d+)?)')
ZERO_TAG = re.compile(r'^(cost |costs )?(US\$0(\.0+)?|free)\.?$', re.I)


def sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.;])\s+(?=[A-Z(`])', text) if s.strip()]


def amounts(sentence):
    out = []
    for m in AMOUNT.finditer(sentence):
        before, after = sentence[max(0, m.start() - 24):m.start()].lower(), sentence[m.end():m.end() + 18].lower()
        kind = 'cap' if re.search(r'\bcaps?\b|limit', before) else 'other' if re.search(r'^\s*(left|expected|per |a |an )|^ to ', after) or 'expected' in before or 'usual' in before else 'spent'
        out.append({'usd': float(m.group(2)), 'kind': kind, 'approx': bool(m.group(1))})
    return out


def film_patterns(f):
    pats = [re.compile(r'(?<![\w/-])' + re.escape(f['id']) + r'(?![\w-])', re.I)]
    if f.get('folder'): pats.append(re.compile(re.escape(f['folder']) + r'(?![\w-])'))
    for a in ALIASES.get(f['id'], []): pats.append(re.compile(r'(?<![\w-])' + re.escape(a) + r'(?![\w-])'))
    return pats


def log_entries(films):
    """{film id: {'lines': [...], 'zero': [dates]}} from docs/LOG.md."""
    pats = {f['id']: film_patterns(f) for f in films}
    out = {f['id']: {'lines': [], 'zero': []} for f in films}
    day = None
    for n, raw in enumerate(open(os.path.join(ROOT, 'docs', 'LOG.md'), encoding='utf-8').read().splitlines(), 1):
        m = LOG_HEAD.match(raw)
        if m: day = f'{m.group(3)}-{MONTHS.index(m.group(2)) + 1:02d}-{int(m.group(1)):02d}'; continue
        if not raw.startswith('- ') or not day: continue
        text = raw[2:]
        named = [fid for fid, ps in pats.items() if any(p.search(text) for p in ps)]
        if not named: continue
        sents = sentences(text)
        if sents and ZERO_TAG.match(sents[-1]):
            for fid in named: out[fid]['zero'].append(day)
        for s in sents:
            am = [a for a in amounts(s) if a['usd'] > 0]
            if not am: continue
            here = [fid for fid in named if any(p.search(s) for p in pats[fid])]
            scope = 'sentence' if here else 'line'      # a figure in a sentence that names no film belongs to the line's films
            for fid in here or named:
                out[fid]['lines'].append({'kind': 'log', 'date': day, 'line': n, 'text': clean(s), 'amounts': am,
                                          'films_named': len(here or named), 'scope': scope})
    for v in out.values(): v['zero'] = sorted(set(v['zero']))
    return out


# ---------------------------------------------------------------------------------------------- runs
def secs(a, b):
    f = lambda s: datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')
    try: return max(0, int((f(b) - f(a)).total_seconds()))
    except (TypeError, ValueError): return 0


def gh_json(path, accept=None):
    args = ['gh', 'api', path] + (['-H', f'Accept: {accept}'] if accept else [])
    r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    if r.returncode: raise RuntimeError((r.stderr or r.stdout).strip()[:200])
    return json.loads(r.stdout)


def fetch_run(repo_short, rid):
    repo = RC if repo_short == 'rc-render' else KF
    run = gh_json(f'repos/{repo}/actions/runs/{rid}')
    jobs, page = [], 1
    while True:
        j = gh_json(f'repos/{repo}/actions/runs/{rid}/jobs?per_page=100&page={page}')
        jobs += j.get('jobs') or []; page += 1
        if len(jobs) >= j.get('total_count', 0) or not j.get('jobs'): break
    return {'id': rid, 'repo': repo, 'workflow': os.path.basename(run.get('path') or '') or run.get('name'), 'name': run.get('name'),
            'event': run.get('event'), 'status': run.get('status'), 'conclusion': run.get('conclusion'),
            'created_at': run.get('created_at'), 'run_started_at': run.get('run_started_at'), 'updated_at': run.get('updated_at'),
            'jobs': [{'name': x.get('name'), 'started_at': x.get('started_at'), 'completed_at': x.get('completed_at'),
                      'conclusion': x.get('conclusion'), 'labels': x.get('labels') or [],
                      'seconds': secs(x.get('started_at'), x.get('completed_at'))} for x in sorted(jobs, key=lambda x: x.get('id') or 0)],
            'fetched': datetime.date.today().isoformat(), 'from': 'gh api actions/runs/<id>/jobs'}


def fetch_run_records():
    """<film id>-run.json records uploaded by rc-render films.yml and remux.yml to release kino-films."""
    rel = gh_json(f'repos/{RC}/releases/tags/kino-films')
    out = []
    for a in rel.get('assets') or []:
        if not a['name'].endswith('-run.json'): continue
        rec = gh_json(f'repos/{RC}/releases/assets/{a["id"]}', accept='application/octet-stream')
        for r in rec.get('runs') or []: out.append((rec.get('film'), r))
    return out


def known_runs():
    """Every run id with its owner: the RUNS table, then director status.json run_url, then "renders" lines with a
    run_id in any ledger (written by films/lib/spend_log.py). {run id: (repo short name, owner id, what, source)}"""
    cat = load(CATALOG) or {'films': []}
    by_folder = {f['folder']: f['id'] for f in cat['films'] if f.get('folder')}
    out = dict(RUNS)
    for p in tracked('films/studio'):
        if p.endswith('/status.json') and '/_' not in p:
            m = re.search(r'github\.com/Eouchi147/([\w-]+)/actions/runs/(\d+)', str((load(p) or {}).get('run_url') or ''))
            fid = by_folder.get(os.path.dirname(p))
            if m and fid: out.setdefault(int(m.group(2)), (m.group(1), fid, 'director job run', p))
    for p in tracked('films', 'ads', 'boards', 'pieces'):
        if not p.endswith('/ledger.json') or '/_' in p: continue
        fid = by_folder.get(os.path.dirname(p))
        for r in (load(p) or {}).get('renders') or []:
            if r.get('where') == 'github' and r.get('run_id') and fid:
                repo = (r.get('repo') or RC).split('/')[-1]
                out.setdefault(int(r['run_id']), (repo, fid, f"{r.get('workflow') or 'render'} (ledger)", p))
    return out


def update_runs(refresh=False):
    store = load(RUNS_FILE, None) or {'about': 'GitHub Actions job times per run, fetched by tools/spend.py --fetch-runs (gh api, read only). Do not edit by hand.', 'runs': {}}
    runs = store['runs']; wanted = {rid: v[0] for rid, v in known_runs().items()}
    got = 0
    for rid, repo in sorted(wanted.items()):
        old = runs.get(str(rid))
        if old and not refresh and old.get('status') == 'completed': continue
        try: runs[str(rid)] = fetch_run(repo, rid); got += 1
        except Exception as e: print(f'spend: run {rid} not fetched: {e}', file=sys.stderr)
    try:
        for film, r in fetch_run_records():
            rid = str(r.get('run_id'))
            if rid in runs and runs[rid].get('from') != 'release record': continue
            runs[rid] = {'id': int(rid), 'repo': r.get('repo'), 'workflow': r.get('workflow'), 'name': r.get('workflow'), 'event': 'workflow_dispatch',
                         'status': 'completed', 'conclusion': r.get('conclusion') or 'recorded at the join', 'created_at': r.get('started'),
                         'run_started_at': r.get('started'), 'updated_at': r.get('ended'), 'film': film,
                         'jobs': [{k: j.get(k) for k in ('name', 'started_at', 'completed_at', 'conclusion', 'labels', 'seconds')} for j in r.get('jobs') or []],
                         'fetched': datetime.date.today().isoformat(), 'from': 'release record'}
            got += 1
    except Exception as e:
        print(f'spend: release records not read: {e}', file=sys.stderr)
    store['runs'] = dict(sorted(runs.items()))
    os.makedirs(os.path.dirname(RUNS_FILE), exist_ok=True)
    with open(RUNS_FILE, 'w', encoding='utf-8') as f: f.write(json.dumps(store, indent=1, ensure_ascii=False) + '\n')
    print(f'spend: {got} run(s) fetched, {len(runs)} stored in {os.path.relpath(RUNS_FILE, ROOT)}')


def run_line(run, what, source):
    jobs = [j for j in run.get('jobs') or [] if j.get('started_at') and j.get('seconds')]
    s = sum(j['seconds'] for j in jobs); bill = sum(math.ceil(j['seconds'] / 60) for j in jobs)
    labels = sorted({l for j in jobs for l in j.get('labels') or []})
    return {'kind': 'runner', 'repo': run.get('repo'), 'run_id': run['id'], 'workflow': run.get('workflow'), 'what': clean(what),
            'conclusion': run.get('conclusion'), 'started': run.get('run_started_at') or run.get('created_at'), 'ended': run.get('updated_at'),
            'date': (run.get('run_started_at') or run.get('created_at') or '')[:10] or None, 'jobs': len(jobs), 'seconds': s,
            'minutes_billable': bill, 'worth_usd': r6(bill * RATES['runner_usd_per_min']['value']), 'runner': ', '.join(labels) or 'not recorded',
            'source': source, 'url': f"https://github.com/{run.get('repo')}/actions/runs/{run['id']}"}


def runs_by_owner():
    store = (load(RUNS_FILE, None) or {}).get('runs') or {}
    owner = collections.defaultdict(list); missing = []
    keys = {str(k): v for k, v in known_runs().items()}
    for rid in sorted(set(keys) | set(store)):
        run = store.get(rid)
        if rid in keys: _, who, what, src = keys[rid]
        elif run and run.get('film'): who, what, src = run['film'], f"{run.get('workflow')} (release record)", 'rc-render release kino-films, <id>-run.json'
        else: continue
        if not run: missing.append((who, int(rid), what, src)); continue
        owner[who].append(run_line(run, what, src))
    return owner, missing


# ---------------------------------------------------------------------------------------------- the Mac lane
def mac():
    """{owner: {'render': [...rows], 'checks': [...rows]}} from data/spend/mac-lane-jobs.csv."""
    out = collections.defaultdict(lambda: {'render': [], 'checks': []})
    if not os.path.exists(MAC_CSV): return out, 0
    rows = list(csv.DictReader(open(MAC_CSV, encoding='utf-8')))
    seen = {(r['film'].rstrip('/'), r['job']) for r in rows}
    for p in tracked('films'):     # Mac renders written by films/lib/spend_log.py, unless the job is already in the CSV
        if not p.endswith('/ledger.json') or '/_' in p: continue
        for x in (load(p) or {}).get('renders') or []:
            folder = os.path.dirname(p); job = x.get('job') or f"ledger-{x.get('at')}"
            if x.get('where') != 'mac' or not x.get('seconds') or (folder, job) in seen: continue
            at = datetime.datetime.strptime(x['at'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc).timestamp() if x.get('at') else ''
            rows.append({'home': 'ledger', 'job': job, 'film': folder, 'start': '', 'end': '', 'frames_saved': x.get('frames') or 0,
                         'w': x.get('w') or '', 'h': x.get('h') or '', 'samples': x.get('samples') or '', 'exit': '0', 'seconds': x['seconds'], 'log_mtime': at})
    for r in rows:
        folder, job = r['film'].rstrip('/'), r['job']
        if folder.startswith('films/cutaway/looks/') or job.startswith('1-seasons-base'):
            look = folder.rsplit('/', 1)[-1] if folder.startswith('films/cutaway/looks/') else 'seasons-base'
            out['mac-look-boards']['render'].append(dict(r, look=look)); continue
        if 'drive-test' in job: out['mac-lane-checks']['checks'].append(r); continue
        fid = MAC_FILM.get(folder) or ('cutaway-series-' + folder.rsplit('/', 1)[-1] if folder.startswith('films/cutaway/series/') else None)
        if not fid: out['mac-lane-checks']['checks'].append(r); continue
        out[fid]['render' if re.search(r'-c\d+$', job) else 'checks'].append(r)
    return out, len(rows)


def kwh(seconds): return seconds * RATES['mac_watts']['value'] / 3.6e6


def mac_summary(rows, what):
    s = round(sum(float(r['seconds'] or 0) for r in rows), 1)
    k = kwh(s)
    dates = sorted({datetime.datetime.fromtimestamp(float(r['log_mtime']), datetime.timezone.utc).strftime('%Y-%m-%d') for r in rows if r.get('log_mtime')})
    return {'kind': 'mac', 'what': what, 'jobs': len(rows), 'frames': sum(int(r['frames_saved'] or 0) for r in rows), 'seconds': s,
            'size': sorted({f"{r['w']}x{r['h']}, {r['samples']} samples" for r in rows if r.get('w')}), 'kwh': round(k, 4),
            'electricity_cad': round(k * RATES['kwh_cad']['value'], 4), 'basis': 'estimated', 'dates': dates,
            'failed': sum(1 for r in rows if str(r.get('exit')) not in ('0', '')), 'source': 'data/spend/mac-lane-jobs.csv'}


# ---------------------------------------------------------------------------------------------- build
def compute_block(runs, macs):
    rs = sorted(runs, key=lambda x: (x['started'] or '', x['run_id']))
    return {'runner': {'runs': rs, 'seconds': sum(r['seconds'] for r in rs), 'minutes_billable': sum(r['minutes_billable'] for r in rs),
                       'worth_usd': r6(sum(r['worth_usd'] for r in rs)), 'paid_usd': 0},
            'mac': {'lines': macs, 'seconds': round(sum(m['seconds'] for m in macs), 1), 'kwh': round(sum(m['kwh'] for m in macs), 4),
                    'electricity_cad': round(sum(m['electricity_cad'] for m in macs), 4)}}


def build():
    epoch = os.environ.get('SOURCE_DATE_EPOCH')
    now = datetime.datetime.fromtimestamp(int(epoch), datetime.timezone.utc) if epoch else datetime.datetime.now(datetime.timezone.utc)
    cat = load(CATALOG) or {'films': []}
    films = cat['films']
    by_folder = {f['folder']: f['id'] for f in films if f.get('folder')}
    ledgers = [p for p in tracked('films', 'ads', 'boards', 'pieces') if p.endswith('/ledger.json') and '/_' not in p and '/tests/' not in p]
    owned = collections.defaultdict(list)       # owner id -> [(path, part)]
    other_meta = {}
    for p in ledgers:
        folder = os.path.dirname(p)
        fid = by_folder.get(folder)
        if fid: owned[fid].append((p, None)); continue
        hit = next((f for f, bs in BOARDS_OF.items() if folder in bs), None)
        if hit: owned[hit].append((p, f'footage board {os.path.basename(folder)}')); continue
        base = next((b for b in OTHER_KINDS if folder.startswith(b + '/')), None)
        key = folder.replace('/', '-')
        kind, label = OTHER_KINDS.get(base, ('other', 'Other paid work'))
        other_meta[key] = (kind, f"{label}: {os.path.basename(folder)}", folder)
        owned[key].append((p, None))
    runs, missing_runs = runs_by_owner()
    macs, mac_rows = mac()
    logs = log_entries(films)

    entries = []
    def entry(eid, title, kind, folder, series=None, status=None):
        paid_lines, cap, cross, director = [], None, [], None
        for p, part in sorted(owned.get(eid, [])):
            led, lines = ledger_lines(p, part)
            paid_lines += lines
            if part is None and led.get('cap') is not None: cap = led.get('cap')
            acc = load(os.path.join(os.path.dirname(p), 'account.json'))
            if acc and acc.get('board_spent') is not None:
                cross.append({'source': os.path.join(os.path.dirname(p), 'account.json'), 'account_usd': r6(acc['board_spent']), 'ledger_usd': r6(acc.get('ledger_total')),
                              'note': 'the OpenRouter key usage before and after the board; it lags by hours and boards run in parallel share it, so the ledger lines are the figure'})
        if folder and folder.startswith('films/studio/'):
            st, br = load(f'{folder}/status.json'), load(f'{folder}/brief.json')
            if st or br:
                director = {'state': (st or {}).get('state'), 'stage': (st or {}).get('stage'), 'usd': r6((st or {}).get('usd')),
                            'cap_usd': (st or {}).get('cap_usd', (br or {}).get('cap_usd')),
                            'stages': stages_spent((st or {}).get('stages') or {}),
                            'message': clean((st or {}).get('message') or '')[:240] or None, 'source': f'{folder}/status.json'}
                if cap is None: cap = director['cap_usd']
        if cap is None and folder and os.path.exists(os.path.join(ROOT, folder, 'ad.json')):
            cap = (load(f'{folder}/ad.json') or {}).get('cap_usd')
        lg = logs.get(eid, {'lines': [], 'zero': []})
        log_lines, log_counted = [], 0.0
        for l in lg['lines']:
            spent = [a for a in l['amounts'] if a['kind'] == 'spent']
            if paid_lines: role, why = 'cross-check', 'a ledger exists: the log figure is shown, not added'
            elif l['films_named'] > 1: role, why = 'shared', f"one figure for {l['films_named']} films named in the same {l['scope']}: not split, not added"
            elif not spent: role, why = 'mention', 'a cap, a balance or an expected figure, not a spend'
            else: role, why = 'counted', 'no ledger for this film: the log is the only record'
            if role == 'counted': log_counted += sum(a['usd'] for a in spent)
            log_lines.append(dict(l, role=role, why=why))
        pay = paid_summary(paid_lines)
        comp = compute_block(runs.get(eid, []), [mac_summary(v, w) for v, w in ((macs[eid]['render'], 'render'), (macs[eid]['checks'], 'check stills')) if v] if eid in macs else [])
        if eid == 'mac-look-boards':
            looks = collections.defaultdict(list)
            for r in macs[eid]['render']: looks[r['look']].append(r)
            comp['mac']['lines'] = [mac_summary(v, f'look board {k}') for k, v in sorted(looks.items())]
        not_rec = []
        if not paid_lines and not log_counted and eid in by_folder.values():
            not_rec.append('paid calls: no ledger for this film' + (' (the log marks its changes US$0)' if lg['zero'] else ''))
        if not comp['runner']['runs'] and kind in ('film', 'director-job', 'board', 'piece', 'showcase'):
            not_rec.append({'film': 'GitHub runner time: no run id written down for this film', 'director-job': 'GitHub runner time: no run recorded'}.get(kind, 'GitHub runner time of the workflow that made it: no run id written down'))
        for who, rid, what, src in missing_runs:
            if who == eid: not_rec.append(f'run {rid} ({what}) named in {src}, its job times not fetched yet (python3 tools/spend.py --fetch-runs)')
        if kind == 'film' and folder and folder.startswith('films/cutaway/') and eid not in macs:
            not_rec.append('Mac lane: no job of this film in the exported job logs')
        if paid_lines and any(l['basis'] == 'unflagged' for l in paid_lines):
            not_rec.append('some paid lines are not flagged measured or estimated (15 Oct code)')
        unread = sum(1 for l in paid_lines if 'reply unreadable, booked at US$0' in l['flags'])
        if unread: not_rec.append(f'{unread} paid call(s) whose reply could not be read were booked at US$0; the provider may have charged a little for each')
        total = r6(pay['usd'] + log_counted)
        rec = {'paid': bool(paid_lines), 'log': bool(lg['lines'] or lg['zero']), 'runner': bool(comp['runner']['runs']), 'mac': bool(comp['mac']['lines'])}
        entries.append({
            'id': eid, 'title': title, 'kind': kind, 'folder': folder, 'series': series, 'status': status,
            'total': {'paid_usd': total, 'measured_usd': pay['measured_usd'], 'estimated_usd': pay['estimated_usd'], 'unflagged_usd': pay['unflagged_usd'],
                      'log_usd': r6(log_counted), 'failed_charged_usd': pay['failed_charged_usd'], 'calls': pay['calls'], 'failed_calls': pay['failed_calls'],
                      'cap_usd': cap, 'runner_minutes': comp['runner']['minutes_billable'], 'runner_seconds': comp['runner']['seconds'],
                      'runner_worth_usd': comp['runner']['worth_usd'], 'mac_seconds': comp['mac']['seconds'], 'mac_kwh': comp['mac']['kwh'],
                      'electricity_cad': comp['mac']['electricity_cad']},
            'record': rec, 'paid': paid_lines, 'director': director, 'cross_checks': cross, 'log': log_lines, 'log_zero': lg['zero'],
            'compute': comp, 'not_recorded': not_rec,
        })

    for f in films:
        kind = 'director-job' if (f.get('folder') or '').startswith('films/studio/') and os.path.exists(os.path.join(ROOT, f['folder'], 'brief.json')) else 'film'
        entry(f['id'], f['title'], kind, f.get('folder'), f.get('series'), f.get('status'))
    film_ids = {f['id'] for f in films}
    for key in sorted(set(other_meta) | {k for k in runs if k not in film_ids} | {k for k in macs if k not in film_ids}):
        kind, title, folder = other_meta.get(key, ('shared' if key.startswith('shared') else 'mac', OTHER_TITLES.get(key, key), None))
        entry(key, title, kind, folder)

    return {'generated': now.strftime('%Y-%m-%dT%H:%M:%SZ'), 'currency': 'USD (electricity in CAD)', 'rates': RATES,
            'how': HOW, 'entries': sorted(entries, key=lambda e: (e['kind'] not in ('film', 'director-job'), e['id'])),
            'totals': totals(entries, mac_rows), 'sources': sources(ledgers)}


HOW = [
    'Paid: every call our code made to a paid model, from the ledger.json files the pipelines commit. Measured means the provider reported the cost; estimated means our code priced it (speech by the characters sent, a fallback price); not flagged means old code that did not record which.',
    'A failed call that still cost money is kept and flagged. Free models cost US$0.',
    'The log: sentences in docs/LOG.md with a US$ figure and the film\'s name. When a ledger exists the log figure is only a cross-check, never added.',
    'GitHub runners: the job times of every run written down for the film, rounded up to whole minutes per job as GitHub bills them. Free on public repos; worth is the list price for the same jobs in a private repo.',
    'Mac lane: render time from the job logs on the drive, with an electricity estimate from an assumed wattage and an assumed price per kWh (both marked as not verified).',
    'Not recorded means nothing was written down. Nothing here is a guess presented as a fact.',
]


def totals(entries, mac_rows):
    T = collections.Counter(); month_paid = collections.Counter(); month_run = collections.Counter(); month_mac = collections.Counter()
    vend = collections.defaultdict(collections.Counter); seat = collections.defaultdict(collections.Counter)
    for e in entries:
        t = e['total']; scope = 'films' if e['kind'] in ('film', 'director-job') else 'other'
        for k in ('paid_usd', 'measured_usd', 'estimated_usd', 'unflagged_usd', 'log_usd', 'failed_charged_usd', 'runner_minutes', 'runner_seconds',
                  'runner_worth_usd', 'mac_seconds', 'mac_kwh', 'electricity_cad', 'calls', 'failed_calls'):
            T[k] += t[k]; T[f'{scope}_{k}'] += t[k]
        for l in e['paid']:
            month_paid[month(l['date']) or 'not dated'] += l['usd']
            v = vend[l['vendor']]; v['usd'] += l['usd']; v['calls'] += 1; v[l['basis']] += l['usd']
            s = seat[l['seat']]; s['usd'] += l['usd']; s['calls'] += 1
        for r in e['compute']['runner']['runs']: month_run[month(r['date']) or 'not dated'] += r['minutes_billable']
        for m in e['compute']['mac']['lines']:
            for d in m['dates'][:1]: month_mac[month(d)] += m['seconds']
    months = sorted(set(month_paid) | set(month_run) | set(month_mac), key=lambda m: (m == 'not dated', m))
    films = [e for e in entries if e['kind'] in ('film', 'director-job')]
    rank = sorted(films, key=lambda e: (-e['total']['paid_usd'], -e['total']['runner_worth_usd'], e['id']))
    return {
        'paid_usd': r6(T['paid_usd']), 'measured_usd': r6(T['measured_usd']), 'estimated_usd': r6(T['estimated_usd']),
        'unflagged_usd': r6(T['unflagged_usd']), 'log_usd': r6(T['log_usd']), 'failed_charged_usd': r6(T['failed_charged_usd']),
        'calls': T['calls'], 'failed_calls': T['failed_calls'],
        'films_paid_usd': r6(T['films_paid_usd']), 'other_paid_usd': r6(T['other_paid_usd']),
        'runner_minutes': T['runner_minutes'], 'runner_seconds': T['runner_seconds'], 'runner_worth_usd': r6(T['runner_worth_usd']),
        'runner_runs': sum(len(e['compute']['runner']['runs']) for e in entries),
        'mac_seconds': round(T['mac_seconds'], 1), 'mac_jobs': mac_rows, 'mac_kwh': round(T['mac_kwh'], 4), 'electricity_cad': round(T['electricity_cad'], 4),
        'by_month': [{'month': m, 'paid_usd': r6(month_paid[m]), 'runner_minutes': month_run[m], 'mac_seconds': round(month_mac[m], 1)} for m in months],
        'by_vendor': sorted([{'vendor': k, 'usd': r6(v['usd']), 'calls': v['calls'], 'measured_usd': r6(v['measured']), 'estimated_usd': r6(v['estimated']),
                              'unflagged_usd': r6(v['unflagged'])} for k, v in vend.items()], key=lambda x: (-x['usd'], x['vendor'])),
        'by_seat': sorted([{'seat': k, 'usd': r6(v['usd']), 'calls': v['calls']} for k, v in seat.items()], key=lambda x: (-x['usd'], x['seat'])),
        'top_films': [{'id': e['id'], 'title': e['title'], 'paid_usd': e['total']['paid_usd'], 'runner_minutes': e['total']['runner_minutes'],
                       'runner_worth_usd': e['total']['runner_worth_usd'], 'mac_seconds': e['total']['mac_seconds']} for e in rank if e['total']['paid_usd'] > 0][:12],
        'no_record': [{'id': e['id'], 'title': e['title']} for e in sorted(films, key=lambda e: e['id']) if not any(e['record'].values())],
        'no_paid_record': [{'id': e['id'], 'title': e['title'], 'log_zero': bool(e['log_zero'])} for e in sorted(films, key=lambda e: e['id']) if not e['record']['paid'] and not e['total']['log_usd']],
        'other': [{'id': e['id'], 'title': e['title'], 'kind': e['kind'], 'paid_usd': e['total']['paid_usd'], 'runner_minutes': e['total']['runner_minutes'],
                   'mac_seconds': e['total']['mac_seconds']} for e in sorted(entries, key=lambda e: (-e['total']['paid_usd'], e['id'])) if e['kind'] not in ('film', 'director-job')],
    }


def sources(ledgers):
    return {'ledgers': ledgers, 'runs': os.path.relpath(RUNS_FILE, ROOT), 'mac': os.path.relpath(MAC_CSV, ROOT), 'log': 'docs/LOG.md',
            'catalog': os.path.relpath(CATALOG, ROOT), 'tool': 'tools/spend.py'}


def main(argv):
    if '--fetch-runs' in argv or '--refresh-runs' in argv: update_runs(refresh='--refresh-runs' in argv)
    data = build()
    text = json.dumps(data, indent=1, ensure_ascii=False, sort_keys=False) + '\n'
    bad = [m.group(0) for m in BAD.finditer(text)]
    if bad: print(f'spend: house style broken ({len(bad)} dash or three dots); fix the words in tools/spend.py'); return 1
    if '--stdout' in argv: sys.stdout.write(text); return 0
    if '--check' in argv:
        old = load(OUT, {})
        same = {k: v for k, v in old.items() if k != 'generated'} == {k: v for k, v in json.loads(text).items() if k != 'generated'}
        print('spend: up to date' if same else 'spend: out of date, run python3 tools/spend.py'); return 0 if same else 1
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f: f.write(text)
    t = data['totals']
    print(f"spend: {len(data['entries'])} entries; paid US${t['paid_usd']:.2f} (measured {t['measured_usd']:.2f}, estimated {t['estimated_usd']:.2f}, "
          f"not flagged {t['unflagged_usd']:.2f}); runners {t['runner_minutes']} min in {t['runner_runs']} runs (worth US${t['runner_worth_usd']:.2f}); "
          f"Mac {t['mac_seconds'] / 3600:.1f} h (about CA${t['electricity_cad']:.2f}) -> {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
