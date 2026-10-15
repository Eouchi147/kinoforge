"""showrunner.py — turns an approved brief into a reviewed pre-production package, with a capped budget.

    python3 harness/director/showrunner.py films/<id>            (needs OPENROUTER_API_KEY)
    python3 harness/director/showrunner.py films/<id> --dry      (no model calls: checks the pipeline wiring)

The chain of command
  HEAD    plans the film (direction, style, narrator, notes per stage), then makes the final review of everything.
  CREW    drafts each stage: three cheap strong models in parallel, so one bad draft never decides the film.
  CHECKS  code checks every draft first (timings, coverage, word counts, causality links); free, exact, instant.
  DEPUTY  reviews the drafts that pass, keeps the best, sends it back with concrete fixes when it is not good enough.
  LOOPS   at most crew.json caps.max_loops revisions per stage and per final review. Then the head either passes the
          film or writes ONE precise question for Sam. Never an endless loop.
  MONEY   every call is booked in films/<id>/ledger.json; a call that could pass the film cap is refused; the day cap
          and the key's own limit are checked before starting.

Stages (in order): story → script → shots → sound → style. Outputs: films/<id>/{plan,story,script,shots,sound,style}.json,
PLAN.md (the readable version), status.json (what the studio shows), and the narration job voice/jobs/<id>.json.
"""
import os, sys, json, re, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agents import ask, fan_out, seat, Ledger, account, CREW, ROOT, OverBudget, AllFailed

FPS = 24
CAPS = CREW['caps']
STYLES = dict(re.findall(r"name: '([^']+)'.*?motion: '([^']+)'", open(os.path.join(ROOT, 'studio-web', 'lib', 'data.js')).read()))
PLAYBOOK = open(os.path.join(ROOT, 'docs', 'SHOWRUNNER_PLAYBOOK.md')).read()
RULES = """Studio rules (blockers above all others):
1. Common sense: complete anatomy; grounded things touch the ground; nobody moves backwards to where they face; every story action is visible and readable on a phone; continuity between shots; nothing stray or meaningless.
2. Polish: clean, smooth, harmonious; nothing harsh or clunky unless the style intends it.
3. One original story per film: no templates, nothing mass-produced. No real people, no existing characters or brands. Kids' films stay kind and safe.
4. Story: hook in the first 3 s; every beat causes the next ("but" / "therefore"); a turn at about 70%; every payoff set up on screen at least 15% of the runtime earlier; an ending image that rhymes with or inverts the opening.
5. Narration is minimal and wise: it never describes what the picture already shows; it adds meaning. Never stretch a line to fill time."""

def strs(**kv): return {k: {'type': 'string', 'description': v} for k, v in kv.items()}
def obj(props, req=None): return {'type': 'object', 'additionalProperties': False, 'required': req or list(props), 'properties': props}
def arr(item): return {'type': 'array', 'items': item}
NUM = {'type': 'number'}

# ------------------------------------------------------------------ schemas
PLAN = obj({
    **strs(direction='3 to 5 sentences: tone, look, feel, what makes this film special', story_spine='the story in 4 sentences: setup, but, therefore, ending',
           style_why='one sentence'),
    'style': {'type': 'string', 'enum': list(STYLES)}, 'length_s': NUM,
    'narrator': obj({'use': {'type': 'boolean'}, **strs(persona='who narrates and how they sound (one sentence)',
                     omni_design='voice design tags for the speech engine, comma separated: gender, age (child/young adult/middle-aged/elderly), pitch (low/moderate/high pitch), accent (e.g. british accent)')}),
    'notes': obj(strs(story='direction for the story writers', script='direction for the narration writers', shots='direction for the shot designers',
                      sound='direction for the sound designers', style='direction for the look')),
    'risks': arr({'type': 'string'}), 'acceptance': arr({'type': 'string'}),
})
BEAT = obj({'id': {'type': 'string'}, 'start': NUM, 'end': NUM, **strs(see='what is on screen: who, where, doing what; a frame description', purpose='what this beat does for the story'),
            'link': {'type': 'string', 'enum': ['open', 'but', 'therefore']}})
STORY = obj({**strs(logline='one sentence, under 25 words', hook='what we see in the first 3 seconds', ending_image='the last image', opening_rhyme='how the ending rhymes with or inverts the opening', turn_beat='id of the turning-point beat'),
             'beats': arr(BEAT), 'characters': arr(obj(strs(name='', look='silhouette-readable design', want='', flaw='', voice='instrument voice for the score'))),
             'setups': arr(obj(strs(setup_beat='beat id', payoff_beat='beat id', what='what is set up and paid off')))})
