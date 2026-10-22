"""spec.py: stages 3 to 5 of the director pipeline. From the cues to a checked, chosen, composed picture spec.

    python3 films/director/spec.py films/studio/<id>

3 PROBE   two candidate specs (cand/a.js, cand/b.js) drafted in parallel by two models from different providers, from:
          the line's SPEC.md, two finished example specs of the line (with their narration), our cues (line and word times),
          the script's picture ideas, and films/director/LESSONS.md.
4 CHECK   check.cjs on each candidate (syntax, lint against the cues, page and console errors, stills at every line, blank
          frames, text off screen or overlapping). Problems go back to the coder seat as edits: at most 3 repair rounds per
          candidate; the best version of each candidate is kept (a repair that makes things worse is dropped).
5 EYES    look.py scores the candidates that pass (contact sheets with the narration under each still); the winner's fixes go
          back to the coder once (COMPOSE), then the checks run again; if the composed spec fails, the winner stands as it was.
Writes spec.js (the winner), cand/*.js, check/<name>/report.json + sheet.jpg, spec_log.json (every round, every model, scores).
"""
import os, sys, json, re, shutil, subprocess, threading, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import look

MAX_REPAIR = 3
EDITS_SCHEMA = {'type': 'object', 'additionalProperties': False, 'required': ['edits', 'note'],
    'properties': {'edits': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False, 'required': ['find', 'replace'],
        'properties': {'find': {'type': 'string', 'description': 'an exact snippet of the current spec, unique in the file (copy it verbatim, a full line or more)'},
                       'replace': {'type': 'string', 'description': 'what replaces it'}}}},
        'note': {'type': 'string'}}}


def rd(p): return open(os.path.join(C.ROOT, p)).read()


def cue_lines(cues, words=True):
    out = [f"duration {cues['duration']} s; title line {cues.get('title_line')}; outro (end card) the last {cues.get('outro_s', 4)} s; "
           f"strong music hits (s): {', '.join(str(round(h, 2)) for h in cues.get('strong_hits', [])[:40])}"]
    for l in cues['lines']:
        out.append(f"{l['id']} [{l['start']:.2f} to {l['end']:.2f}] {l['text']}")
        if words and l.get('words'): out.append('    words: ' + ' '.join(f"{w[0]}@{w[1]:.2f}" for w in l['words']))
    return '\n'.join(out)


def context(job):
    """The shared, cacheable system prompt: the engine's spec, two example films, the rules and the lessons."""
    L = job.line; parts = [
        f"You write spec files for the KINOFORGE {L['series']} engine ({L['engine']}, {L['aspect']}, rendered at {L['render'][0]}x{L['render'][1]}, 24 fps). "
        "A spec is one ES module, `export default { ... };`, that drives a whole film from the narration's cue times. The picture follows the sound: "
        "never change timing, only refer to cue times.",
        '# The engine: SPEC.md\n' + rd(L['spec_md'])]
    for k, ex in enumerate(L['examples']):
        exc = json.load(open(os.path.join(C.ROOT, ex, 'cues.json')))
        parts.append(f"# Example film {k + 1}: {exc.get('title', ex)} ({ex})\n## Its narration (cues)\n{cue_lines(exc, words=False)}\n## Its spec.js\n```js\n{rd(ex + '/spec.js')}\n```")
    parts.append('# House rules for every spec of this line\n' + '\n'.join('- ' + r for r in L.get('spec_rules', [])))
    les = os.path.join(C.HERE, 'LESSONS.md')
    if os.path.exists(les): parts.append('# Lessons from earlier jobs (follow them)\n' + open(les).read())
    return '\n\n'.join(parts)


def job_text(job):
    s = job.read('script.json'); cues = job.read('cues.json'); b = job.brief
    pics = '\n'.join(f"{l['id']}: {l['picture']}" for l in s['lines'])
    return (f"# This film\nTitle: {s['title']} ({s['year_label']}). Subject: {b.get('subject') or b.get('title')}. "
            + (f"Angle: {b['angle']}. " if b.get('angle') else '') + (f"Notes: {b['notes']}. " if b.get('notes') else '') +
            f"\n## The picture idea for each line (from the writer)\n{pics}\n## The cues (every line with its word times; refer to words as 'l03.word')\n{cue_lines(cues)}")


