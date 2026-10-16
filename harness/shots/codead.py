"""codead.py — an ad built in code: render the scene, voice it, score it, add UI sounds, mix it.

    python3 harness/shots/codead.py ads/<id>            (needs OPENROUTER_API_KEY, node + Playwright, ffmpeg, numpy)

ads/<id>/ad.json:
    {"id", "scene": "ads/<id>", "w", "h", "fps", "cap_usd",
     "voice": "sarah", "vo": [{"start": s, "text": "..."}],          ElevenLabs v3 through OpenRouter, one file per line
     "music": {"prompt": "...", "gain_db": -15},                       Lyria 3 through OpenRouter (streamed); skipped if it fails
     "sfx": [{"t": s, "kind": "ring|click|pop|whoosh|check|chime"}]}  synthesised here, no files, no licences
The picture comes from the scene page (HTML/CSS, see harness/dom-render.cjs): no AI fees, no AI glitches.
Writes ads/<id>/out/<id>.mp4 (16:9 master), <id>-sheet.jpg (contact sheet), stems, and ads/<id>/ledger.json.
Money: every paid call is booked against cap_usd and the whole test budget (pieces/BUDGET.json) first.
"""
import os, sys, json, subprocess, math, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from factory import speech, music, Budget, run, log, ROOT

SR = 48000


def dur_of(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout.strip() or 0)


def synth(kind, np):
    """Short, quiet interface sounds. Returns a mono float array at 48 kHz."""
    t = lambda d: np.arange(int(SR * d)) / SR
    if kind == 'ring':
        x = t(0.42); env = np.minimum(1, x / 0.01) * np.exp(-x * 4)
        return 0.10 * env * (np.sin(2 * np.pi * 659 * x) + 0.7 * np.sin(2 * np.pi * 831 * x)) * (0.75 + 0.25 * np.sin(2 * np.pi * 18 * x))
    if kind == 'impact':   # a deep, clean hit for a drop or a logo slam
        x = t(1.2); f = 46 + 60 * np.exp(-x * 18); ph = 2 * np.pi * np.cumsum(f) / SR
        return 0.55 * np.minimum(1, x / 0.004) * np.exp(-x * 3.5) * np.sin(ph)
    if kind == 'tick':
        x = t(0.025); return 0.12 * np.exp(-x * 400) * np.sin(2 * np.pi * 3200 * x)
    if kind == 'riser':   # 1.5 s of soft noise rising into a cut
        x = t(1.5); rng = np.random.default_rng(3); n = rng.standard_normal(len(x))
        for k in (40, 40): n = np.convolve(n, np.ones(k) / k, mode='same')
        n = n / (np.abs(n).max() + 1e-9); return 0.14 * (x / x[-1]) ** 2.5 * n
    if kind == 'click':
        x = t(0.03); return 0.25 * np.exp(-x * 220) * np.sin(2 * np.pi * 2400 * x)
    if kind == 'pop':
        x = t(0.12); f = 820 - 380 * np.minimum(1, x / 0.06); ph = 2 * np.pi * np.cumsum(f) / SR
        return 0.09 * np.minimum(1, x / 0.006) * np.exp(-x * 34) * np.sin(ph)   # a soft, round pop (the listening check found the first one sharp)
    if kind == 'whoosh':
        x = t(0.5); rng = np.random.default_rng(7); n = rng.standard_normal(len(x))
        for k in (90, 90, 90): n = np.convolve(n, np.ones(k) / k, mode='same')   # three box filters: a soft, dark air movement, not hiss
        n = n / (np.abs(n).max() + 1e-9)
        return 0.10 * np.sin(np.pi * x / x[-1]) ** 2 * n
    if kind == 'check':
        a, b = t(0.09), t(0.16)
        s1 = 0.06 * np.exp(-a * 25) * np.sin(2 * np.pi * 660 * a); s2 = 0.06 * np.exp(-b * 14) * np.sin(2 * np.pi * 990 * b)
        return np.concatenate([s1, s2])
    if kind == 'chime':
        x = t(1.4); env = np.minimum(1, x / 0.01) * np.exp(-x * 3.2)
        return 0.06 * env * (np.sin(2 * np.pi * 784 * x) + 0.4 * np.sin(2 * np.pi * 1175 * x) + 0.12 * np.sin(2 * np.pi * 1568 * x))
    raise ValueError(kind)


def write_wav(path, mono, np):
    st = np.clip(np.stack([mono, mono], 1), -1, 1); w = wave.open(path, 'wb')
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes()); w.close()


