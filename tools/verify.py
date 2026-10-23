#!/usr/bin/env python3
"""verify.py: every KINOFORGE gate in one command. Run it before you commit, before you push, before you say "done".

    bash tools/verify.sh                 fast gates (about 1 min, no browser, no network, no money)
    bash tools/verify.sh --full          fast gates + the director tests in Chromium, check.cjs on every Battle Map film,
                                         the score engine selftest (about 8 to 10 min)
    bash tools/verify.sh --only text,docs    some gates only (names below)
    bash tools/verify.sh --since <ref>   docs gate: judge the commits after <ref> (default: what is not yet on origin/main)
    bash tools/verify.sh --list          list the gates

Exit 0 = every gate passed. Exit 1 = at least one FAIL (each FAIL says how to fix it). Warnings never fail.
Known exceptions live in ONE file, tools/verify-allow.txt (gate, path pattern, reason). Do not add an exception to get
a green run: fix the thing. An exception is for frozen legacy work only, with the reason written down.

The gates (docs/MEMORY.md explains the house rules they enforce):
  secrets    no API keys, tokens or private keys in tracked files
  json       every tracked .json parses
  syntax     every tracked .py compiles; every .js/.mjs/.cjs passes node --check (studio-web is built by Vercel instead)
  text       house style for words on screen and in narration: no em dash, no en dash, no "..." or the ellipsis character
             (JSON on-screen fields, string literals in film and ad code, Python strings in Blender films)
  prompts    AI image or video prompts never ask for words, logos or numbers (they are set in code)
  battlemap  films/lib/battlemap/tools/scenes.mjs on every Battle Map film (scene plan, camera speed, shot count, jump cuts)
  social     social/lib/check.mjs on every batch, and the social lane's unit tests
  director   the director's tests that need no browser (Fast)
  workflows  a workflow that installs Playwright runs on ubuntu-24.04 (Playwright 1.56 does not install on ubuntu-latest)
  docs       a change to code or films comes with a docs/LOG.md line (or, for one film folder, its NOTES.md); LOG.md keeps
             its newest-first dated headings
 full only:
  director-full  every director test, including the spec stage in Chromium
  check          films/director/check.cjs on every Battle Map film (loads it in Chromium, renders stills, craft checks)
  score          films/lib/score/selftest.py (needs numpy, scipy, soundfile)
"""
import ast, concurrent.futures as cf, fnmatch, json, os, re, subprocess, sys, tempfile, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ALLOW_FILE = os.path.join(ROOT, 'tools', 'verify-allow.txt')
FAST = ['secrets', 'json', 'syntax', 'workflows', 'text', 'prompts', 'battlemap', 'social', 'director', 'docs']
FULL = FAST[:-2] + ['director-full', 'check', 'score', 'docs']
BAD_TEXT = re.compile('[–—…]|\\.\\.\\.')
BINARY = re.compile(r'\.(png|jpe?g|webp|gif|mp3|m4a|wav|ogg|flac|mp4|webm|mov|ttf|otf|woff2?|glb|gltf|blend|npz|npy|bin|zip|tgz|gz|pdf|ico|exr|hdr)$', re.I)


def sh(cmd, **kw):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, **kw)


def tracked(*paths):
    out = sh(['git', 'ls-files', '-z', '--', *paths]).stdout
    return [p for p in out.split('\0') if p and os.path.isfile(os.path.join(ROOT, p))]


# ------------------------------------------------------------------ the allowlist (one file, every exception with a reason)
class Allow:
    def __init__(self):
        self.rules, self.used = [], set()
        if os.path.exists(ALLOW_FILE):
            for n, line in enumerate(open(ALLOW_FILE, encoding='utf-8'), 1):
                body = line.split('#', 1)[0].strip()
                if not body: continue
                gate, pat = body.split(None, 1)
                if '#' not in line: raise SystemExit(f'tools/verify-allow.txt line {n}: every exception needs a reason after "#"')
                self.rules.append((gate, pat.strip(), n))

    def ok(self, gate, path):
        for g, pat, n in self.rules:
            if g == gate and fnmatch.fnmatch(path, pat): self.used.add(n); return True
        return False

    def unused(self, gates):
        # the docs gate only sees the current change set, so its exceptions are often idle: never report those
        return [(g, p, n) for g, p, n in self.rules if n not in self.used and g in gates and g != 'docs']


