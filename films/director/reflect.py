"""reflect.py: stage 7 of the director pipeline. One short set of lessons from this job, appended to LESSONS.md.

    python3 films/director/reflect.py films/studio/<id>

Reads spec_log.json (what the checks caught each round, what the repairs fixed, what the eyes asked for) and script.json
(what the fact check cut). A cheap crew model turns that into at most 3 one-line rules for the next spec; if it fails,
the most common error kinds are written as the lesson. LESSONS.md keeps the newest 40 lessons (seed lessons included).
"""
import os, sys, json, re, time
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

LESSONS = os.path.join(C.HERE, 'LESSONS.md')
KEEP = 40
SCHEMA = {'type': 'object', 'additionalProperties': False, 'required': ['lessons'],
          'properties': {'lessons': {'type': 'array', 'items': {'type': 'string'}, 'description': 'at most 3, each one sentence, a rule for the next spec'}}}


def kind(msg):
    m = re.sub(r'\d+(\.\d+)?', 'N', msg)
    m = re.sub(r'"[^"]*"', '"x"', m)
    return m.split(':')[0] + ':' + ':'.join(m.split(':')[1:2])[:60]


def digest(job):
    slog = job.read('spec_log.json', {}); script = job.read('script.json', {})
    hard = Counter(); soft = Counter(); first = {}
    for r in slog.get('rounds', []):
        if 'round' not in r: continue
        for h in r.get('hard', []): k = kind(h); hard[k] += 1; first.setdefault(k, h)
        for s in r.get('soft', []): k = kind(s); soft[k] += 1; first.setdefault(k, s)
    eyes = slog.get('eyes', {})
    fixes = [f for c in eyes.get('candidates', []) for f in c.get('fixes', [])]
    return {'film': script.get('title'), 'line': job.line['name'],
            'errors_caught': [{'kind': k, 'count': n, 'example': first[k][:200]} for k, n in hard.most_common(8)],
            'layout_problems': [{'kind': k, 'count': n, 'example': first[k][:200]} for k, n in soft.most_common(6)],
            'repairs': [r for r in slog.get('rounds', []) if 'repair' in r][:8], 'eyes_fixes': fixes[:10],
            'compose': slog.get('compose'), 'final': slog.get('final'),
            'fact_check_cuts': script.get('cuts', []), 'claims_flagged': [v.get('reason') for r in script.get('rounds', []) for v in r.get('not_true', [])][:6]}


def write_lessons(new, tag):
    head, items = [], []
    if os.path.exists(LESSONS):
        for ln in open(LESSONS).read().splitlines():
            (items if ln.startswith('- ') else head).append(ln)
    day = time.strftime('%Y-%m-%d')
    fresh = [f'- {day} {tag}: {l.strip().rstrip(".")}.' for l in new if l.strip()]
    items = (fresh + items)[:KEEP]
    while head and not head[-1].strip(): head.pop()
    open(LESSONS, 'w').write('\n'.join(head) + '\n\n' + '\n'.join(items) + '\n')
    return fresh


def main(d):
    job = C.Job(d)
    C.set_status(job.dir, 'reflect', 'running', 'Writing down what this job taught.', commit=False)
    dg = digest(job); lessons = []
    try:
        old = open(LESSONS).read() if os.path.exists(LESSONS) else ''
        res, model = C.ask('crew', [{'role': 'system', 'content': 'You keep the lessons file of an automated film pipeline: a coder model writes a spec for a '
                                     f'spec-driven animation engine ({job.line["engine"]}); code checks and an eyes model catch problems; repairs fix them. '
                                     'From this job\'s digest, write at most 3 lessons, one sentence each, phrased as concrete rules that would have '
                                     'prevented the problems in the next spec. Do not repeat a lesson already in the file. If nothing new was learned, return none.'},
                                    {'role': 'user', 'content': f'Current lessons file:\n{old}\n\nThis job:\n{json.dumps(dg, indent=1)[:12000]}'}],
                           SCHEMA, job.ledger, name='lessons', max_tokens=800, label='reflect')
        lessons = [re.sub(r'[—–]', ',', l) for l in res['lessons'][:3]]
    except C.OverBudget: raise
    except Exception as e:
        C.log('reflect model failed, writing the digest instead:', str(e)[:200])
        lessons = [f"Most common check error: {e_['kind']} (x{e_['count']}), e.g. {e_['example'][:120]}" for e_ in dg['errors_caught'][:2]]
    fresh = write_lessons(lessons, job.id)
    job.write('reflect.json', {'digest': dg, 'lessons': fresh})
    C.set_status(job.dir, 'reflect', 'done', f'{len(fresh)} lessons added.', extra_paths=[LESSONS])
    return fresh


if __name__ == '__main__':
    main(sys.argv[1])