def main(adir):
    import numpy as np
    ad = json.load(open(os.path.join(adir, 'ad.json'))); aid = ad['id']
    out = os.path.join(adir, 'out'); os.makedirs(out, exist_ok=True)
    B = Budget(adir, float(ad.get('cap_usd', 0.5)))

    # 1. picture: the scene page, frame by frame
    rdir = os.path.join(out, 'render')
    sub = int((ad.get('render') or {}).get('sub', 1))   # subframes per frame, averaged: real motion blur
    r = subprocess.run(['node', os.path.join(ROOT, 'harness', 'dom-render.cjs'), ad['scene'], '--w', str(ad.get('w', 1920)), '--h', str(ad.get('h', 1080)), '--out', rdir,
                        '--sub', str(sub)], cwd=ROOT, capture_output=True, text=True, timeout=5400)
    print(r.stdout[-800:], r.stderr[-800:]); assert r.returncode == 0, 'render failed'
    pic = os.path.join(rdir, os.path.basename(ad['scene'].rstrip('/')) + '.mp4'); D = dur_of(pic); log('picture', pic, f'{D:.2f}s')

    # 2. voice: one file per line; a line that would run into the next is gently sped up (at most 12%)
    vo = []; A = ad.get('audio')
    if A:   # music-first ads: audio was made by prep.py and the scene was timed to it; reuse the files, no new fees
        for item in A.get('vo', []) + A.get('dialogue', []):
            wav = os.path.join(out, os.path.basename(item['file'])[:-4] + f"-{int(item['start'] * 1000)}.wav")
            run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(adir, item['file']), '-ar', str(SR), '-ac', '2', wav]); vo.append((item['start'], wav))
    for k, line in enumerate([] if A else ad.get('vo', [])):
        mp3 = speech(B, line['text'], ad.get('voice', 'sarah'), os.path.join(out, f'vo{k}.mp3'), f'vo {k}')
        wav = os.path.join(out, f'vo{k}.wav'); run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-ar', str(SR), '-ac', '2', wav])
        room = (ad['vo'][k + 1]['start'] if k + 1 < len(ad['vo']) else D) - line['start'] - 0.15; d = dur_of(wav)
        if d > room > 0:
            tempo = min(1.12, d / room); fast = wav[:-4] + '.fit.wav'
            run(['ffmpeg', '-v', 'error', '-y', '-i', wav, '-filter:a', f'atempo={tempo:.3f}', fast]); wav = fast
            log(f'vo {k}: {d:.2f}s in a {room:.2f}s gap, sped up x{tempo:.2f}')
        vo.append((line['start'], wav)); log(f'vo {k}: {dur_of(wav):.2f}s at {line["start"]}s')

    # 3. score (optional: the ad still works on voice and sound design alone)
    mus = None
    if A and A.get('music'):
        mus = os.path.join(out, 'music_cut.wav'); off = float(A.get('music_offset', 0))
        run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{off:.3f}', '-i', os.path.join(adir, A['music']), '-ar', str(SR), '-ac', '2', mus])
    elif ad.get('music'):
        try: mus = music(B, ad['music']['prompt'], os.path.join(out, 'music.wav'), 'music')
        except Exception as e: log('music failed:', e)
    log('music:', mus or 'none')

    # 4. interface sounds
    fx = np.zeros(int(SR * (D + 2)))
    for c in ad.get('sfx', []):
        s = synth(c['kind'], np); i0 = int(c['t'] * SR); fx[i0:i0 + len(s)] += s[:len(fx) - i0]
    fxw = os.path.join(out, 'sfx.wav'); write_wav(fxw, fx, np)

    # 5. mix: voice on top, the score ducked under it, sounds underneath, mastered to -14 LUFS for social platforms
    ins = ['-i', pic]; fl = []; n = 1
    for start, wav in vo:
        ins += ['-i', wav]; ms = int(start * 1000); fl.append(f'[{n}:a]adelay={ms}|{ms}[v{n}]'); n += 1
    vlabels = ''.join(f'[v{i}]' for i in range(1, n))
    if vo: fl.append(f'{vlabels}amix=inputs={len(vo)}:normalize=0:duration=longest,apad=whole_dur={D:.3f},atrim=0:{D:.3f},asplit=2[vo][vokey]')
    else: fl.append(f'anullsrc=r={SR}:cl=stereo,atrim=0:{D:.3f},asplit=2[vo][vokey]')
    ins += ['-i', fxw]; fx_i = n; n += 1
    fl.append(f'[{fx_i}:a]atrim=0:{D:.3f},volume=-3dB[fx]')
    if mus:
        ins += ['-i', mus]; m_i = n; n += 1
        g = float((A or {}).get('music_gain_db', (ad.get('music') or {}).get('gain_db', -15))); fo = float((A or {}).get('music_fade_s', 2.2))
        fl.append(f'[{m_i}:a]aformat=sample_rates={SR}:channel_layouts=stereo,atrim=0:{D:.3f},afade=t=in:d=0.05,afade=t=out:st={max(0, D - fo):.2f}:d={fo:.2f},volume={g}dB[m]')
        ratio = float((A or {}).get('duck_ratio', 3))
        fl.append(f'[m][vokey]sidechaincompress=threshold=0.05:ratio={ratio}:attack=40:release=500[md]')
        fl.append('[vo][md][fx]amix=inputs=3:normalize=0:duration=longest[mix]')
    else:
        fl.append('[vokey]anullsink'); fl.append('[vo][fx]amix=inputs=2:normalize=0:duration=longest[mix]')
    fl.append(f'[mix]loudnorm=I=-14:TP=-1.5:LRA=11,atrim=0:{D:.3f}[a]')
    final = os.path.join(out, f'{aid}.mp4')
    grain = int((ad.get('post') or {}).get('grain', 0))
    vcodec = ['-c:v', 'copy'] if not grain else ['-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p']
    if grain: fl.append(f'[0:v]noise=alls={grain}:allf=t[vid]')
    run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fl), '-map', '[vid]' if grain else '0:v', '-map', '[a]', *vcodec, '-c:a', 'aac', '-b:a', '256k',
         '-ar', str(SR), '-t', f'{D:.3f}', '-movflags', '+faststart', final])
    run(['ffmpeg', '-v', 'error', '-y', '-i', final, '-vf', 'fps=0.6,scale=480:-2,tile=4x4:padding=4:color=white', '-frames:v', '1', os.path.join(out, f'{aid}-sheet.jpg')])
    listen(B, final, ad, out)
    log('done', final, f'{dur_of(final):.2f}s', f'| spent ${B.led.total:.3f} of ${B.led.cap}')