ALLOW = Allow()


class Gate:
    def __init__(self, name):
        self.name, self.fails, self.warns, self.n, self.t0 = name, [], [], 0, time.time()

    def fail(self, where, what, fix):
        self.fails.append(f'{where}: {what}\n      how to fix: {fix}')

    def warn(self, msg):
        self.warns.append(msg)


# ------------------------------------------------------------------ secrets
SECRET_RES = [
    (re.compile(r'sk-or-v1-[0-9a-f]{20,}'), 'OpenRouter key'),
    (re.compile(r'\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{32,}'), 'OpenAI or Anthropic style key'),
    (re.compile(r'\bgh[pousr]_[A-Za-z0-9]{30,}'), 'GitHub token'),
    (re.compile(r'\bgithub_pat_[A-Za-z0-9_]{40,}'), 'GitHub fine-grained token'),
    (re.compile(r'\bAKIA[0-9A-Z]{16}\b'), 'AWS access key'),
    (re.compile(r'\bAIza[0-9A-Za-z_-]{35}\b'), 'Google API key'),
    (re.compile(r'\bxox[abprs]-[0-9A-Za-z-]{10,}'), 'Slack token'),
    (re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'), 'private key'),
]


def g_secrets(g):
    for p in tracked():
        if BINARY.search(p) or p == 'tools/verify.py': continue
        try:
            if os.path.getsize(os.path.join(ROOT, p)) > 3_000_000: continue
            s = open(os.path.join(ROOT, p), encoding='utf-8', errors='ignore').read()
        except OSError: continue
        g.n += 1
        for rx, what in SECRET_RES:
            m = rx.search(s)
            if m and not ALLOW.ok('secrets', p):
                line = s.count('\n', 0, m.start()) + 1
                g.fail(f'{p}:{line}', f'looks like a {what}', 'remove it from the file AND from git history, then ask Sam to revoke the key. '
                       'Keys live only in GitHub or Vercel secrets, added by Sam. Never handle keys.')


# ------------------------------------------------------------------ json
def g_json(g):
    for p in tracked('*.json'):
        if 'node_modules/' in p: continue
        g.n += 1
        try: json.load(open(os.path.join(ROOT, p), encoding='utf-8'))
        except Exception as e:
            if not ALLOW.ok('json', p): g.fail(p, f'not valid JSON ({e})', 'fix the syntax (trailing comma, missing quote); python3 -m json.tool <file> shows where')


# ------------------------------------------------------------------ syntax
def g_syntax(g):
    for p in tracked('*.py'):
        g.n += 1
        try: compile(open(os.path.join(ROOT, p), encoding='utf-8').read(), p, 'exec')
        except SyntaxError as e:
            if not ALLOW.ok('syntax', p): g.fail(f'{p}:{e.lineno}', f'Python syntax error: {e.msg}', 'fix the line; python3 -m py_compile <file> to re-check')
    js = [p for p in tracked('*.js', '*.mjs', '*.cjs') if not p.startswith('studio-web/') and 'node_modules/' not in p]

    def one(p):
        r = sh(['node', '--check', p]); return p, r.returncode, (r.stderr or '').strip().splitlines()
    with cf.ThreadPoolExecutor(8) as ex:
        for p, code, err in ex.map(one, js):
            g.n += 1
            if code and not ALLOW.ok('syntax', p):
                msg = next((l for l in err if 'Error' in l), err[-1] if err else 'node --check failed')
                g.fail(p, f'JavaScript syntax error: {msg}', f'node --check {p} shows the line')


# ------------------------------------------------------------------ workflows
def g_workflows(g):
    for p in tracked('.github/workflows'):
        if not p.endswith(('.yml', '.yaml')): continue
        g.n += 1; s = open(os.path.join(ROOT, p), encoding='utf-8').read()
        if 'playwright' in s and re.search(r'runs-on:\s*ubuntu-latest', s) and not ALLOW.ok('workflows', p):
            g.fail(p, 'installs Playwright on ubuntu-latest', 'use runs-on: ubuntu-24.04 (Playwright 1.56 cannot install on the newer image; seen 22 Oct 2026)')
        if '\t' in s: g.fail(p, 'a tab character in YAML', 'indent with spaces')


# ------------------------------------------------------------------ text (house style for on-screen and spoken words)
# JSON keys whose values are never on screen or spoken (fact checks, notes, prompts, reasons, logs).
TEXT_SKIP_KEYS = {'_', 'claim', 'claims', 'reason', 'correction', 'verdicts', 'note', 'notes', 'prompt', 'why', 'job', 'music',
                  'description', 'listen', 'source', 'sources', 'log', 'message', 'brief', 'voice_brief', 'music_prompt',
                  'picture', 'checks', 'problems', 'fixes', 'words', 'comment', 'transcript', 'stages', 'outputs', 'run_url', 'heard', 'asr', 'recognized'}
TEXT_JSON = re.compile(r'(^|/)(cues|ad|script|film|batch|brief|board|card|cards|captions|vo|dialogue)\.json$')
CONTENT_DIRS = ('films/battles/', 'films/dark-corners/', 'films/noor/', 'films/cutaway/', 'films/studio/', 'films/styles/',
                'ads/', 'social/templates/', 'social/batches/', 'social/clients/')
CONTENT_SKIP = ('ads/lib/', 'ads/fonts/')


def js_strings(src):
    """String literals of a JS file (comments skipped; ${...} removed from template literals). Yields (offset, text)."""
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c == '/' and src.startswith('//', i): j = src.find('\n', i); i = n if j < 0 else j; continue
        if c == '/' and src.startswith('/*', i): j = src.find('*/', i + 2); i = n if j < 0 else j + 2; continue
        if c in '\'"`':
            j = i + 1
            while j < n and src[j] != c:
                if src[j] == '\\': j += 1
                elif src[j] == '\n' and c != '`': break
                j += 1
            s = src[i + 1:j]
            if c == '`': s = re.sub(r'\$\{[^}]*\}', '', s)
            yield i, s; i = j + 1; continue
        i += 1


def py_strings(src):
    tree = ast.parse(src); docs = set()
    for node in ast.walk(tree):
        body = getattr(node, 'body', None)
        if isinstance(body, list) and body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant): docs.add(id(body[0].value))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docs: yield node.lineno, node.value


