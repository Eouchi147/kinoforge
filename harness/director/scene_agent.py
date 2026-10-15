"""scene_agent.py — writes a film's scene from its story and its style pack's prototype, then proves it renders.

    python3 harness/director/scene_agent.py films/showcase/<id>          (needs OPENROUTER_API_KEY; runs on GitHub)

1. Copies the style's prototype (proto/<template>) to proto/<id> as the starting point: its engine, look and helpers.
2. CODER seat (smartest cheap models, live) rewrites the scene file and audio.py for the new story, shot by shot.
3. CHECKS: the score must run and last the film; sample frames (middle of every other shot) must render without page
   errors and must not be blank. Errors go back to the coder (max 3 repairs).
4. EYES seat looks at the sample frames against the shot list once; real problems go back to the coder (1 pass).
5. Money: one ledger per film, capped at crew.json caps.scene_usd. Result: films/showcase/<id>/build.json.
"""
import os, sys, json, re, shutil, subprocess, time, base64, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import urllib.request, urllib.error
from agents import seat, market, Ledger, CREW, ROOT, API, KEY, ask, OverBudget

FILE_RE = re.compile(r'^=====FILE:\s*(\S+)\s*=====\s*\n(.*?)^=====END=====\s*$', re.S | re.M)
README = open(os.path.join(ROOT, 'harness', 'README.md')).read()
RULES = open(os.path.join(ROOT, 'docs', 'SHOWRUNNER_PLAYBOOK.md')).read().split('## 4.')[0]

def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

def write(messages, book, label, max_tokens=32000):
    """Free-text completion down the coder chain; returns (text, model)."""
    mk = market(); errs = []
    for model in seat('coder'):
        m = mk.get(model) or {'in': 0, 'out': 0}
        in_tok = len(json.dumps(messages)) / 3.5
        if not book.room((in_tok * m['in'] + max_tokens * m['out']) / 1e6 * 0.6): errs.append(f'{model}: cap'); continue
        body = {'model': model, 'messages': messages, 'max_tokens': max_tokens, 'usage': {'include': True}, 'temperature': 0.4}
        req = urllib.request.Request(f'{API}/chat/completions', data=json.dumps(body).encode(),
                                     headers={'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json', 'X-Title': 'KINOFORGE scene agent'})
        t0 = time.time()
        try:
            j = json.load(urllib.request.urlopen(req, timeout=900))
            text = j['choices'][0]['message']['content'] or ''
            u = j.get('usage') or {}
            book.add(seat='coder', model=j.get('model', model), task=label, usd=float(u.get('cost') or 0), s=round(time.time() - t0, 1), ok=bool(FILE_RE.search(text)))
            if FILE_RE.search(text): return text, model
            errs.append(f'{model}: no files in reply ({j["choices"][0].get("finish_reason")})')
        except urllib.error.HTTPError as e:
            errs.append(f'{model}: {e.code} {e.read().decode(errors="ignore")[:160]}'); book.add(seat='coder', model=model, task=label, usd=0, s=round(time.time() - t0, 1), ok=False)
            if e.code == 402: raise OverBudget('key limit')
        except Exception as e:
            errs.append(f'{model}: {type(e).__name__} {e}'[:200]); book.add(seat='coder', model=model, task=label, usd=0, s=round(time.time() - t0, 1), ok=False)
    raise RuntimeError('coder chain failed: ' + ' | '.join(errs))

def apply(text, d, allowed):
    wrote = []
    for path, body in FILE_RE.findall(text):
        path = path.strip().lstrip('./')
        if '/' in path or path not in allowed: continue
        open(os.path.join(d, path), 'w').write(body.rstrip() + '\n'); wrote.append(path)
    return wrote

def files_block(d, names):
    return '\n\n'.join(f'=====FILE: {n}=====\n{open(os.path.join(d, n)).read()}\n=====END=====' for n in names if os.path.exists(os.path.join(d, n)))

