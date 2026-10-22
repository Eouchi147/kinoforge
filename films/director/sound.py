"""sound.py: stage 2 of the director pipeline. The narration, the score and the timeline.

    python3 films/director/sound.py films/studio/<id>

Runs harness/shots/prep.py (voice from brief.voice, Lyria score, Whisper word timings) then the line's mix
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
    run([sys.executable, 'harness/shots/prep.py', C.rel(job.dir)])
    vo = json.load(open(job.p('audio', 'vo.json')))
    if len(vo['lines']) != len(script['lines']): raise RuntimeError(f'{len(vo["lines"])} voice lines for {len(script["lines"])} script lines')
    if not job.has('audio', 'music.mp3'): raise RuntimeError('no score (Lyria failed): see the log')
    run([sys.executable, L['mix'], C.rel(job.dir), '--title-line', str(L.get('title_line', 1))])
    cues = job.read('cues.json'); film = job.read('film.json')
    film['duration'] = cues['duration']; job.write('film.json', film)
    nowords = [l['id'] for l in cues['lines'] if not l.get('words')]
    open(job.p('index.html'), 'w').write(index_html(job, script['title']))
    job.ledger = C.Ledger(job.brief['cap_usd'], job.p('ledger.json'))
    msg = f'{len(cues["lines"])} lines on the score, {cues["duration"]:.1f} s, voice {vo["voice"]}.' + (f' No word timings for {", ".join(nowords)}.' if nowords else '')
    C.set_status(job.dir, 'sound', 'done', msg, outputs={'audio': C.rel(job.p('audio', 'mix.m4a')), 'duration': cues['duration']})


if __name__ == '__main__':
    main(sys.argv[1])
