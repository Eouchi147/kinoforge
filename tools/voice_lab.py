"""voice_lab.py: audition free, openly licensed voices for a storyteller read (no API, no key, no money).

Run by .github/workflows/voice-lab.yml, one mode per step (each engine has its own Python environment):

    plan      <folder> <engines> <work>      write <work>/plan.json from <folder>/ad.json (prep.vo lines prep.audition.lines)
    kokoro-ref <work>                        make the synthetic reference clips with Kokoro (Apache 2.0), kokoro venv
    render    <engine> <work>                render the raw lines of the takes of one engine into <work>/raw/<take>/
    finish    <folder> <work>                trim, slow, comma pauses, level, Whisper check, pitch analysis, report.json,
                                             voicelab.m4a and voicelab.txt in <folder>/voicelab/

Engines: chatterbox (Resemble AI, MIT; built-in voice, or a synthetic Kokoro reference), parler (Parler-TTS large v1,
Apache 2.0), parler-mini (Parler-TTS mini v1, Apache 2.0). Never a recording of a real person as a reference.
Skipped on purpose: Index-TTS2 (Bilibili custom licence, not a plain commercial grant), Higgs Audio v2 (community licence
with user limits, GPU sized), StyleTTS2 (weights carry a disclosure condition and need espeak), Orpheus (3B Llama, about 8x
slower than real time on 4 CPU cores and a long build).
"""
import os, sys, json, re, time, subprocess, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESC_A = ('A young woman with a warm, bright, smiling voice reads a story to young children slowly and expressively, with gentle '
          'excitement. Very clear, close-sounding, studio quality audio.')
DESC_B = ('Lea speaks slowly in a warm, cheerful, smiling storyteller voice, with lively intonation and gentle pauses, like a '
          'favourite teacher reading a picture book at story time. Very clear audio, very close recording, no background noise.')
DESC_C = ('Jenna delivers a sweet, bright, friendly read in a high, happy voice, slowly and clearly, with a lot of expression and a '
          'smile in every sentence, for children aged six to eight. Very close recording, studio quality, no background noise.')
REF_TEXT = ('Hello, little explorers! Today we are going on a wonderful adventure together, and I am so happy that you are here. '
            'Are you ready? Let us find out!')
LIC = {'chatterbox': 'MIT (Resemble AI, ResembleAI/chatterbox; output carries an inaudible Perth watermark)',
       'parler': 'Apache 2.0 (parler-tts/parler-tts-large-v1; text encoder flan-t5 Apache 2.0)',
       'parler-mini': 'Apache 2.0 (parler-tts/parler-tts-mini-v1; text encoder flan-t5 Apache 2.0)',
       'kokoro': 'Apache 2.0 (hexgrad/Kokoro-82M), used only to make the synthetic reference clip'}
REPO = {'chatterbox': 'ResembleAI/chatterbox', 'parler': 'parler-tts/parler-tts-large-v1', 'parler-mini': 'parler-tts/parler-tts-mini-v1',
        'kokoro': 'hexgrad/Kokoro-82M'}
SR = 24000
GAP_LINE, GAP_TAKE, COMMA_PAUSE = 0.7, 1.6, 0.30
RATE_LO, RATE_HI, RATE_AIM = 2.3, 3.0, 2.7


def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)
def plain(t): return re.sub(r'\[[^\]]*\]\s*', '', t).strip()
def clean(s): return re.sub(r'\s*(\.\.\.|…|[–—])\s*', ', ', s or '').replace(' - ', ', ')   # house style in anything we write


