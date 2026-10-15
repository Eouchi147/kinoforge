"""board.py — a style board: a few stills per direction, so Sam picks a look before any video money is spent.

    python3 harness/shots/board.py boards/<id>            (needs OPENROUTER_API_KEY)

boards/<id>/board.json:
    {"cap_usd": 1.5, "aspect": "16:9",
     "frames": [{"id": "hero-1", "direction": "hero", "model": "bytedance-seed/seedream-5-0-pro", "prompt": "..."}]}
Writes boards/<id>/out/<frame id>.png and .jpg, boards/<id>/ledger.json and boards/<id>/account.json
(the OpenRouter key's usage before and after, so the spend is the account's own number, not an estimate).
Frames may set "aspect" (e.g. "1:1") and "cutout": true (background removed with rembg -> <id>.cut.png, transparent).
Optional "clips": [{"id", "from": frame id or a path under the board, "prompt", "seconds", "model"}] make short image-to-video
tests from approved stills. Every call is booked against cap_usd before it is made; nothing runs past the cap.
"""
import os, sys, json, time, base64, urllib.request, urllib.error, concurrent.futures as cf
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'director'))
from agents import Ledger, API, KEY

BACKUP = {'bytedance-seed/seedream-5-0-pro': 'google/gemini-3-pro-image', 'google/gemini-3-pro-image': 'bytedance-seed/seedream-5-0-pro'}
WORST = 0.16   # booked per image before the call; the real cost replaces it
MODS = {}      # model -> output modalities that worked (Seedream is image-only)


def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)


def key_usage():
    try:
        req = urllib.request.Request(f'{API}/key', headers={'Authorization': f'Bearer {KEY}'})
        d = json.load(urllib.request.urlopen(req, timeout=30))['data']
        return {'usage': d.get('usage'), 'limit': d.get('limit'), 'remaining': d.get('limit_remaining')}
    except Exception as e:
        return {'error': str(e)[:120]}


class Book:
    def __init__(self, led): self.led, self.pending, self.lock = led, 0.0, __import__('threading').Lock()
    def take(self):
        with self.lock:
            if not self.led.room(self.pending + WORST): return False
            self.pending += WORST; return True
    def give(self):
        with self.lock: self.pending = max(0.0, self.pending - WORST)


def one(book, model, prompt, aspect, out, label):
    body = {'model': model, 'messages': [{'role': 'user', 'content': prompt}], 'modalities': MODS.get(model, ['image', 'text']),
            'image_config': {'aspect_ratio': aspect}, 'usage': {'include': True}}
    for attempt in range(4):
        if not book.take(): raise RuntimeError('board cap reached')
        t0 = time.time()
        try:
            req = urllib.request.Request(f'{API}/chat/completions', data=json.dumps(body).encode(),
                                         headers={'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json', 'X-Title': 'KINOFORGE style board'})
            j = json.load(urllib.request.urlopen(req, timeout=300))
            imgs = j['choices'][0]['message'].get('images') or []
            cost = float((j.get('usage') or {}).get('cost') or 0)
            book.led.add(seat='image', model=model, task=label, usd=round(cost, 5), s=round(time.time() - t0, 1), ok=bool(imgs))
            if imgs:
                open(out, 'wb').write(base64.b64decode(imgs[0]['image_url']['url'].split(',', 1)[1])); return model
            log(label, model, 'no image:', str(j['choices'][0]['message'].get('content'))[:160])
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors='ignore')[:300]; log(label, model, 'error', e.code, msg[:200])
            if e.code == 402: raise RuntimeError('OpenRouter key limit reached')
            if e.code == 404 and 'modalit' in msg and body['modalities'] != ['image']: body['modalities'] = MODS[model] = ['image']; continue
            if e.code == 400 and 'image_config' in body: body.pop('image_config'); continue
            if e.code in (400, 404): break
            time.sleep(12)
        except Exception as e:
            log(label, model, 'error', type(e).__name__, str(e)[:160]); time.sleep(5)
        finally:
            book.give()
    return None


VPRICE = {'google/veo-3.1-fast': 0.12, 'google/veo-3.1-lite': 0.05, 'google/veo-3.1': 0.40, 'kwaivgi/kling-v3.0-pro': 0.168}   # worst case per second


