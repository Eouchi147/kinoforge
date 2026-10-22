"""script.py: stage 1 of the director pipeline. The brief in, a fact-checked narration out.

    python3 films/director/script.py films/studio/<id>

1. The writer seat (head) drafts the narration in the house structure of the line, one picture idea per line, plus a
   claims list (every fact the script states, with the exact words that state it).
2. A checker seat (deputy) from a DIFFERENT provider verifies every claim: true, doubtful or false, with a reason.
3. Doubtful or false claims (and any house-rule problem) go back to the writer, at most 2 rewrite rounds.
4. Anything still not true after the last check is cut by code (its sentence, or its line).
5. Code guards: no em or en dashes, no "...", no URLs, kid-safe words for kid lines, line and word counts.
Writes script.json (lines, claims, verdicts, rounds, cuts) and ad.json (the prep block for harness/shots/prep.py).
"""
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

MAX_ROUNDS = 2

SCRIPT_SCHEMA = {'type': 'object', 'additionalProperties': False,
    'required': ['title', 'year_label', 'lines', 'claims', 'music_prompt', 'notes'],
    'properties': {
        'title': {'type': 'string', 'description': 'on-screen film title, e.g. "The Battle of Tours"'},
        'year_label': {'type': 'string', 'description': 'the date for the title and end cards, e.g. "732" or "AD 732" or "1066"'},
        'lines': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False, 'required': ['text', 'picture'],
                  'properties': {'text': {'type': 'string', 'description': 'what the narrator says'},
                                 'picture': {'type': 'string', 'description': 'the ONE clear picture idea for this line'}}}},
        'claims': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False, 'required': ['id', 'claim', 'line', 'quote'],
                   'properties': {'id': {'type': 'string'}, 'claim': {'type': 'string', 'description': 'the fact, stated plainly and completely'},
                                  'line': {'type': 'integer', 'description': '0-based index of the line that states it'},
                                  'quote': {'type': 'string', 'description': 'the exact words of that line that state it (copied verbatim)'}}}},
        'music_prompt': {'type': 'string', 'description': 'a Lyria prompt for the score: instruments and colour of the period and place, tempo, shape; instrumental'},
        'notes': {'type': 'string', 'description': 'one or two sentences: what you chose to leave out and why'}}}

VERDICT_SCHEMA = {'type': 'object', 'additionalProperties': False, 'required': ['verdicts'],
    'properties': {'verdicts': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False,
        'required': ['id', 'verdict', 'reason', 'correction'],
        'properties': {'id': {'type': 'string'}, 'verdict': {'type': 'string', 'enum': ['true', 'doubtful', 'false']},
                       'reason': {'type': 'string'}, 'correction': {'type': 'string', 'description': 'the accurate statement, or empty'}}}}}}


def targets(brief):
    s = brief['target_seconds']
    return {'lines': max(7, min(20, round(s / 8.6))), 'words': round(s * 2.15)}


def writer_system(job):
    L, b = job.line, job.brief; T = targets(b)
    return (f"You are the head writer of KINOFORGE's {L['series']} series ({L['aspect']} animated films, narration first: the picture is built to your words).\n"
            f"Write the narration for one film. Length: about {T['words']} words in about {T['lines']} lines (target {int(b['target_seconds'])} seconds of film). "
            "A line is one to three short sentences, at most 35 words.\n"
            f"Structure: {L['structure']}\n"
            "Beats are linked by the logic of but and therefore, never and then (do not start lines with the words But or Therefore "
            "more than once or twice; vary: so, then, which meant, until). One clear picture idea per line, written in the `picture` field "
            f"(it will be animated in the {L['style']} style). {L['picture_rules']}\n"
            f"Tone: {b.get('tone') or L['default_tone']}.\n"
            "House rules: plain spoken English for the ear; no em or en dashes; no \"...\"; no URLs; no stage directions or [tags]; numbers the "
            "narrator can say; every fact must be well established in mainstream history (when sources disagree, say so plainly, e.g. "
            "\"the chroniclers say\"); never invent quotes, names or numbers."
            + (" This series is for kids: no gore, no wounds, no cruelty described; losses are numbers." if L.get('kid_safe') else '') +
            "\nReturn the claims list: EVERY factual statement in the script (dates, places, numbers, names, who did what, outcomes), "
            "each with the 0-based line index and the exact words of that line that state it.")


def brief_text(b):
    keys = ['title', 'subject', 'angle', 'notes', 'audience', 'tone', 'target_seconds']
    return '\n'.join(f'{k}: {b[k]}' for k in keys if b.get(k) not in (None, ''))


