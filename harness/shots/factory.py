"""factory.py — the shot factory: a brief in, a finished ad or short film out, on OpenRouter with a hard budget.

    python3 harness/shots/factory.py pieces/<id>            (needs OPENROUTER_API_KEY)

 1 TREATMENT  head director writes the piece: look, reference sheet, shots (each a keyframe + a motion), voiceover, music, end card
 2 REFERENCES one image per product / character / location, made once, reused by every shot (consistency)
 3 KEYFRAMES  one still per shot from the references; eyes score it; a weak one is redone once (cents)
 4 CLIPS      each keyframe animated by a video model as the first frame; eyes check 3 frames per clip; a broken clip is redone once
 5 SOUND      ElevenLabs voiceover, Lyria score, the clips' own ambience underneath; ducked and mastered to -14 LUFS
 6 EDIT       cuts / dissolves, one grade over everything, end card with the brand line typeset in code (AI never draws text)
 7 REVIEW     head director looks at the finished contact sheet and writes the verdict
Money: pieces/<id>/ledger.json; the piece's cap (tier) and the whole test budget (pieces/BUDGET.json) are checked before every call.
"""
import os, sys, json, time, base64, subprocess, glob, re, math, urllib.request, urllib.error
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'director'))
from agents import ask, Ledger, ROOT, API, KEY, OverBudget, AllFailed

TIERS = {   # video model, resolution, keyframe model, per-piece cap
    'draft':    {'video': 'google/veo-3.1-lite', 'res': '720p', 'image': 'google/gemini-nano-banana-2.1', 'cap': 4.0},
    'standard': {'video': 'google/veo-3.1-fast', 'res': '1080p', 'image': 'google/gemini-nano-banana-2.1', 'cap': 9.0},
    'premium':  {'video': 'google/veo-3.1', 'res': '1080p', 'image': 'google/gemini-3-pro-image', 'cap': 12.0},
    'kling':    {'video': 'kwaivgi/kling-v3.0-pro', 'res': '720p', 'image': 'google/gemini-nano-banana-2.1', 'cap': 9.0},
}
PRICE = {'google/veo-3.1-lite': {'720p': 0.05, '1080p': 0.08}, 'google/veo-3.1-fast': {'720p': 0.10, '1080p': 0.12},
         'google/veo-3.1': {'720p': 0.40, '1080p': 0.40}, 'kwaivgi/kling-v3.0-pro': {'720p': 0.168}}
DURS = {'google/veo-3.1-lite': [4, 6, 8], 'google/veo-3.1-fast': [4, 6, 8], 'google/veo-3.1': [4, 6, 8], 'kwaivgi/kling-v3.0-pro': list(range(3, 16))}
VOICES = 'george sarah adam alice bella bill brian callum charlie chris daniel eric harry jessica laura liam lily matilda river roger will'.split()
H = lambda: {'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json', 'X-Title': 'KINOFORGE shot factory'}

def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)
def post(path, body, timeout=600):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(), headers=H())
    return urllib.request.urlopen(req, timeout=timeout)
def get(url, timeout=120):
    return urllib.request.urlopen(urllib.request.Request(url, headers=H()), timeout=timeout)
def b64(path, mime='image/png'): return f'data:{mime};base64,' + base64.b64encode(open(path, 'rb').read()).decode()
def run(cmd): r = subprocess.run(cmd, capture_output=True, text=True); assert r.returncode == 0, r.stderr[-1500:]; return r

class Budget:
    """The piece's ledger plus the whole test budget across pieces."""
    def __init__(self, pdir, cap):
        self.led = Ledger(cap, os.path.join(pdir, 'ledger.json'))
        bf = os.path.join(ROOT, 'pieces', 'BUDGET.json'); self.total_cap = json.load(open(bf))['total_usd'] if os.path.exists(bf) else 50.0
        self.others = sum(json.load(open(p)).get('total', 0) for p in glob.glob(os.path.join(ROOT, 'pieces', '*', 'ledger.json')) if not p.startswith(pdir))
    def check(self, worst, what):
        if not self.led.room(worst): raise OverBudget(f'{what}: the piece cap ${self.led.cap} would be passed (spent ${self.led.total:.2f})')
        if self.others + self.led.total + worst > self.total_cap: raise OverBudget(f'{what}: the test budget ${self.total_cap} would be passed')
    def add(self, **c): self.led.add(**c)