def probe(sid, kind, story, tmp):
    """Run the score and render sample frames. Returns (errors, frame_paths)."""
    errs, frames = [], []
    d = os.path.join(ROOT, 'proto', sid)
    r = subprocess.run([sys.executable, os.path.join(d, 'audio.py'), os.path.join(tmp, 'a.wav')], capture_output=True, text=True, timeout=900, cwd=ROOT)
    if r.returncode: errs.append('audio.py failed:\n' + (r.stderr or r.stdout)[-2500:])
    else:
        try:
            import soundfile as sf; info = sf.info(os.path.join(tmp, 'a.wav'))
            if abs(info.duration - story['duration']) > 1.5: errs.append(f'audio.py wrote {info.duration:.1f}s; the film is {story["duration"]}s')
        except Exception as e: errs.append(f'audio output unreadable: {e}')
    shots = story['shots']; picks = [int((s['start'] + s['end']) / 2 * story['fps']) for s in shots[::2]][:7]
    w, h = (270, 480) if story['fmt'] == '9:16' else (480, 270)
    for f in picks:
        out = os.path.join(tmp, f'p{f}')
        if kind == 'web':
            cmd = ['node', 'harness/render.cjs', f'proto/{sid}', '--w', str(w), '--h', str(h), '--start', str(f), '--end', str(f + 1), '--jpg', '--out', out]
        else:
            cmd = [sys.executable, 'harness/blender_render.py', f'proto/{sid}', '--out', out, '--w', str(w), '--h', str(h), '--samples', '8', '--start', str(f), '--end', str(f + 1)]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=ROOT)
        log_ = (r.stdout or '') + (r.stderr or '')
        pe = [l for l in log_.splitlines() if 'pageerror' in l or 'Error' in l or 'Traceback' in l]
        if r.returncode or pe:
            errs.append(f'frame {f} ({kind}) failed:\n' + '\n'.join(pe[:15] or log_.splitlines()[-25:])); break
        img = sorted(glob.glob(os.path.join(out, 'frames', '*')))
        if not img: errs.append(f'frame {f}: no image written: the scene is shorter than {story["duration"]} s. SHOTS must add up to the full film.'); break
        frames.append((f, img[0]))
        try:
            from PIL import Image, ImageStat
            st = ImageStat.Stat(Image.open(img[0]).convert('L'))
            if st.stddev[0] < 3.0: errs.append(f'frame {f} (shot "{next(s["direction"][:60] for s in shots if s["start"] * 24 <= f < s["end"] * 24)}") is blank: one flat colour (mean {st.mean[0]:.0f}). Something is not drawn or the camera sees nothing.')
        except Exception: pass
    return errs, frames