def all_takes(engines):
    T = []
    if 'chatterbox' in engines:
        T += [dict(id='cb-default-e50-c50', engine='chatterbox', label='Chatterbox built-in voice, calm', settings=dict(exaggeration=0.5, cfg_weight=0.5, temperature=0.8)),
              dict(id='cb-default-e80-c30', engine='chatterbox', label='Chatterbox built-in voice, expressive and slower', settings=dict(exaggeration=0.8, cfg_weight=0.3, temperature=0.8)),
              dict(id='cb-heart-e60-c40', engine='chatterbox', label='Chatterbox, synthetic Kokoro af_heart reference', ref='af_heart', settings=dict(exaggeration=0.6, cfg_weight=0.4, temperature=0.8)),
              dict(id='cb-heart-e80-c30', engine='chatterbox', label='Chatterbox, synthetic Kokoro af_heart reference, more expression', ref='af_heart', settings=dict(exaggeration=0.8, cfg_weight=0.3, temperature=0.8)),
              dict(id='cb-lily-e70-c30', engine='chatterbox', label='Chatterbox, synthetic Kokoro bf_lily reference', ref='bf_lily', settings=dict(exaggeration=0.7, cfg_weight=0.3, temperature=0.8))]
    if 'parler' in engines:
        T += [dict(id='parler-L-a', engine='parler', label='Parler-TTS large, young woman storyteller', settings=dict(description=DESC_A)),
              dict(id='parler-L-b', engine='parler', label='Parler-TTS large, Lea, favourite teacher', settings=dict(description=DESC_B)),
              dict(id='parler-L-c', engine='parler', label='Parler-TTS large, Jenna, bright and sweet', settings=dict(description=DESC_C))]
    if 'parler-mini' in engines:
        T += [dict(id='parler-M-a', engine='parler-mini', label='Parler-TTS mini, young woman storyteller', settings=dict(description=DESC_A)),
              dict(id='parler-M-b', engine='parler-mini', label='Parler-TTS mini, Lea, favourite teacher', settings=dict(description=DESC_B))]
    return T


# ------------------------------------------------------------------ plan
def cmd_plan(folder, engines, work):
    ad = json.load(open(os.path.join(folder, 'ad.json'))); P = ad['prep']; keep = P.get('audition', {}).get('lines', [0, 1, 4])
    lines = [{'k': k, 'text': plain(P['vo'][k]['text'])} for k in keep]
    engines = [e.strip() for e in engines.split(',') if e.strip()]
    takes = all_takes(engines)
    for t in takes: t['licence'] = LIC[t['engine']] + ('; ' + LIC['kokoro'] if t.get('ref') else ''); t['model'] = REPO[t['engine']]
    os.makedirs(work, exist_ok=True)
    json.dump({'folder': folder, 'engines': engines, 'lines': lines, 'takes': takes, 'ref_text': REF_TEXT}, open(os.path.join(work, 'plan.json'), 'w'), indent=1)
    print('takes:', ', '.join(t['id'] for t in takes)); print('refs:', ','.join(sorted({t['ref'] for t in takes if t.get('ref')})))


def load_plan(work): return json.load(open(os.path.join(work, 'plan.json')))


def hf_licence(repo):
    try:
        from huggingface_hub import HfApi
        return str(HfApi().model_info(repo).card_data.license)
    except Exception as e: return f'not read ({type(e).__name__})'


# ------------------------------------------------------------------ renderers (each runs in its own venv)
def cmd_kokoro_ref(work):
    sys.path.insert(0, os.path.join(ROOT, 'harness', 'audio')); import tts
    plan = load_plan(work); os.makedirs(os.path.join(work, 'ref'), exist_ok=True)
    for v in sorted({t['ref'] for t in plan['takes'] if t.get('ref')}):
        out = os.path.join(work, 'ref', v + '.wav')
        _, dur = tts.say(plan['ref_text'], voice=v, speed=0.95, lang='en-gb' if v[0] == 'b' else 'en-us', out=out)
        log(f'reference {v}: {dur:.1f} s (Kokoro, synthetic)')


def raw_path(work, take, k): return os.path.join(work, 'raw', take['id'], f'line{k}.wav')


