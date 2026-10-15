"""sheets.py — contact sheets for the review loop (what the Eyes judges look at).

    python3 harness/review/sheets.py VIDEO.mp4 OUTDIR [--every 4] [--keys 120,660,1206] [--fps 24]

Writes sheet-01.jpg, sheet-02.jpg ... (4 x 4 tiles of 640 px, each labelled with its frame number) sampling one frame
every N seconds, plus keys.jpg with the listed key moments (each beat's cause and effect). Uses ffmpeg only.
"""
import sys, os, subprocess, json

def run(args): subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def probe(v):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', v], capture_output=True, text=True).stdout
    return float(json.loads(out)['format']['duration'])

def tile(video, frames, fps, out, cols=4):
    tmp = out + '.d'; os.makedirs(tmp, exist_ok=True); paths = []
    for k, f in enumerate(frames):
        p = os.path.join(tmp, f'{k:03d}.jpg')
        run(['ffmpeg', '-y', '-ss', f'{f / fps:.3f}', '-i', video, '-frames:v', '1', '-vf',
             f"scale=640:-2,drawtext=text='{f}':x=8:y=8:fontsize=20:fontcolor=white:box=1:boxcolor=black@0.55", '-q:v', '3', p])
        paths.append(p)
    n = len(paths); rows = (n + cols - 1) // cols
    inputs = sum([['-i', p] for p in paths], [])
    layout = '|'.join(f'{(k % cols)}*w0_{(k // cols)}*h0'.replace('0*w0', '0').replace('0*h0', '0') if False else f'{"+".join(["w0"] * (k % cols)) or 0}_{"+".join(["h0"] * (k // cols)) or 0}' for k in range(n))
    if n == 1:
        run(['ffmpeg', '-y', '-i', paths[0], out]); import shutil; shutil.rmtree(tmp, ignore_errors=True); return
    run(['ffmpeg', '-y', *inputs, '-filter_complex', f'xstack=inputs={n}:layout={layout}:fill=black', '-q:v', '3', out])
    import shutil; shutil.rmtree(tmp, ignore_errors=True)

def main():
    video, outdir = sys.argv[1], sys.argv[2]; os.makedirs(outdir, exist_ok=True)
    opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
    fps = int(opt('--fps', 24)); every = float(opt('--every', 4)); keys = [int(x) for x in opt('--keys', '').split(',') if x]
    dur = probe(video); total = int(dur * fps)
    frames = list(range(int(fps), total, int(every * fps)))
    for s in range(0, len(frames), 16):
        tile(video, frames[s:s + 16], fps, os.path.join(outdir, f'sheet-{s // 16 + 1:02d}.jpg'))
    if keys:
        for s in range(0, len(keys), 16): tile(video, keys[s:s + 16], fps, os.path.join(outdir, f'keys-{s // 16 + 1:02d}.jpg'))
    print(sorted(f for f in os.listdir(outdir) if f.endswith('.jpg')))

if __name__ == '__main__':
    main()
