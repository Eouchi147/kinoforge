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
Writes spec.js (the winner; spec.json on a Blender line, see blender_line.py), cand/*.js, check/<name>/report.json + sheet.jpg, spec_log.json (every round, every model, scores).
"""
import os, sys, json, re, shutil, subprocess, threading, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import look
import blender_line as BL

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
    L = job.line; sf, lang = spec_name(job)
    what = ("A spec is one JSON object (data only, no code) in the format of the SPEC.md below that drives a whole film from the narration's cue "
            "times: the engine builds the worlds, cameras, eggs, animals and words from it." if lang == 'json' else
            "A spec is one ES module, `export default { ... };`, that drives a whole film from the narration's cue times.")
    parts = [
        f"You write spec files for the KINOFORGE {L['series']} engine ({L['engine']}, {L['aspect']}, rendered at {L['render'][0]}x{L['render'][1]}, 24 fps). "
        + what + " The picture follows the sound: never change timing, only refer to cue times.",
        '# The engine: SPEC.md\n' + rd(L['spec_md'])]
    if C.craft(): parts.append("# The studio's craft rules (CRAFT.md; Sam's words are the ground truth; the checks enforce section 9)\n" + C.craft())
    for k, ex in enumerate(L['examples']):
        exc = json.load(open(os.path.join(C.ROOT, ex, 'cues.json')))
        parts.append(f"# Example film {k + 1}: {exc.get('title', ex)} ({ex})\n## Its narration (cues)\n{cue_lines(exc, words=False)}\n## Its {sf}\n```{lang}\n{rd(ex + '/' + sf)}\n```")
    if L.get('style_refs'): parts.append('# Look reference (hand-built, not a spec): ' + ', '.join(L['style_refs']) + '. Match its restraint and rhythm.')
    parts.append('Note: the example films were made before CRAFT.md. Learn the engine from them, not the craft: do not copy their '
                 'clip-art icons, their missing scene list or their fast camera moves.')
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


def eyes(job, cands):
    """The eyes on the candidates' contact sheets; with no sheet at all (Blender could not render one) the code checks decide."""
    if any(c.get('sheet') and os.path.exists(c['sheet']) for c in cands): return look.score(job, cands)
    return look.fallback(cands, 'no contact sheet could be rendered: the code checks decide')


def spec_name(job):
    """(spec file name, code fence language) of the job's line: spec.js for the web engines, spec.json (data) for Blender lines."""
    sf = BL.spec_file(job.line); return sf, ('json' if sf.endswith('.json') else 'js')


def code_of(job, text):
    return BL.json_block(text) if spec_name(job)[1] == 'json' else C.code_block(text)


def draft_problem(job, text):
    if spec_name(job)[1] == 'json': return BL.json_problem(text)
    return None if 'export default' in C.code_block(text) else 'no `export default` module in the reply'


def draft_prompt(job):
    if spec_name(job)[1] == 'json':
        return [{'role': 'system', 'content': context(job)},
                {'role': 'user', 'content': job_text(job) + f"\n\nWrite the complete spec.json for this film ({job.line['aspect']}), at the quality of the example. "
                 "Reply with the whole JSON object in ONE ```json fenced block and nothing after it."}]
    return [{'role': 'system', 'content': context(job)},
            {'role': 'user', 'content': job_text(job) + "\n\nWrite the complete spec.js for this film, at the quality of the examples. Reply with the whole module "
             "in ONE ```js fenced block and nothing after it."}]


def spec_models(job):
    """The draft models. Paid mode: the main draft by the `coder` role (Opus); a second draft by `coder2` (Sonnet) only when
    the cap still leaves room for the repairs, the eyes and the lessons (config.json estimate_usd). Free mode: two free code
    models from different providers. brief.seats.spec = [roleA, roleB] overrides."""
    over = job.brief.get('seats', {}).get('spec')
    if C.FREE_ONLY:
        seats = over or ['coder', 'coder']
    else:
        E = C.CONFIG.get('estimate_usd', {}); scale = job.brief['target_seconds'] / 150
        rest = (E.get('repair', 0.12) * 3 + E.get('eyes', 0.05) * 2 + E.get('reflect', 0.01)) * scale
        two = job.ledger.total + 2 * E.get('spec_draft', 0.5) * scale + rest <= job.brief['cap_usd']
        seats = over or (['coder', 'coder2'] if two else ['coder'])
    out, used = [], set()
    for s_ in seats:
        ms = C.seat_models(s_)
        pick = next((m for m in ms if C.provider(m) not in used and all(m != x[1] for x in out)), None) if C.FREE_ONLY else \
               next((m for m in ms if all(m != x[1] for x in out)), None)
        if pick: out.append((s_, pick)); used.add(C.provider(pick))
    if C.FREE_ONLY and len(out) < 2:   # not enough providers: allow the same provider, different model
        for m in C.seat_models('coder'):
            if all(m != x[1] for x in out): out.append(('coder', m))
            if len(out) == 2: break
    return out[:2]


def check(job, spec_rel, name, max_stills=None):
    """Run check.cjs (the line's validator for a Blender line); returns the report dict."""
    if BL.is_blender(job.line): return BL.check(job, spec_rel, name)
    max_stills = max_stills or int(os.environ.get('KF_CHECK_MAX', 28))
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
    return [s for s in rep.get('soft', []) if not s.startswith(('lint warning', 'engine warning', 'note:'))]


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
            {'role': 'user', 'content': job_text(job) + f"\n\n# The current {spec_name(job)[0]}\n```{spec_name(job)[1]}\n{src}\n```\n\n# Problems found by the checks\n" +
             '\n'.join('- ' + p for p in problems[:40]) + (f"\n\n{extra}" if extra else '') +
             "\n\nFix every problem with the smallest edits. Return edits: each `find` is an exact, unique snippet of the current spec (copy it "
             "verbatim, include enough of the line to be unique) and `replace` is the new text. Do not rewrite parts that work."}]
    seat = job.brief.get('seats', {}).get('repair', 'coder' if C.FREE_ONLY else 'repair')
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
    ext = os.path.splitext(spec_name(job)[0])[1]
    path = job.p('cand', f'{name}{ext}'); rel = f'./cand/{name}{ext}'
    best = None; carry = []
    for r in range(MAX_REPAIR + 1):
        open(path, 'w').write(src)
        rep = check(job, rel, name)
        rec = {'round': r, 'ok': rep['ok'], 'hard': rep['hard'][:30], 'soft': rep.get('soft', [])[:30], 'bytes': len(src), 'check_s': rep.get('check_s'),
               'ready_s': rep.get('ready_s'), 'still_s': rep.get('still_s')}
        log.append({'candidate': name, **rec}); C.log(f'{name} round {r}: ok={rep["ok"]} hard={len(rep["hard"])} soft={len(rep.get("soft", []))}')
        if best is None or badness(rep) < badness(best['report']):
            best = {'src': src, 'report': rep, 'round': r}
            shutil.copy(path, job.p('cand', f'{name}.best{ext}'))
            if os.path.exists(job.p('check', name)):
                shutil.rmtree(job.p('check', f'{name}.best'), ignore_errors=True); shutil.copytree(job.p('check', name), job.p('check', f'{name}.best'))
        C.set_status(job.dir, 'check', 'running', f'Draft {name.upper()}, round {r}: {len(rep["hard"])} errors, {len(fixable_soft(rep))} layout problems.', commit=False)
        problems = rep['hard'] + fixable_soft(rep)
        if not problems or r == MAX_REPAIR: break
        if rep['ok'] and r >= 2: break   # it ships; layout polish is left to the compose round
        if not rep['ok']: problems += [s for s in rep.get('soft', []) if s.startswith(('lint warning', 'engine warning'))][:8]
        got = None
        for attempt in range(4):   # free models are rate limited and overloaded at times: wait and try again
            try:
                got = repair(job, src, problems + carry, model, f'repair {name} {r + 1}'); break
            except C.OverBudget: raise
            except Exception as e:
                log.append({'candidate': name, 'repair': r + 1, 'attempt': attempt, 'error': str(e)[:300]}); C.log('repair failed:', str(e)[:300])
                if not re.search(r'429|503|overloaded|rate limit', str(e)) or attempt == 3: break
                C.set_status(job.dir, 'check', 'running', f'Draft {name.upper()}, repair {r + 1}: the free models are busy, waiting {90 * (attempt + 1)} s.', commit=False)
                time.sleep(90 * (attempt + 1))
        if not got:
            rep['hard'] = rep['hard'] + [f'repair {r + 1} could not run: the free models did not answer (see the log)']; best['report'] = best['report'] if best else rep
            break
        src, model, fails, note = got
        carry = [f'(from your last edits) {f}' for f in fails]
        log.append({'candidate': name, 'repair': r + 1, 'model': model, 'failed_edits': fails, 'note': note})
    shutil.copy(job.p('cand', f'{name}.best{ext}'), path)
    if os.path.exists(job.p('check', f'{name}.best')):
        shutil.rmtree(job.p('check', name), ignore_errors=True); shutil.move(job.p('check', f'{name}.best'), job.p('check', name))
    os.remove(job.p('cand', f'{name}.best{ext}'))
    if BL.is_blender(job.line) and best['report']['ok']:   # the eyes need pictures: a low-resolution contact sheet rendered in Blender
        C.set_status(job.dir, 'check', 'running', f'Draft {name.upper()} passes; rendering its check stills in Blender.', commit=False)
        BL.stills(job, rel, name)
    return {'name': name, 'model': model, 'src': best['src'], 'report': best['report'], 'best_round': best['round'], 'sheet': job.p('check', name, 'sheet.jpg')}


def main(d):
    job = C.Job(d); BL.apply_format(job); sf, lang = spec_name(job); ext = os.path.splitext(sf)[1]
    if not job.has('cues.json'): raise RuntimeError('no cues.json: run the sound stage first')
    log_path = job.p('spec_log.json'); slog = job.read('spec_log.json', {'rounds': []})
    if job.has(sf) and slog.get('final', {}).get('ok'):
        C.log('spec exists and passed its checks, skipped'); return
    os.makedirs(job.p('cand'), exist_ok=True)
    # 3. probe: two drafts in parallel
    models = spec_models(job)
    C.set_status(job.dir, 'spec', 'running', ('Two coders are drafting the picture: ' if len(models) > 1 else 'The coder is drafting the picture: ') + ', '.join(m for _, m in models) + '.')
    msgs = draft_prompt(job); drafts = {}; errs = {}
    def draft(name, seat, model):
        try:
            text, used = C.complete(seat, msgs, job.ledger, max_tokens=28000, only=model, label=f'spec draft {name}',
                                    validate=lambda t: draft_problem(job, t))
            drafts[name] = (code_of(job, text), used)
        except Exception as e: errs[name] = e
    names = ['a', 'b'][:len(models)]
    th = [threading.Thread(target=draft, args=(n, s, m)) for n, (s, m) in zip(names, models)]
    for t in th: t.start()
    for t in th: t.join()
    for n, e in errs.items():
        if isinstance(e, C.OverBudget): raise e
        C.log(f'draft {n} failed: {str(e)[:300]}')
    for attempt in range(4):   # no draft yet: down the coder chain again, waiting longer each time (rate limits, overload)
        if drafts: break
        if attempt: C.set_status(job.dir, 'spec', 'running', f'The free models are busy; trying again in {120 * attempt} s.', commit=False); time.sleep(120 * attempt)
        try:
            text, used = C.complete('coder', msgs, job.ledger, max_tokens=28000, label='spec draft (fallback)',
                                    validate=lambda t: draft_problem(job, t))
            drafts['a'] = (code_of(job, text), used)
        except C.OverBudget: raise
        except Exception as e:
            C.log('fallback draft failed:', str(e)[:300])
            if attempt == 3: raise
    for n, (src, m) in drafts.items(): open(job.p('cand', f'{n}{ext}'), 'w').write(src)
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
        C.set_status(job.dir, 'check', 'failed', f'No draft passed the checks ({summary}; at most {MAX_REPAIR} repairs each). First error: {best["report"]["hard"][0][:200]}')
        raise SystemExit(1)
    C.set_status(job.dir, 'check', 'done', summary + '.')
    # 5. eyes, then compose rounds; Gate 2: the picture must reach the eyes score threshold before any render
    G = C.GATES; need = float(G.get('eyes_min_score', 6.5)); E = C.CONFIG.get('estimate_usd', {})
    C.set_status(job.dir, 'eyes', 'running', 'The eyes are comparing the drafts.' if len(alive) > 1 else 'The eyes are reviewing the draft.')
    verdict = eyes(job, [{'name': c['name'], 'sheet': c['sheet'], 'report': c['report']} for c in alive])
    slog['eyes'] = verdict; job.write('spec_log.json', slog)
    win = next(c for c in alive if c['name'] == verdict['winner'])
    sc = lambda v, n: next((c.get('total') for c in v['candidates'] if c['name'] == n), None)
    fx = lambda v, n: next((c.get('fixes') for c in v['candidates'] if c['name'] == n), []) or []
    cur = {'src': win['src'], 'report': win['report'], 'dir': win['name'], 'score': sc(verdict, win['name']), 'fixes': fx(verdict, win['name'])}
    slog['compose'] = []
    for r in range(int(G.get('compose_rounds', 2))):
        todo = cur['fixes'] + fixable_soft(cur['report'])
        good = cur['score'] is not None and cur['score'] >= need
        if not todo or (r > 0 and good): break
        if not C.FREE_ONLY and job.ledger.total + E.get('repair', 0.12) + E.get('eyes', 0.05) > job.brief['cap_usd']:
            slog['compose'].append({'round': r, 'skipped': 'no room left in the cap'}); break
        C.set_status(job.dir, 'eyes', 'running', f'Composing {len(todo)} fixes from the eyes (round {r + 1}).', commit=False)
        try:
            new, used, fails, note = repair(job, cur['src'], todo, win['model'], f'compose {r + 1}', extra='These are notes from the picture editor who watched the contact sheet. '
                                            'Apply the ones you can do with the engine; keep everything that already works.')
        except C.OverBudget: raise
        except Exception as e:
            slog['compose'].append({'round': r, 'error': str(e)[:300]}); C.log('compose failed:', str(e)[:300]); break
        if new == cur['src']: break
        name = f'compose{r + 1}'; open(job.p('cand', f'{name}{ext}'), 'w').write(new)
        rep = check(job, f'./cand/{name}{ext}', name)
        if rep['ok'] and BL.is_blender(job.line): BL.stills(job, f'./cand/{name}{ext}', name)
        rec = {'round': r, 'model': used, 'failed_edits': fails, 'note': note, 'ok': rep['ok'], 'hard': rep['hard'][:20], 'soft': rep.get('soft', [])[:20]}
        if not rep['ok']: rec['kept'] = False; slog['compose'].append(rec); break
        v2 = eyes(job, [{'name': name, 'sheet': job.p('check', name, 'sheet.jpg'), 'report': rep}]); s2 = sc(v2, name)
        rec.update(score=s2, before=cur['score'])
        if cur['score'] is None or (s2 is not None and s2 >= cur['score']):
            cur = {'src': new, 'report': rep, 'dir': name, 'score': s2, 'fixes': fx(v2, name)}; rec['kept'] = True
        else: rec['kept'] = False
        slog['compose'].append(rec); job.write('spec_log.json', slog)
        if not rec['kept']: break
    shutil.rmtree(job.p('check', 'final'), ignore_errors=True); shutil.copytree(job.p('check', cur['dir']), job.p('check', 'final'))
    score = cur['score']; composed = cur['dir'] != win['name']
    passed = (score is not None and score >= need) or (score is None and C.FREE_ONLY)
    slog['final'] = {'ok': passed, 'candidate': win['name'], 'model': win['model'], 'composed': composed, 'score': score, 'need': need,
                     'soft': cur['report'].get('soft', [])[:20], 'still_s': cur['report'].get('still_s'), 'bytes': len(cur['src'])}
    job.write('spec_log.json', slog)
    if not passed:
        open(job.p('cand', f'best-unapproved{ext}'), 'w').write(cur['src'])
        C.set_status(job.dir, 'eyes', 'failed', 'Stopped at the picture gate, so no render: ' + (f'the eyes scored it {score}/10 (it needs {need}).' if score is not None
                     else 'the eyes model could not score it.') + ' The best version and its contact sheet are kept for a look.',
                     outputs={'check_sheet': C.rel(job.p('check', 'final', 'sheet.jpg'))})
        raise SystemExit(1)
    open(job.p(sf), 'w').write(cur['src'])
    C.set_status(job.dir, 'eyes', 'done', f'Draft {win["name"].upper()} ({win["model"]}) wins' + (f' at {score}/10' if score is not None else '') +
                 (', fixes composed and re-checked.' if composed else ', kept as checked.'),
                 outputs={'spec': C.rel(job.p(sf)), 'check_sheet': C.rel(job.p('check', 'final', 'sheet.jpg')), 'eyes_score': score,
                          **({'render_cost': cur['report'].get('cost')} if BL.is_blender(job.line) else {})})


if __name__ == '__main__':
    main(sys.argv[1])