def sheet(frames, out):
    from PIL import Image, ImageDraw
    ims = [Image.open(p).convert('RGB') for _, p in frames]
    if not ims: return None
    w, h = ims[0].size; cols = 4; rows = (len(ims) + cols - 1) // cols
    S = Image.new('RGB', (w * cols, h * rows), 'black'); dr = ImageDraw.Draw(S)
    for k, (im, (f, _)) in enumerate(zip(ims, frames)):
        S.paste(im.resize((w, h)), ((k % cols) * w, (k // cols) * h)); dr.text(((k % cols) * w + 6, (k // cols) * h + 4), f'frame {f}', fill='yellow')
    S.save(out, quality=88); return out

EYES = {'type': 'object', 'additionalProperties': False, 'required': ['score', 'issues'], 'properties': {
    'score': {'type': 'number', 'description': '0-10: does each frame show its shot, readable, polished, cinematic?'},
    'issues': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False, 'required': ['frame', 'problem', 'fix'], 'properties': {
        'frame': {'type': 'integer'}, 'problem': {'type': 'string'}, 'fix': {'type': 'string', 'description': 'a concrete code-level change'}}}}}}

def main(fdir):
    fdir = os.path.join(ROOT, fdir) if not os.path.isabs(fdir) else fdir
    story = json.load(open(os.path.join(fdir, 'story.json'))); sid = story['id']; tpl = story['template']
    book = Ledger(CREW['caps'].get('scene_usd', 0.6), os.path.join(fdir, 'ledger.json'))
    src, d = os.path.join(ROOT, 'proto', tpl), os.path.join(ROOT, 'proto', sid)
    shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(src, d, ignore=shutil.ignore_patterns('__pycache__', 'REVIEW.md', 'lines', 'tools', 'NOTES.md', 'timing.json'))
    kind = 'blender' if os.path.exists(os.path.join(d, 'blender.py')) else 'web'
    main_file = 'blender.py' if kind == 'blender' else 'scene.js'
    allowed = sorted(f for f in os.listdir(d) if f.endswith(('.js', '.py', '.html', '.json')))
    allowed += ['NOTES.md']
    code_files = [f for f in allowed if f != 'NOTES.md']
    log(f'{sid}: {kind} from {tpl}; files {code_files}; coder seats {seat("coder")}')
    sys_msg = (f'You are the lead technical director of KINOFORGE, a studio that renders films procedurally and deterministically. You write production code: '
               f'complete, runnable, no placeholders, no TODOs, no "rest unchanged". You think like a film director: rhythm, motivated cuts, lens choice, light, emotion, beauty.\n\n'
               f'THE HARNESS CONTRACT:\n{README}\n\nTHE STUDIO RULES:\n{RULES}')
    task = (f'Make this film in the style of the prototype below. Keep the prototype\'s engine, look, helpers and quality bar; replace its story, sets, '
            f'characters, shots, timing and score with the new film.\n\nTHE FILM (story.json):\n{json.dumps(story, indent=1)}\n\n'
            f'Requirements:\n- Total length exactly {story["duration"]} s at {story["fps"]} fps; SHOTS (or the Blender shot table/DURATION) must follow the story\'s shot list, '
            f'one entry per shot with the same durations, in order. Each shot\'s size, lens, camera move and transition-in as written. Cuts are hard cuts unless the shot says dissolve/fade/iris/wipe.\n'
            f'- Every action in the shot list is visible on screen at its shot. Complete bodies, grounded characters, nothing stray. Polished and harmonious.\n'
            f'- Narration is added later from story.narration (do NOT synthesise speech); leave room in the score under its windows (lower the music there).\n'
            f'- audio.py writes the score and effects for the whole {story["duration"]} s (python3 audio.py out.wav), in the spirit of story.music, using the prototype\'s audio tools.\n'
            f'- Deterministic in (frame, time). Fast enough: well under 2 s per frame at 1280x720 on a CPU.\n'
            f'- {"Vertical 9:16: design every frame for 720x1280." if story["fmt"] == "9:16" else "16:9 at 1280x720."}\n'
            f'- Rewrite {main_file} and audio.py completely; also write NOTES.md (logline, shot list, colour script, sound plan). Rewrite other files only if needed.\n\n'
            f'Reply with every file you write, each exactly in this form and nothing else:\n=====FILE: name=====\n<full file content>\n=====END=====\n\n'
            f'THE PROTOTYPE ({tpl}):\n{files_block(d, code_files)}')
    tmp = os.path.join('/tmp', 'probe-' + sid)
    text, model = write([{'role': 'system', 'content': sys_msg}, {'role': 'user', 'content': task}], book, 'write')
    wrote = apply(text, d, allowed); log(f'{sid}: {model} wrote {wrote}')
    report = {'id': sid, 'template': tpl, 'kind': kind, 'writer': model, 'repairs': [], 'eyes': None}
    convo = [{'role': 'system', 'content': sys_msg}, {'role': 'user', 'content': task}, {'role': 'assistant', 'content': text[:2000] + '\n…(files applied)'}]
    def repair(problems, label):
        nonlocal wrote
        msg = (f'The files you wrote have these problems. Fix them and reply with every file you change, complete, in the same =====FILE format.\n\nPROBLEMS:\n{problems}\n\n'
               f'THE CURRENT FILES:\n{files_block(d, [f for f in code_files if f in wrote or f == main_file or f == "audio.py"])}')
        t, m = write(convo[:2] + [{'role': 'user', 'content': msg}], book, label)
        w2 = apply(t, d, allowed); log(f'{sid}: {label} by {m}: {w2}'); return w2
    for k in range(4):
        shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
        errs, frames = probe(sid, kind, story, tmp)
        log(f'{sid}: probe {k}: {len(errs)} problems, {len(frames)} frames')
        if not errs: break
        report['repairs'].append(errs)
        if k == 3: break
        try: repair('\n\n'.join(errs), f'repair {k + 1}')
        except (RuntimeError, OverBudget) as e: log('repair stopped:', e); break
    ok = not errs
    if ok and frames:
        sh = sheet(frames, os.path.join(fdir, 'probe.jpg'))
        shots_txt = '\n'.join(f'{s["start"]:.0f}-{s["end"]:.0f}s: {s["direction"]}' for s in story['shots'])
        content = [{'type': 'text', 'text': f'Sample frames (labelled with frame numbers, 24 fps) from a film in the "{story["style"]}" style. Shot list:\n{shots_txt}\n\nLook at each frame against its shot. Report only real, visible problems: wrong or missing subject, unreadable composition, broken or floating characters, ugly or harsh artefacts, nonsense. Concrete fixes.'},
                   {'type': 'image_url', 'image_url': {'url': 'data:image/jpeg;base64,' + base64.b64encode(open(sh, 'rb').read()).decode()}}]
        try:
            ev, em = ask('eyes', [{'role': 'user', 'content': content}], EYES, book, name='eyes', max_tokens=1500, label='eyes')
            report['eyes'] = {'by': em, **ev}; log(f'{sid}: eyes {ev["score"]}/10, {len(ev["issues"])} issues')
            if ev['score'] < 7 and ev['issues']:
                backup = {f: open(os.path.join(d, f)).read() for f in code_files if os.path.exists(os.path.join(d, f))}
                repair('\n'.join(f'frame {i["frame"]}: {i["problem"]} -> {i["fix"]}' for i in ev['issues']), 'look pass')
                shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
                errs2, frames2 = probe(sid, kind, story, tmp)
                if errs2:
                    for f, s in backup.items(): open(os.path.join(d, f), 'w').write(s)
                    log(f'{sid}: look pass broke the scene; kept the previous version')
                else: sheet(frames2, os.path.join(fdir, 'probe.jpg')); report['look_pass'] = True
        except Exception as e: log('eyes skipped:', e)
    report.update(ok=ok, usd=round(book.total, 4), problems=None if ok else errs)
    json.dump(report, open(os.path.join(fdir, 'build.json'), 'w'), indent=1)
    log(f'{sid}: {"READY" if ok else "FAILED"}; ${book.total:.3f}')
    if not ok: sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[1])
