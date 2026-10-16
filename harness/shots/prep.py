"""prep.py — music-first audio prep for an ad: the score, its beat map, the voice (cast from candidates) and dialogue
word timings. Everything is written to ads/<id>/audio/ and committed, so the scene can be timed to the real audio
and every later render reuses the same files (no new AI fees).

    python3 harness/shots/prep.py ads/<id>        (needs OPENROUTER_API_KEY; librosa, faster-whisper for dialogue)

ads/<id>/ad.json, the "prep" block:
    {"music": {"prompt": "..."},                                   Lyria 3 clip (about 30 s), streamed
     "voice_cast": ["eric", "brian", "river"],                      candidates; an audio model scores each reel, best wins
     "vo": [{"text": "..."}],                                       narration lines (ElevenLabs v3 tags like [warmly] allowed)
     "dialogue": [{"who": "ai", "voice": "matilda", "text": "..."}]}  fixed voices; word timestamps with Whisper
Writes: audio/music.mp3 + audio/music.json (bpm, beats, downbeat guess, 0.1 s energy curve, biggest energy jump),
        audio/vo/line<k>.mp3 + audio/vo.json (voice, durations), audio/casting.json,
        audio/dialogue/line<k>.mp3 + audio/dialogue.json (durations, words with start and end).
"""
import os, sys, json, re, base64, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from factory import speech, music, Budget, run, log
from agents import ask

def dur_of(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout.strip() or 0)

def plain(t): return re.sub(r'\[[^\]]*\]\s*', '', t).strip()   # the words without v3 delivery tags

def beat_map(path):
    import librosa, numpy as np
    y, sr = librosa.load(path, sr=22050, mono=True)
    tempo, frames = librosa.beat.beat_track(y=y, sr=sr, units='frames')
    beats = librosa.frames_to_time(frames, sr=sr).round(3).tolist()
    hop = int(sr * 0.1); rms = librosa.feature.rms(y=y, frame_length=hop * 2, hop_length=hop)[0]
    rms = (rms / (rms.max() + 1e-9)).round(3).tolist()
    # downbeat guess: the beat phase (0..3) whose beats carry the most low-end energy
    onset = librosa.onset.onset_strength(y=y, sr=sr)
    phase = int(np.argmax([sum(onset[f] for f in frames[p::4] if f < len(onset)) for p in range(4)])) if len(frames) >= 8 else 0
    smooth = np.convolve(rms, np.ones(5) / 5, mode='same'); jump = np.diff(smooth)
    drop = round(float((int(np.argmax(jump)) + 1) * 0.1), 2)
    return {'bpm': round(float(np.atleast_1d(tempo)[0]), 2), 'beats': beats, 'downbeats': beats[phase::4], 'energy_hop_s': 0.1,
            'energy': rms, 'biggest_rise_s': drop, 'duration': round(len(y) / sr, 3)}

CAST = {'type': 'object', 'additionalProperties': False, 'required': ['scores', 'best', 'why'],
        'properties': {'scores': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False, 'required': ['voice', 'score', 'note'],
                       'properties': {'voice': {'type': 'string'}, 'score': {'type': 'number'}, 'note': {'type': 'string'}}}},
                       'best': {'type': 'string'}, 'why': {'type': 'string'}}}

