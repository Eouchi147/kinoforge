"""voice_free.py: the narration with a free open voice on the runner (no API, no money).

    <tts python> films/director/voice_free.py films/studio/<id>

Engines (ad.json prep.voice = "engine" or "engine|option"):
  chatterbox           Chatterbox (Resemble AI, MIT), CPU, built-in voice; "chatterbox|path/to/ref.wav" clones a reference
                       voice that is in this repo (only voices we have the right to use)
  kokoro|bm_george     Kokoro-82M (Apache 2.0, ONNX) through harness/audio/tts.py; model files in $KOKORO_DIR
Every line is checked by speech recognition (faster-whisper base.en); a take with a word error rate over 0.15 is redone
with another seed (at most 3 takes, the best is kept). Silence is trimmed at both ends. Writes audio/vo/line<k>.mp3 and
audio/vo.json in prep.py's format ({voice, lines: [{text, file, dur, words: [[word, start, end]]}]}) plus wer and takes.
"""
import os, sys, json, re, time, subprocess

def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)
def plain(t): return re.sub(r'\[[^\]]*\]\s*', '', t).strip()

def norm(s): return re.sub(r"[^a-z0-9' ]", ' ', s.lower().replace('-', ' ')).split()

def wer(ref, hyp):
    r, h = norm(ref), norm(hyp); d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        p, d[0] = d[0], i
        for j in range(1, len(h) + 1): p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (r[i - 1] != h[j - 1]))
    return d[len(h)] / max(len(r), 1)

def pcm16k(p):
    """Decode with ffmpeg ourselves (newer PyAV breaks faster-whisper's own decoder)."""
    import numpy as np
    raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()

def ff(*a): subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', *a], check=True)
def dur_of(p): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout.strip() or 0)

TRIM = 'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.12,areverse'


class Chatterbox:
    def __init__(self, opt, s):
        import torch
        from chatterbox.tts import ChatterboxTTS
        torch.set_num_threads(os.cpu_count() or 4); self.torch = torch
        self.m = ChatterboxTTS.from_pretrained(device='cpu'); self.ref = opt; self.s = s
    def say(self, text, out_wav, seed):
        import torchaudio as ta
        self.torch.manual_seed(seed)
        kw = dict(exaggeration=float(self.s.get('exaggeration', 0.55)), cfg_weight=float(self.s.get('cfg', 0.4)), temperature=float(self.s.get('temperature', 0.75)))
        if self.ref: kw['audio_prompt_path'] = self.ref
        ta.save(out_wav, self.m.generate(text, **kw), self.m.sr)


class Kokoro:
    def __init__(self, opt, s):
        sys.path.insert(0, os.path.join(ROOT, 'harness', 'audio')); import tts
        self.tts = tts; self.voice = opt or 'bm_george'; self.s = s
    def say(self, text, out_wav, seed):
        speed = float(self.s.get('speed', 1.0)) * (1.0 + 0.03 * ((seed % 3) - 1))   # another take: a touch faster or slower
        self.tts.say(text, voice=self.voice, speed=speed, out=out_wav)


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main(d):
    ad = json.load(open(os.path.join(d, 'ad.json'))); P = ad['prep']; out = os.path.join(d, 'audio'); os.makedirs(os.path.join(out, 'vo'), exist_ok=True)
    if os.path.exists(os.path.join(out, 'vo.json')): log('vo.json exists, skipped'); return
    engine, _, opt = P.get('voice', 'chatterbox').partition('|')
    if opt and engine == 'chatterbox': opt = os.path.join(ROOT, opt) if not os.path.isabs(opt) else opt
    E = {'chatterbox': Chatterbox, 'kokoro': Kokoro}[engine](opt, P.get('voice_settings', {}))
    from faster_whisper import WhisperModel
    asr = WhisperModel('base.en', device='cpu', compute_type='int8'); lines = []; t_all = time.time()
    for k, line in enumerate(P['vo']):
        text = plain(line['text']); best = None
        for take in range(3):
            t0 = time.time(); raw = os.path.join(out, 'vo', f'line{k}.take{take}.wav'); mp3 = os.path.join(out, 'vo', f'line{k}.take{take}.mp3')
            E.say(text, raw, seed=1 + take * 17 + k)
            ff('-i', raw, '-af', TRIM, '-ar', '48000', '-ac', '1', '-b:a', '160k', mp3); os.remove(raw)
            segs, _ = asr.transcribe(pcm16k(mp3), word_timestamps=True, language='en', beam_size=3)
            segs = list(segs); hyp = ' '.join(s.text for s in segs).strip(); e = wer(text, hyp)
            words = [[w.word.strip(), round(w.start, 3), round(w.end, 3)] for s in segs for w in (s.words or [])]
            rec = {'mp3': mp3, 'wer': round(e, 3), 'hyp': hyp, 'words': words, 'secs': round(time.time() - t0, 1)}
            log(f'line {k} take {take}: wer {e:.2f}, {rec["secs"]} s, "{hyp[:80]}"')
            if best is None or e < best['wer']:
                if best: os.remove(best['mp3'])
                best = rec
            else: os.remove(mp3)
            if e <= 0.15: break
        dst = os.path.join(out, 'vo', f'line{k}.mp3'); os.replace(best['mp3'], dst)
        lines.append({'text': text, 'file': f'audio/vo/line{k}.mp3', 'dur': round(dur_of(dst), 3), 'words': best['words'], 'wer': best['wer'], 'heard': best['hyp']})
    voice = engine + (('|' + os.path.relpath(opt, ROOT) if engine == 'chatterbox' else '|' + opt) if opt else '')
    json.dump({'voice': voice, 'engine': engine, 'cost_usd': 0, 'seconds': round(time.time() - t_all, 1), 'lines': lines}, open(os.path.join(out, 'vo.json'), 'w'), indent=1)
    bad = [k for k, l in enumerate(lines) if l['wer'] > 0.25]
    log(f'voice done: {len(lines)} lines in {time.time() - t_all:.0f} s' + (f'; lines still misheard (wer > 0.25): {bad}' if bad else ''))


if __name__ == '__main__':
    main(sys.argv[1].rstrip('/'))
