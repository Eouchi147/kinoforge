"""narrate.py — directed narration with an automatic take checker (KINOFORGE voice lane).

    python3 harness/voice/narrate.py JOB.json ENGINE OUTDIR

A job is a list of lines, each placed at a fixed time on the picture:
    {"film": "dragon-tale", "duration": 126.5, "takes": 3, "profile": "fable",
     "persona": "plain-words description of the narrator (voice design engines)",
     "kokoro_ref": "bm_fable",                     # reference voice for cloning engines
     "lines": [{"id": "L1", "text": "...", "start": 0.6, "end": 6.9, "wpm": [125, 150],
                "tone": "amused, a twinkle in the voice", "exaggeration": 0.55}]}

Engines (all licence-clean for monetized use):
    qwen-design   Qwen3-TTS 1.7B VoiceDesign (Apache-2.0): persona + per-line tone in plain words
    qwen-clone    Qwen3-TTS: one designed reference clip, then every line cloned from it (steadier timbre)
    chatterbox    Resemble Chatterbox (MIT): cloned from a Kokoro reference, emotion via `exaggeration`
    kokoro        Kokoro-82M (Apache-2.0): the old baseline, for comparison

For every line: N takes -> Whisper transcript -> checks (missing / extra / repeated words, pace, unwanted pauses,
fits its window, same voice as the other lines) -> the best passing take. The winners are placed at their start
times on one track. Everything measured is written to report.json, so a reviewer (human or the Ears judge) sees why.
"""
import sys, os, json, re, time, traceback
import numpy as np, soundfile as sf

SR = 48000
job = json.load(open(sys.argv[1])); ENGINE = sys.argv[2]; OUT = sys.argv[3]
os.makedirs(os.path.join(OUT, 'takes'), exist_ok=True)
TAKES = int(job.get('takes', 3))
log = lambda *a: print(f'[{time.strftime("%H:%M:%S")}]', *a, flush=True)