def g_text(g):
    fix = 'rewrite the words: a comma, a colon, "to" for ranges (600 to 800) or a new sentence instead of a dash; a full stop instead of "..."'

    def walk(v, path, p):
        if isinstance(v, dict):
            for k, x in v.items():
                if k not in TEXT_SKIP_KEYS: walk(x, f'{path}.{k}', p)
        elif isinstance(v, list):
            for i, x in enumerate(v): walk(x, f'{path}[{i}]', p)
        elif isinstance(v, str) and BAD_TEXT.search(v) and not ALLOW.ok('text', p):
            g.fail(f'{p} {path or "(root)"}', f'dash or "..." in words that reach the screen or the voice: {v[:80]!r}', fix)

    for p in tracked('films', 'ads', 'social', 'boards', 'pieces'):
        if p.endswith('.json') and TEXT_JSON.search(p):
            g.n += 1
            try: walk(json.load(open(os.path.join(ROOT, p), encoding='utf-8')), '', p)
            except ValueError: pass   # the json gate reports it
        if not p.startswith(CONTENT_DIRS) or p.startswith(CONTENT_SKIP): continue
        if re.search(r'\.(m?js|html)$', p):
            g.n += 1; src = open(os.path.join(ROOT, p), encoding='utf-8', errors='replace').read()
            for off, s in js_strings(src):
                if BAD_TEXT.search(s) and not ALLOW.ok('text', p):
                    g.fail(f'{p}:{src.count(chr(10), 0, off) + 1}', f'dash or "..." in a string: {s[:80]!r}', fix)
        elif p.endswith('.py'):
            g.n += 1
            try: strings = list(py_strings(open(os.path.join(ROOT, p), encoding='utf-8').read()))
            except SyntaxError: continue   # the syntax gate reports it
            for line, s in strings:
                if BAD_TEXT.search(s) and not ALLOW.ok('text', p):
                    g.fail(f'{p}:{line}', f'dash or "..." in a string: {s[:80]!r}', fix + ' (comments and docstrings are fine)')


