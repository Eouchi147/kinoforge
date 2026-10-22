"""look.py: the eyes. The eyes seat scores candidate films from their contact sheets and picks the winner.

    python3 films/director/look.py films/studio/<id> a b        (sheets from check/<name>/sheet.jpg)

Each sheet is a grid of stills with the narration line under each. The eyes score clarity (could a child follow it),
match to the words, and beauty (0 to 10 each), list concrete fixes for each candidate, and name the winner.
If the eyes seat fails, the candidate with the fewest problems in code wins (no fixes).
"""
import os, sys, json, base64, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

EYES_SCHEMA = {'type': 'object', 'additionalProperties': False, 'required': ['candidates', 'winner', 'why'],
    'properties': {'candidates': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False,
        'required': ['name', 'clarity', 'match', 'beauty', 'fixes'],
        'properties': {'name': {'type': 'string'}, 'clarity': {'type': 'number'}, 'match': {'type': 'number'}, 'beauty': {'type': 'number'},
                       'fixes': {'type': 'array', 'items': {'type': 'string'}, 'description': 'concrete fixes, each naming the time or line, at most 6'}}}},
        'winner': {'type': 'string'}, 'why': {'type': 'string'}}}


def sheet_data_url(path, width=1150):
    from PIL import Image
    im = Image.open(path).convert('RGB')
    if im.width > width: im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=80)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


def fallback(cands, note):
    best = min(cands, key=lambda c: (not c['report']['ok'], len(c['report']['hard']), len(c['report']['soft'])))
    return {'candidates': [{'name': c['name'], 'clarity': None, 'match': None, 'beauty': None, 'total': None, 'fixes': []} for c in cands],
            'winner': best['name'], 'why': note, 'model': None}


def score(job, cands):
    """cands: [{name, sheet (path), report (dict)}] -> {candidates: [...with total], winner, why, model}"""
    cands = [c for c in cands if c.get('sheet') and os.path.exists(c['sheet'])] or cands
    if not cands: raise ValueError('no candidates to look at')
    L = job.line; script = job.read('script.json') or {}
    content = [{'type': 'text', 'text':
        f"You are the picture editor of KINOFORGE's {L['series']} series ({L['aspect']}, {L['style']} style). Below are contact sheets of "
        f"{len(cands)} candidate cut(s) of the same film, \"{script.get('title', job.brief.get('title'))}\". Under each still: its time, the narration line id "
        "and the narration heard at that moment. Score each candidate 0 to 10 on: clarity (could a child of 10 follow who is where and what happens), "
        "match (does each picture show what the words say at that moment), beauty (composition, readable labels, no clutter, nothing cut off). "
        "List up to 6 concrete fixes for each candidate, each naming the time or line id and what to change in the picture (camera, labels, timing, "
        "which element to add or remove). Name the winner exactly as given."}]
    for c in cands:
        r = c['report']
        content += [{'type': 'text', 'text': f"Candidate {c['name']} (problems found in code: {len(r['hard'])} hard, {len(r['soft'])} soft)"},
                    {'type': 'image_url', 'image_url': {'url': sheet_data_url(c['sheet'])}}]
    names = [c['name'] for c in cands]
    def valid(d):
        if d.get('winner') not in names: return f'winner must be one of {names}'
    try:
        res, model = C.ask(job.brief.get('seats', {}).get('eyes', 'eyes'), [{'role': 'user', 'content': content}], EYES_SCHEMA, job.ledger,
                           name='eyes', max_tokens=2500, validate=valid, label='eyes: candidates')
    except C.OverBudget: raise
    except Exception as e:
        C.log('eyes failed, the code checks decide:', str(e)[:300]); return fallback(cands, f'eyes seat failed: {str(e)[:160]}')
    for c in res['candidates']:
        c['total'] = round(sum(float(c.get(k) or 0) for k in ('clarity', 'match', 'beauty')) / 3, 2)
    res['model'] = model
    return res


if __name__ == '__main__':
    job = C.Job(sys.argv[1])
    cands = [{'name': n, 'sheet': job.p('check', n, 'sheet.jpg'), 'report': json.load(open(job.p('check', n, 'report.json')))} for n in sys.argv[2:]]
    print(json.dumps(score(job, cands), indent=1))
