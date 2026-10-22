# KINOFORGE render lane on Sam's Mac (Apple M-series GPU through Metal). Run ONCE inside the Blender app's Python console:
#   exec(open('<repo>/harness/mac/go.py').read())
# It starts a background thread that watches <repo>/mac-queue/ for job files (*.json) and renders them one at a time
# with a separate background Blender process (blender -b --python harness/blender_render.py -- ...), so the app stays usable.
# Job: {"film": "films/cutaway/venice", "out": "out/venice-test", "w": 1280, "h": 720, "samples": 24,
#       "start": 1000, "end": 1020, "device": "METAL"}   (out is relative to the repo; frames land in <out>/frames)
# The lane writes mac-queue/heartbeat.txt every 10 s, <job>.log while rendering, and moves the job to mac-queue/done/.
import os, json, time, threading, subprocess, glob, bpy
def _kf_lane(root):
    q = os.path.join(root, 'mac-queue'); os.makedirs(os.path.join(q, 'done'), exist_ok=True)
    while True:
        try:
            open(os.path.join(q, 'heartbeat.txt'), 'w').write(time.strftime('%Y-%m-%dT%H:%M:%S') + '\n')
            jobs = sorted(glob.glob(os.path.join(q, '*.json')))
            if jobs:
                jf = jobs[0]; j = json.load(open(jf)); log = jf[:-5] + '.log'
                cmd = [bpy.app.binary_path, '-b', '--python', os.path.join(root, 'harness', 'blender_render.py'), '--', j['film'],
                       '--out', os.path.join(root, j['out']), '--w', str(j.get('w', 1280)), '--h', str(j.get('h', 720)),
                       '--fps', str(j.get('fps', 24)), '--start', str(j['start']), '--end', str(j['end']), '--device', j.get('device', 'METAL')]
                if j.get('samples'): cmd += ['--samples', str(j['samples'])]
                t0 = time.time()
                with open(log, 'w') as lf:
                    lf.write('cmd: ' + ' '.join(cmd) + '\n'); lf.flush()
                    rc = subprocess.call(cmd, cwd=root, stdout=lf, stderr=subprocess.STDOUT)
                    lf.write(f'\nexit {rc} after {time.time() - t0:.1f} s\n')
                os.replace(jf, os.path.join(q, 'done', os.path.basename(jf))); os.replace(log, os.path.join(q, 'done', os.path.basename(log)))
        except Exception as e:
            open(os.path.join(q, 'lane-error.txt'), 'a').write(time.strftime('%H:%M:%S ') + repr(e) + '\n')
        time.sleep(10)
_root = '/Users/sam/Desktop/Projects/AI tools/Video Production/kinoforge-render'
threading.Thread(target=_kf_lane, args=(_root,), daemon=True).start()
print('KINOFORGE Mac lane started: watching', _root + '/mac-queue')