# ------------------------------------------------------------------ images
IMAGE_BACKUPS = ['google/gemini-3.1-flash-image', 'bytedance-seed/seedream-5-0-pro', 'openai/gpt-image-2', 'black-forest-labs/flux-3-image']
def image(B, model, prompt, refs, out, label):
    """One image; on rate limits or failures waits and retries, then falls through to backup models."""
    for m in [model] + [x for x in IMAGE_BACKUPS if x != model]:
        try: return _image(B, m, prompt, refs, out, label)
        except AllFailed as e: log(label, f'{m} failed ({e}); next model')
    raise AllFailed(f'{label}: every image model failed')

def _image(B, model, prompt, refs, out, label):
    B.check(0.15, label)
    content = [{'type': 'text', 'text': prompt}] + [{'type': 'image_url', 'image_url': {'url': b64(r)}} for r in refs]
    body = {'model': model, 'messages': [{'role': 'user', 'content': content}], 'modalities': ['image', 'text'], 'usage': {'include': True}}
    t0 = time.time()
    for attempt in range(3):
        try:
            j = json.load(post('/chat/completions', body, 300))
            imgs = (j['choices'][0]['message'].get('images') or [])
            cost = float((j.get('usage') or {}).get('cost') or 0)
            B.add(seat='image', model=model, task=label, usd=round(cost, 5), s=round(time.time() - t0, 1), ok=bool(imgs))
            if imgs:
                url = imgs[0]['image_url']['url']; open(out, 'wb').write(base64.b64decode(url.split(',', 1)[1])); return out
            log(label, 'no image in reply', str(j['choices'][0]['message'].get('content'))[:200])
        except urllib.error.HTTPError as e:
            log(label, model, 'image error', e.code, e.read().decode(errors='ignore')[:160])
            if e.code == 402: raise OverBudget('key limit')
            if e.code in (400, 404): break
            time.sleep(20 * (attempt + 1)); continue
        except Exception as e: log(label, model, 'image error', type(e).__name__, str(e)[:160])
        time.sleep(5)
    raise AllFailed(f'{label}: no image from {model}')

# ------------------------------------------------------------------ video
def clip(B, tier, prompt, first_frame, dur, aspect, out, label, audio=True):
    T = TIERS[tier]; price = PRICE.get(T['video'], {}).get(T['res'], 0.4)
    B.check(price * dur * 1.05, label)
    body = {'model': T['video'], 'prompt': prompt, 'duration': dur, 'resolution': T['res'], 'aspect_ratio': aspect, 'generate_audio': audio,
            'frame_images': [{'type': 'image_url', 'image_url': {'url': b64(first_frame)}, 'frame_type': 'first_frame'}]}
    t0 = time.time()
    try: job = json.load(post('/videos', body, 120))
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors='ignore')[:400]; log(label, 'submit error', e.code, msg)
        if e.code == 402: raise OverBudget('key limit')
        raise AllFailed(f'{label}: {e.code} {msg}')
    poll = job.get('polling_url') or f"{API}/videos/{job['id']}"
    while time.time() - t0 < 1500:
        time.sleep(15)
        try: st = json.load(get(poll))
        except Exception as e: log(label, 'poll hiccup', e); continue
        if st['status'] == 'completed':
            cost = float((st.get('usage') or {}).get('cost') or price * dur)
            B.add(seat='video', model=T['video'], task=label, usd=round(cost, 4), s=round(time.time() - t0, 1), ok=True)
            url = (st.get('unsigned_urls') or st.get('urls'))[0]
            open(out, 'wb').write(get(url, 300).read()); return out
        if st['status'] == 'failed':
            B.add(seat='video', model=T['video'], task=label, usd=float((st.get('usage') or {}).get('cost') or 0), s=round(time.time() - t0, 1), ok=False)
            raise AllFailed(f"{label}: {st.get('error')}")
    raise AllFailed(f'{label}: timed out')