def draft_prompt(job):
    return [{'role': 'system', 'content': context(job)},
            {'role': 'user', 'content': job_text(job) + "\n\nWrite the complete spec.js for this film, at the quality of the examples. Reply with the whole module "
             "in ONE ```js fenced block and nothing after it."}]


def spec_models(job):
    """Two draft models from different providers. brief.seats.spec = [seatA, seatB] overrides; default: head + coder when
    the cap allows the head seat (cap >= 1.4), else the two best coder models."""
    seats = job.brief.get('seats', {}).get('spec') or (['head', 'coder'] if job.brief['cap_usd'] >= 1.4 else ['coder', 'coder'])
    out, used = [], set()
    for s in seats:
        for m in C.seat_models(s):
            if C.provider(m) not in used: out.append((s, m)); used.add(C.provider(m)); break
    if len(out) < 2:   # not enough providers: allow the same provider, different model
        for m in C.seat_models('coder'):
            if all(m != x[1] for x in out): out.append(('coder', m))
            if len(out) == 2: break
    return out[:2]


def check(job, spec_rel, name, max_stills=int(os.environ.get('KF_CHECK_MAX', 28))):
    """Run check.cjs; returns the report dict."""
    out = job.p('check', name)
    shutil.rmtree(out, ignore_errors=True)
    cmd = ['node', os.path.join(C.HERE, 'check.cjs'), C.rel(job.dir), '--spec', spec_rel, '--out', out, '--line', job.line['name'], '--max', str(max_stills)]
    t0 = time.time(); r = subprocess.run(cmd, cwd=C.ROOT, capture_output=True, text=True, timeout=1800)
    C.log(f'check {name}: {r.stdout.strip()[-300:]} ({time.time() - t0:.0f} s)')
    if r.returncode not in (0, 2) or not os.path.exists(os.path.join(out, 'report.json')):
        return {'ok': False, 'hard': [f'checker failed: {(r.stderr or r.stdout)[-400:]}'], 'soft': [], 'stills': []}
    rep = json.load(open(os.path.join(out, 'report.json'))); rep['check_s'] = round(time.time() - t0, 1)
    return rep


def fixable_soft(rep):
    return [s for s in rep.get('soft', []) if not s.startswith('lint warning')]


def badness(rep):
    return (not rep['ok'], len(rep['hard']), len(fixable_soft(rep)), len(rep.get('soft', [])))


def apply_edits(src, edits):
    fails = []
    for k, e in enumerate(edits):
        f = e['find']
        n = src.count(f)
        if not f or n == 0:
            # tolerate whitespace differences at the ends
            f2 = f.strip(); n2 = src.count(f2) if f2 else 0
            if n2 == 1: src = src.replace(f2, e['replace'].strip(), 1); continue
            fails.append(f'edit {k}: find text not in the spec: {f[:120]!r}'); continue
        if n > 1: fails.append(f'edit {k}: find text occurs {n} times, make it unique: {f[:120]!r}'); continue
        src = src.replace(f, e['replace'], 1)
    return src, fails


def repair(job, src, problems, model, label, extra=''):
    """Ask the coder seat for edits that fix the problems. Returns (new_src, model, edit_failures)."""
    msgs = [{'role': 'system', 'content': context(job)},
            {'role': 'user', 'content': job_text(job) + f"\n\n# The current spec.js\n```js\n{src}\n```\n\n# Problems found by the checks\n" +
             '\n'.join('- ' + p for p in problems[:40]) + (f"\n\n{extra}" if extra else '') +
             "\n\nFix every problem with the smallest edits. Return edits: each `find` is an exact, unique snippet of the current spec (copy it "
             "verbatim, include enough of the line to be unique) and `replace` is the new text. Do not rewrite parts that work."}]
    seat = job.brief.get('seats', {}).get('repair', 'coder')
    only = model if model in C.seat_models(seat) else None
    try:
        res, used = C.ask(seat, msgs, EDITS_SCHEMA, job.ledger, name='edits', max_tokens=12000, only=only, label=label)
    except C.AllFailed:
        if not only: raise
        res, used = C.ask(seat, msgs, EDITS_SCHEMA, job.ledger, name='edits', max_tokens=12000, label=label + ' (fallback)')
    new, fails = apply_edits(src, res['edits'])
    return new, used, fails, res.get('note', '')


