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


def ensure_pad(job, P):
    """The beat grid for the narration (and the stand-in score): a quiet pad made in code, long enough for the film.
    Made before the voice, so prep.py never calls Lyria unless the brief asked for it (music: "lyria")."""
    mus = job.p('audio', 'music.mp3')
    if os.path.exists(mus) or not (P.get('music') or {}).get('engine'): return
    os.makedirs(job.p('audio'), exist_ok=True)
    words = sum(len(l['text'].split()) for l in P['vo'])
    secs = round((words / 2.3 + len(P['vo']) * 0.9 + 20) * 1.3, 1)
    import pad; pad.make(mus, secs, mood='dark' if not job.line.get('kid_safe') else 'warm')


def beat_grid(job):
    sys.path.insert(0, os.path.join(C.ROOT, 'harness', 'shots'))
    from prep import beat_map
    json.dump(beat_map(job.p('audio', 'music.mp3')), open(job.p('audio', 'music.json'), 'w'))


def wer(ref, hyp):
    n = lambda s: re.sub(r"[^a-z0-9' ]", ' ', s.lower().replace('-', ' ')).split()
    r, h = n(ref), n(hyp); d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        p, d[0] = d[0], i
        for j in range(1, len(h) + 1): p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (r[i - 1] != h[j - 1]))
    return d[len(h)] / max(len(r), 1)


def vo_check(job, P):
    """Every paid narration line checked by Whisper (prep.py's word timings): a line heard wrong (word error rate over the
    gate) is spoken again, at most `vo_retakes` times, booked against the cap like every other call."""
    vo = json.load(open(job.p('audio', 'vo.json'))); G = C.GATES; bad = []
    for k, l in enumerate(vo['lines']):
        l['wer'] = round(wer(l['text'], ' '.join(w[0] for w in l.get('words', []))), 3)
        if l['wer'] > G.get('vo_max_wer', 0.25): bad.append(k)
    if bad and G.get('vo_retakes', 1):
        sys.path.insert(0, os.path.join(C.ROOT, 'harness', 'shots'))
        from factory import speech, Budget
        from faster_whisper import WhisperModel
        import librosa
        B = Budget(job.dir, job.brief['cap_usd']); wm = WhisperModel('base.en', device='cpu', compute_type='int8')
        for k in bad:
            for t in range(G.get('vo_retakes', 1)):
                l = vo['lines'][k]; tmp = job.p('audio', 'vo', f'line{k}.retake{t}.mp3')
                speech(B, P['vo'][k]['text'], vo['voice'], tmp, f'vo retake {k}', P.get('voice_instructions'))
                pcm, _ = librosa.load(tmp, sr=16000, mono=True); segs, _ = wm.transcribe(pcm, word_timestamps=True, language='en')
                words = [[w.word.strip(), round(w.start, 3), round(w.end, 3)] for sg in segs for w in (sg.words or [])]
                e = wer(l['text'], ' '.join(w[0] for w in words)); C.log(f'line {k} retake {t}: wer {e:.2f} (was {l["wer"]})')
                if e < l['wer']:
                    os.replace(tmp, job.p(l['file'])); l.update(words=words, wer=round(e, 3))
                    l['dur'] = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', job.p(l['file'])], capture_output=True, text=True).stdout or l['dur'])
                elif os.path.exists(tmp): os.remove(tmp)
                if l['wer'] <= G.get('vo_max_wer', 0.25): break
    json.dump(vo, open(job.p('audio', 'vo.json'), 'w'), indent=1)
    return [k for k, l in enumerate(vo['lines']) if l['wer'] > G.get('vo_max_wer', 0.25)]


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
    ad = job.read('ad.json'); P = ad['prep']; music_note = ''; misheard = []
    ensure_pad(job, P)
    if str(P.get('voice', '')).split('|')[0] in ('chatterbox', 'kokoro'):   # free voice on the runner
        if not job.has('audio', 'vo.json'): run([os.environ.get('KF_TTS_PYTHON', sys.executable), 'films/director/voice_free.py', C.rel(job.dir)])
        beat_grid(job)
    else:                                                                     # paid voice (ElevenLabs), checked line by line
        if C.FREE_ONLY: raise RuntimeError('free-only mode: ad.json asks for a paid voice; re-run the script stage')
        run([sys.executable, 'harness/shots/prep.py', C.rel(job.dir)])
        job.ledger = C.Ledger(job.brief['cap_usd'], job.p('ledger.json'))
        misheard = vo_check(job, P)
    job.write('ad.json', ad)
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
    msg = f'{len(cues["lines"])} lines on the score, {cues["duration"]:.1f} s, voice {vo["voice"]}.' + (f' No word timings for {", ".join(nowords)}.' if nowords else '') + music_note + \
        (f' Lines still heard imperfectly after a retake: {", ".join(f"l{k:02d}" for k in misheard)}.' if misheard else '')
    C.set_status(job.dir, 'sound', 'done', msg, outputs={'audio': C.rel(job.p('audio', 'mix.m4a')), 'duration': cues['duration']})


if __name__ == '__main__':
    main(sys.argv[1])