def main(adir):
    ad = json.load(open(os.path.join(adir, 'ad.json'))); P = ad['prep']
    out = os.path.join(adir, 'audio'); os.makedirs(out, exist_ok=True)
    B = Budget(adir, float(ad.get('cap_usd', 0.6)))

    # 1. the score and its beat map
    if P.get('music') and not os.path.exists(os.path.join(out, 'music.mp3')):
        got = music(B, P['music']['prompt'], os.path.join(out, 'music_raw.wav'), 'music')
        if got:
            run(['ffmpeg', '-v', 'error', '-y', '-i', got, '-ar', '48000', '-ac', '2', '-b:a', '256k', os.path.join(out, 'music.mp3')])
            if got != os.path.join(out, 'music.mp3'): os.remove(got)
    if os.path.exists(os.path.join(out, 'music.mp3')):
        bm = beat_map(os.path.join(out, 'music.mp3')); json.dump(bm, open(os.path.join(out, 'music.json'), 'w'))
        log('music:', bm['bpm'], 'bpm,', len(bm['beats']), 'beats,', bm['duration'], 's, biggest rise at', bm['biggest_rise_s'], 's')

    # 2. narration: every candidate voice reads every line; an audio model scores the reels; the best voice is kept
    if P.get('vo') and not os.path.exists(os.path.join(out, 'vo.json')):
        reels = {}
        for v in P.get('voice_cast', ['eric']):
            files = []
            for k, line in enumerate(P['vo']):
                d = os.path.join(out, 'cast', v); os.makedirs(d, exist_ok=True)
                files.append(speech(B, line['text'], v, os.path.join(d, f'line{k}.mp3'), f'vo {v} {k}'))
            reel = os.path.join(out, 'cast', f'{v}-reel.mp3')
            lst = os.path.join(out, 'cast', f'{v}.txt'); open(lst, 'w').write(''.join(f"file '{os.path.abspath(f)}'\n" for f in files))
            run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-ac', '1', '-b:a', '96k', reel]); reels[v] = (files, reel)
        best = list(reels)[0]; cast = None
        if len(reels) > 1:
            content = [{'type': 'text', 'text': 'You are a casting director for premium TV and social ads. Score each narrator reel 0 to 10 for: natural, '
                        'human delivery (no robotic cadence), warmth and confidence, clarity, and fit for this brief: ' + P.get('voice_brief', 'a premium tech brand ad') +
                        '. The reels are in this order: ' + ', '.join(reels) + '. Return the best voice name exactly as given.'}]
            for v, (files, reel) in reels.items():
                content += [{'type': 'text', 'text': f'Reel: {v}'}, {'type': 'input_audio', 'input_audio': {'data': base64.b64encode(open(reel, 'rb').read()).decode(), 'format': 'mp3'}}]
            try:
                cast, model = ask('ears', [{'role': 'user', 'content': content}], CAST, B.led, name='cast', max_tokens=1200, label='voice casting')
                if cast.get('best') in reels: best = cast['best']
                cast['model'] = model
            except Exception as e: log('casting check failed, keeping', best, str(e)[:200])
        lines = []
        for k, (line, f) in enumerate(zip(P['vo'], reels[best][0])):
            dst = os.path.join(out, 'vo', f'line{k}.mp3'); os.makedirs(os.path.dirname(dst), exist_ok=True); os.replace(f, dst)
            lines.append({'text': plain(line['text']), 'file': f'audio/vo/line{k}.mp3', 'dur': round(dur_of(dst), 3)})
        json.dump({'voice': best, 'lines': lines}, open(os.path.join(out, 'vo.json'), 'w'), indent=1)
        json.dump(cast or {'best': best}, open(os.path.join(out, 'casting.json'), 'w'), indent=1)
        log('voice:', best, [l['dur'] for l in lines])

    # 3. dialogue: fixed voices, then word timestamps for kinetic captions
    if P.get('dialogue') and not os.path.exists(os.path.join(out, 'dialogue.json')):
        from faster_whisper import WhisperModel
        wm = WhisperModel('base.en', device='cpu', compute_type='int8'); lines = []
        for k, line in enumerate(P['dialogue']):
            dst = os.path.join(out, 'dialogue', f'line{k}.mp3'); os.makedirs(os.path.dirname(dst), exist_ok=True)
            speech(B, line['text'], line['voice'], dst, f'dialogue {k}')
            import librosa   # decode ourselves: newer PyAV breaks faster-whisper's own decoder
            pcm, _sr = librosa.load(dst, sr=16000, mono=True)
            segs, _ = wm.transcribe(pcm, word_timestamps=True, language='en')
            words = [{'w': w.word.strip(), 'start': round(w.start, 3), 'end': round(w.end, 3)} for s in segs for w in (s.words or [])]
            lines.append({'who': line['who'], 'voice': line['voice'], 'text': plain(line['text']), 'file': f'audio/dialogue/line{k}.mp3',
                          'dur': round(dur_of(dst), 3), 'words': words})
            log('dialogue', k, line['who'], lines[-1]['dur'], 's,', len(words), 'words')
        json.dump({'lines': lines}, open(os.path.join(out, 'dialogue.json'), 'w'), indent=1)
    log('prep done | spent', f'${B.led.total:.3f}')

if __name__ == '__main__':
    main(sys.argv[1].rstrip('/'))
