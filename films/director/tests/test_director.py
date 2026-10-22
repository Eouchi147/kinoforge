"""Unit tests of the director pipeline with recorded/mock model replies (no paid calls, no network).

    python3 films/director/tests/test_director.py            (all, about 3 min: runs check.cjs in Chromium)
    python3 films/director/tests/test_director.py Fast       (no Chromium)

The Chromium test builds a throwaway job films/studio/_selftest from the Battle of Hastings (cues, film.json, script),
feeds the spec stage one broken draft and one good draft, and checks the repair, eyes and compose logic end to end.
"""
import os, sys, json, shutil, unittest, tempfile, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
os.environ.pop('KF_COMMIT', None)
import common as C
C.agents.market = lambda: {}          # no network: seats fall back to their `prefer` lists
C.agents._market = {}
C.agents.account = lambda: {'remaining': 5.0}
REAL_ASK, REAL_COMPLETE = C.ask, C.complete
import script as S, spec as SP, look as LK, reflect as RF, start as ST, sound as SO

HAST = os.path.join(C.ROOT, 'films', 'battles', 'hastings')
JOB = os.path.join(C.ROOT, 'films', 'studio', '_selftest')


def make_job(brief_extra=None, with_sound=True):
    shutil.rmtree(JOB, ignore_errors=True); os.makedirs(JOB)
    b = {'id': '_selftest', 'title': 'The Battle of Hastings', 'line': 'battle-map', 'subject': 'The Battle of Hastings, 1066', 'audience': 'kids 8 to 14',
         'target_seconds': 150, 'cap_usd': 1.5, 'approved_at': '2026-10-22T09:00:00Z', **(brief_extra or {})}
    json.dump(b, open(os.path.join(JOB, 'brief.json'), 'w'))
    if with_sound:
        cues = json.load(open(os.path.join(HAST, 'cues.json')))
        shutil.copy(os.path.join(HAST, 'cues.json'), JOB)
        film = json.load(open(os.path.join(HAST, 'film.json'))); film['id'] = '_selftest'; film['line'] = 'battle-map'
        json.dump(film, open(os.path.join(JOB, 'film.json'), 'w'))
        json.dump({'title': 'The Battle of Hastings', 'year_label': '1066', 'lines': [{'id': l['id'], 'text': l['text'], 'picture': 'the map'} for l in cues['lines']]},
                  open(os.path.join(JOB, 'script.json'), 'w'))
        job = C.Job(JOB); open(os.path.join(JOB, 'index.html'), 'w').write(SO.index_html(job, 'The Battle of Hastings'))
    return C.Job(JOB) if with_sound or b['line'] in C.lines_config() else None


class Mock:
    """A recorded model: replies by the schema name (ask) or the label (complete); books a fake cost in the ledger."""
    def __init__(self, replies, texts=None):
        self.replies, self.texts, self.calls = replies, texts or {}, []

    def ask(self, seat, messages, schema, ledger, name='reply', max_tokens=2000, validate=None, only=None, allow_free=False, label=''):
        self.calls.append(('ask', seat, name, label, only, messages))
        r = self.replies[name]; data = r(messages, label) if callable(r) else r
        if isinstance(data, list): data = data.pop(0) if len(data) > 1 else data[0]
        if validate and validate(data): raise C.AllFailed(validate(data))
        ledger.add(seat=seat, model=only or f'{seat}/model', task=label, usd=0.01, s=0.1, ok=True)
        return json.loads(json.dumps(data)), only or ('anthropic/x' if seat == 'head' else f'{seat}-prov/model')

    def complete(self, seat, messages, ledger, max_tokens=24000, only=None, label='', validate=None):
        self.calls.append(('complete', seat, label, only))
        t = self.texts[label]; t = t(messages) if callable(t) else t
        if validate and validate(t): raise C.AllFailed(validate(t))
        ledger.add(seat=seat, model=only, task=label, usd=0.02, s=0.1, ok=True)
        return t, only or 'x/model'


def install(m):
    C.ask, C.complete = m.ask, m.complete