def run_candidate(job, name, src, model, log):
    """Check and repair one candidate (at most MAX_REPAIR rounds). Keeps the best version. Returns the candidate record."""
    path = job.p('cand', f'{name}.js'); rel = f'./cand/{name}.js'
    best = None; carry = []
    for r in range(MAX_REPAIR + 1):
        open(path, 'w').write(src)
        rep = check(job, rel, name)
        rec = {'round': r, 'ok': rep['ok'], 'hard': rep['hard'][:30], 'soft': rep.get('soft', [])[:30], 'bytes': len(src), 'check_s': rep.get('check_s'),
               'ready_s': rep.get('ready_s'), 'still_s': rep.get('still_s')}
        log.append({'candidate': name, **rec}); C.log(f'{name} round {r}: ok={rep["ok"]} hard={len(rep["hard"])} soft={len(rep.get("soft", []))}')
        if best is None or badness(rep) < badness(best['report']):
            best = {'src': src, 'report': rep, 'round': r}
            shutil.copy(path, job.p('cand', f'{name}.best.js'))
            if os.path.exists(job.p('check', name)):
                shutil.rmtree(job.p('check', f'{name}.best'), ignore_errors=True); shutil.copytree(job.p('check', name), job.p('check', f'{name}.best'))
        C.set_status(job.dir, 'check', 'running', f'Draft {name.upper()}, round {r}: {len(rep["hard"])} errors, {len(fixable_soft(rep))} layout problems.', commit=False)
        problems = rep['hard'] + fixable_soft(rep)
        if not problems or r == MAX_REPAIR: break
        if rep['ok'] and r >= 2: break   # it ships; layout polish is left to the compose round
        if not rep['ok']: problems += [s for s in rep.get('soft', []) if s.startswith('lint warning')][:8]
        try:
            src, model, fails, note = repair(job, src, problems + carry, model, f'repair {name} {r + 1}')
            carry = [f'(from your last edits) {f}' for f in fails]
            log.append({'candidate': name, 'repair': r + 1, 'model': model, 'failed_edits': fails, 'note': note})
        except C.OverBudget: raise
        except Exception as e:
            log.append({'candidate': name, 'repair': r + 1, 'error': str(e)[:300]}); C.log('repair failed:', str(e)[:300]); break
    shutil.copy(job.p('cand', f'{name}.best.js'), path)
    if os.path.exists(job.p('check', f'{name}.best')):
        shutil.rmtree(job.p('check', name), ignore_errors=True); shutil.move(job.p('check', f'{name}.best'), job.p('check', name))
    os.remove(job.p('cand', f'{name}.best.js'))
    return {'name': name, 'model': model, 'src': best['src'], 'report': best['report'], 'best_round': best['round'], 'sheet': job.p('check', name, 'sheet.jpg')}


