# KINOFORGE render lane on Sam's Mac (Apple M-series GPU through Metal). Run ONCE inside the Blender app's Python console:
#   exec(open('/Users/sam/Desktop/Projects/AI tools/Video Production/kinoforge-render/harness/mac/go.py').read())
# It starts a background thread that watches <root>/mac-jobs/ (renamed from mac-queue so an older lane still running in the same Blender session stays idle) for job files (*.json) and runs them one at a time, in
# file-name order (name check jobs "0-..." so they jump ahead of film chunks "5-..."). Every job runs under `caffeinate -i`
# so the Mac does not sleep while it works. Job kinds:
#   render (default): {"film": "films/cutaway/x", "out": "out/x", "w": 1280, "h": 720, "samples": 24, "start": 0,
#                      "end": 48, "device": "METAL"}   frames land in <out>/frames
#   sync:   {"kind": "sync", "ref": "main", "paths": ["harness", "films/lib", "films/styles", "films/cutaway", "ads/fonts"]}
#           refreshes the code copy from GitHub (public tarball, curl + tar, no credentials)
# The lane writes mac-jobs/heartbeat.txt every 10 s, <job>.log while running, and moves the job and log to mac-jobs/done/.
# Re-running this file stops the previous lane thread (generation counter) and starts the new one.
import os, json, time, threading, subprocess, glob, bpy
_root = '/Users/sam/Desktop/Projects/AI tools/Video Production/kinoforge-render'
_gen = bpy.app.driver_namespace.get('kf_lane_gen', 0) + 1
bpy.app.driver_namespace['kf_lane_gen'] = _gen

def _kf_run(cmd, log, cwd):
    t0 = time.time()
    with open(log, 'w') as lf:
        lf.write('cmd: ' + ' '.join(cmd) + '\n'); lf.flush()
        rc = subprocess.call(['caffeinate', '-i'] + cmd, cwd=cwd, stdout=lf, stderr=subprocess.STDOUT)
        lf.write(f'\nexit {rc} after {time.time() - t0:.1f} s\n')
    return rc

def _kf_lane(root, gen):
    q = os.path.join(root, 'mac-jobs'); os.makedirs(os.path.join(q, 'done'), exist_ok=True)
    while bpy.app.driver_namespace.get('kf_lane_gen') == gen:
        try:
            open(os.path.join(q, 'heartbeat.txt'), 'w').write(time.strftime('%Y-%m-%dT%H:%M:%S') + f' gen {gen}\n')
            jobs = sorted(glob.glob(os.path.join(q, '*.json')))
            if jobs:
                jf = jobs[0]; j = json.load(open(jf)); log = jf[:-5] + '.log'
                if j.get('kind') == 'sync':
                    ref = j.get('ref', 'main'); paths = ' '.join(f'"kinoforge-{ref}/{p}/*"' for p in j.get('paths', []))
                    sh = (f'curl -sSL https://codeload.github.com/Eouchi147/kinoforge/tar.gz/{ref} | '
                          f'tar -xzf - --strip-components=1 {paths}')
                    _kf_run(['/bin/bash', '-c', sh], log, root)
                else:
                    cmd = [bpy.app.binary_path, '-b', '--python', os.path.join(root, 'harness', 'blender_render.py'), '--', j['film'],
                           '--out', os.path.join(root, j['out']), '--w', str(j.get('w', 1280)), '--h', str(j.get('h', 720)),
                           '--fps', str(j.get('fps', 24)), '--start', str(j['start']), '--end', str(j['end']),
                           '--device', j.get('device', 'METAL')]
                    if j.get('samples'): cmd += ['--samples', str(j['samples'])]
                    _kf_run(cmd, log, root)
                os.replace(jf, os.path.join(q, 'done', os.path.basename(jf)))
                if os.path.exists(log): os.replace(log, os.path.join(q, 'done', os.path.basename(log)))
        except Exception as e:
            open(os.path.join(q, 'lane-error.txt'), 'a').write(time.strftime('%H:%M:%S ') + repr(e) + '\n')
        time.sleep(10)

threading.Thread(target=_kf_lane, args=(_root, _gen), daemon=True).start()
print(f'KINOFORGE Mac lane (gen {_gen}) started: watching {_root}/mac-jobs')