def install_real():
    C.ask, C.complete = REAL_ASK, REAL_COMPLETE


class Fast(unittest.TestCase):
    def tearDown(self): shutil.rmtree(JOB, ignore_errors=True)

    def test_house_rules(self):
        t, fx = C.house_clean('In 732—the year of the battle… it was 10–12 miles.')
        self.assertNotRegex(t, '[—–…]'); self.assertIn('10 to 12', t); self.assertTrue(fx)
        self.assertEqual(C.house_problems('A bloody battle at www.x.com', True), ['contains a URL', 'not kid-safe: bloody'])
        self.assertEqual(C.house_problems('A bloody battle', False), [])

    def test_lines_config(self):
        L = C.line('battle-map'); self.assertEqual(L['examples'], ['films/battles/cannae', 'films/battles/hastings'])
        self.assertEqual(L['render'], [1280, 720])
        self.assertIn('battle-map', C.available_lines())
        if os.path.exists(os.path.join(C.ROOT, 'films/lib/kinetic/SPEC.md')) and C.discover_examples('films/lib/kinetic'):
            self.assertIn('kinetic', C.available_lines()); self.assertEqual(C.line('kinetic')['render'], [720, 1280])
        self.assertEqual(C.discover_examples('films/lib/battlemap')[:1], ['films/battles/agincourt'])

    def test_code_block(self):
        self.assertEqual(C.code_block('Here:\n```js\nexport default {a: 1};\n```\nDone'), 'export default {a: 1};\n')
        self.assertEqual(C.code_block('```javascript\nexport default {};'), 'export default {};\n')   # cut reply, no closing fence

    def test_apply_edits(self):
        src = "a: 'l01.x',\nb: 'l01.x',\nc: 3,\n"
        out, fails = SP.apply_edits(src, [{'find': 'c: 3', 'replace': 'c: 4'}, {'find': "'l01.x'", 'replace': 'y'}, {'find': 'zz', 'replace': 'q'}])
        self.assertIn('c: 4', out); self.assertEqual(len(fails), 2); self.assertIn('occurs 2 times', fails[0]); self.assertIn('not in the spec', fails[1])

    def test_script_stage(self):
        job = make_job(with_sound=False)
        draft = {'title': 'The Battle of Hastings', 'year_label': '1066', 'music_prompt': 'medieval drums', 'notes': '',
                 'lines': [{'text': 'In 1066 England had three kings — in one year.', 'picture': 'three crowns'},
                           {'text': 'The Battle of Hastings.', 'picture': 'title'}] +
                          [{'text': f'Line {k} says something true about the battle with enough words to count properly here.', 'picture': 'map'} for k in range(2, 17)],
                 'claims': [{'id': 'c1', 'claim': 'England had three kings in 1066', 'line': 0, 'quote': 'England had three kings'},
                            {'id': 'c2', 'claim': 'Harold was shot in the eye', 'line': 5, 'quote': 'Line 5 says something'}]}
        fixed = json.loads(json.dumps(draft)); fixed['claims'][1]['claim'] = 'Harold died in the battle'
        v0 = {'verdicts': [{'id': 'c1', 'verdict': 'true', 'reason': 'ok', 'correction': ''}, {'id': 'c2', 'verdict': 'doubtful', 'reason': 'disputed', 'correction': 'the tapestry may show it'}]}
        v1 = {'verdicts': [{'id': 'c1', 'verdict': 'true', 'reason': 'ok', 'correction': ''}, {'id': 'c2', 'verdict': 'true', 'reason': 'ok', 'correction': ''}]}
        m = Mock({'script': [draft, fixed], 'verdicts': [v0, v1]}); install(m)
        s = S.main(JOB)
        self.assertEqual(len(s['rounds']), 2); self.assertEqual(s['cuts'], [])
        self.assertNotIn('—', s['lines'][0]['text'])
        checkers = [c for c in m.calls if c[2] == 'verdicts']
        self.assertTrue(all(C.provider(c[4]) != 'anthropic' for c in checkers), 'the checker must be another provider than the writer')
        ad = json.load(open(os.path.join(JOB, 'ad.json')))
        self.assertTrue(C.FREE_ONLY)
        self.assertEqual(ad['prep']['voice'], 'chatterbox'); self.assertEqual(ad['prep']['music']['engine'], 'procedural'); self.assertNotIn('voice_cast', ad['prep'])
        self.assertEqual(len(ad['prep']['vo']), 17); self.assertIn('Instrumental', ad['prep']['music']['prompt'])
        self.assertIn('# Craft:', m.calls[0][5][0]['content'])                     # the writer reads CRAFT.md
        self.assertTrue(ad['_'].startswith('Battle Map: The Battle of Hastings'))
        st = json.load(open(os.path.join(JOB, 'status.json')))
        self.assertEqual((st['stage'], st['state']), ('script', 'done')); self.assertAlmostEqual(st['usd'], 0.04, places=4)
        for k in ('stage', 'state', 'message', 'usd', 'outputs', 'updated_at'): self.assertIn(k, st)

    def test_script_cut(self):
        data = {'lines': [{'text': 'Hook.'}, {'text': 'Title.'}, {'text': 'True part. The arrow hit his eye.'}, {'text': 'Only a dubious line.'}],
                'claims': [{'id': 'a', 'line': 2, 'quote': 'The arrow hit his eye'}, {'id': 'b', 'line': 3, 'quote': 'nowhere'}, {'id': 'c', 'line': 2, 'quote': 'True part'}]}
        cuts = S.cut(data, {'a', 'b'}, 1)
        self.assertEqual([l['text'] for l in data['lines']], ['Hook.', 'Title.', 'True part.'])
        self.assertEqual([c['id'] for c in data['claims']], ['c']); self.assertEqual(len(cuts), 2)

    def test_over_cap(self):
        job = make_job(with_sound=False)
        led = C.Ledger(0.05, None); led.add(seat='x', usd=0.05)
        self.assertFalse(led.room(0.01))

    def test_start_bad_brief(self):
        make_job({'line': 'clay', 'cap_usd': 9}, with_sound=False)
        b, probs = ST.check_brief(JOB)
        self.assertTrue(any('unknown line' in p for p in probs)); self.assertTrue(any('cap_usd' in p for p in probs))

    def test_start_resume_and_fresh(self):
        make_job(); os.environ['OPENROUTER_API_KEY'] = 'test'
        try:
            open(os.path.join(JOB, 'spec.js'), 'w').write('x')
            self.assertTrue(ST.open_job(JOB, 'resume', False))
            self.assertTrue(os.path.exists(os.path.join(JOB, 'cues.json')))            # resume keeps the sound
            ST.open_job(JOB, 'spec', False); self.assertFalse(os.path.exists(os.path.join(JOB, 'spec.js')))
            b = json.load(open(os.path.join(JOB, 'brief.json'))); b['approved_at'] = 'later'; json.dump(b, open(os.path.join(JOB, 'brief.json'), 'w'))
            ST.open_job(JOB, 'resume', True)                                               # a new approval starts fresh
            self.assertEqual(sorted(os.listdir(JOB)), ['brief.json', 'status.json'])
        finally: os.environ.pop('OPENROUTER_API_KEY', None)

    def test_reflect(self):
        job = make_job()
        json.dump({'rounds': [{'candidate': 'a', 'round': 0, 'ok': False, 'hard': ['lint: moves[3].at: word "zzz" (#0) not found in l06: x'], 'soft': []}],
                   'eyes': {'candidates': [{'name': 'a', 'fixes': ['l03: zoom in']}]}, 'final': {'ok': True}}, open(os.path.join(JOB, 'spec_log.json'), 'w'))
        tmp = tempfile.mktemp(suffix='.md'); shutil.copy(RF.LESSONS, tmp); RF.LESSONS = tmp
        try:
            install(Mock({'lessons': {'lessons': ['Copy cue words exactly — always']}}))
            fresh = RF.main(JOB)
            self.assertEqual(len(fresh), 1); self.assertNotIn('—', fresh[0])
            txt = open(tmp).read(); self.assertIn('_selftest: Copy cue words exactly', txt); self.assertIn('seed', txt)
            for k in range(45): RF.write_lessons([f'lesson {k}'], 't')
            self.assertEqual(sum(1 for l in open(tmp) if l.startswith('- ')), RF.KEEP)
        finally: os.remove(tmp)

    def test_spec_models_free(self):
        job = make_job({'cap_usd': 1.5})
        ms = SP.spec_models(job); self.assertEqual(len(ms), 2); self.assertNotEqual(C.provider(ms[0][1]), C.provider(ms[1][1]))
        self.assertTrue(all(C.is_free(m) for _, m in ms), ms)

    def test_free_guards(self):
        install_real(); led = C.Ledger(1.0, None)
        with self.assertRaises(C.PaidRefused): C.ask('head', [], {}, led, only='anthropic/claude-opus-5.5')
        with self.assertRaises(C.PaidRefused): C.complete('coder', [], led, only='z-ai/glm-5.3')
        orig = C.agents.ask
        def charging(seat, messages, schema, ledger, only=None, **kw): ledger.add(seat=seat, model=only, usd=0.01); return {}, only
        C.agents.ask = charging
        try:
            with self.assertRaises(C.OverBudget): C.ask('crew', [], {}, led)       # a 'free' model that charged stops the job
        finally: C.agents.ask = orig
        C.agents._market = None
        mk = {'a/x:free': {'id': 'a/x:free', 'iq': 40, 'mods': ['text', 'image'], 'created': 1, 'in': 0, 'out': 0},
              'b/y:free': {'id': 'b/y:free', 'iq': 50, 'mods': ['text'], 'created': 1, 'in': 0, 'out': 0},
              'c/z': {'id': 'c/z', 'iq': 90, 'mods': ['text', 'image'], 'created': 1, 'in': 1, 'out': 1}}
        old = C.agents.market; C.agents.market = lambda: mk
        try:
            self.assertEqual(C.free_chain('crew')[:2], ['b/y:free', 'a/x:free'])
            self.assertEqual(C.free_chain('eyes'), ['a/x:free'])                      # eyes need image input
        finally: C.agents.market = old

    def test_free_sound(self):
        """The free sound stage without the TTS: a recorded vo.json (Hastings lines), the placeholder pad, the beat map, the mix."""
        job = make_job(with_sound=False)
        cues = json.load(open(os.path.join(HAST, 'cues.json'))); vo = json.load(open(os.path.join(HAST, 'audio', 'vo.json')))
        n = 5; os.makedirs(os.path.join(JOB, 'audio', 'vo'))
        for k in range(n): shutil.copy(os.path.join(HAST, 'audio', 'vo', f'line{k}.mp3'), os.path.join(JOB, 'audio', 'vo'))
        json.dump({'voice': 'chatterbox', 'lines': vo['lines'][:n]}, open(os.path.join(JOB, 'audio', 'vo.json'), 'w'))
        json.dump({'title': 'The Battle of Hastings', 'year_label': '1066', 'lines': [{'id': f'l{k:02d}', 'text': l['text'], 'picture': 'x'} for k, l in enumerate(vo['lines'][:n])]},
                  open(os.path.join(JOB, 'script.json'), 'w'))
        json.dump(S.make_ad(C.Job(JOB), {'title': 'The Battle of Hastings', 'year_label': '1066', 'music_prompt': 'drums', 'lines': [{'text': l['text']} for l in vo['lines'][:n]]}),
                  open(os.path.join(JOB, 'ad.json'), 'w'))
        SO.main(JOB)
        c = json.load(open(os.path.join(JOB, 'cues.json'))); f = json.load(open(os.path.join(JOB, 'film.json')))
        self.assertEqual(len(c['lines']), n); self.assertTrue(c['beats']); self.assertEqual((f['render_w'], f['render_h']), (1280, 720))
        self.assertTrue(os.path.getsize(os.path.join(JOB, 'audio', 'mix.m4a')) > 10000)
        note = json.load(open(os.path.join(JOB, 'ad.json')))['prep'].get('music_note', '')
        if os.path.exists(os.path.join(C.ROOT, 'films/lib/score/remix.py')):
            self.assertEqual(note, 'Score: procedural engine.'); self.assertTrue(os.path.exists(os.path.join(JOB, 'audio', 'score.json')))
        else: self.assertIn('placeholder', note)
        self.assertIn("get('spec')", open(os.path.join(JOB, 'index.html')).read())


