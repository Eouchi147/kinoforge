"""battle_mix.py: lay a Battle Map film's narration on the score's beat grid, then mix it.

    python3 films/lib/battle_mix.py films/battles/<id> [--title-line 1]

Reads audio/vo.json (lines, durations, word timings from prep), audio/music.mp3 + audio/music.json (beats, biggest rise).
Writes cues.json (every line with start, end and word times on the film timeline, beats, strong hits), film.json
(duration and render sizes) and audio/mix.m4a (narration over the ducked score, -14 LUFS by a two-pass linear loudnorm).
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
MUSIC = f'{d}/audio/music.mp3'
need = sum(l['dur'] for l in vo['lines']) + len(vo['lines']) * (GAP + 0.35) + LEAD + OUTRO + TITLE_HOLD + 4
if mu['duration'] < need:
    # the score is too short: repeat whole bars from the middle (cut on downbeats, 40 ms cross-fades), shift the beat grid
    db = np.array(mu['downbeats']); bar = float(np.median(np.diff(db))); n = int(np.ceil((need - mu['duration']) / bar))
    i = int(np.argmin(np.abs(db - mu['duration'] * 0.4))); a, b = float(db[i]), float(db[min(i + n, len(db) - 1)])
    ext = f'{d}/audio/music_ext.wav'
    subprocess.run(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-i', MUSIC, '-filter_complex',
        f'[0:a]asplit=3[x][y][z];[x]atrim=0:{b},asetpts=N/SR/TB[p1];[y]atrim={a}:{b},asetpts=N/SR/TB[p2];[z]atrim={b},asetpts=N/SR/TB[p3];'
        '[p1][p2]acrossfade=d=0.04:c1=tri:c2=tri[q];[q][p3]acrossfade=d=0.04:c1=tri:c2=tri[o]', '-map', '[o]', ext], check=True)
    L = b - a; beats = np.concatenate([beats[beats < b], beats[(beats >= a) & (beats < b)] + L, beats[beats >= b] + L])
    mu['downbeats'] = list(np.concatenate([db[db < b], db[(db >= a) & (db < b)] + L, db[db >= b] + L]).round(3))
    mu['beats'] = list(beats.round(3)); mu['duration'] += L; MUSIC = ext
    if rise >= b: rise += L
    print(f'score extended by {L:.1f} s (bars {a:.2f} to {b:.2f} repeated)')

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
y, sr = librosa.load(MUSIC, sr=22050, mono=True, duration=dur)
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
ins, fl = ['-i', MUSIC], []
for k, l in enumerate(lines):
    ins += ['-i', f"{d}/{l['file']}"]; ms = int(l['start'] * 1000)
    fl.append(f'[{k + 1}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms},volume=1.0[v{k}]')
fl.append(''.join(f'[v{k}]' for k in range(len(lines))) + f'amix=inputs={len(lines)}:normalize=0,apad=whole_dur={dur}[vo]')
fl.append('[vo]asplit=2[voA][voS]')
fl.append(f'[0:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{dur},volume=-7dB,afade=t=in:d=0.4,afade=t=out:st={dur - 2.6}:d=2.6[mu]')
fl.append('[mu][voS]sidechaincompress=threshold=0.04:ratio=3.5:attack=25:release=420:makeup=1[duck]')
fl.append('[duck][voA]amix=inputs=2:normalize=0[out]')
# two-pass linear loudnorm (P8): pass 1 renders the mix before loudnorm and measures it, pass 2 applies the measured values with
# linear=true, so the whole mix gets one constant gain (no dynamic gain riding) and lands on -14 LUFS with true peak under -1.5 dBTP
LN = 'I=-14:TP=-1.5:LRA=11'
pre = f'{d}/audio/mix_pre.wav'
subprocess.run(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error'] + ins + ['-filter_complex', ';'.join(fl), '-map', '[out]', '-t', str(dur),
                '-c:a', 'pcm_f32le', pre], check=True)

def loudnorm_json(args):
    err = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-i', pre, '-af', f'loudnorm={LN}{args}:print_format=json', '-f', 'null', '-'],
                         capture_output=True, text=True, check=True).stderr
    return json.loads(err[err.rindex('{'):err.rindex('}') + 1])

m = loudnorm_json('')
for k in ('input_i', 'input_tp', 'input_lra', 'input_thresh', 'target_offset'):
    m[k] = float(m[k])
if m['input_i'] < -69:
    sys.exit('battle_mix: the mix is silent (loudnorm measured ' + str(m['input_i']) + ' LUFS)')
meas = (f":measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
        f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-i', pre, '-af', f'loudnorm={LN}{meas}', '-ar', '48000',
                '-c:a', 'aac', '-b:a', '256k', f'{d}/audio/mix.m4a'], check=True)
os.remove(pre)
print(f"loudnorm pass 1: {m['input_i']} LUFS, true peak {m['input_tp']}, LRA {m['input_lra']}; pass 2 applied linearly (offset {m['target_offset']} dB)")
print(fid, 'duration', dur, 's;', len(lines), 'lines; title line at', lines[TITLE]['start'], 's; rise', rise, '; hits', len(hits))