# ------------------------------------------------------------------ prompts (words, logos and numbers are set in code)
PROMPT_KEYS = {'prompt', 'image_prompt', 'video_prompt', 'still_prompt'}
ASKS_TEXT = re.compile(r'\b(that says|saying|which reads|lettering|written on|inscription|logo|wordmark|typography|headline|caption|signage|text)\b', re.I)
NEGATED = re.compile(r'\b(no|without|never|not|zero|free of|avoid)\b[^.;:]{0,40}$', re.I)


def g_prompts(g):
    def walk(v, key, p):
        if isinstance(v, dict):
            for k, x in v.items(): walk(x, k, p)
        elif isinstance(v, list):
            for x in v: walk(x, key, p)
        elif isinstance(v, str) and key in PROMPT_KEYS:
            g.n += 1
            for m in ASKS_TEXT.finditer(v):
                if not NEGATED.search(v[max(0, m.start() - 60):m.start()]) and not ALLOW.ok('prompts', p):
                    g.fail(p, f'an AI prompt mentions "{m.group(0)}" without forbidding it: ...{v[max(0, m.start() - 50):m.end() + 20]!r}',
                           'AI images and video never carry words, logos or numbers: say "no text, no logos" in the prompt and set the words in code over the picture'); break
    for p in tracked('boards', 'pieces', 'films', 'ads', 'social'):
        if p.endswith('.json'):
            try: walk(json.load(open(os.path.join(ROOT, p), encoding='utf-8')), '', p)
            except ValueError: pass


# ------------------------------------------------------------------ battlemap (scene plan checks, no browser)
def battle_map_films():
    out = []
    for p in tracked('films'):
        if not p.endswith('/spec.js') or '/tests/' in p: continue
        d = os.path.dirname(p)
        if not os.path.exists(os.path.join(ROOT, d, 'cues.json')): continue
        line = ''
        for f in ('film.json', 'brief.json'):
            try: line = line or json.load(open(os.path.join(ROOT, d, f))).get('line', '')
            except Exception: pass
        style = ''
        try: style = json.load(open(os.path.join(ROOT, d, 'film.json'))).get('style', '')
        except Exception: pass
        if d.startswith('films/battles/') or line == 'battle-map' or style == 'terrain': out.append(d)
    return sorted(set(out))


def g_battlemap(g):
    for d in battle_map_films():
        g.n += 1
        r = sh(['node', 'films/lib/battlemap/tools/scenes.mjs', d])
        if r.returncode and not ALLOW.ok('battlemap', d):
            errs = [l.strip() for l in (r.stdout + r.stderr).splitlines() if re.search(r'error|Error|ERROR', l)][:6]
            g.fail(d, 'Battle Map scene checks failed: ' + ' | '.join(errs or ['exit code %d' % r.returncode]),
                   f'node films/lib/battlemap/tools/scenes.mjs {d} prints the plan and every error; films/lib/battlemap/SPEC.md section 11 says how to plan scenes and shots')
        elif 'warning' in r.stdout.lower():
            n = len([l for l in r.stdout.splitlines() if 'warning' in l.lower()])
            if n: g.warn(f'{d}: {n} scene warning line(s); read them with scenes.mjs')


# ------------------------------------------------------------------ social
def g_social(g):
    for p in tracked('social/batches'):
        if p.endswith('/batch.json'):
            d = os.path.dirname(p); g.n += 1
            r = sh(['node', 'social/lib/check.mjs', d])
            if r.returncode and not ALLOW.ok('social', d):
                g.fail(d, 'social batch check failed: ' + ' | '.join((r.stdout + r.stderr).strip().splitlines()[-4:]), f'node social/lib/check.mjs {d}; rules in social/README.md')
    if os.path.exists(os.path.join(ROOT, 'social/lib/social.test.mjs')):
        g.n += 1; r = sh(['node', '--test', 'social/lib/social.test.mjs'])
        if r.returncode: g.fail('social/lib/social.test.mjs', 'unit tests fail', 'node --test social/lib/social.test.mjs shows which')