SCRIPT = obj({'narrated': {'type': 'boolean'}, 'lines': arr(obj({'id': {'type': 'string'}, 'text': {'type': 'string'}, 'start': NUM, 'end': NUM,
                                                                  'tone': {'type': 'string'}, 'wpm_lo': NUM, 'wpm_hi': NUM}))})
SIZES = ['extreme wide', 'wide', 'medium', 'close-up', 'extreme close-up', 'insert']
SHOTS = obj({'shots': arr(obj({'id': {'type': 'string'}, 'start': NUM, 'end': NUM, 'beat': {'type': 'string'}, 'size': {'type': 'string', 'enum': SIZES},
                               **strs(move='camera move, or "locked"', motivation='why the camera does this', frame='what the frame shows')})),
             'cues': arr(obj({'frame': {'type': 'integer'}, 'event': {'type': 'string'}}))})
SOUND = obj({'music': arr(obj({'start': NUM, 'end': NUM, **strs(mood='', instruments='')})), 'voices': arr(obj(strs(character='', instrument=''))),
             'sfx': arr(obj({'t': NUM, 'length': NUM, 'sound': {'type': 'string'}})), 'mix_notes': {'type': 'string'}})
STYLE = obj({'pack': {'type': 'string', 'enum': list(STYLES)}, **strs(motion_profile='how things move in this film', lighting='', textures='', camera_rules=''),
             'palette': arr(obj(strs(name='', hex='#rrggbb'))), 'forbid': arr({'type': 'string'})})
REVIEW = obj({'best': {'type': 'integer', 'description': 'index of the best draft (0-based)'}, 'score': {'type': 'number', 'description': '0 to 10 against the brief, the plan and the rules'},
              'blockers': arr({'type': 'string'}), 'fixes': arr({'type': 'string', 'description': 'a concrete change, not a vague wish'})})
FINAL = obj({'verdict': {'type': 'string', 'enum': ['pass', 'fix']}, 'score': NUM,
             'fixes': arr(obj({'stage': {'type': 'string', 'enum': ['story', 'script', 'shots', 'sound', 'style']}, **strs(problem='', fix='')})),
             'question_for_sam': {'type': ['string', 'null'], 'description': 'only if you cannot decide without him: one precise question'},
             'summary_for_sam': {'type': 'string', 'description': 'two plain sentences: what this film is and why it will work'}})

# ------------------------------------------------------------------ code checks (free, exact)
def contiguous(items, length, what):
    p = []
    if not items: return [f'no {what}']
    items = sorted(items, key=lambda x: x['start'])
    if abs(items[0]['start']) > 0.05: p.append(f'the first {what[:-1]} must start at 0 s')
    for a, b in zip(items, items[1:]):
        if abs(a['end'] - b['start']) > 0.05: p.append(f'{what} {a["id"]} ends at {a["end"]} s but {b["id"]} starts at {b["start"]} s: no gaps or overlaps')
    if abs(items[-1]['end'] - length) > 1.0: p.append(f'the last {what[:-1]} ends at {items[-1]["end"]} s; the film is {length} s')
    for x in items:
        if x['end'] <= x['start']: p.append(f'{what[:-1]} {x["id"]} ends before it starts')
    return p

def check_story(d, ctx):
    L = ctx['length']; p = contiguous(d['beats'], L, 'beats'); ids = [b['id'] for b in d['beats']]
    if d['beats'] and d['beats'][0]['link'] != 'open': p.append('the first beat link must be "open"')
    p += [f'beat {b["id"]} must link with "but" or "therefore"' for b in d['beats'][1:] if b['link'] == 'open']
    if d['beats'] and d['beats'][0]['end'] > 6: p.append('the hook beat is too long: the first beat must land within 3 to 6 s')
    tb = next((b for b in d['beats'] if b['id'] == d['turn_beat']), None)
    if not tb: p.append(f'turn_beat "{d["turn_beat"]}" is not a beat id')
    elif not 0.5 * L <= tb['start'] <= 0.85 * L: p.append(f'the turn starts at {tb["start"]} s; it should sit between {0.5 * L:.0f} and {0.85 * L:.0f} s (about 70%)')
    start = {b['id']: b['start'] for b in d['beats']}
    for s in d['setups']:
        if s['setup_beat'] not in start or s['payoff_beat'] not in start: p.append(f'setup "{s["what"]}" names a beat that does not exist'); continue
        if start[s['payoff_beat']] - start[s['setup_beat']] < 0.15 * L: p.append(f'"{s["what"]}" is paid off too soon after it is set up (needs {0.15 * L:.0f} s or more)')
    if not d['characters']: p.append('no characters')
    if len(d['logline'].split()) > 28: p.append('the logline is longer than 25 words')
    return p