def cmd_render(engine, work):
    plan = load_plan(work); takes = [t for t in plan['takes'] if t['engine'] == engine]
    if not takes: log(f'{engine}: no takes in the plan'); return
    meta = {'engine': engine, 'repo': REPO[engine], 'licence_on_hub': hf_licence(REPO[engine]), 'takes': {}}
    log(f'{engine}: model licence on the hub: {meta["licence_on_hub"]}')
    t_load = time.time()
    if engine == 'chatterbox':
        import torch, torchaudio as ta
        from chatterbox.tts import ChatterboxTTS
        torch.set_num_threads(os.cpu_count() or 4); m = ChatterboxTTS.from_pretrained(device='cpu')
        def say(take, text, out, seed):
            torch.manual_seed(seed); s = take['settings']; kw = dict(s)
            if take.get('ref'): kw['audio_prompt_path'] = os.path.join(work, 'ref', take['ref'] + '.wav')
            ta.save(out, m.generate(text, **kw), m.sr)
    else:
        import torch, soundfile as sf
        from parler_tts import ParlerTTSForConditionalGeneration
        from transformers import AutoTokenizer, set_seed
        torch.set_num_threads(os.cpu_count() or 4)
        m = ParlerTTSForConditionalGeneration.from_pretrained(REPO[engine]).to('cpu'); tok = AutoTokenizer.from_pretrained(REPO[engine])
        def say(take, text, out, seed):
            set_seed(seed); d = tok(take['settings']['description'], return_tensors='pt'); p = tok(text, return_tensors='pt')
            with torch.no_grad():
                g = m.generate(input_ids=d.input_ids, attention_mask=d.attention_mask, prompt_input_ids=p.input_ids, prompt_attention_mask=p.attention_mask)
            sf.write(out, g.cpu().numpy().squeeze().astype('float32'), m.config.sampling_rate)
    log(f'{engine}: model loaded in {time.time() - t_load:.0f} s')
    for take in takes:
        os.makedirs(os.path.dirname(raw_path(work, take, 0)), exist_ok=True); secs = {}
        for ln in plan['lines']:
            out = raw_path(work, take, ln['k'])
            if os.path.exists(out): continue
            t0 = time.time()
            try: say(take, ln['text'], out, seed=11 + ln['k'])
            except Exception as e: log(f'{take["id"]} line {ln["k"]} FAILED: {type(e).__name__}: {e}'); continue
            secs[ln['k']] = round(time.time() - t0, 1); log(f'{take["id"]} line {ln["k"]}: {secs[ln["k"]]} s')
        meta['takes'][take['id']] = {'render_secs': secs}
        json.dump(meta, open(os.path.join(work, f'meta-{engine}.json'), 'w'), indent=1)