def to48(x, sr):
    x = np.asarray(x, dtype=np.float32).reshape(-1)
    if sr != SR:
        from scipy.signal import resample_poly
        from math import gcd
        g = gcd(SR, sr); x = resample_poly(x, SR // g, sr // g).astype(np.float32)
    return x

def trim(x, thr_db=-45, keep=0.03):
    """Cut silence at both ends (keep 30 ms)."""
    if len(x) == 0: return x
    env = np.convolve(np.abs(x), np.ones(480) / 480, mode='same'); thr = env.max() * 10 ** (thr_db / 20)
    idx = np.where(env > thr)[0]
    if len(idx) == 0: return x
    a = max(0, idx[0] - int(keep * SR)); b = min(len(x), idx[-1] + int(keep * SR)); return x[a:b]

# ------------------------------------------------------------------ engines
def kokoro_engine():
    from kokoro_onnx import Kokoro
    d = os.environ.get('KOKORO_DIR', 'models/kokoro'); k = Kokoro(os.path.join(d, 'kokoro-v1.0.onnx'), os.path.join(d, 'voices-v1.0.bin'))
    voice = job.get('kokoro_ref', 'bm_fable'); lang = 'en-gb' if voice.startswith('b') else 'en-us'
    def gen(line, take):
        speed = [1.0, 0.94, 1.05][take % 3] * float(line.get('kokoro_speed', 0.92))
        s, sr = k.create(line['text'], voice=voice, speed=speed, lang=lang); return to48(s, sr)
    return gen

def kokoro_reference(path, text):
    """A short clean reference clip in the Kokoro voice the film used before (for cloning engines)."""
    from kokoro_onnx import Kokoro
    d = os.environ.get('KOKORO_DIR', 'models/kokoro'); k = Kokoro(os.path.join(d, 'kokoro-v1.0.onnx'), os.path.join(d, 'voices-v1.0.bin'))
    voice = job.get('kokoro_ref', 'bm_fable'); lang = 'en-gb' if voice.startswith('b') else 'en-us'
    s, sr = k.create(text, voice=voice, speed=0.92, lang=lang); sf.write(path, to48(s, sr), SR); return path

REF_TEXT = job.get('ref_text', "Long ago, when the hills were young, the lanterns of the valley were lit by hand, one by one, every single evening.")

def chatterbox_engine():
    import torch
    from chatterbox.tts import ChatterboxTTS
    torch.manual_seed(0)
    m = ChatterboxTTS.from_pretrained(device='cpu')
    ref = kokoro_reference(os.path.join(OUT, 'reference.wav'), REF_TEXT)
    def gen(line, take):
        torch.manual_seed(1000 * take + 7)
        ex = float(line.get('exaggeration', 0.5)) + [0.0, 0.1, -0.08][take % 3]
        cfg = float(line.get('cfg', 0.35)) + [0.0, -0.05, 0.05][take % 3]
        w = m.generate(line['text'], audio_prompt_path=ref, exaggeration=ex, cfg_weight=cfg)
        return to48(w.squeeze(0).cpu().numpy(), m.sr)
    return gen

def qwen_load(name):
    import torch
    from qwen_tts import Qwen3TTSModel
    return Qwen3TTSModel.from_pretrained(name, device_map='cpu', dtype=torch.float32)

def qwen_design_engine():
    import torch
    m = qwen_load('Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign')
    persona = job['persona']
    def gen(line, take):
        torch.manual_seed(1000 * take + 11)
        instruct = persona + ' ' + line.get('tone', '')
        wavs, sr = m.generate_voice_design(text=line['text'], language='English', instruct=instruct.strip())
        return to48(wavs[0], sr)
    return gen

def qwen_clone_engine():
    import torch, gc
    d = qwen_load('Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign')
    torch.manual_seed(3)
    wavs, sr = d.generate_voice_design(text=REF_TEXT, language='English', instruct=job['persona'] + ' ' + job.get('ref_tone', 'calm and warm.'))
    ref = os.path.join(OUT, 'reference.wav'); sf.write(ref, to48(wavs[0], sr), SR)
    del d; gc.collect()
    b = qwen_load('Qwen/Qwen3-TTS-12Hz-1.7B-Base')
    prompt = b.create_voice_clone_prompt(ref_audio=ref, ref_text=REF_TEXT, x_vector_only_mode=False)
    def gen(line, take):
        torch.manual_seed(1000 * take + 13)
        w, sr2 = b.generate_voice_clone(text=line['text'], language='English', voice_clone_prompt=prompt)
        return to48(w[0], sr2)
    return gen

ENGINES = {'kokoro': kokoro_engine, 'chatterbox': chatterbox_engine, 'qwen-design': qwen_design_engine, 'qwen-clone': qwen_clone_engine}

# ------------------------------------------------------------------ the take checker
_asr = None
def asr():
    global _asr
    if _asr is None:
        from faster_whisper import WhisperModel
        _asr = WhisperModel(os.environ.get('KF_ASR', 'medium.en'), device='cpu', compute_type='int8')
    return _asr

NUM = {'0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four', '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine', '10': 'ten',
       '12': 'twelve', '20': 'twenty', '29': 'twenty nine', '29.5': 'twenty nine and a half'}
def words(s):
    s = s.lower().replace('’', "'").replace('-', ' ')
    s = re.sub(r"\d+(\.\d+)?", lambda m: ' ' + NUM.get(m.group(0), m.group(0)) + ' ', s)
    return re.findall(r"[a-z']+", s)

def edit_ops(ref, hyp):
    """Levenshtein alignment -> counts of substitutions, deletions (missing words), insertions (extra words)."""
    n, m = len(ref), len(hyp); D = np.zeros((n + 1, m + 1), int); D[:, 0] = range(n + 1); D[0, :] = range(m + 1)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i, j] = min(D[i - 1, j] + 1, D[i, j - 1] + 1, D[i - 1, j - 1] + (ref[i - 1] != hyp[j - 1]))
    i, j, S, Dl, I = n, m, 0, 0, 0
    while i > 0 or j > 0:
        if i > 0 and j > 0 and D[i, j] == D[i - 1, j - 1] + (ref[i - 1] != hyp[j - 1]): S += ref[i - 1] != hyp[j - 1]; i -= 1; j -= 1
        elif i > 0 and D[i, j] == D[i - 1, j] + 1: Dl += 1; i -= 1
        else: I += 1; j -= 1
    return S, Dl, I

