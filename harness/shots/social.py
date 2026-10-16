"""social.py: the sound and the finish for social videos (social/, workflow .github/workflows/social.yml).

    python3 harness/shots/social.py music  social/batches/<client>/<batch>                       (needs OPENROUTER_API_KEY)
    python3 harness/shots/social.py finish social/batches/<client>/<batch> <video id> <picture.mp4> <out dir>
    python3 harness/shots/social.py ledger social/batches/<client>/<batch> <dir of *-render.json>

music:  one Lyria clip for the whole batch (batch.json "music": prompt, cap_usd), made once: skipped when audio/music.mp3
        exists or music is off. Booked against the batch cap and the whole test budget first (factory.Budget); every call
        lands in <batch>/ledger.json. No other paid call exists in the social lane.
finish: the picture from harness/dom-render.cjs plus the batch music (trimmed from offset_s, faded, under gain_db) mastered to
        -14 LUFS for social platforms, or a silent track when there is no music; H.264 is copied untouched. Writes
        <client>-<batch>-<id>.mp4, -cover.jpg (the template's cover moment, where the words are on screen) and -render.json.
ledger: adds the render records to <batch>/ledger.json under "renders" (the paid calls stay under "calls").
"""
import os, sys, json, glob, subprocess, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SR = 48000
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)
def run(cmd):
    if cmd and cmd[0] == 'ffmpeg' and '-nostdin' not in cmd: cmd = ['ffmpeg', '-nostdin'] + cmd[1:]
    r = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=900); assert r.returncode == 0, r.stderr[-1500:]; return r
def dur_of(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout.strip() or 0)
def load(bdir): return json.load(open(os.path.join(bdir, 'batch.json')))
def music_on(b): return bool(b.get('music') and b['music'].get('enabled', True) and b['music'].get('prompt'))


def keep_renders(bdir, fn):
    """Run fn (which may rewrite ledger.json through the Ledger) without losing the "renders" list."""
    lp = os.path.join(bdir, 'ledger.json'); old = json.load(open(lp)).get('renders') if os.path.exists(lp) else None
    out = fn()
    if old is not None and os.path.exists(lp):
        d = json.load(open(lp)); d['renders'] = old; json.dump(d, open(lp, 'w'), indent=1)
    return out


def music(bdir):
    b = load(bdir); mp3 = os.path.join(bdir, 'audio', 'music.mp3')
    if not music_on(b): log('music: off for this batch'); return
    if os.path.exists(mp3): log('music: already made', mp3, f'{dur_of(mp3):.1f}s'); return
    from factory import music as lyria, Budget
    os.makedirs(os.path.dirname(mp3), exist_ok=True)
    def make():
        B = Budget(bdir, float(b['music'].get('cap_usd', 0.2)))
        got = lyria(B, b['music']['prompt'], os.path.join(bdir, 'audio', 'music_raw.wav'), 'music')
        log('music spend so far:', f'${B.led.total:.3f} of ${B.led.cap}')
        return got
    got = keep_renders(bdir, make)
    if not got: log('music: Lyria gave no audio; the videos will have a silent track'); return
    run(['ffmpeg', '-v', 'error', '-y', '-i', got, '-ar', str(SR), '-ac', '2', '-b:a', '256k', mp3])
    if os.path.abspath(got) != os.path.abspath(mp3): os.remove(got)
    log('music:', mp3, f'{dur_of(mp3):.1f}s')