def check_script(d, ctx):
    p, L, use = [], ctx['length'], ctx['plan']['narrator']['use']
    if use and not d['lines']: p.append('the plan has a narrator but the script has no lines')
    if not use and d['lines']: p.append('the plan has no narrator; leave lines empty')
    lines = sorted(d['lines'], key=lambda l: l['start'])
    for a, b in zip(lines, lines[1:]):
        if a['end'] > b['start'] - 0.3: p.append(f'line {a["id"]} runs into {b["id"]}: leave at least 0.3 s between lines')
    for l in lines:
        words = len(re.findall(r"[A-Za-z0-9']+", l['text'])); win = l['end'] - l['start']
        if l['start'] < 0 or l['end'] > L: p.append(f'line {l["id"]} is outside the film (0 to {L} s)')
        if not 80 <= l['wpm_lo'] < l['wpm_hi'] <= 185: p.append(f'line {l["id"]}: the pace range must sit inside 80 to 185 words per minute')
        need = words * 60 / max(l['wpm_hi'], 1) + 0.3
        if need > win: p.append(f'line {l["id"]} has {words} words: even at {l["wpm_hi"]:.0f} wpm it needs {need:.1f} s but its window is {win:.1f} s. Shorten the line or widen the window')
        if words > 30: p.append(f'line {l["id"]} is too long for one breath ({words} words); split it')
    total = sum(len(re.findall(r"[A-Za-z0-9']+", l['text'])) for l in lines)
    if total > L * 1.6: p.append(f'too much narration ({total} words in {L} s): narration must be minimal')
    return p

def check_shots(d, ctx):
    L = ctx['length']; p = contiguous(d['shots'], L, 'shots')
    p += [f'shot {s["id"]} is shorter than 1 s' for s in d['shots'] if s['end'] - s['start'] < 1.0]
    beats = {b['id'] for b in ctx['done']['story']['beats']}
    p += [f'shot {s["id"]} names beat "{s["beat"]}" which does not exist' for s in d['shots'] if s['beat'] not in beats]
    p += [f'beat {b} has no shot' for b in beats - {s['beat'] for s in d['shots']}]
    p += [f'cue at frame {c["frame"]} is outside the film' for c in d['cues'] if not 0 <= c['frame'] <= L * FPS]
    return p

def check_sound(d, ctx):
    L = ctx['length']; p = []
    p += [f'sound "{s["sound"]}" at {s["t"]} s needs a length between 0.1 and 8 s' for s in d['sfx'] if not 0.1 <= s['length'] <= 8]
    p += [f'sound "{s["sound"]}" at {s["t"]} s is outside the film' for s in d['sfx'] if not 0 <= s['t'] <= L]
    covered = sum(max(0, min(m['end'], L) - max(m['start'], 0)) for m in d['music'])
    if covered < 0.75 * L: p.append(f'music covers only {covered:.0f} of {L} s; the score should carry the film')
    chars = {c['name'] for c in ctx['done']['story']['characters']}
    p += [f'character {c} has no instrument voice' for c in chars - {v['character'] for v in d['voices']}]
    return p

def check_style(d, ctx):
    p = [f'colour "{c["name"]}" is not a valid hex' for c in d['palette'] if not re.fullmatch(r'#[0-9a-fA-F]{6}', c['hex'])]
    if not 4 <= len(d['palette']) <= 8: p.append('the palette needs 4 to 8 colours')
    if d['pack'] != ctx['plan']['style']: p.append(f'the plan chose {ctx["plan"]["style"]}; the style pack must match')
    return p

STAGES = {
    'story':  (STORY, check_story,  'Write the story: beats with start/end seconds covering the whole film, characters, set-ups and pay-offs, the turn, the ending image.'),
    'script': (SCRIPT, check_script, 'Write the narration: few lines, each in its own time window between beats it adds meaning to. Give each line a tone direction and a target pace (wpm_lo, wpm_hi).'),
    'shots':  (SHOTS, check_shots,  'Design the shots: contiguous shots covering the whole film, each tied to a beat, with size, move and motivation. Add cues (frame numbers at 24 fps) for every key action.'),
    'sound':  (SOUND, check_sound,  'Design the sound: music cues covering the film, an instrument voice per character, every effect with a time and a length.'),
    'style':  (STYLE, check_style,  'Define the look: the style pack, how things move, lighting, textures, camera rules, a 4 to 8 colour palette, and a forbid list.'),
}
ORDER = list(STAGES)

