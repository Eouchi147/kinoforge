"""battle_mix.py: lay a Battle Map film's narration on the score's beat grid, then mix it.

    python3 films/lib/battle_mix.py films/battles/<id> [--title-line 1]

Reads audio/vo.json (lines, durations, word timings from prep), audio/music.mp3 + audio/music.json (beats, biggest rise).
Writes cues.json (every line with start, end and word times on the film timeline, beats, strong hits), film.json
(duration and render sizes) and audio/mix.m4a (narration over the ducked score, -14 LUFS).
Placement: each line starts on the first beat at least GAP after the previous line ends; the title line (index 1,
"This is the Battle of X.") lands on the score's biggest rise when it is reachable, with a held pause after it for the
title card; the film ends with a 4 s outro for the end card while the score resolves.
"""
import json, os, sys, subprocess
import numpy as np

d = sys.argv[1].rstrip('/'); TITLE = int(sys.argv[sys.argv.index('--title-line') + 1]) if '--title-line' in sys.argv else 1
vo = json.load(open(f'{d}/audio/vo.json')); mu = json.load(open(f'{d}/audio/music.json')); ad = json.load(open(f'{d}/ad.json'))
beats = np.array(mu['beats']); rise = float(mu['biggest_rise_s'])
GAP, LEAD, OUTRO, TITLE_HOLD = 0.32, 1.2, 4.2, 2.6

def next_beat(t):
    b = beats[beats >= t]
    return float(b[0]) if len(b) else t

t = LEAD; lines = []
for k, l in enumerate(vo['lines']):
    if k == 0: start = next_beat(LEAD)
    elif k == TITLE and lines[-1]['end'] + 0.3 <= rise <= lines[-1]['end'] + 4.5: start = rise
    else:
        gap = GAP + (TITLE_HOLD if k == TITLE + 1 else 0)
        start = next_beat(lines[-1]['end'] + gap)
    words = [[w, round(start + a, 3), round(start + b, 3)] for w, a, b in l.get('words', [])]
    lines.append({'id': f'l{k:02d}', 'text': l['text'], 'file': l['file'], 'start': round(start, 3), 'end': round(start + l['dur'], 3), 'words': words})
dur = round(lines[-1]['end'] + OUTRO, 3)

# strong musical hits within the film (onset strength peaks of the score)
import librosa
y, sr = librosa.load(f'{d}/audio/music.mp3', sr=22050, mono=True, duration=dur)
env = librosa.onset.onset_strength(y=y, sr=sr); fr = librosa.onset.onset_detect(onset_envelope=env, sr=sr)
hits = [round(float(librosa.frames_to_time(f, sr=sr)), 3) for f in fr if env[f] > np.percentile(env, 96)]
hop = int(sr * 0.1); rms = librosa.feature.rms(y=y, frame_length=hop * 2, hop_length=hop)[0]
fid = ad['id']; title = ad['_'].split(': ', 1)[1].split(' (')[0] if ': ' in ad['_'] else fid
cues = {'id': fid, 'title': title, 'duration': dur, 'outro_s': OUTRO, 'title_line': lines[TITLE]['id'], 'bpm': mu['bpm'],
        'beats': [b for b in mu['beats'] if b < dur], 'downbeats': [b for b in mu['downbeats'] if b < dur], 'strong_hits': hits,
        'energy_hop_s': 0.1, 'energy': [round(float(v), 3) for v in rms / (rms.max() + 1e-9)], 'lines': lines,
        'audio': 'audio/mix.m4a', 'note': 'Narration on the beat grid of the score. Picture follows these times.'}
json.dump(cues, open(f'{d}/cues.json', 'w'), indent=1)
film = {'id': fid, 'series': 'Battle Map', 'title': title, 'style': 'terrain', 'duration': dur, 'fps': 24, 'render_w': 1280, 'render_h': 720,
        'w': 1920, 'h': 1080, 'audio': 'audio/mix.m4a', 'note': 'Picture in the KINOFORGE Terrain style; sound from films/lib/battle_mix.py.'}
if os.path.exists(f'{d}/film.json'): film = {**json.load(open(f'{d}/film.json')), 'duration': dur}
json.dump(film, open(f'{d}/film.json', 'w'), indent=1)

# the mix: narration (delayed to its start) over the score, ducked under the voice, faded out on the end card
ins, fl = ['-i', f'{d}/audio/music.mp3'], []
for k, l in enumerate(lines):
    ins += ['-i', f"{d}/{l['file']}"]; ms = int(l['start'] * 1000)
    fl.append(f'[{k + 1}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms},volume=1.0[v{k}]')
fl.append(''.join(f'[v{k}]' for k in range(len(lines))) + f'amix=inputs={len(lines)}:normalize=0,apad=whole_dur={dur}[vo]')
fl.append('[vo]asplit=2[voA][voS]')
fl.append(f'[0:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{dur},volume=-7dB,afade=t=in:d=0.4,afade=t=out:st={dur - 2.6}:d=2.6[mu]')
fl.append('[mu][voS]sidechaincompress=threshold=0.04:ratio=3.5:attack=25:release=420:makeup=1[duck]')
fl.append('[duck][voA]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]')
subprocess.run(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error'] + ins + ['-filter_complex', ';'.join(fl), '-map', '[out]', '-t', str(dur),
                '-c:a', 'aac', '-b:a', '256k', f'{d}/audio/mix.m4a'], check=True)
print(fid, 'duration', dur, 's;', len(lines), 'lines; title line at', lines[TITLE]['start'], 's; rise', rise, '; hits', len(hits))
