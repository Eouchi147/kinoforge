"""The director on a Blender line (cutaway) with mock model replies: no network, no money, no Blender (about 10 s).

    python3 films/director/tests/test_cutaway_line.py

Builds a throwaway job films/studio/_cltest from the line's example (films/cutaway/meadow), feeds the spec stage a draft
with a wrong cue word and a good draft, and checks: the validator is the check, the repair fixes the word, the eyes get
the contact sheets (mocked here; tools/stills.py renders them on the runner), spec.json is written, the render cost is
reported, and the sound stage's hand-off copies the generic scene and sets the 9:16 sizes.
"""
import json, os, re, shutil, sys, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
os.environ.pop('KF_COMMIT', None)
from test_director import C, SP, Mock, install, install_real, Mode  # noqa: E402  (offline seats, mocks)
import blender_line as BL  # noqa: E402

EX = os.path.join(C.ROOT, 'films', 'cutaway', 'meadow')
JOB = os.path.join(C.ROOT, 'films', 'studio', '_cltest')


def make_job(fmt='16:9'):
    shutil.rmtree(JOB, ignore_errors=True); os.makedirs(JOB)
    json.dump({'id': '_cltest', 'title': 'What Lies Under a Meadow', 'line': 'cutaway', 'format': fmt, 'subject': 'What lies under a meadow',
               'audience': 'families', 'target_seconds': 40, 'cap_usd': 1.0, 'approved_at': '2026-10-23T01:00:00Z'}, open(os.path.join(JOB, 'brief.json'), 'w'))
    shutil.copy(os.path.join(EX, 'cues.json'), JOB); cues = json.load(open(os.path.join(EX, 'cues.json')))
    film = json.load(open(os.path.join(EX, 'film.json'))); film['id'] = '_cltest'; json.dump(film, open(os.path.join(JOB, 'film.json'), 'w'))
    json.dump({'title': 'What Lies Under a Meadow', 'year_label': '', 'lines': [{'id': l['id'], 'text': l['text'], 'picture': 'the cut'} for l in cues['lines']]},
              open(os.path.join(JOB, 'script.json'), 'w'))
    return C.Job(JOB)


def fake_stills(job, rel, name, max_stills=8):
    from PIL import Image
    os.makedirs(job.p('check', name), exist_ok=True); p = job.p('check', name, 'sheet.jpg'); Image.new('RGB', (64, 36)).save(p); return p


class CutawayLine(unittest.TestCase):
    def tearDown(self): shutil.rmtree(JOB, ignore_errors=True); install_real()

    def test_line(self):
        L = C.line('cutaway'); self.assertEqual(L['examples'], ['films/cutaway/meadow']); self.assertEqual(L['spec_file'], 'spec.json')
        self.assertIn('cutaway', C.available_lines())

    def test_sound_handoff_vertical(self):
        job = make_job('9:16'); open(job.p('index.html'), 'w').write('x')
        BL.prepare(job, 'What Lies Under a Meadow')
        f = json.load(open(job.p('film.json')))
        self.assertEqual((f['render_w'], f['render_h'], f['w'], f['h'], f['samples']), (720, 1280, 1080, 1920, 20))
        self.assertTrue(os.path.exists(job.p('blender.py'))); self.assertFalse(os.path.exists(job.p('index.html')))

    def test_json_block(self):
        self.assertEqual(json.loads(BL.json_block('Here:\n```json\n{"sets": {}, "scenes": []}\n```\nthanks')), {'sets': {}, 'scenes': []})
        self.assertIsNotNone(BL.json_problem('no json here')); self.assertIsNone(BL.json_problem('{"sets": {}, "scenes": []}'))

    def test_spec_stage(self):
        with Mode(free=True):
            job = make_job()
            good = json.dumps(json.load(open(os.path.join(EX, 'spec.json'))), indent=1)
            bad = good.replace('"l02.mole"', '"l02.molehill"', 1); self.assertNotEqual(bad, good)
            seen = {}
            def edits(messages, label):
                if label.startswith('repair a'):
                    self.assertIn('molehill', messages[-1]['content']); self.assertIn('```json', messages[-1]['content'])
                    return {'edits': [{'find': '"l02.molehill"', 'replace': '"l02.mole"'}], 'note': 'fixed the word'}
                return {'edits': [], 'note': 'nothing'}
            def eyes(messages, label):
                names = re.findall(r'Candidate (\w+)', ' '.join(c.get('text', '') for c in messages[0]['content'] if c['type'] == 'text'))
                seen['eyes'] = names
                return {'candidates': [{'name': n, 'clarity': 8, 'match': 8, 'beauty': 8, 'fixes': []} for n in names], 'winner': names[-1], 'why': 'clear'}
            install(Mock({'edits': edits, 'eyes': eyes}, {'spec draft a': '```json\n' + bad + '\n```', 'spec draft b': 'Here it is\n```json\n' + good + '\n```'}))
            real = BL.stills; BL.stills = fake_stills
            try: SP.main(JOB)
            finally: BL.stills = real
            log = json.load(open(job.p('spec_log.json')))
            ra = [r for r in log['rounds'] if r.get('candidate') == 'a' and 'round' in r]
            self.assertFalse(ra[0]['ok']); self.assertTrue(any('molehill' in h for h in ra[0]['hard'])); self.assertTrue(ra[-1]['ok'])
            self.assertEqual(sorted(seen['eyes']), ['a', 'b'])
            self.assertTrue(os.path.exists(job.p('spec.json'))); self.assertFalse(os.path.exists(job.p('spec.js')))
            st = json.load(open(job.p('status.json'))); self.assertEqual((st['stage'], st['state']), ('eyes', 'done'))
            self.assertEqual(st['outputs']['render_cost']['usd'], 0.0); self.assertGreater(st['outputs']['render_cost']['frames'], 900)


if __name__ == '__main__':
    unittest.main(verbosity=1)