# ------------------------------------------------------------------ sound
def speech(B, text, voice, out, label):
    B.check(0.05, label)
    req = urllib.request.Request(API + '/audio/speech', data=json.dumps({'model': 'elevenlabs/eleven-v3', 'input': text, 'voice': voice, 'response_format': 'mp3'}).encode(), headers=H())
    t0 = time.time(); data = urllib.request.urlopen(req, timeout=180).read()
    B.add(seat='voice', model='elevenlabs/eleven-v3', task=label, usd=round(len(text) * 40 / 1e6, 5), s=round(time.time() - t0, 1), ok=True)
    open(out, 'wb').write(data); return out

def music(B, prompt, out, label):
    """Lyria 3 through chat completions; returns the file or None (the edit then uses the clips' own audio)."""
    B.check(0.1, label)
    body = {'model': 'google/lyria-3-clip-preview', 'messages': [{'role': 'user', 'content': prompt}], 'modalities': ['text', 'audio'], 'audio': {'format': 'wav'}, 'usage': {'include': True}}
    try:
        j = json.load(post('/chat/completions', body, 300)); m = j['choices'][0]['message']
        B.add(seat='music', model='google/lyria-3-clip-preview', task=label, usd=float((j.get('usage') or {}).get('cost') or 0.04), s=0, ok=True)
        a = m.get('audio') or {}
        data = a.get('data') if isinstance(a, dict) else None
        if not data:
            for part in (m.get('content') if isinstance(m.get('content'), list) else []):
                if isinstance(part, dict) and part.get('type') in ('input_audio', 'audio', 'output_audio'):
                    data = (part.get('input_audio') or part.get('audio') or {}).get('data') or part.get('data')
        if not data: log('music: no audio in reply; keys', list(m.keys())); return None
        raw = base64.b64decode(data.split(',', 1)[-1]); open(out, 'wb').write(raw); return out
    except Exception as e:
        log('music failed:', e); return None

# ------------------------------------------------------------------ review
SCORE = {'type': 'object', 'additionalProperties': False, 'required': ['score', 'problems'], 'properties': {
    'score': {'type': 'number', 'description': '0-10 as a frame of a premium commercial'}, 'problems': {'type': 'array', 'items': {'type': 'string'}}}}
def look(B, label, prompt, images):
    content = [{'type': 'text', 'text': prompt}] + [{'type': 'image_url', 'image_url': {'url': b64(p, 'image/jpeg' if p.endswith('.jpg') else 'image/png')}} for p in images]
    try:
        r, m = ask('eyes', [{'role': 'user', 'content': content}], SCORE, B.led, name='look', max_tokens=800, label=label); return r
    except Exception as e:
        log(label, 'eyes unavailable:', e); return {'score': 10, 'problems': []}

def frames_of(path, n, outdir, tag):
    dur = float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path]).stdout.strip() or 4)
    outs = []
    for k in range(n):
        o = os.path.join(outdir, f'{tag}-{k}.jpg'); run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{dur * (k + 0.5) / n:.2f}', '-i', path, '-frames:v', '1', '-vf', 'scale=640:-2', o]); outs.append(o)
    return outs

