"""place.py — places the best take of every line on the film's clock, borrowing slack instead of stretching speech.

    python3 harness/voice/place.py JOB.json RUN_DIR OUT.wav [--max-shift 0.6] [--gap 0.25]

RUN_DIR is an unzipped voice-lane result (report.json + takes/). For each line the best passing take is used. A line
whose takes failed ONLY because they run longer than the window (every word right, no repeats, pace inside the target,
voice matches) is still usable: it is placed at its start and the following lines are pushed later, each by at most
--max-shift seconds and only into their own unused time, keeping at least --gap seconds of air between lines.
Writes OUT.wav (48 kHz, picture clock) and OUT.json (where every line landed and why).
"""
import sys, json, os
import numpy as np, soundfile as sf

def main():
    job, run, out = sys.argv[1], sys.argv[2], sys.argv[3]
    opt = lambda k, d: float(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
    max_shift, gap = opt('--max-shift', 0.6), opt('--gap', 0.25)
    J = json.load(open(job)); R = json.load(open(os.path.join(run, 'report.json')))
    by = {l['id']: l for l in R['lines']}
    only_window = lambda t: t['reasons'] and all(r.startswith('too long for its window') for r in t['reasons'])
    plan = []
    for L in J['lines']:
        takes = by[L['id']]['takes']
        good = [t for t in takes if t['pass']]
        how = 'passed'
        if not good:
            good = [t for t in takes if only_window(t)]; how = 'longer than its window, slack borrowed'
        if not good: sys.exit(f"{L['id']}: no usable take: {[t['reasons'] for t in takes]}")
        if how != 'passed':
            good.sort(key=lambda t: t['duration'])          # the shortest usable take needs the least borrowing
        else:
            good.sort(key=lambda t: t['score'])
        t = good[0]
        plan.append({'id': L['id'], 'take': t['take'], 'file': t['file'], 'start': L['start'], 'dur': t['duration'], 'how': how,
                     'wpm': t['wpm'], 'voice_match': t['voice_match']})
    # resolve overlaps front to back
    for a, b in zip(plan, plan[1:]):
        need = a['start'] + a['dur'] + gap - b['start']
        if need > 0:
            if need > max_shift + 1e-6: sys.exit(f"{b['id']} would have to move {need:.2f}s (limit {max_shift}s); shorten {a['id']} or widen its window")
            b['start'] = round(b['start'] + need, 3); b['shift'] = round(need, 3)
    end = J.get('duration') or (plan[-1]['start'] + plan[-1]['dur'] + 1)
    if plan[-1]['start'] + plan[-1]['dur'] > end: sys.exit(f"{plan[-1]['id']} runs past the end of the film")
    SR = 48000; mix = np.zeros(int(end * SR) + SR, dtype=np.float32)
    for p in plan:
        x, sr = sf.read(os.path.join(run, p['file']), dtype='float32')
        if x.ndim > 1: x = x.mean(1)
        if sr != SR:
            from scipy.signal import resample_poly; x = resample_poly(x, SR, sr).astype(np.float32)
        a = int(p['start'] * SR); mix[a:a + len(x)] += x[:len(mix) - a]
    sf.write(out, mix[:int(end * SR)], SR, subtype='PCM_24')
    json.dump(plan, open(os.path.splitext(out)[0] + '.json', 'w'), indent=1)
    for p in plan: print(f"{p['id']} take {p['take']} at {p['start']:.2f}s ({p['dur']:.2f}s, {p['wpm']:.0f} wpm){'  pushed +%.2fs' % p['shift'] if p.get('shift') else ''}  {p['how']}")

if __name__ == '__main__':
    main()