def guard(job, data):
    """Code guards: auto-fix what code can fix, return the problems the writer must fix."""
    L = job.line; T = targets(job.brief); problems = []
    for k, ln in enumerate(data['lines']):
        ln['text'], _ = C.house_clean(ln['text'])
        for p in C.house_problems(ln['text'], L.get('kid_safe')): problems.append(f'line {k}: {p}')
        if len(ln['text'].split()) > 40: problems.append(f'line {k}: too long ({len(ln["text"].split())} words, max 35)')
        if re.search(r'\[[^\]]*\]', ln['text']): problems.append(f'line {k}: remove the [tag]')
    data['title'], _ = C.house_clean(data['title'])
    n = len(data['lines']); words = sum(len(l['text'].split()) for l in data['lines'])
    if not (T['lines'] - 4 <= n <= T['lines'] + 4): problems.append(f'{n} lines; aim for about {T["lines"]}')
    if not (T['words'] * 0.72 <= words <= T['words'] * 1.3): problems.append(f'{words} words; aim for about {T["words"]}')
    tl = L.get('title_line', 1)
    if n > tl and len(data['lines'][tl]['text'].split()) > 9: problems.append(f'line {tl} must be only the title line (e.g. "{data["title"]}.")')
    return problems


def check_claims(job, data, avoid_provider, round_no):
    claims = [{'id': c['id'], 'claim': c['claim'], 'in_line': data['lines'][c['line']]['text'] if 0 <= c['line'] < len(data['lines']) else ''} for c in data['claims']]
    msgs = [{'role': 'system', 'content': 'You are a strict history fact checker for an educational film studio. For each claim answer: "true" (well established '
             'in mainstream scholarship), "doubtful" (disputed, uncertain, legendary, or stated with more certainty than the sources allow), or "false". '
             'Judge the claim as worded in its line. Give a one-sentence reason and, when not true, the accurate statement. Return a verdict for every id.'},
            {'role': 'user', 'content': f'Film subject: {job.brief.get("subject") or job.brief.get("title")}\n\nClaims:\n' + json.dumps(claims, indent=1, ensure_ascii=False)}]
    models = [m for m in C.seat_models(job.brief.get('seats', {}).get('checker', 'deputy')) if C.provider(m) != avoid_provider]
    last = None
    for m in models or [None]:
        try:
            v, used = C.ask(job.brief.get('seats', {}).get('checker', 'deputy'), msgs, VERDICT_SCHEMA, job.ledger, name='verdicts', max_tokens=3000,
                            only=m, label=f'fact check round {round_no}')
            got = {x['id']: x for x in v['verdicts']}
            for c in data['claims']:   # a claim the checker skipped counts as doubtful
                got.setdefault(c['id'], {'id': c['id'], 'verdict': 'doubtful', 'reason': 'not checked', 'correction': ''})
            return got, used
        except C.OverBudget: raise
        except Exception as e: last = e; C.log('checker failed:', m, str(e)[:200])
    raise C.AllFailed(f'no checker from a provider other than {avoid_provider}: {last}')


def cut(data, bad_ids, title_line):
    """Cut every claim still not true: its sentence (by quote), or its whole line. Title line and hook are never dropped whole."""
    cuts = []; drop = set()
    for c in data['claims']:
        if c['id'] not in bad_ids or not (0 <= c['line'] < len(data['lines'])): continue
        ln = data['lines'][c['line']]; q = c['quote'].strip().rstrip('.')
        sents = re.split(r'(?<=[.!?])\s+', ln['text'])
        keep = [s for s in sents if not (q and q.lower() in s.lower())]
        if q and len(keep) < len(sents) and keep:
            ln['text'] = ' '.join(keep); cuts.append({'claim': c['id'], 'cut': 'sentence', 'line': c['line']})
        elif c['line'] > title_line:
            drop.add(c['line']); cuts.append({'claim': c['id'], 'cut': 'line', 'line': c['line']})
        else:
            cuts.append({'claim': c['id'], 'cut': 'kept (hook or title line): check by hand', 'line': c['line']})
    if drop:
        data['lines'] = [l for k, l in enumerate(data['lines']) if k not in drop]
    data['claims'] = [c for c in data['claims'] if c['id'] not in bad_ids]
    return cuts


def make_ad(job, data):
    L, b = job.line, job.brief
    mp = (data.get('music_prompt') or '').strip() or L['music_prompt']
    if 'instrumental' not in mp.lower(): mp += ' Instrumental only, no vocals.'
    if C.FREE_ONLY:   # free engines on the runner: no ElevenLabs, no Lyria
        v = b['voice'] if b['voice'].split('|')[0] in ('chatterbox', 'kokoro') else C.CONFIG.get('free_voice', 'chatterbox')
        return {'_': f"{L['series']}: {data['title']} ({data['year_label']}). Narration by films/director/script.py; free sound by films/director/sound.py.",
                'id': job.id, 'cap_usd': b['cap_usd'],
                'prep': {'voice': v, 'voice_settings': L.get('free_voice_settings', {}), 'vo_words': True,
                         'music': {**C.CONFIG.get('free_music', {'engine': 'procedural'}), 'prompt': mp, 'line': L['name'], 'style': L.get('music_style', '')},
                         'vo': [{'text': l['text']} for l in data['lines']]}}
    return {'_': f"{L['series']}: {data['title']} ({data['year_label']}). Narration by films/director/script.py; prepared by harness/shots/prep.py.",
            'id': job.id, 'cap_usd': b['cap_usd'],
            'prep': {'music': {'prompt': mp, 'models': ['google/lyria-3-pro-preview', 'google/lyria-3-clip-preview']},
                     'voice_cast': [b['voice']], 'cast_lines': 3, 'vo_words': True,
                     'voice_brief': L['voice_brief'], 'voice_instructions': L['voice_instructions'],
                     'vo': [{'text': l['text']} for l in data['lines']]}}


