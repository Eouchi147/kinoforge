"""sound.py: stage 2 of the director pipeline. The narration, the score and the timeline.

    python3 films/director/sound.py films/studio/<id>

Free-only mode (default, films/director/config.json): the narration with a free open voice on the runner
(voice_free.py: Chatterbox or Kokoro, checked by Whisper); the narration is placed on the beat grid of a quiet pad made in
code (pad.py), then the free procedural score engine (config.json music_engines: films/lib/score/remix.py) re-scores it
and writes the final mix (the pad stays as the score if the engine is missing or fails). Paid mode: harness/shots/prep.py (ElevenLabs, Lyria). Then the line's mix
(films/lib/battle_mix.py: narration on the score's beat grid, title line on the biggest rise, -14 LUFS), so the folder
gets audio/, cues.json, film.json (sizes from the line) and index.html (the line's example page, loading ./spec.js).
Every paid call is booked in the job's ledger.json against brief.cap_usd (prep reads ad.json cap_usd).
"""
import os, sys, json, re, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C


def index_html(job, title):
    """The line's example page with our title; the spec can be swapped with ?spec= (used by check.cjs for candidates)."""
    src = open(os.path.join(C.ROOT, job.line['examples'][0], 'index.html')).read()
    src = re.sub(r'<title>.*?</title>', f'<title>{job.line["series"]}: {title}</title>', src, flags=re.S)
    src = src.replace("'./spec.js'", "(new URLSearchParams(location.search).get('spec') || './spec.js')")
    src = src.replace('"./spec.js"', "(new URLSearchParams(location.search).get('spec') || './spec.js')")
    if "get('spec')" not in src: raise RuntimeError('the example index.html does not load ./spec.js; cannot make the page')
    return src


def run(cmd):
    C.log('$', ' '.join(cmd))
    r = subprocess.run(cmd, cwd=C.ROOT, text=True, stdout=sys.stdout, stderr=subprocess.STDOUT)
    if r.returncode: raise RuntimeError(f'{os.path.basename(cmd[1])} failed (exit {r.returncode})')


def free_sound(job, P):
    """Narration with a free open voice (voice_free.py, in the TTS python: $KF_TTS_PYTHON) and the score from a free
    engine (config.json music_engines; the placeholder pad when the engine is not there), then the beat map."""
    if not job.has('audio', 'vo.json'):
        run([os.environ.get('KF_TTS_PYTHON', sys.executable), 'films/director/voice_free.py', C.rel(job.dir)])
    vo = json.load(open(job.p('audio', 'vo.json')))
    mus = job.p('audio', 'music.mp3')
    if not os.path.exists(mus):   # the beat grid (and the stand-in score): a quiet pad made in code
        secs = sum(l['dur'] for l in vo['lines']) + len(vo['lines']) * 0.9 + 14
        import pad; pad.make(mus, secs, mood='dark' if not job.line.get('kid_safe') else 'warm')
    sys.path.insert(0, os.path.join(C.ROOT, 'harness', 'shots'))
    from prep import beat_map
    json.dump(beat_map(mus), open(job.p('audio', 'music.json'), 'w'))


def main(d):
    job = C.Job(d); L = job.line; script = job.read('script.json')
    if not script: raise RuntimeError('no script.json: run the script stage first')
    if job.has('cues.json') and job.has('audio', 'mix.m4a') and job.has('film.json') and job.has('index.html'):
        C.log('sound exists, skipped'); return
    C.set_status(job.dir, 'sound', 'running', 'Recording the narration and the score.')
    if not job.has('film.json'):
        job.write('film.json', {'id': job.id, 'series': L['series'], 'title': script['title'], 'year': script['year_label'], 'style': L['style'],
                                'line': L['name'], 'fps': L['fps'], 'render_w': L['render'][0], 'render_h': L['render'][1],
                                'w': L['delivery'][0], 'h': L['delivery'][1], 'audio': 'audio/mix.m4a',
                                'note': 'Made by the KINOFORGE director (films/director/). Picture: ' + L['engine'] + '.'})
    ad = job.read('ad.json'); P = ad['prep']; music_note = ''
    if P.get('voice') or (P.get('music') or {}).get('engine'):
        free_sound(job, P); job.write('ad.json', ad)         # free engines on the runner
    else:
        if C.FREE_ONLY: raise RuntimeError('free-only mode: ad.json asks for paid sound (ElevenLabs, Lyria); re-run the script stage')
        run([sys.executable, 'harness/shots/prep.py', C.rel(job.dir)])
    vo = json.load(open(job.p('audio', 'vo.json')))
    if len(vo['lines']) != len(script['lines']): raise RuntimeError(f'{len(vo["lines"])} voice lines for {len(script["lines"])} script lines')
    if not job.has('audio', 'music.mp3'): raise RuntimeError('no score: see the log')
    run([sys.executable, L['mix'], C.rel(job.dir), '--title-line', str(L.get('title_line', 1))])
    music_note = ''
    eng = (P.get('music') or {}).get('engine')
    if eng:   # the free score engine re-scores the placed narration and writes a new mix
        cmd = [str(a).format(job=C.rel(job.dir)) for a in C.CONFIG.get('music_engines', {}).get(eng, {}).get('remix', [])]
        tool = next((a for a in cmd if a.endswith('.py')), None)
        if tool and os.path.exists(os.path.join(C.ROOT, tool)):
            try: run(cmd); music_note = f' Score: {eng} engine.'
            except RuntimeError as e: music_note = f' Score: placeholder pad ({eng} engine failed: {e}).'
        else: music_note = f' Score: placeholder pad ({eng} engine not found).'
        P['music_note'] = music_note.strip(); job.write('ad.json', ad)
    cues = job.read('cues.json'); film = job.read('film.json')
    film['duration'] = cues['duration']; job.write('film.json', film)
    nowords = [l['id'] for l in cues['lines'] if not l.get('words')]
    open(job.p('index.html'), 'w').write(index_html(job, script['title']))
    job.ledger = C.Ledger(job.brief['cap_usd'], job.p('ledger.json'))
    msg = f'{len(cues["lines"])} lines on the score, {cues["duration"]:.1f} s, voice {vo["voice"]}.' + (f' No word timings for {", ".join(nowords)}.' if nowords else '') + music_note
    C.set_status(job.dir, 'sound', 'done', msg, outputs={'audio': C.rel(job.p('audio', 'mix.m4a')), 'duration': cues['duration']})


if __name__ == '__main__':
    main(sys.argv[1])