# ------------------------------------------------------------------ the loop
def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

def context(ctx, upto):
    done = {k: v for k, v in ctx['done'].items() if k in ORDER[:ORDER.index(upto)]}
    return (f"Brief (approved by Sam): {json.dumps(ctx['brief'])}\n\nThe head's plan: {json.dumps(ctx['plan'])}\n\n"
            + (f"Approved stages so far: {json.dumps(done)}\n\n" if done else '') + f"Film length: {ctx['length']} s at {FPS} fps.")

def crew_msgs(ctx, name, extra=''):
    schema, _, task = STAGES[name]
    return [{'role': 'system', 'content': f'You are on the crew of KINOFORGE, an animation studio. You draft one stage of a film for the head director.\n{RULES}\nStyle packs: ' + '; '.join(f'{k} ({v})' for k, v in STYLES.items())},
            {'role': 'user', 'content': f"{context(ctx, name)}\n\nThe head's note for this stage: {ctx['plan']['notes'][name]}\n\nYour task: {task}{extra}\nReply with the JSON object only."}]

def stage(ctx, name, fixes=None):
    schema, check, _ = STAGES[name]; book = ctx['ledger']; loops = CAPS['max_loops']
    extra = ('\n\nThe head sent this stage back. Fix exactly these problems:\n- ' + '\n- '.join(fixes) + f"\nThe previous version: {json.dumps(ctx['done'][name])}") if fixes else ''
    drafts = fan_out('crew', 3, crew_msgs(ctx, name, extra), schema, book, name=name, max_tokens=3500, label=f'{name}: draft')
    drafts = [(d, m, check(d, ctx)) for d, m in drafts]
    log(f'{name}: {len(drafts)} drafts, code-check problems {[len(p) for _, _, p in drafts]}')
    # code problems first: the crew fixes them for free-ish before any reviewer reads the draft
    for i, (d, m, probs) in enumerate(drafts):
        k = 0
        while probs and k < loops:
            fix = '\n\nYour draft failed these checks. Return the corrected full JSON:\n- ' + '\n- '.join(probs[:12]) + f'\nYour draft: {json.dumps(d)}'
            try: d, m = ask('crew', crew_msgs(ctx, name, extra + fix), schema, book, name=name, max_tokens=3500, only=m, label=f'{name}: self-fix')
            except (AllFailed, ValueError): break
            probs = check(d, ctx); k += 1
        drafts[i] = (d, m, probs)
    drafts.sort(key=lambda x: len(x[2]))
    drafts = drafts[:3]
    review_log = []
    for rnd in range(loops + 1):
        listing = '\n\n'.join(f'DRAFT {i} (by {m}; code checks: {"pass" if not p else "; ".join(p[:6])}):\n{json.dumps(d)}' for i, (d, m, p) in enumerate(drafts))
        msgs = [{'role': 'system', 'content': f'You are the deputy director of KINOFORGE. You review crew drafts against the brief, the plan and the rules, strictly but fairly.\n{RULES}'},
                {'role': 'user', 'content': f'{context(ctx, name)}\n\nStage: {name}. The head\'s note: {ctx["plan"]["notes"][name]}\n\n{listing}\n\nPick the best draft, score it 0-10, list blockers (rule breaks, nonsense, anything a viewer would notice) and concrete fixes. 8 or more with no blockers means it is ready.'}]
        r, rm = ask('deputy', msgs, REVIEW, book, name='review', max_tokens=1500, label=f'{name}: review {rnd}')
        best = drafts[min(max(r['best'], 0), len(drafts) - 1)]
        review_log.append({'round': rnd, 'by': rm, 'score': r['score'], 'blockers': r['blockers'], 'fixes': r['fixes'], 'draft_by': best[1]})
        log(f'{name}: review {rnd} by {rm}: {r["score"]}/10, {len(r["blockers"])} blockers')
        if (r['score'] >= 8 and not r['blockers'] and not best[2]) or rnd == loops: break
        fix = '\n\nThe deputy director sent your draft back. Apply these fixes and return the full corrected JSON:\n- ' + '\n- '.join(r['blockers'] + r['fixes'] + best[2]) + f'\nThe draft: {json.dumps(best[0])}'
        try: d, m = ask('crew', crew_msgs(ctx, name, extra + fix), schema, book, name=name, max_tokens=3500, label=f'{name}: revise {rnd}')
        except AllFailed: break
        drafts = [(d, m, check(d, ctx))]
    ctx['done'][name] = best[0]; ctx['reviews'][name] = review_log
    return best[0]