# ------------------------------------------------------------------ director
def run_director_tests(g, which):
    env = dict(os.environ); env.pop('OPENROUTER_API_KEY', None); env.pop('KF_COMMIT', None)
    cmd = [sys.executable, 'films/director/tests/test_director.py'] + ([which] if which else [])
    r = sh(cmd, env=env, timeout=1500); g.n += 1
    tail = (r.stdout + r.stderr).strip().splitlines()
    summary = [l for l in tail if re.match(r'^(Ran|OK|FAILED|FAIL:|ERROR:)', l)]
    if r.returncode:
        g.fail('films/director/tests/test_director.py' + (f' {which}' if which else ''), 'director tests fail: ' + ' | '.join(summary[-6:]),
               'run the same command to see the traceback; never edit a test to make it pass unless the test is wrong (then say why in docs/LOG.md)')


def g_director(g): run_director_tests(g, 'Fast')


def g_director_full(g): run_director_tests(g, '')


def g_check(g):
    for d in battle_map_films():
        out = tempfile.mkdtemp(prefix='kf-check-'); g.n += 1
        r = sh(['node', 'films/director/check.cjs', d, '--line', 'battle-map', '--out', out], timeout=900)
        try: rep = json.load(open(os.path.join(out, 'report.json')))
        except Exception: rep = None
        if (r.returncode or not rep or not rep.get('ok')) and not ALLOW.ok('check', d):
            hard = (rep or {}).get('hard') or [(r.stderr or 'no report').strip()[-200:]]
            g.fail(d, 'director check: ' + ' | '.join(hard[:5]), f'node films/director/check.cjs {d} --line battle-map; open the report.json and sheet.jpg it writes; CRAFT.md section 9')
        elif rep and rep.get('soft'):
            g.warn(f'{d}: {len(rep["soft"])} soft problem(s) (text overlap or off screen); see check.cjs report')


def g_score(g):
    g.n += 1
    try: r = sh([sys.executable, 'films/lib/score/selftest.py'], timeout=600)
    except subprocess.TimeoutExpired: g.fail('films/lib/score/selftest.py', 'timed out', 'run it by hand'); return
    if r.returncode:
        bad = [l for l in r.stdout.splitlines() if l.startswith('FAIL')] or (r.stderr.strip().splitlines()[-3:])
        g.fail('films/lib/score/selftest.py', ' | '.join(bad[:6]), 'pip install numpy scipy soundfile, then run it by hand')


# ------------------------------------------------------------------ docs (memory freshness)
BOT = re.compile(r'github-actions|\[bot\]', re.I)
LOG_HEAD = re.compile(r'^## (\d{1,2}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{4})\s*$')
MONTHS = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()


def needs_log(p):
    if p.startswith('docs/') or p in ('AGENTS.md', 'CLAUDE.md', 'README.md', 'LICENSE') or p.startswith('.agents/memory/'): return False
    return not ALLOW.ok('docs', p)


def own_notes(p):
    """The NOTES.md that can document a change to a single film or style folder (films/<series>/<id>/...), else None."""
    m = re.match(r'^(films/(?:battles|dark-corners|noor|cutaway/[^/]+|studio|styles|showcase)/[^/]+)/', p)
    return m.group(1) + '/NOTES.md' if m else None


