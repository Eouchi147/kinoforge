"""diagnose.py — listen to a finished narration track and report what a viewer would notice.

    python3 harness/voice/diagnose.py SCRIPT.json AUDIO OUT.json

SCRIPT.json = {"lines": [{"id", "text", "start"}...]} (the intended script and where each line should start).
Reports per line: what was heard, missing / extra / repeated words, pace (words per minute) and pauses,
so "the narrator repeats words" or "slows down for no reason" becomes a list of exact times.
"""
import sys, json, re, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np

script = json.load(open(sys.argv[1])); audio = sys.argv[2]; out = sys.argv[3]
from faster_whisper import WhisperModel
m = WhisperModel(os.environ.get('KF_ASR', 'medium.en'), device='cpu', compute_type='int8')
segs, _ = m.transcribe(audio, language='en', word_timestamps=True, beam_size=5, condition_on_previous_text=False)
W = [w for s in segs for w in (s.words or [])]
norm = lambda s: re.findall(r"[a-z']+", s.lower().replace('’', "'").replace('-', ' '))
heard = [(norm(w.word)[0] if norm(w.word) else '', w.start, w.end) for w in W]
heard = [h for h in heard if h[0]]

lines = script['lines']; res = []
for i, L in enumerate(lines):
    a = L['start'] - 0.4; b = lines[i + 1]['start'] - 0.2 if i + 1 < len(lines) else 1e9
    ws = [h for h in heard if a <= h[1] < b]
    hyp = [h[0] for h in ws]; ref = norm(L['text'])
    reps = [(ws[k][0], round(ws[k][1], 2)) for k in range(1, len(ws)) if ws[k][0] == ws[k - 1][0] and not any(ref[j] == ref[j - 1] == ws[k][0] for j in range(1, len(ref)))]
    gaps = [(round(ws[k][1] - ws[k - 1][2], 2), round(ws[k - 1][2], 2)) for k in range(1, len(ws)) if ws[k][1] - ws[k - 1][2] > 0.45]
    span = (ws[-1][2] - ws[0][1]) if ws else 0
    wpm = round(60 * len(ref) / span, 1) if span > 0.3 else None
    extra = [w for w in hyp if w not in ref]; missing = [w for w in ref if w not in hyp]
    res.append({'id': L['id'], 'script': L['text'], 'heard': ' '.join(hyp), 'starts_at': round(ws[0][1], 2) if ws else None,
                'repeated': reps, 'extra_words': extra, 'missing_words': missing, 'wpm': wpm, 'pauses_over_0.45s': gaps})
rates = [r['wpm'] for r in res if r['wpm']]
summary = {'audio': os.path.basename(audio), 'median_wpm': float(np.median(rates)) if rates else None,
           'lines_with_repeats': [r['id'] for r in res if r['repeated']],
           'slow_lines': [r['id'] for r in res if r['wpm'] and rates and r['wpm'] < 0.8 * np.median(rates)],
           'lines_with_wrong_words': [r['id'] for r in res if r['extra_words'] or r['missing_words']]}
json.dump({'summary': summary, 'lines': res}, open(out, 'w'), indent=1)
print(json.dumps(summary, indent=1))