LISTEN = {'type': 'object', 'additionalProperties': False, 'required': ['transcript', 'voice', 'music', 'sounds', 'mix', 'problems'],
          'properties': {'transcript': {'type': 'string'}, 'voice': {'type': 'string'}, 'music': {'type': 'string'}, 'sounds': {'type': 'string'},
                         'mix': {'type': 'string'}, 'problems': {'type': 'array', 'items': {'type': 'string'}}}}


def listen(B, final, ad, out):
    """An audio model listens to the finished mix and writes notes (a check before Sam hears it; cents)."""
    import base64
    from agents import ask
    mp3 = os.path.join(out, 'listen.mp3'); run(['ffmpeg', '-v', 'error', '-y', '-i', final, '-vn', '-ac', '1', '-b:a', '96k', mp3])
    script = ' | '.join(f"{l['start']}s: {l.get('text', '')}" for l in ((ad.get('audio') or {}).get('vo', []) + (ad.get('audio') or {}).get('dialogue', [])) or ad.get('vo', []))
    msg = [{'role': 'user', 'content': [
        {'type': 'text', 'text': 'You are a strict audio supervisor for premium TV and social ads. Listen to this finished ad mix. '
         'Transcribe the voiceover with timestamps. Judge: the voice (clear, natural, warm, any glitches or mispronunciations, rushed?), '
         'the music (audible under the voice? fits a premium tech brand? any artefacts?), the interface sound effects (pleasant or harsh?), '
         'and the mix balance. List concrete problems with timestamps; an empty list if none. The intended script is: ' + script},
        {'type': 'input_audio', 'input_audio': {'data': base64.b64encode(open(mp3, 'rb').read()).decode(), 'format': 'mp3'}}]}]
    try:
        notes, model = ask('ears', msg, LISTEN, B.led, name='listen', max_tokens=1800, label='listen to the mix')
        notes['model'] = model; json.dump(notes, open(os.path.join(out, f"{ad['id']}-listen.json"), 'w'), indent=1)
        log('listened:', model, '| problems:', notes['problems'])
    except Exception as e:
        log('listen check failed:', str(e)[:300])


if __name__ == '__main__':
    main(sys.argv[1].rstrip('/'))