def main(d):
    job = C.Job(d)
    if not job.has('cues.json'): raise RuntimeError('no cues.json: run the sound stage first')
    log_path = job.p('spec_log.json'); slog = job.read('spec_log.json', {'rounds': []})
    if job.has('spec.js') and slog.get('final', {}).get('ok'):
        C.log('spec exists and passed its checks, skipped'); return
    os.makedirs(job.p('cand'), exist_ok=True)
    # 3. probe: two drafts in parallel
    models = spec_models(job)
    C.set_status(job.dir, 'spec', 'running', 'Two coders are drafting the picture: ' + ', '.join(m for _, m in models) + '.')
    msgs = draft_prompt(job); drafts = {}; errs = {}
    def draft(name, seat, model):
        try:
            text, used = C.complete(seat, msgs, job.ledger, max_tokens=28000, only=model, label=f'spec draft {name}',
                                    validate=lambda t: None if 'export default' in C.code_block(t) else 'no `export default` module in the reply')
            drafts[name] = (C.code_block(text), used)
        except Exception as e: errs[name] = e
    names = ['a', 'b'][:len(models)]
    th = [threading.Thread(target=draft, args=(n, s, m)) for n, (s, m) in zip(names, models)]
    for t in th: t.start()
    for t in th: t.join()
    for n, e in errs.items():
        if isinstance(e, C.OverBudget): raise e
        C.log(f'draft {n} failed: {str(e)[:300]}')
    if not drafts:   # one more try down the coder chain
        text, used = C.complete('coder', msgs, job.ledger, max_tokens=28000, label='spec draft (fallback)')
        drafts['a'] = (C.code_block(text), used)
    for n, (src, m) in drafts.items(): open(job.p('cand', f'{n}.js'), 'w').write(src)
    slog['drafts'] = {n: {'model': m, 'bytes': len(src)} for n, (src, m) in drafts.items()}; slog['draft_errors'] = {n: str(e)[:300] for n, e in errs.items()}
    job.write('spec_log.json', slog)
    C.set_status(job.dir, 'spec', 'done', f'{len(drafts)} drafts: ' + ', '.join(f'{n.upper()} by {m}' for n, (_, m) in drafts.items()) + '.')
    # 4. checks and repairs, one candidate after the other (one Chromium at a time)
    C.set_status(job.dir, 'check', 'running', 'Checking the drafts in Chromium.')
    cands = []
    for n, (src, m) in sorted(drafts.items()):
        cands.append(run_candidate(job, n, src, m, slog['rounds'])); job.write('spec_log.json', slog)
    alive = [c for c in cands if c['report']['ok']]
    summary = '; '.join(f"{c['name'].upper()}: {'passes' if c['report']['ok'] else str(len(c['report']['hard'])) + ' errors left'}" for c in cands)
    if not alive:
        best = min(cands, key=lambda c: badness(c['report']))
        slog['final'] = {'ok': False, 'candidate': best['name'], 'hard': best['report']['hard'][:20]}; job.write('spec_log.json', slog)
        C.set_status(job.dir, 'check', 'failed', f'No draft passed the checks after {MAX_REPAIR} repairs ({summary}). First error: {best["report"]["hard"][0][:200]}')
        raise SystemExit(1)
    C.set_status(job.dir, 'check', 'done', summary + '.')
    # 5. eyes, then one compose round
    C.set_status(job.dir, 'eyes', 'running', 'The eyes are comparing the drafts.')
    verdict = look.score(job, [{'name': c['name'], 'sheet': c['sheet'], 'report': c['report']} for c in alive])
    slog['eyes'] = verdict; job.write('spec_log.json', slog)
    win = next(c for c in alive if c['name'] == verdict['winner'])
    fixes = next((c['fixes'] for c in verdict['candidates'] if c['name'] == win['name']), []) or []
    final_src, final_rep, composed = win['src'], win['report'], False
    todo = fixes + fixable_soft(win['report'])
    if todo:
        C.set_status(job.dir, 'eyes', 'running', f'Draft {win["name"].upper()} wins; composing {len(todo)} fixes from the eyes.', commit=False)
        try:
            new, used, fails, note = repair(job, win['src'], todo, win['model'], 'compose', extra='These are notes from the picture editor who watched the contact sheet. '
                                            'Apply the ones you can do with the engine; keep everything that already works.')
            if new != win['src']:
                open(job.p('cand', 'final.js'), 'w').write(new)
                rep = check(job, './cand/final.js', 'final')
                slog['compose'] = {'model': used, 'failed_edits': fails, 'note': note, 'ok': rep['ok'], 'hard': rep['hard'][:20], 'soft': rep.get('soft', [])[:20]}
                if rep['ok'] and len(fixable_soft(rep)) <= len(fixable_soft(win['report'])) + 1:
                    final_src, final_rep, composed = new, rep, True
        except C.OverBudget: raise
        except Exception as e:
            slog['compose'] = {'error': str(e)[:300]}; C.log('compose failed:', str(e)[:300])
    if not composed:   # the final check folder is the winner's
        shutil.rmtree(job.p('check', 'final'), ignore_errors=True); shutil.copytree(job.p('check', win['name']), job.p('check', 'final'))
        if os.path.exists(job.p('cand', 'final.js')): os.rename(job.p('cand', 'final.js'), job.p('cand', 'final-rejected.js'))
    open(job.p('spec.js'), 'w').write(final_src)
    score = next((c.get('total') for c in verdict['candidates'] if c['name'] == win['name']), None)
    slog['final'] = {'ok': True, 'candidate': win['name'], 'model': win['model'], 'composed': composed, 'score': score, 'soft': final_rep.get('soft', [])[:20],
                     'still_s': final_rep.get('still_s'), 'bytes': len(final_src)}
    job.write('spec_log.json', slog)
    C.set_status(job.dir, 'eyes', 'done', f'Draft {win["name"].upper()} ({win["model"]}) wins' + (f' at {score}/10' if score is not None else '') +
                 (', fixes composed and re-checked.' if composed else ', kept as checked.'),
                 outputs={'spec': C.rel(job.p('spec.js')), 'check_sheet': C.rel(job.p('check', 'final', 'sheet.jpg'))})


if __name__ == '__main__':
    main(sys.argv[1])