# ------------------------------------------------------------------ finish (main Python: ffmpeg, Whisper, librosa)
def finish(folder, work):
    import numpy as np, soundfile as sf, librosa
    sys.path.insert(0, os.path.join(ROOT, 'films', 'director')); import voice_free as vf
    from faster_whisper import WhisperModel
    asr = WhisperModel('base.en', device='cpu', compute_type='int8')
    plan = load_plan(work); out_root = os.path.join(folder, 'voicelab'); shutil.rmtree(out_root, ignore_errors=True); os.makedirs(out_root)
    metas = {}
    for f in os.listdir(work):
        if f.startswith('meta-') and f.endswith('.json'): metas[f[5:-5]] = json.load(open(os.path.join(work, f)))

    def hear(wav):
        segs, _ = asr.transcribe(vf.pcm16k(wav), word_timestamps=True, language='en', beam_size=3); segs = list(segs)
        return ' '.join(s.text for s in segs).strip(), [[w.word.strip(), w.start, w.end] for s in segs for w in (s.words or [])]

    def level(x):
        env = np.abs(x); act = x[env > 0.02 * env.max()] if env.max() > 0 else x
        g = 10 ** (-21 / 20) / (np.sqrt(np.mean(act ** 2)) + 1e-9); y = x * g
        pk = np.abs(y).max()
        return y if pk < 0.95 else y * (0.95 / pk)

    def comma_pauses(x, text, words):
        """Add a short pause after each word that ends in a comma in the script (aligned with Whisper by position)."""
        tw = text.split(); hw = [re.sub(r"[^a-z0-9']", '', w[0].lower()) for w in words]
        if [re.sub(r"[^a-z0-9']", '', w.lower()) for w in tw] != hw: return x, 'skipped (words did not align)'
        cuts = []
        for i, w in enumerate(tw[:-1]):
            if not w.endswith(','): continue
            gap = words[i + 1][1] - words[i][2]
            if gap >= COMMA_PAUSE: continue
            c = int(words[i][2] * SR); a, b = max(c - int(0.06 * SR), 0), min(c + int(0.06 * SR), len(x))
            fr = np.array([np.sqrt(np.mean(x[j:j + 120] ** 2)) for j in range(a, max(b - 120, a + 1), 60)])
            cut = a + int(np.argmin(fr)) * 60 if len(fr) else c
            cuts.append((cut, COMMA_PAUSE - max(gap, 0)))
        for cut, d in sorted(cuts, reverse=True):
            x = np.concatenate([x[:cut], np.zeros(int(d * SR), dtype=x.dtype), x[cut:]])
        return x, f'{len(cuts)} added, {COMMA_PAUSE} s each'

    report = {'_': 'Voice lab by analysis (no listening). words_per_s while speaking (target 2.3 to 3.0), pitch range in semitones (10th to 90th percentile), '
              'movement in semitones per second (flat, robotic reads are low), pause share, word error rate of Whisper base.en. pitch_median_hz under about 165 may be a '
              'lower or male-sounding voice. Lines are trimmed, slowed with a pitch-preserving stretch when faster than 3.0 words/s (stretch is in the settings), given a '
              '0.3 s pause after commas where the script has one, and levelled to the same loudness.', 'takes': {}, 'failed': []}
    listen = []; order = []
    for take in plan['takes']:
        tid = take['id']; td = os.path.join(out_root, tid); os.makedirs(td); rows = []; stretch = []; cp = []; ok = True
        for ln in plan['lines']:
            raw = raw_path(work, take, ln['k'])
            if not os.path.exists(raw): ok = False; break
            tmp = os.path.join(work, f'tmp-{tid}-{ln["k"]}.wav'); text = ln['text']
            vf.ff('-i', raw, '-af', vf.TRIM, '-ar', str(SR), '-ac', '1', tmp)
            x, _ = sf.read(tmp, dtype='float32'); nw = len(text.split()); wps0 = nw / max(len(x) / SR, 0.1); f = 1.0
            if wps0 > RATE_HI:
                f = max(RATE_AIM / wps0, 0.8)   # atempo below 1 slows without changing pitch; 0.8 is the limit before it sounds processed
                vf.ff('-i', tmp, '-af', f'atempo={f:.4f}', '-ar', str(SR), '-ac', '1', tmp + '.s.wav'); os.replace(tmp + '.s.wav', tmp); x, _ = sf.read(tmp, dtype='float32')
            _, words = hear(tmp); x, note = comma_pauses(x, text, words)
            x = level(x); fin = os.path.join(td, f'line{ln["k"]}.wav'); sf.write(fin, x, SR, subtype='PCM_16'); os.remove(tmp)
            heard, words = hear(fin); e = vf.wer(text, heard)
            y, sr = librosa.load(fin, sr=22050, mono=True)
            f0, vfl, _ = librosa.pyin(y, fmin=60, fmax=450, sr=sr, frame_length=1024); f0 = f0[vfl & ~np.isnan(f0)]
            st = 12 * np.log2(f0 / np.median(f0)) if len(f0) else np.zeros(1); hop = 512 / sr
            mv = float(np.abs(np.diff(st)).mean() / hop) if len(st) > 2 else 0.0
            rms = librosa.feature.rms(y=y)[0]; pause = float((rms < 0.1 * rms.max()).mean())
            speak = (words[-1][2] - words[0][1]) if words else len(x) / SR
            rows.append({'line': ln['k'], 'dur': round(len(x) / SR, 3), 'words_per_s': round(nw / max(speak, 0.1), 2),
                         'pitch_median_hz': round(float(np.median(f0)), 1) if len(f0) else 0,
                         'pitch_range_st': round(float(np.percentile(st, 90) - np.percentile(st, 10)), 2), 'pitch_move_st_per_s': round(mv, 2),
                         'pause_share': round(pause, 3), 'wer': round(e, 3), 'heard': clean(heard)})
            stretch.append(round(f, 3)); cp.append(note); log(f'{tid} line {ln["k"]}: {rows[-1]["words_per_s"]} w/s, range {rows[-1]["pitch_range_st"]} st, wer {e:.2f}, stretch {f:.2f}')
        if not ok or not rows: report['failed'].append(tid); shutil.rmtree(td, ignore_errors=True); continue
        mean = {k: round(float(np.mean([r[k] for r in rows])), 3) for k in ('words_per_s', 'pitch_median_hz', 'pitch_range_st', 'pitch_move_st_per_s', 'pause_share', 'wer')}
        m = metas.get(take['engine'], {})
        report['takes'][tid] = {'label': take['label'], 'engine': take['engine'], 'model': take['model'], 'licence': take['licence'],
                                'licence_on_hub': m.get('licence_on_hub'), 'settings': {**take['settings'], **({'reference': take['ref'] + ' (Kokoro, synthetic)'} if take.get('ref') else {}),
                                'stretch_per_line': stretch, 'comma_pauses': cp},
                                'render_secs': m.get('takes', {}).get(tid, {}).get('render_secs'), 'lines': rows, 'mean': mean}
        order.append(tid)
    # numbers-only ranking: rate inside 2.3 to 3.0, words recognised, wide and lively pitch, female-range median
    def score(m):
        r = m['words_per_s']; s = 0 if RATE_LO <= r <= RATE_HI else -abs(r - (RATE_LO if r < RATE_LO else RATE_HI)) * 3
        return round(s - 6 * m['wer'] + m['pitch_range_st'] * 0.5 + m['pitch_move_st_per_s'] * 0.05 + (0 if m['pitch_median_hz'] >= 165 else -2), 2)
    for tid in order: report['takes'][tid]['numbers_score'] = score(report['takes'][tid]['mean'])
    report['listening_order'] = order; report['by_numbers'] = sorted(order, key=lambda t: -report['takes'][t]['numbers_score'])
    # the listening file: each take's lines, 0.7 s between lines, 1.6 s between takes; AAC 160k with chapters
    t = 0.0; chunks = []; txt = ['voicelab.m4a: listening order (a chapter per take). Take, start, engine, settings, licence, mean w/s, pitch range, word error', '']
    chap = []
    for n, tid in enumerate(order, 1):
        start = t
        for i, ln in enumerate(plan['lines']):
            x, _ = sf.read(os.path.join(out_root, tid, f'line{ln["k"]}.wav'), dtype='float32'); chunks.append(x); t += len(x) / SR
            g = GAP_LINE if i < len(plan['lines']) - 1 else GAP_TAKE; chunks.append(np.zeros(int(g * SR), dtype='float32')); t += g
        R = report['takes'][tid]; mm = R['mean']
        chap.append((start, t - GAP_TAKE, f'{n}. {tid}'))
        txt.append(f'{n:2d}. {int(start // 60)}:{start % 60:04.1f}  {tid}  ({R["label"]})')
        txt.append(f'      {R["engine"]}; {json.dumps({k: v for k, v in R["settings"].items() if k not in ("stretch_per_line", "comma_pauses")})}')
        txt.append(f'      licence {R["licence"]}; hub says {R["licence_on_hub"]}')
        txt.append(f'      {mm["words_per_s"]} w/s, median {mm["pitch_median_hz"]} Hz, range {mm["pitch_range_st"]} st, movement {mm["pitch_move_st_per_s"]}, word error {mm["wer"]}')
    if chunks:
        wav = os.path.join(work, 'all.wav'); sf.write(wav, np.concatenate(chunks), SR, subtype='PCM_16')
        meta = [';FFMETADATA1', 'title=Voice lab: ' + os.path.basename(folder.rstrip('/'))]
        for a, b, name in chap: meta += ['[CHAPTER]', 'TIMEBASE=1/1000', f'START={int(a * 1000)}', f'END={int(b * 1000)}', f'title={name}']
        mf = os.path.join(work, 'chapters.txt'); open(mf, 'w').write('\n'.join(meta) + '\n')
        vf.ff('-i', wav, '-i', mf, '-map_metadata', '1', '-map_chapters', '1', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', os.path.join(out_root, 'voicelab.m4a'))
    if report['failed']: txt += ['', 'No audio (engine failed or too slow): ' + ', '.join(report['failed'])]
    txt += ['', 'By the numbers only (nobody has listened yet): ' + ', '.join(report['by_numbers'])]
    open(os.path.join(out_root, 'voicelab.txt'), 'w').write(clean('\n'.join(txt)).replace(' ', ' ') + '\n')
    json.dump(report, open(os.path.join(out_root, 'report.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({t: {**report['takes'][t]['mean'], 'score': report['takes'][t]['numbers_score']} for t in order}, indent=1)); print('failed:', report['failed'])


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'plan': cmd_plan(a[1].rstrip('/'), a[2], a[3])
    elif a[0] == 'kokoro-ref': cmd_kokoro_ref(a[1])
    elif a[0] == 'render': cmd_render(a[1], a[2])
    elif a[0] == 'finish': finish(a[1].rstrip('/'), a[2])
    else: raise SystemExit(__doc__)