def doubled(ws): return sum(1 for a, b in zip(ws, ws[1:]) if a == b)

def check(x, line):
    """Measure one take. Returns a dict with pass/fail and a score (lower is better)."""
    tmp = os.path.join(OUT, '_asr.wav'); sf.write(tmp, x, SR)
    segs, _ = asr().transcribe(tmp, language='en', word_timestamps=True, beam_size=5, vad_filter=False, condition_on_previous_text=False)
    W = [w for s in segs for w in (s.words or [])]
    hyp_text = ' '.join(w.word.strip() for w in W); hyp = words(hyp_text); ref = words(line['text'])
    S, Dl, I = edit_ops(ref, hyp); wer = (S + Dl + I) / max(1, len(ref))
    rep = max(0, doubled(hyp) - doubled(ref))
    dur = len(x) / SR; window = line['end'] - line['start']
    t0 = W[0].start if W else 0.0; t1 = W[-1].end if W else dur
    speech = max(0.3, t1 - t0); wpm = 60 * len(ref) / speech
    gaps = [W[k + 1].start - W[k].end for k in range(len(W) - 1)]
    punct = len(re.findall(r'[.,;:!?…]|\.\.\.', line['text'].strip().rstrip('.!?…')))   # pauses the script asks for (inside the line)
    long_gaps = [g for g in gaps if g > 1.2]; mid_gaps = [g for g in gaps if g > 0.5]
    lo, hi = line.get('wpm', [130, 165])
    reasons = []
    allowed = max(0, len(ref) // 12)
    if S + Dl + I > allowed: reasons.append(f'words wrong: {S} swapped, {Dl} missing, {I} extra')
    if rep: reasons.append(f'{rep} repeated word(s)')
    if dur > window - 0.1: reasons.append(f'too long for its window ({dur:.2f}s > {window - 0.1:.2f}s)')
    if long_gaps: reasons.append(f'pause of {max(long_gaps):.2f}s')
    if len(mid_gaps) > punct + 1: reasons.append(f'{len(mid_gaps)} pauses over 0.5s where the script has {punct}')
    if wpm < lo * 0.88: reasons.append(f'too slow ({wpm:.0f} wpm)')
    if wpm > hi * 1.12: reasons.append(f'too fast ({wpm:.0f} wpm)')
    mid = (lo + hi) / 2
    score = abs(wpm - mid) / mid + 2.0 * wer + 0.5 * rep + 0.2 * len(mid_gaps)
    return {'heard': hyp_text, 'wer': round(wer, 3), 'repeats': rep, 'duration': round(dur, 2), 'window': round(window, 2),
            'wpm': round(wpm, 1), 'max_gap': round(max(gaps) if gaps else 0.0, 2), 'pass': not reasons, 'reasons': reasons, 'score': round(score, 4)}

_enc = None
def embed(x):
    global _enc
    try:
        from resemblyzer import VoiceEncoder, preprocess_wav
        if _enc is None: _enc = VoiceEncoder('cpu')
        from scipy.signal import resample_poly
        y = resample_poly(x, 1, 3).astype(np.float32)            # 48 kHz -> 16 kHz
        return _enc.embed_utterance(preprocess_wav(y, source_sr=16000))
    except Exception as e:
        log('speaker embedding unavailable:', e); return None

def loud(x, target=-20.0):
    try:
        import pyloudnorm as pyln
        L = pyln.Meter(SR).integrated_loudness(x)
        if np.isfinite(L): x = x * 10 ** ((target - L) / 20)
    except Exception: x = x / (np.abs(x).max() + 1e-9) * 0.5
    return np.clip(x, -0.99, 0.99).astype(np.float32)

# ------------------------------------------------------------------ run
report = {'film': job['film'], 'engine': ENGINE, 'lines': [], 'started': time.strftime('%Y-%m-%d %H:%M:%S')}
try:
    t_load = time.time(); gen = ENGINES[ENGINE](); report['load_s'] = round(time.time() - t_load, 1); log(ENGINE, 'loaded in', report['load_s'], 's')
except Exception:
    report['error'] = traceback.format_exc(); log(report['error']); json.dump(report, open(os.path.join(OUT, 'report.json'), 'w'), indent=1); sys.exit(0)

all_takes = []
for line in job['lines']:
    entry = {'id': line['id'], 'text': line['text'], 'takes': []}
    for k in range(TAKES):
        t0 = time.time()
        try:
            x = loud(trim(gen(line, k)))
        except Exception:
            entry['takes'].append({'take': k, 'error': traceback.format_exc()[-600:]}); continue
        path = os.path.join(OUT, 'takes', f"{line['id']}_{k}.wav"); sf.write(path, x, SR, subtype='PCM_16')
        try: q = check(x, line)
        except Exception: q = {'pass': False, 'reasons': ['checker crashed'], 'score': 99.0, 'error': traceback.format_exc()[-1500:]}; log(q['error'])
        q.update({'take': k, 'file': os.path.relpath(path, OUT), 'gen_s': round(time.time() - t0, 1)})
        entry['takes'].append(q); all_takes.append((line['id'], k, x)); log(line['id'], k, 'PASS' if q['pass'] else 'fail', q['reasons'], q['heard'])
    report['lines'].append(entry)

# same voice on every line: distance of each take from the engine's average voice
embs = {(lid, k): embed(x) for lid, k, x in all_takes}
good = [e for e in embs.values() if e is not None]
if good:
    centre = np.mean(good, axis=0); centre /= np.linalg.norm(centre)
    for entry in report['lines']:
        for q in entry['takes']:
            e = embs.get((entry['id'], q.get('take')))
            if e is not None:
                sim = float(np.dot(e, centre) / np.linalg.norm(e)); q['voice_match'] = round(sim, 3)
                if sim < 0.75: q['pass'] = False; q['reasons'].append(f'voice drifts from the others ({sim:.2f})')
                q['score'] = round(q['score'] + (1 - sim), 4)

# pick, place, write
n = int(job['duration'] * SR); track = np.zeros(n, np.float32); picked = {}
for entry in report['lines']:
    ok = [q for q in entry['takes'] if q.get('pass')]
    pool = ok or [q for q in entry['takes'] if 'score' in q]
    if not pool: entry['chosen'] = None; continue
    best = min(pool, key=lambda q: q['score']); entry['chosen'] = best['take']; entry['chosen_passed'] = bool(ok)
    x, _ = sf.read(os.path.join(OUT, best['file']), dtype='float32')
    line = next(l for l in job['lines'] if l['id'] == entry['id'])
    a = int(line['start'] * SR); b = min(n, a + len(x)); track[a:b] += x[:b - a]; picked[entry['id']] = best['file']
sf.write(os.path.join(OUT, f"{job['film']}-{ENGINE}-narration.wav"), np.stack([track, track], 1), SR, subtype='PCM_24')
report['passed_lines'] = sum(1 for e in report['lines'] if e.get('chosen_passed'))
report['total_lines'] = len(report['lines']); report['finished'] = time.strftime('%Y-%m-%d %H:%M:%S')
json.dump(report, open(os.path.join(OUT, 'report.json'), 'w'), indent=1)
log('done', report['passed_lines'], '/', report['total_lines'], 'lines passed')