class Chromium(unittest.TestCase):
    """The spec stage with a broken draft and a good draft (the real check.cjs, Chromium, the Hastings film)."""
    def tearDown(self): shutil.rmtree(JOB, ignore_errors=True)

    def test_spec_stage(self):
        os.environ['KF_CHECK_MAX'] = '6'; os.environ['KF_CRAFT'] = '0'   # Hastings predates CRAFT.md; the craft checks have their own test
        job = make_job()
        good = open(os.path.join(HAST, 'spec.js')).read()
        bad = good.replace("at: 'l06.stood'", "at: 'l06.zzzz'", 1); self.assertNotEqual(bad, good)
        def edits(messages, label):
            if label.startswith('repair a'):
                self.assertIn('zzzz', messages[-1]['content'])
                return {'edits': [{'find': "at: 'l06.zzzz'", 'replace': "at: 'l06.stood'"}], 'note': 'fixed the word'}
            if label == 'compose': return {'edits': [{'find': "text: 'A RUMOR'", 'replace': "text: 'A RUMOUR'"}], 'note': 'spelling'}
            return {'edits': [], 'note': 'nothing'}
        def eyes(messages, label):
            imgs = [c for c in messages[0]['content'] if c['type'] == 'image_url']; self.assertEqual(len(imgs), 2)
            return {'candidates': [{'name': 'a', 'clarity': 7, 'match': 7, 'beauty': 7, 'fixes': []},
                                   {'name': 'b', 'clarity': 8, 'match': 8, 'beauty': 8, 'fixes': ['l09: spell rumour the British way']}], 'winner': 'b', 'why': 'clearer'}
        m = Mock({'edits': edits, 'eyes': eyes}, {'spec draft a': '```js\n' + bad + '```', 'spec draft b': 'Here it is\n```js\n' + good + '```'}); install(m)
        SP.main(JOB)
        log = json.load(open(os.path.join(JOB, 'spec_log.json')))
        ra = [r for r in log['rounds'] if r.get('candidate') == 'a' and 'round' in r]
        self.assertFalse(ra[0]['ok']); self.assertTrue(any('zzzz' in h for h in ra[0]['hard'])); self.assertTrue(ra[-1]['ok'])
        self.assertEqual(log['final']['candidate'], 'b'); self.assertTrue(log['final']['composed'])
        self.assertIn("'A RUMOUR'", open(os.path.join(JOB, 'spec.js')).read())
        self.assertTrue(os.path.exists(os.path.join(JOB, 'check', 'final', 'sheet.jpg')))
        st = json.load(open(os.path.join(JOB, 'status.json'))); self.assertEqual((st['stage'], st['state']), ('eyes', 'done'))
        self.assertIn('spec', st['outputs'])
        os.environ.pop('KF_CRAFT', None)

    def test_craft_checks(self):
        """CRAFT.md section 9 in code, on a film made before it: every rule it breaks is reported."""
        out = tempfile.mkdtemp(); os.environ.pop('KF_CRAFT', None)
        import subprocess
        subprocess.run(['node', os.path.join(C.HERE, 'check.cjs'), 'films/battles/hastings', '--line', 'battle-map', '--times', '30', '--out', out], cwd=C.ROOT, check=True, capture_output=True)
        r = json.load(open(os.path.join(out, 'report.json'))); hard = ' | '.join(r['hard'])
        self.assertFalse(r['ok'])
        for k in ('no scene list', 'cuts with no written reason', 'icon star', 'camera move from'): self.assertIn(k, hard)
        self.assertTrue(any('no legend' in x for x in r['soft'] + r['hard']))
        self.assertEqual(r['craft']['shots'], 5)
        shutil.rmtree(out)


if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0]] + sys.argv[1:], verbosity=2)