def head_plan(ctx):
    msgs = [{'role': 'system', 'content': f'You are the head director (Showrunner) of KINOFORGE. You plan the film your crew will build.\n{RULES}\n\nThe studio playbook:\n{PLAYBOOK}'},
            {'role': 'user', 'content': f"Sam approved this brief: {json.dumps(ctx['brief'])}\n\nStyle packs and their motion: " + '; '.join(f'{k} ({v})' for k, v in STYLES.items())
             + "\n\nMake the plan: creative direction, the story spine, the style pack, the narrator (keep the brief's narrator unless it breaks a rule), a note for each stage, risks to watch, and what 'done' means (acceptance)."}]
    return ask('head', msgs, PLAN, ctx['ledger'], name='plan', max_tokens=2500, label='plan')

def head_final(ctx):
    msgs = [{'role': 'system', 'content': f'You are the head director (Showrunner) of KINOFORGE, making the final review before the film goes into production.\n{RULES}'},
            {'role': 'user', 'content': f"Brief: {json.dumps(ctx['brief'])}\n\nYour plan: {json.dumps(ctx['plan'])}\n\nThe package:\n" + '\n\n'.join(f'{k.upper()}: {json.dumps(v)}' for k, v in ctx['done'].items())
             + f"\n\nThe deputy's review notes: {json.dumps({k: v[-1] for k, v in ctx['reviews'].items()})}"
             + '\n\nCheck it all fits together (story, words, shots, sound and look tell ONE film), against your acceptance list and the rules. verdict "pass" only if you would put your name on it. Otherwise list fixes per stage. Ask Sam only what you truly cannot decide.'}]
    return ask('head', msgs, FINAL, ctx['ledger'], name='final', max_tokens=2500, label='final review')

def write_status(fdir, **s):
    json.dump({**s, 'updated': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}, open(os.path.join(fdir, 'status.json'), 'w'), indent=1)

def plan_md(ctx, final):
    b, p, d = ctx['brief'], ctx['plan'], ctx['done']
    out = [f"# {b.get('title')}\n", f"*{final['summary_for_sam']}*\n", f"**Style:** {p['style']}. {p['style_why']}  ", f"**Length:** {ctx['length']} s  ",
           f"**Narrator:** {p['narrator']['persona'] if p['narrator']['use'] else 'none'}\n", f"## Direction\n{p['direction']}\n", '## Beats']
    out += [f"- **{x['start']:.1f}–{x['end']:.1f} s** ({x['link']}) {x['see']}" for x in d['story']['beats']]
    if d['script']['lines']:
        out += ['\n## Narration'] + [f"- **{l['start']:.1f} s** “{l['text']}” — {l['tone']}" for l in d['script']['lines']]
    out += ['\n## Shots'] + [f"- {s['start']:.1f}–{s['end']:.1f} s · {s['size']} · {s['move']} — {s['frame']}" for s in d['shots']['shots']]
    out += ['\n## Look', f"{d['style']['motion_profile']}  ", 'Palette: ' + ', '.join(f"{c['name']} {c['hex']}" for c in d['style']['palette'])]
    led = ctx['ledger']
    out += [f"\n## Cost\n${led.total:.3f} of ${led.cap:.2f} (by seat: {json.dumps({k: round(v, 3) for k, v in json.load(open(led.path))['by_seat'].items()})})"]
    return '\n'.join(out) + '\n'

def voice_job(ctx):
    p, s, b = ctx['plan'], ctx['done']['script'], ctx['brief']
    return {'film': b['id'], 'duration': ctx['length'], 'takes': 4, 'profile': p['narrator']['persona'], 'persona': p['narrator']['persona'],
            'lines': [{'id': l['id'], 'text': l['text'], 'start': l['start'], 'end': l['end'], 'tone': l['tone'], 'wpm': [l['wpm_lo'], l['wpm_hi']]} for l in s['lines']],
            'omni': {'design': p['narrator']['omni_design'], 'ref_text': 'Long ago, when the hills were young, the lanterns of the valley were lit by hand, one by one, every single evening.'}}