def g_docs(g, since):
    # 1. LOG.md: newest-first dated headings
    lines = open(os.path.join(ROOT, 'docs/LOG.md'), encoding='utf-8').read().splitlines()
    heads = [(i, LOG_HEAD.match(l)) for i, l in enumerate(lines) if l.startswith('## ')]
    bad = [lines[i] for i, m in heads if not m]
    if bad: g.fail('docs/LOG.md', f'heading not in the form "## 22 Oct 2026": {bad[0]!r}', 'use "## <day> <Mon> <year>" headings, newest first')
    dates = [(int(m.group(3)), MONTHS.index(m.group(2)), int(m.group(1))) for _, m in heads if m]
    if dates != sorted(dates, reverse=True): g.fail('docs/LOG.md', 'dated headings are not newest first', 'move the newest day to the top, under the intro')
    if not dates: g.fail('docs/LOG.md', 'no dated heading', 'add "## <day> <Mon> <year>" at the top')
    # 2. the change set: commits after `since` (bots excluded) plus the working tree
    if since is None:
        r = sh(['git', 'rev-parse', '--verify', '-q', 'origin/main'])
        since = sh(['git', 'merge-base', 'HEAD', 'origin/main']).stdout.strip() if r.returncode == 0 else 'HEAD'
    changed = set()
    revs = sh(['git', 'rev-list', '--no-merges', '--format=%H %an <%ae>', f'{since}..HEAD']).stdout.splitlines() if since and since != 'HEAD' else []
    commits = [l.split(' ', 1) for l in revs if not l.startswith('commit ')]
    for h, who in commits:
        if BOT.search(who): continue
        changed |= set(sh(['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', h]).stdout.split())
    changed |= set(sh(['git', 'diff', '--name-only', 'HEAD']).stdout.split())
    changed |= set(sh(['git', 'ls-files', '--others', '--exclude-standard']).stdout.split())
    g.n = len(changed)
    if not changed: return
    if 'docs/LOG.md' in changed:
        removed = [l for l in sh(['git', 'diff', since if since != 'HEAD' else 'HEAD', '--', 'docs/LOG.md']).stdout.splitlines()
                   if l.startswith('-') and not l.startswith('---') and l[1:].strip()]
        if removed: g.warn(f'docs/LOG.md: {len(removed)} line(s) removed or rewritten; the log is append-only (add a correcting line instead)')
        if 'docs/STATUS.md' not in changed: g.warn('docs/STATUS.md not updated in this change set; update it if the state of the project changed')
        return
    undocumented = sorted(p for p in changed if needs_log(p) and not (own_notes(p) and own_notes(p) in changed))
    if undocumented:
        g.fail(', '.join(undocumented[:5]) + (f' and {len(undocumented) - 5} more' if len(undocumented) > 5 else ''),
               f'{len(undocumented)} changed file(s) with no docs/LOG.md line in this change set',
               'add one dated line under today\'s heading in docs/LOG.md (what changed, why, the cost) and update docs/STATUS.md; '
               'a builder working inside one film folder may write the line in that folder\'s NOTES.md instead')


GATES = {'secrets': g_secrets, 'json': g_json, 'syntax': g_syntax, 'workflows': g_workflows, 'text': g_text, 'prompts': g_prompts, 'battlemap': g_battlemap,
         'social': g_social, 'director': g_director, 'director-full': g_director_full, 'check': g_check, 'score': g_score}


def main(argv):
    full = '--full' in argv
    if '--list' in argv: print('fast: ' + ' '.join(FAST) + '\nfull: ' + ' '.join(FULL)); return 0
    only = argv[argv.index('--only') + 1].split(',') if '--only' in argv else (FULL if full else FAST)
    since = argv[argv.index('--since') + 1] if '--since' in argv else os.environ.get('VERIFY_SINCE') or None
    if since and set(since) == {'0'}: since = 'HEAD~1'   # a new branch push in CI
    unknown = [x for x in only if x not in FULL and x not in FAST]
    if unknown: print('unknown gate(s): ' + ', '.join(unknown) + '; --list shows them'); return 2
    results = []
    for name in only:
        g = Gate(name)
        try: (g_docs(g, since) if name == 'docs' else GATES[name](g))
        except subprocess.TimeoutExpired as e: g.fail(name, f'timed out ({e.timeout} s)', 'run it by hand to see where it hangs')
        except FileNotFoundError as e: g.fail(name, f'a tool is missing: {e}', 'install node 22 and python 3.11 or newer')
        results.append(g)
        mark = 'PASS' if not g.fails else 'FAIL'
        print(f'{mark}  {name:<14} {g.n:>5} checked  {time.time() - g.t0:5.1f} s')
        for f in g.fails[:25]: print('   x ' + f)
        if len(g.fails) > 25: print(f'   ... and {len(g.fails) - 25} more')
        for w in g.warns[:10]: print('   ! ' + w)
        sys.stdout.flush()
    for gate, pat, n in ALLOW.unused(only):
        print(f'   ! tools/verify-allow.txt line {n} ({gate} {pat}) matched nothing: delete it if the exception is gone')
    failed = [g.name for g in results if g.fails]
    print('\nverify: ' + ('ALL GATES PASS' if not failed else 'FAILED: ' + ', '.join(failed)))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
