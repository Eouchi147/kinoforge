"""board.py — a style board: a few stills per direction, so Sam picks a look before any video money is spent.

    python3 harness/shots/board.py boards/<id>            (needs OPENROUTER_API_KEY)

boards/<id>/board.json:
    {"cap_usd": 1.5, "aspect": "16:9",
     "frames": [{"id": "hero-1", "direction": "hero", "model": "bytedance-seed/seedream-5-0-pro", "prompt": "..."}]}
Writes boards/<id>/out/<frame id>.png and .jpg, boards/<id>/ledger.json and boards/<id>/account.json
(the OpenRouter key's usage before and after, so the spend is the account's own number, not an estimate).
Images only: this script cannot start a video job.
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
                if m and one(book, m, f['prompt'], aspect, out, f['id']):
                    im = Image.open(out).convert('RGB'); im.thumbnail((1920, 1920)); im.save(out[:-4] + '.jpg', quality=90)   # saved at once: a later failure never loses it
                    log(f['id'], 'done with', m); return f['id'], m
        except Exception as e: log(f['id'], 'stopped:', e)
        return f['id'], None

    with cf.ThreadPoolExecutor(3) as ex: results = list(ex.map(job, spec['frames']))
    after = key_usage(); log('key after:', after)
    spent = round(after['usage'] - before['usage'], 4) if 'usage' in after and 'usage' in before else None
    json.dump({'before': before, 'after': after, 'board_spent': spent, 'ledger_total': round(led.total, 4),
               'frames': dict(results)}, open(os.path.join(bdir, 'account.json'), 'w'), indent=1)
    log('board spent', spent, '| ledger', round(led.total, 4), '| missing:', [f for f, m in results if not m])


if __name__ == '__main__':
    main(sys.argv[1].rstrip('/'))