def run(fdir, dry=False):
    fdir = os.path.join(ROOT, fdir) if not os.path.isabs(fdir) else fdir
    brief = json.load(open(os.path.join(fdir, 'brief.json')))
    led = Ledger(CAPS['film_usd'], os.path.join(fdir, 'ledger.json'))
    ctx = {'brief': brief, 'ledger': led, 'done': {}, 'reviews': {}}
    log(f"film {brief['id']}: seats head={seat('head')[:2]} deputy={seat('deputy')[:2]} crew={seat('crew')[:3]}; cap ${led.cap} (spent so far ${led.total:.3f})")
    if dry: return log('dry run: wiring ok')
    a = account()
    if a and a.get('today') is not None and a['today'] >= CAPS['day_usd']:
        return write_status(fdir, state='needs_sam', stage='plan', question=f"Today's spending cap (${CAPS['day_usd']}) is reached. Build tomorrow, or raise the cap?", usd=led.total)
    if a and a.get('remaining') is not None and a['remaining'] < CAPS['reserve_usd']:
        return write_status(fdir, state='needs_sam', stage='plan', question=f"Your OpenRouter key has ${a['remaining']:.2f} left. Raise its limit on openrouter.ai, then rebuild.", usd=led.total)
    try:
        write_status(fdir, state='running', stage='plan', usd=led.total)
        ctx['plan'], hm = head_plan(ctx); log(f'plan by {hm}: {ctx["plan"]["style"]}, narrator={ctx["plan"]["narrator"]["use"]}')
        ctx['length'] = float(brief.get('length_seconds') or ctx['plan']['length_s'] or 90)
        json.dump(ctx['plan'], open(os.path.join(fdir, 'plan.json'), 'w'), indent=1)
        for name in ORDER:
            write_status(fdir, state='running', stage=name, usd=round(led.total, 4))
            stage(ctx, name)
            json.dump(ctx['done'][name], open(os.path.join(fdir, f'{name}.json'), 'w'), indent=1)
        final = None
        for loop in range(CAPS['max_loops'] + 1):
            final, fm = head_final(ctx); log(f'final review {loop} by {fm}: {final["verdict"]} {final["score"]}/10, {len(final["fixes"])} fixes')
            if final['verdict'] == 'pass' or loop == CAPS['max_loops'] or final.get('question_for_sam'): break
            by = {}
            for f in final['fixes']: by.setdefault(f['stage'], []).append(f'{f["problem"]} → {f["fix"]}')
            for name in ORDER:                      # redo only what the head sent back, in story order
                if name in by:
                    stage(ctx, name, fixes=by[name]); json.dump(ctx['done'][name], open(os.path.join(fdir, f'{name}.json'), 'w'), indent=1)
        json.dump({'final': final, 'reviews': ctx['reviews']}, open(os.path.join(fdir, 'reviews.json'), 'w'), indent=1)
        open(os.path.join(fdir, 'PLAN.md'), 'w').write(plan_md(ctx, final))
        if ctx['plan']['narrator']['use'] and ctx['done']['script']['lines']:
            json.dump(voice_job(ctx), open(os.path.join(ROOT, 'voice', 'jobs', f"{brief['id']}.json"), 'w'), indent=1)
        ok = final['verdict'] == 'pass'
        write_status(fdir, state='ready' if ok else 'needs_sam', stage='pre-production', score=final['score'], summary=final['summary_for_sam'],
                     question=None if ok else (final.get('question_for_sam') or 'The head could not get every stage to pass in the allowed loops. Read PLAN.md and tell the director what to change.'),
                     open_fixes=[] if ok else final['fixes'], usd=round(led.total, 4))
        log(f'done: {"ready" if ok else "needs Sam"}; spent ${led.total:.3f} of ${led.cap}')
    except OverBudget as e:
        write_status(fdir, state='needs_sam', stage=ORDER[len(ctx['done'])] if len(ctx['done']) < len(ORDER) else 'final', usd=round(led.total, 4),
                     question=f'The film reached its budget ({e}). Raise the cap (crew.json) or let the director finish with cheaper models?')
        log('stopped: budget', e)
    except AllFailed as e:
        write_status(fdir, state='failed', stage=ORDER[len(ctx['done'])] if len(ctx['done']) < len(ORDER) else 'final', usd=round(led.total, 4), error=str(e)[:500])
        log('stopped: every model failed', e); raise SystemExit(1)

if __name__ == '__main__':
    run(sys.argv[1], dry='--dry' in sys.argv)