# ------------------------------------------------------------------ the treatment
def S(d=''): return {'type': 'string', 'description': d}
TREAT = {'type': 'object', 'additionalProperties': False, 'required': ['title', 'logline', 'look', 'references', 'shots', 'voiceover', 'voice', 'music', 'end_card'], 'properties': {
    'title': S(), 'logline': S('one sentence'),
    'look': S('the visual style in one dense paragraph used in EVERY prompt: medium (photoreal / stylised 3D / clay...), lens and camera language, lighting, palette, texture, grade'),
    'references': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False, 'required': ['id', 'what', 'prompt'], 'properties': {
        'id': S('short id'), 'what': {'type': 'string', 'enum': ['product', 'character', 'location']}, 'prompt': S('a clean reference image: the subject alone, neutral background for product/character, every distinctive detail described; NO text, NO logos')}}},
    'shots': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False, 'required': ['id', 'seconds', 'use_from', 'use', 'speed', 'refs', 'keyframe', 'motion', 'transition'], 'properties': {
        'id': S('S1, S2...'), 'seconds': {'type': 'integer', 'description': 'generated length (model option)'},
        'use_from': {'type': 'number', 'description': 'where the cut starts inside the generated clip (s)'}, 'use': {'type': 'number', 'description': 'seconds of screen time this cut gets (can be shorter than generated: fast editing)'},
        'speed': {'type': 'string', 'enum': ['normal', 'slow']}, 'refs': {'type': 'array', 'items': {'type': 'string'}},
        'keyframe': S('the FIRST frame of the shot as a still: composition, subject, lens, light; NO text, NO logos, NO letters anywhere'),
        'motion': S('what moves during the shot: subject action + camera move, physically plausible, one clear idea'),
        'transition': {'type': 'string', 'enum': ['cut', 'dissolve', 'whip', 'flash', 'fade_from_black'], 'description': 'how this shot comes in'}}}},
    'voiceover': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False, 'required': ['start', 'text'], 'properties': {'start': {'type': 'number'}, 'text': S('one short line; ElevenLabs v3 audio tags like [warmly] allowed')}}},
    'voice': {'type': 'string', 'enum': VOICES}, 'music': S('a music prompt: genre, instruments, tempo, mood arc, no vocals'),
    'end_card': {'type': 'object', 'additionalProperties': False, 'required': ['brand', 'line', 'cta'], 'properties': {'brand': S(), 'line': S('tagline'), 'cta': S('call to action, or empty')}}}}

def treatment(B, brief, tier):
    durs = DURS[TIERS[tier]['video']]
    sys_p = ('You are the creative director of a premium commercial and short-film studio. You write treatments that AI image and video models execute shot by shot. '
             'Rules: hook in the first 1.5 s; every shot one clear idea; motivated camera; real physics; complete bodies; the product identical in every shot (always reference it); '
             'premium light and composition; emotion first, features second; brand voice in few words. NEVER ask the models for text, logos, labels, signs or letters: the brand name and '
             'lines are typeset in the edit. People: invented, no real persons or look-alikes. Voiceover: sparse, after the hook, never describing what we see.')
    dpath = os.path.join(ROOT, 'harness', 'shots', 'directions', f'{brief.get("direction", "classic")}.md')
    direction = open(dpath).read() if os.path.exists(dpath) else ''
    user = (f'BRIEF:\n{json.dumps(brief, indent=1)}\n\nDIRECTION (follow it in every shot, cut and sound choice):\n{direction}\n\n'
            f'Timing: each shot is GENERATED at one of {durs} seconds (the video model\'s options) and then CUT: use_from + use must fit inside the generated length; '
            f'"slow" shots play at 2/3 speed, so they need use x 0.67 s of source. The used times add up to {brief["duration"]} s; the last {brief.get("end_card_s", 3)} s of the last shot carry the end card '
            f'(make that shot calm and at least {brief.get("end_card_s", 3) + 1} s). Aspect {brief.get("aspect", "16:9")}. Voiceover: about 2.5 words per second, first 1.5 s clear. Music: give a tempo in BPM.')
    complete = lambda d: None if all(k in d for k in TREAT['required']) and len(d.get('shots') or []) >= 2 else f'incomplete treatment (keys {list(d)[:6]})'
    t, m = ask('head', [{'role': 'system', 'content': sys_p}, {'role': 'user', 'content': user}], TREAT, B.led, name='treatment', max_tokens=14000, label='treatment', validate=complete)
    json.dump(t, open(os.path.join(ROOT, 'pieces', brief['id'], 'treatment.raw.json'), 'w'), indent=1)
    for s in t['shots']:
        s.setdefault('speed', 'normal'); s.setdefault('transition', 'cut'); s.setdefault('refs', [])
        s['seconds'] = int(round(float(s.get('seconds') or durs[0]))); s['use'] = float(s.get('use') or s['seconds']); s['use_from'] = float(s.get('use_from') or 0)
        need = s['use_from'] + s['use'] * (0.67 if s['speed'] == 'slow' else 1.0)
        s['seconds'] = min([d for d in durs if d >= need] or [max(durs)], key=lambda d: abs(d - max(s['seconds'], need)))
        s['use_from'] = max(0.0, min(s['use_from'], s['seconds'] - s['use'] * (0.67 if s['speed'] == 'slow' else 1.0)))
    return t, m