def clip(led, model, prompt, img, seconds, out, label):
    """One image-to-video test: the still is the first frame. Booked at the worst-case price before submitting."""
    from PIL import Image
    worst = VPRICE.get(model, 0.4) * seconds * 1.05
    if not led.room(worst): raise RuntimeError(f'{label}: the board cap ${led.cap} would be passed')
    im = Image.open(img).convert('RGB'); w, h = im.size; ta = 16 / 9
    if abs(w / h - ta) > 0.01:
        if w / h > ta: nw = int(h * ta); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else: nh = int(w / ta); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    tmp = out[:-4] + '.first.jpeg'; im.save(tmp, quality=93)
    H = {'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json', 'X-Title': 'KINOFORGE style board'}
    body = {'model': model, 'prompt': prompt, 'duration': seconds, 'resolution': '1080p', 'aspect_ratio': '16:9', 'generate_audio': False,
            'frame_images': [{'type': 'image_url', 'image_url': {'url': 'data:image/jpeg;base64,' + base64.b64encode(open(tmp, 'rb').read()).decode()}, 'frame_type': 'first_frame'}]}
    t0 = time.time()
    job = json.load(urllib.request.urlopen(urllib.request.Request(f'{API}/videos', data=json.dumps(body).encode(), headers=H), timeout=120))
    poll = job.get('polling_url') or f"{API}/videos/{job['id']}"; log(label, 'submitted', model, f'{seconds}s')
    while time.time() - t0 < 1500:
        time.sleep(15)
        try: st = json.load(urllib.request.urlopen(urllib.request.Request(poll, headers=H), timeout=60))
        except Exception as e: log(label, 'poll hiccup', e); continue
        if st['status'] == 'completed':
            cost = float((st.get('usage') or {}).get('cost') or 0); est = not cost
            if est: cost = VPRICE.get(model, 0.4) * seconds   # no cost reported: book the list price so the cap still holds
            led.add(seat='video', model=model, task=label, usd=round(cost, 4), s=round(time.time() - t0, 1), ok=True, note='estimated' if est else 'reported')
            url = (st.get('unsigned_urls') or st.get('urls'))[0]
            open(out, 'wb').write(urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=300).read()); log(label, 'done', f'${cost}'); return model
        if st['status'] == 'failed':
            led.add(seat='video', model=model, task=label, usd=float((st.get('usage') or {}).get('cost') or 0), s=round(time.time() - t0, 1), ok=False)
            raise RuntimeError(f"{label}: {st.get('error')}")
    raise RuntimeError(f'{label}: timed out')


def main(bdir):
    spec = json.load(open(os.path.join(bdir, 'board.json')))
    outd = os.path.join(bdir, 'out'); os.makedirs(outd, exist_ok=True)
    led = Ledger(float(spec.get('cap_usd', 1.5)), os.path.join(bdir, 'ledger.json')); book = Book(led)
    before = key_usage(); log('key before:', before)
    aspect = spec.get('aspect', '16:9')

    from PIL import Image
    def job(f):
        out = os.path.join(outd, f['id'] + '.png')
        if os.path.exists(out): return f['id'], 'kept'
        try:
            for m in [f['model'], BACKUP.get(f['model'])]:
                if m and one(book, m, f['prompt'], f.get('aspect', aspect), out, f['id']):
                    im = Image.open(out).convert('RGB'); im.thumbnail((1920, 1920)); im.save(out[:-4] + '.jpg', quality=90)   # saved at once: a later failure never loses it
                    log(f['id'], 'done with', m); return f['id'], m
        except Exception as e: log(f['id'], 'stopped:', e)
        return f['id'], None

    with cf.ThreadPoolExecutor(3) as ex: results = list(ex.map(job, spec.get('frames', [])))
    cut_session = None
    for f in spec.get('frames', []):
        src = os.path.join(outd, f['id'] + '.png')
        if f.get('cutout') and os.path.exists(src) and not os.path.exists(src[:-4] + '.cut.png'):
            try:
                from rembg import remove, new_session
                cut_session = cut_session or new_session('isnet-general-use')
                cut = remove(Image.open(src).convert('RGB'), session=cut_session); bb = cut.getbbox()
                (cut.crop(bb) if bb else cut).save(src[:-4] + '.cut.png'); log(f['id'], 'cut out')
            except Exception as e: log(f['id'], 'cutout failed:', e)
    clips = {}
    for c in spec.get('clips', []):
        frm = c['from']; img = os.path.join(outd, frm + '.png') if os.path.exists(os.path.join(outd, frm + '.png')) else os.path.join(bdir, frm)
        out = os.path.join(outd, c['id'] + '.mp4')
        if os.path.exists(out): clips[c['id']] = 'kept'; continue
        if not os.path.exists(img): log(c['id'], 'no source still', img); clips[c['id']] = None; continue
        try: clips[c['id']] = clip(led, c.get('model', 'google/veo-3.1-fast'), c['prompt'], img, int(c.get('seconds', 6)), out, c['id'])
        except Exception as e: log(c['id'], 'clip stopped:', e); clips[c['id']] = None
    results = list(results) + list(clips.items())
    after = key_usage(); log('key after:', after)
    spent = round(after['usage'] - before['usage'], 4) if 'usage' in after and 'usage' in before else None
    json.dump({'before': before, 'after': after, 'board_spent': spent, 'ledger_total': round(led.total, 4),
               'frames': dict(results)}, open(os.path.join(bdir, 'account.json'), 'w'), indent=1)
    log('board spent', spent, '| ledger', round(led.total, 4), '| missing:', [f for f, m in results if not m])


if __name__ == '__main__':
    main(sys.argv[1].rstrip('/'))
