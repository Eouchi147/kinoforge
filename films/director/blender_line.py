"""blender_line.py: what the director pipeline does differently for a line rendered in Blender (lines.json "kind": "blender").

The Cutaway line is the first: the coder seat writes DATA (spec.json, a JSON object in the format of the line's SPEC.md),
not code; the check stage runs the line's validator (pure Python, about a second, no Blender) instead of check.cjs; the
eyes get a contact sheet rendered by the line's stills tool (Blender, low resolution, on the runner); the sound stage
copies the line's generic scene (blender.py) into the job folder instead of an index.html; the render stage is the same
films-render.yml (it renders any folder with a blender.py).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402


def is_blender(L): return (L or {}).get('kind') == 'blender'


def spec_file(L): return (L or {}).get('spec_file') or 'spec.js'


def apply_format(job):
    """A line with several formats (Cutaway: 16:9 and 9:16): the brief's `format` picks the aspect and the sizes."""
    L = job.line; f = job.brief.get('format')
    if L.get('formats') and f in L['formats']:
        L['aspect'] = f; L['render'] = list(L['formats'][f]['render']); L['delivery'] = list(L['formats'][f]['delivery'])
    return L


def json_block(text):
    """The JSON object in a reply (a ```json block, else the outermost braces), re-dumped so edits find stable text."""
    blocks = re.findall(r'```(?:json|JSON)?[ \t]*\n(.*?)```', text, re.S)
    raw = max(blocks, key=len) if blocks else text
    a, b = raw.find('{'), raw.rfind('}')
    if a < 0 or b <= a: return raw.strip() + '\n'
    raw = raw[a:b + 1]
    try: return json.dumps(json.loads(raw), indent=1, ensure_ascii=False) + '\n'
    except ValueError: return raw + '\n'


def json_problem(text):
    try: d = json.loads(json_block(text))
    except ValueError as e: return f'the reply is not one valid JSON object: {e}'
    if not isinstance(d, dict) or 'scenes' not in d or 'sets' not in d: return 'the JSON object needs "sets" and "scenes"'
    return None


def prepare(job, title):
    """The sound stage's last step for a Blender line: film.json gets the line's samples and the brief's format; the
    folder gets the line's generic scene as blender.py (no index.html)."""
    L = apply_format(job)
    shutil.copy(os.path.join(C.ROOT, L['scene']), job.p('blender.py'))
    film = job.read('film.json') or {}
    film.update({'render_w': L['render'][0], 'render_h': L['render'][1], 'w': L['delivery'][0], 'h': L['delivery'][1],
                 'samples': L.get('samples', 20), 'format': L['aspect'], 'style': L['style'], 'line': L['name']})
    job.write('film.json', film)
    if job.has('index.html'): os.remove(job.p('index.html'))


def check(job, spec_rel, name):
    """The line's validator on one candidate: the same report shape as check.cjs ({ok, hard, soft, stills: []})."""
    out = job.p('check', name); shutil.rmtree(out, ignore_errors=True); os.makedirs(out, exist_ok=True)
    rp = os.path.join(out, 'report.json'); t0 = time.time()
    r = subprocess.run([sys.executable, os.path.join(C.ROOT, job.line['validator']), job.dir, '--spec', spec_rel.lstrip('./'), '--out', rp, '--quiet'],
                       cwd=C.ROOT, capture_output=True, text=True, timeout=600)
    C.log(f'validate {name}: {r.stdout.strip()[-300:]} ({time.time() - t0:.0f} s)')
    if not os.path.exists(rp): return {'ok': False, 'hard': [f'validator failed: {(r.stderr or r.stdout)[-400:]}'], 'soft': [], 'stills': []}
    rep = json.load(open(rp)); rep.setdefault('stills', [])
    # notes about the job (estimated cues, the cost) the coder cannot fix by editing go last, marked as notes
    rep['soft'] = [s for s in rep['soft'] if not s.startswith('cues.json is an estimate')] + \
                  ['note: ' + s for s in rep['soft'] if s.startswith('cues.json is an estimate')]
    rep['check_s'] = round(time.time() - t0, 1)
    return rep


def stills(job, spec_rel, name, max_stills=8):
    """Contact sheet of a candidate for the eyes: the line's stills tool in the Blender Python ($KF_BPY_PYTHON, set by
    film.yml), 480 px, 8 samples. Returns the sheet path or None (no Blender here, or it failed)."""
    py = os.environ.get('KF_BPY_PYTHON') or sys.executable
    out = job.p('check', name); t0 = time.time()
    try:
        r = subprocess.run([py, os.path.join(C.ROOT, job.line['stills']), job.dir, '--spec', spec_rel.lstrip('./'), '--out', out,
                            '--w', '480', '--samples', '8', '--max', str(max_stills)], cwd=C.ROOT, capture_output=True, text=True, timeout=2400)
    except Exception as e:
        C.log(f'stills {name} failed: {e}'); return None
    C.log(f'stills {name}: exit {r.returncode}, {time.time() - t0:.0f} s; ' + (r.stdout.strip().splitlines() or [''])[-1][-200:])
    sheet = os.path.join(out, 'sheet.jpg')
    if r.returncode or not os.path.exists(sheet):
        C.log('stills stderr:', (r.stderr or '')[-600:]); return None
    return sheet