def main(d):
    job = C.Job(d)
    if job.has('script.json') and job.has('ad.json'):
        C.log('script exists, skipped'); return job.read('script.json')
    b = job.brief; seats = b.get('seats', {}); wseat = seats.get('writer', 'head')
    C.set_status(job.dir, 'script', 'running', 'The writer is drafting the narration.')
    msgs = [{'role': 'system', 'content': writer_system(job)}, {'role': 'user', 'content': 'The approved brief:\n' + brief_text(b)}]
    data, writer = C.ask(wseat, msgs, SCRIPT_SCHEMA, job.ledger, name='script', max_tokens=5000, label='script draft')
    rounds = []
    for r in range(MAX_ROUNDS + 1):
        problems = guard(job, data)
        verdicts, checker = check_claims(job, data, C.provider(writer), r)
        bad = {k: v for k, v in verdicts.items() if v['verdict'] != 'true'}
        rounds.append({'round': r, 'writer': writer, 'checker': checker, 'claims': len(data['claims']), 'not_true': list(bad.values()), 'guards': problems})
        C.log(f'round {r}: {len(data["claims"])} claims, {len(bad)} not true, {len(problems)} guard problems')
        if not bad and not problems: break
        if r == MAX_ROUNDS: break
        C.set_status(job.dir, 'script', 'running', f'Rewrite {r + 1}: {len(bad)} claims to fix, {len(problems)} house-rule problems.', commit=False)
        fb = {'claims_to_fix': list(bad.values()), 'house_rule_problems': problems}
        msgs2 = msgs + [{'role': 'assistant', 'content': json.dumps(data, ensure_ascii=False)},
                        {'role': 'user', 'content': 'A fact checker and the house rules flagged these. Rewrite the script: fix or remove every flagged claim '
                         '(prefer the correction; if a fact is uncertain, say so plainly or leave it out), fix every problem, keep the structure, tone and '
                         'length, and return the complete script with a fresh claims list.\n' + json.dumps(fb, indent=1, ensure_ascii=False)}]
        data, writer = C.ask(wseat, msgs2, SCRIPT_SCHEMA, job.ledger, name='script', max_tokens=5000, label=f'script rewrite {r + 1}')
    cuts = cut(data, set(bad), job.line.get('title_line', 1)) if bad else []
    problems = guard(job, data)
    hard = [p for p in problems if 'kid-safe' in p or 'URL' in p]
    if hard:   # last resort: drop the offending lines (never the hook or the title line)
        idx = {int(re.match(r'line (\d+)', p).group(1)) for p in hard if p.startswith('line ')}
        tl = job.line.get('title_line', 1)
        data['lines'] = [l for k, l in enumerate(data['lines']) if k not in idx or k <= tl]
        cuts += [{'cut': 'line (house rule)', 'line': k} for k in sorted(idx) if k > tl]
        for l in data['lines']: l['text'] = C.URL.sub('', l['text'])
    lines = [{'id': f'l{k:02d}', 'text': l['text'], 'picture': l['picture']} for k, l in enumerate(data['lines'])]
    script = {'title': data['title'], 'year_label': data['year_label'], 'line': job.line['name'], 'series': job.line['series'], 'lines': lines,
              'words': sum(len(l['text'].split()) for l in lines), 'claims': data['claims'],
              'verdicts': rounds[-1]['not_true'] if rounds else [], 'rounds': rounds, 'cuts': cuts, 'notes': data.get('notes', ''),
              'music_prompt': data.get('music_prompt', ''), 'writer': writer, 'checker': rounds[-1]['checker'] if rounds else None,
              'usd': round(job.ledger.total, 4)}
    job.write('script.json', script); job.write('ad.json', make_ad(job, data))
    C.set_status(job.dir, 'script', 'done', f'{len(lines)} lines, {script["words"]} words, {len(data["claims"])} claims checked, {len(cuts)} cut.',
                 outputs={'script': C.rel(job.p('script.json'))})
    return script


if __name__ == '__main__':
    main(sys.argv[1])