# ------------------------------------------------------------------ edit
def _font_file(weight):
    for pat in [f'/usr/share/fonts/**/Inter*{weight}*.[ot]tf', f'/usr/share/fonts/**/Inter-{weight}.*', '/usr/share/fonts/**/DejaVuSans-Bold.ttf', '/usr/share/fonts/**/*.ttf']:
        hits = sorted(glob.glob(pat, recursive=True))
        if hits: return hits[0]
def end_card(card, w, h, out):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def font(sz, bold=True):
        f = _font_file('SemiBold' if bold else 'Regular')
        return ImageFont.truetype(f, sz) if f else ImageFont.load_default()
    d.rectangle([0, 0, w, h], fill=(0, 0, 0, 120))
    big, mid, small = font(int(h * 0.085)), font(int(h * 0.035), False), font(int(h * 0.028))
    lines = [(card['brand'].upper(), big, 0.42, 255), (card['line'], mid, 0.54, 235), (card.get('cta') or '', small, 0.64, 210)]
    for text, f, y, a in lines:
        if not text: continue
        tw = d.textlength(text, font=f); d.text(((w - tw) / 2, h * y), text, font=f, fill=(255, 255, 255, a))
    im.save(out)

def beats(wav):
    """Onset times (s) of the music: spectral-flux peaks, so cuts can land on the beat."""
    import numpy as np
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', wav, '-ac', '1', '-ar', '11025', '-f', 's16le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    if len(x) < 11025: return []
    hop, n = 256, 1024; frames = np.lib.stride_tricks.sliding_window_view(x, n)[::hop] * np.hanning(n)
    mag = np.abs(np.fft.rfft(frames, axis=1)); flux = np.maximum(0, np.diff(mag, axis=0)).sum(1)
    flux = (flux - flux.mean()) / (flux.std() + 1e-9); thr = np.convolve(flux, np.ones(16) / 16, 'same') + 0.8
    pk = [i for i in range(1, len(flux) - 1) if flux[i] > thr[i] and flux[i] >= flux[i - 1] and flux[i] >= flux[i + 1]]
    return [round((i + 1) * hop / 11025, 3) for i in pk]

def snap(t, onsets, window=0.3):
    """Move each cut to the nearest musical onset (within window), keeping every shot at least 0.7 s."""
    if not onsets: return
    acc = 0.0
    for k, s in enumerate(t['shots'][:-1]):
        end = acc + s['use']; near = min(onsets, key=lambda o: abs(o - end))
        if abs(near - end) <= window and near - acc >= 0.7:
            delta = near - end; s['use'] = round(s['use'] + delta, 3); t['shots'][k + 1]['use'] = round(max(0.7, t['shots'][k + 1]['use'] - delta), 3)
        acc += s['use']