def finish(bdir, vid, pic, outdir):
    sys.path.insert(0, os.path.join(ROOT, 'social', 'lib'))
    b = load(bdir); v = next(x for x in b['videos'] if x['id'] == vid)
    tpl = json.load(open(os.path.join(ROOT, 'social', 'templates', v.get('template') or b.get('defaults', {}).get('template'), 'template.json')))
    name = f"{b['client']}-{b['batch']}-{vid}"; os.makedirs(outdir, exist_ok=True)
    D = dur_of(pic); final = os.path.join(outdir, name + '.mp4'); m = b.get('music') or {}
    mp3 = os.path.join(bdir, 'audio', 'music.mp3'); has_music = music_on(b) and os.path.exists(mp3)
    if has_music:
        off = float(v.get('music_offset_s', m.get('offset_s', 0))); g = float(m.get('gain_db', -15)); fo = min(1.6, D / 4)
        af = (f'[1:a]aformat=sample_rates={SR}:channel_layouts=stereo,atrim=0:{D:.3f},afade=t=in:d=0.35,afade=t=out:st={max(0, D - fo):.2f}:d={fo:.2f},'
              f'volume={g}dB,loudnorm=I=-14:TP=-1.5:LRA=11,atrim=0:{D:.3f}[a]')
        run(['ffmpeg', '-v', 'error', '-y', '-i', pic, '-ss', f'{off:.3f}', '-i', mp3, '-filter_complex', af, '-map', '0:v', '-map', '[a]', '-c:v', 'copy',
             '-c:a', 'aac', '-b:a', '192k', '-ar', str(SR), '-t', f'{D:.3f}', '-movflags', '+faststart', final])
    else:   # a silent stereo track: some platforms treat a video with no audio stream as broken
        run(['ffmpeg', '-v', 'error', '-y', '-i', pic, '-f', 'lavfi', '-t', f'{D:.3f}', '-i', f'anullsrc=r={SR}:cl=stereo', '-map', '0:v', '-map', '1:a',
             '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k', '-t', f'{D:.3f}', '-movflags', '+faststart', final])
    cover = os.path.join(outdir, name + '-cover.jpg'); ct = float(v.get('cover_s', tpl.get('cover', 1.0)))
    run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{min(ct, D - 0.05):.3f}', '-i', final, '-frames:v', '1', '-q:v', '2', cover])
    lufs = None
    if has_music:   # measure what was delivered
        r = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-i', final, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True)
        for line in r.stderr.splitlines()[::-1]:
            if line.strip().startswith('I:'): lufs = float(line.split()[1]); break
    probe = json.loads(run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_name,width,height,r_frame_rate', '-of', 'json', final]).stdout)
    rec = {'id': vid, 'name': name, 'template': v.get('template'), 'card': (v.get('card') or {}).get('name'), 'photo': v.get('photo'),
           'duration_s': round(dur_of(final), 2), 'bytes': os.path.getsize(final), 'music': has_music, 'lufs': lufs, 'streams': probe.get('streams'),
           'assets': [name + '.mp4', name + '-cover.jpg', name + '-captions.json'], 'rendered_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    json.dump(rec, open(os.path.join(outdir, name + '-render.json'), 'w'), indent=1)
    log('finished', final, f"{rec['duration_s']}s", f"{rec['bytes'] / 1e6:.1f} MB", f'LUFS {lufs}' if lufs is not None else 'silent track')


def ledger(bdir, recdir):
    lp = os.path.join(bdir, 'ledger.json')
    d = json.load(open(lp)) if os.path.exists(lp) else {'cap': float(((load(bdir).get('music') or {}).get('cap_usd', 0))), 'total': 0.0, 'by_seat': {}, 'calls': []}
    have = {r['id']: r for r in d.get('renders', [])}
    for f in sorted(glob.glob(os.path.join(recdir, '*-render.json'))):
        r = json.load(open(f)); have[r['id']] = r
    d['renders'] = [have[k] for k in sorted(have)]
    json.dump(d, open(lp, 'w'), indent=1)
    log('ledger:', lp, f"{len(d['renders'])} renders, spend ${d.get('total', 0):.3f}")


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'music': music(sys.argv[2].rstrip('/'))
    elif cmd == 'finish': finish(sys.argv[2].rstrip('/'), sys.argv[3], sys.argv[4], sys.argv[5])
    elif cmd == 'ledger': ledger(sys.argv[2].rstrip('/'), sys.argv[3])
    else: print(__doc__); sys.exit(2)