def edit(pdir, t, brief, clips, vo_files, music_file):
    aspect = brief.get('aspect', '16:9'); w, h = (1080, 1920) if aspect == '9:16' else (1920, 1080)
    norm = []
    for s, c in zip(t['shots'], clips):
        o = os.path.join(pdir, 'work', f'n-{s["id"]}.mp4')
        has_a = bool(run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0', c]).stdout.strip())
        src = ['-i', c] if has_a else ['-i', c, '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo']
        run(['ffmpeg', '-v', 'error', '-y', *src, '-t', str(s['seconds']), '-map', '0:v', '-map', '0:a' if has_a else '1:a', '-vf', f'scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps=24,format=yuv420p',
             '-af', 'aresample=48000', '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-c:a', 'aac', '-ar', '48000', '-ac', '2', o]); norm.append(o)
    # join: cuts are hard; a dissolve overlaps 0.5 s
    v_in = ''.join(f'-i {n} ' for n in norm).split()
    fc = [f'[{k}:v]fps=24,settb=AVTB,setpts=PTS-STARTPTS[p{k}];[{k}:a]asettb=AVTB,asetpts=PTS-STARTPTS[q{k}]' for k in range(len(norm))]
    L = lambda sh: sh.get('use', sh['seconds'])
    cur, acur, t_acc = '[p0]', '[q0]', L(t['shots'][0])
    for k in range(1, len(norm)):
        tr = t['shots'][k]['transition']
        xf = {'dissolve': ('fade', 0.5), 'whip': ('smoothleft', 0.22), 'flash': ('fadewhite', 0.22)}.get(tr)
        if xf:   # (xfade shorter than ~0.2 s is unreliable, so a hard cut uses concat instead)
            d = xf[1]; fc.append(f'{cur}[p{k}]xfade=transition={xf[0]}:duration={d}:offset={t_acc - d:.3f}[v{k}]'); fc.append(f'{acur}[q{k}]acrossfade=d={d}[a{k}]')
        else:
            d = 0.0; fc.append(f'{cur}{acur}[p{k}][q{k}]concat=n=2:v=1:a=1[v{k}][a{k}]')
        cur, acur, t_acc = f'[v{k}]', f'[a{k}]', t_acc + L(t['shots'][k]) - d
    first_fade = 'fade=t=in:st=0:d=0.6,' if t['shots'][0]['transition'] == 'fade_from_black' else ''
    fc.append(f'{cur}{first_fade}eq=contrast=1.04:saturation=1.04,vignette=PI/6,fade=t=out:st={t_acc - 0.6:.2f}:d=0.6[vg]')
    pic = os.path.join(pdir, 'work', 'picture.mp4')
    run(['ffmpeg', '-v', 'error', '-y', *v_in, '-filter_complex', ';'.join(fc), '-map', '[vg]', '-map', acur, '-c:v', 'libx264', '-crf', '16', '-c:a', 'aac', pic])
    total = t_acc; ec_s = brief.get('end_card_s', 3)
    card = os.path.join(pdir, 'work', 'card.png'); end_card(t['end_card'], w, h, card)
    # sound: clip ambience low, music bed ducked under the voice, voice on top, master -14 LUFS
    inputs, mixes = ['-i', pic, '-loop', '1', '-t', f'{total:.2f}', '-i', card], []
    k = 2; fa = ['[0:a]volume=0.35[amb]']; parts = ['[amb]']
    if music_file:
        inputs += ['-stream_loop', '-1', '-i', music_file]; fa.append(f'[{k}:a]atrim=0:{total:.2f},afade=t=out:st={total - 1.5:.2f}:d=1.5,volume=0.8[mus]'); k += 1
    vo_labels = []
    for i, (st, f) in enumerate(vo_files):
        inputs += ['-i', f]; fa.append(f'[{k}:a]adelay={int(st * 1000)}|{int(st * 1000)},volume=1.6[vo{i}]'); vo_labels.append(f'[vo{i}]'); k += 1
    if vo_labels:
        fa.append(f'{"".join(vo_labels)}amix=inputs={len(vo_labels)}:normalize=0,asplit[vox][vkey]')
        if music_file: fa.append('[mus][vkey]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[musd]'); parts.append('[musd]')
        else: fa.append('[vkey]anullsink')
        parts.append('[vox]')
    elif music_file: parts.append('[mus]')
    fa.append(f'{"".join(parts)}amix=inputs={len(parts)}:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[aout]')
    fa.append(f'[1:v]format=rgba,fade=t=in:st={total - ec_s:.2f}:d=0.6:alpha=1[card]')
    fa.append(f'[0:v][card]overlay=0:0:enable=\'gte(t,{total - ec_s:.2f})\'[vout]')
    final = os.path.join(pdir, f'{brief["id"]}.mp4')
    run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(fa), '-map', '[vout]', '-map', '[aout]', '-t', f'{total:.2f}',
         '-c:v', 'libx264', '-crf', '17', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', final])
    if aspect == '16:9':   # social cutdown: the 16:9 film centred on a blurred fill
        run(['ffmpeg', '-v', 'error', '-y', '-i', final, '-filter_complex', '[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=30,eq=brightness=-0.08[bg];[0:v]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2',
             '-c:v', 'libx264', '-crf', '18', '-c:a', 'copy', os.path.join(pdir, f'{brief["id"]}-9x16.mp4')])
    return final

# ------------------------------------------------------------------ main
def main(pdir):
    pdir = os.path.join(ROOT, pdir) if not os.path.isabs(pdir) else pdir
    brief = json.load(open(os.path.join(pdir, 'brief.json'))); tier = brief.get('tier', 'draft'); T = TIERS[tier]
    os.makedirs(os.path.join(pdir, 'work'), exist_ok=True)
    B = Budget(pdir, brief.get('cap_usd', T['cap']))
    report = {'id': brief['id'], 'tier': tier, 'models': T, 'steps': []}
    def save(): report['usd'] = round(B.led.total, 4); json.dump(report, open(os.path.join(pdir, 'report.json'), 'w'), indent=1)
    tpath = os.path.join(pdir, 'treatment.json')
    if os.path.exists(tpath): t = json.load(open(tpath)); log('treatment reused')
    else:
        t, m = treatment(B, brief, tier); json.dump(t, open(tpath, 'w'), indent=1); report['steps'].append({'treatment': m}); log(f'treatment by {m}: {len(t["shots"])} shots')
    save()
    look_txt = t['look']
    refs = {}
    for r in t['references']:
        o = os.path.join(pdir, 'work', f'ref-{r["id"]}.png')
        if not os.path.exists(o): image(B, T['image'], f'{r["prompt"]}\nStyle: {look_txt}\nA clean reference image. No text, no letters, no logos.', [], o, f'ref {r["id"]}')
        refs[r['id']] = o
    log('references', list(refs))
    kfs = []
    for s in t['shots']:
        o = os.path.join(pdir, 'work', f'kf-{s["id"]}.png'); rr = [refs[x] for x in s['refs'] if x in refs]
        prompt = f'{s["keyframe"]}\nStyle: {look_txt}\nKeep every referenced subject exactly as in the reference images. Aspect {brief.get("aspect", "16:9")}. No text, no letters, no logos, no watermarks.'
        if not os.path.exists(o): image(B, T['image'], prompt, rr, o, f'keyframe {s["id"]}')
        v = look(B, f'look {s["id"]}', f'This still is the first frame of shot {s["id"]} of a premium commercial: "{s["keyframe"]}". Score it as a frame of a premium ad. List visible problems: wrong subject, anatomy, product deformed vs reference, text or letters, ugly composition, artefacts.', [o] + rr[:2])
        if v['score'] < 7:
            log(f'{s["id"]} keyframe {v["score"]}: redo ({v["problems"][:3]})')
            image(B, T['image'], prompt + '\nAvoid: ' + '; '.join(v['problems'][:5]), rr, o, f'keyframe {s["id"]} redo')
        kfs.append(o)
    save()
    clips = []
    for s, kf in zip(t['shots'], kfs):
        o = os.path.join(pdir, 'work', f'clip-{s["id"]}.mp4')
        mp = f'{s["motion"]}. {look_txt} Smooth, physically plausible motion; subjects keep their exact appearance; no text appears.'
        if not os.path.exists(o):
            try: clip(B, tier, mp, kf, s['seconds'], brief.get('aspect', '16:9'), o, f'clip {s["id"]}')
            except AllFailed as e: log('clip failed, one retry:', e); clip(B, tier, mp, kf, s['seconds'], brief.get('aspect', '16:9'), o, f'clip {s["id"]} retry')
            fr = frames_of(o, 3, os.path.join(pdir, 'work'), f'chk-{s["id"]}')
            v = look(B, f'check {s["id"]}', f'Three frames (start, middle, end) of one shot of a premium ad: "{s["motion"]}". Score 0-10. Problems: morphing, melting or deformed bodies or product, extra limbs, flicker, text, nonsense motion.', fr)
            report['steps'].append({'clip': s['id'], 'score': v['score'], 'problems': v['problems']})
            if v['score'] < 6 and B.led.room(PRICE.get(T['video'], {}).get(T['res'], 0.4) * s['seconds'] * 1.1):
                log(f'{s["id"]} clip {v["score"]}: regenerate once'); os.rename(o, o + '.rejected.mp4')
                clip(B, tier, mp + ' Avoid: ' + '; '.join(v['problems'][:4]), kf, s['seconds'], brief.get('aspect', '16:9'), o, f'clip {s["id"]} redo')
        clips.append(o); save()
    vo = []
    voice = brief.get('voice') or t['voice']
    for i, line in enumerate(t['voiceover']):
        o = os.path.join(pdir, 'work', f'vo-{i}.mp3')
        if not os.path.exists(o): speech(B, line['text'], voice, o, f'vo {i}')
        vo.append((line['start'], o))
    mus = os.path.join(pdir, 'work', 'music.wav')
    mus = mus if os.path.exists(mus) else music(B, f'{t["music"]} Instrumental only, about {brief["duration"]} seconds, clean ending.', mus, 'music')
    if mus:
        try: on = beats(mus); snap(t, on); log(f'music: {len(on)} onsets; cuts snapped to the beat')
        except Exception as e: log('beat snap skipped:', e)
    final = edit(pdir, t, brief, clips, vo, mus)
    sheet = os.path.join(pdir, 'contact.jpg')
    run(['ffmpeg', '-v', 'error', '-y', '-i', final, '-vf', f"fps={max(1, len(t['shots']) * 2)}/{brief['duration']},scale=480:-2,tile=4x{math.ceil(len(t['shots']) * 2 / 4)}", '-frames:v', '1', sheet])
    try:
        V = {'type': 'object', 'additionalProperties': False, 'required': ['verdict', 'score', 'notes'], 'properties': {'verdict': {'type': 'string', 'enum': ['ship', 'fix']}, 'score': {'type': 'number'}, 'notes': {'type': 'array', 'items': {'type': 'string'}}}}
        r, m = ask('head', [{'role': 'user', 'content': [{'type': 'text', 'text': f'You are the creative director. This contact sheet (2 frames per shot, in order) is the finished piece "{t["title"]}": {t["logline"]}. Brief: {json.dumps(brief)}. Would you show this to a premium client? Verdict, score 0-10, and the concrete notes for the next version.'},
                                                                 {'type': 'image_url', 'image_url': {'url': b64(sheet, 'image/jpeg')}}]}], V, B.led, name='verdict', max_tokens=1200, label='final review')
        report['verdict'] = {'by': m, **r}; log('verdict', r['verdict'], r['score'])
    except Exception as e: log('final review skipped:', e)
    save(); log(f'done: {final}  ${B.led.total:.2f}')

if __name__ == '__main__':
    import traceback
    try: main(sys.argv[1])
    except OverBudget as e: print('STOPPED (budget):', e); sys.exit(2)
    except Exception: traceback.print_exc(); sys.exit(1)
