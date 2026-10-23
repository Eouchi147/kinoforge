#!/usr/bin/env python3
"""qc.py: automatic quality gate for a finished film file (ffmpeg and ffprobe only, no libvmaf).

    python3 tools/qc.py <video.mp4> [--film <film folder>] [--out qc.json]

Writes qc.json (pass/fail per check, the numbers, the exact ffmpeg commands) and a contact sheet next to it
(<out stem>-sheet.jpg, about 20 tiles), prints a short summary, and exits 1 when any check fails (2 on a usage or tool error).

Checks (each is "pass", "fail", "info" for numbers that are only reported, or "skip" with the reason):
  duration, resolution, fps     against <film>/film.json (duration within one frame, w, h, fps)
  loudness, true_peak           ebur128: integrated loudness within 1 LU of the target, true peak at or below -1 dBTP.
                                Target: film.json "lufs"; else -16 for the Cutaway showcase line, loops and looks (nature,
                                no voice); else -14 (narrated films, ads, social).
  dead_air                      silencedetect -50 dB for 1 s or more inside the film (the first and last 0.5 s are not counted)
  frozen_frames                 freezedetect (2 s); skipped when film.json has "loop" or "still"
  black_frames                  blackdetect (0.5 s); black that touches the start or the end for at most 1.5 s is a fade
  hard_cuts                     scdet score above 10. A film with "cuts": false, a loop, a seasons folder or the
                                "Cutaway showcase" series must have none (Sam, 23 Oct); any other film: the count is reported
  flicker                       frame-to-frame YAVG jumps (signalstats): high-frequency energy of the brightness series,
                                with cuts and steps removed, plus single-frame pops. Thresholds: FLICKER_* below
  loop_seam                     "loop": true films: SSIM of the last frame against the first, against an ordinary frame step

Video checks run on a copy scaled to 640 px wide (the numbers do not need full size, and a 160 s film takes seconds).
"""
import argparse, json, math, os, re, subprocess, sys, tempfile
from pathlib import Path

# ---- thresholds (one place, so a verdict can change them) ----
LUFS_TOL = 1.0            # LU around the target
TP_MAX = -1.0             # dBTP
SILENCE_DB, SILENCE_MIN = -50, 1.0
EDGE = 0.5                # s at the start and the end where silence is not counted
FREEZE_N, FREEZE_D = 0.003, 2
BLACK_D = 0.5
FADE_MAX = 1.5            # s of black at the start or the end that counts as a fade
SCD_T = 10                # scdet threshold (documented good range 8 to 14)
FLICKER_RMS_MAX = 1.5     # RMS of the second difference of YAVG (0..255 scale), steps and cut frames removed
FLICKER_POP = 3.0         # a single frame this many brightness levels (0..255) off its neighbours, then back, is a pop
FLICKER_STEP = 6.0        # a second difference above this is a step (cut, fade, ramp), not shimmer
SEAM_SLACK = 0.02         # the seam SSIM may be this far under an ordinary step
ANALYSIS_W = 640
SHEET_TILES, SHEET_COLS, SHEET_ROWS, SHEET_W = 20, 5, 4, 384


def run(cmd, check=True):
    p = subprocess.run(cmd, capture_output=True, text=True, errors='replace')
    if check and p.returncode != 0:
        sys.exit(f"qc: command failed ({p.returncode}): {shell(cmd)}\n{p.stderr[-800:]}")
    return p


def shell(cmd):
    return ' '.join(c if re.fullmatch(r'[\w./:=,@%+-]+', c) else "'" + c.replace("'", "'\\''") + "'" for c in cmd)


def result(status, msg, **nums):
    return {'status': status, 'detail': msg, **nums}


def probe(video):
    cmd = ['ffprobe', '-v', 'error', '-show_entries',
           'format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,avg_frame_rate,duration,nb_frames',
           '-of', 'json', str(video)]
    j = json.loads(run(cmd).stdout)
    v = next((s for s in j['streams'] if s['codec_type'] == 'video'), None)
    a = next((s for s in j['streams'] if s['codec_type'] == 'audio'), None)
    if not v:
        sys.exit('qc: no video stream in ' + str(video))
    num, den = (v['r_frame_rate'].split('/') + ['1'])[:2]
    fps = float(num) / float(den or 1)
    dur = float(j['format']['duration'])
    return {'cmd': shell(cmd), 'duration': dur, 'w': v['width'], 'h': v['height'], 'fps': fps,
            'video_codec': v['codec_name'], 'audio_codec': a['codec_name'] if a else None, 'has_audio': a is not None}


def kind_flags(film, film_dir):
    """What the film.json (and its folder) say about how the film is judged."""
    f = film or {}
    path = str(film_dir or '').lower()
    series = str(f.get('series', '')).lower()
    loop = bool(f.get('loop'))
    still = bool(f.get('still'))
    seasons = 'seasons' in path or 'seasons' in str(f.get('id', '')).lower()
    if 'cuts' in f:
        no_cuts, why_cuts = (f['cuts'] is False), 'film.json "cuts"'
    elif loop or seasons:
        no_cuts, why_cuts = True, 'a loop / seasons-loop style has no cuts'
    elif series == 'cutaway showcase':
        no_cuts, why_cuts = True, 'Cutaway showcase films are one fixed view, no cuts (Sam, 23 Oct)'
    else:
        no_cuts, why_cuts = False, 'cuts are allowed in this kind of film; the count is only reported'
    if 'lufs' in f:
        lufs, why_l = float(f['lufs']), 'film.json "lufs"'
    elif f.get('style') == 'cutaway' and series.startswith('cutaway') and '/ads/' not in path.replace('\\', '/') + '/':
        lufs, why_l = -16.0, 'inferred: Cutaway showcase, loop or look film (nature sound, no voice)'
    else:
        lufs, why_l = -14.0, 'default for narrated films, ads and social'
    return {'loop': loop, 'still': still, 'no_cuts': no_cuts, 'why_cuts': why_cuts, 'lufs': lufs, 'why_lufs': why_l}


# ---------------------------------------------------------------- the passes
def audio_pass(video):
    af = f'silencedetect=n={SILENCE_DB}dB:d={SILENCE_MIN},ebur128=peak=true:framelog=quiet'
    cmd = ['ffmpeg', '-nostdin', '-hide_banner', '-nostats', '-i', str(video), '-vn', '-af', af, '-f', 'null', '-']
    err = run(cmd).stderr
    m = lambda pat: (re.search(pat, err.split('Summary:')[-1]) if 'Summary:' in err else None)
    I, LRA, TP = m(r'I:\s+(-?[\d.]+|-inf) LUFS'), m(r'LRA:\s+(-?[\d.]+) LU'), m(r'Peak:\s+(-?[\d.]+|-inf) dBFS')
    sil, start = [], None
    for line in err.splitlines():
        if 'silence_start:' in line:
            start = float(line.split('silence_start:')[1].strip())
        elif 'silence_end:' in line:
            end = float(re.search(r'silence_end:\s*([\d.]+)', line).group(1))
            d = float(re.search(r'silence_duration:\s*([\d.]+)', line).group(1))
            sil.append([round(end - d, 3), round(end, 3)])
            start = None
    if start is not None:
        sil.append([round(start, 3), None])  # silent to the end of the file
    num = lambda x: (float(x.group(1)) if x and x.group(1) != '-inf' else None)
    return {'cmd': shell(cmd), 'I': num(I), 'LRA': num(LRA), 'TP': num(TP), 'silences': sil}


def video_pass(video, tmp):
    """One decode: freezedetect, blackdetect, scdet, signalstats (YAVG per frame)."""
    yfile = os.path.join(tmp, 'yavg.txt')
    vf = (f'scale={ANALYSIS_W}:-2,freezedetect=n={FREEZE_N}:d={FREEZE_D},blackdetect=d={BLACK_D},'
          f'scdet=t={SCD_T}:s=0,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file={yfile}')
    cmd = ['ffmpeg', '-nostdin', '-hide_banner', '-nostats', '-i', str(video), '-an', '-vf', vf, '-f', 'null', '-']
    err = run(cmd).stderr
    freezes, cur = [], None
    for line in err.splitlines():
        if 'lavfi.freezedetect.freeze_start' in line:
            cur = float(line.rsplit(':', 1)[1])
        elif 'lavfi.freezedetect.freeze_end' in line and cur is not None:
            freezes.append([round(cur, 3), round(float(line.rsplit(':', 1)[1]), 3)]); cur = None
    if cur is not None:
        freezes.append([round(cur, 3), None])
    blacks = [[float(a), float(b)] for a, b in re.findall(r'black_start:([\d.]+) black_end:([\d.]+)', err)]
    cuts = [{'time': float(t), 'score': float(s)} for s, t in re.findall(r'lavfi\.scd\.score:\s*([\d.]+),\s*lavfi\.scd\.time:\s*([\d.]+)', err)]
    ys = []
    for line in open(yfile):
        if 'YAVG=' in line:
            ys.append(float(line.split('=')[1]))
    return {'cmd': shell(cmd), 'freezes': freezes, 'blacks': blacks, 'cuts': cuts, 'yavg': ys}


def ssim_all(cmd):
    err = run(cmd).stderr
    m = re.search(r'SSIM.*?All:([\d.]+)', err)
    return float(m.group(1)) if m else None


def seam_pass(video, fps, tmp):
    """SSIM of the last frame against the first, against an ordinary frame step (first to second, and the last step)."""
    sc = f'scale={ANALYSIS_W}:-2'
    f0, f1, fl2, fl1 = (os.path.join(tmp, n) for n in ('f0.png', 'f1.png', 'l2.png', 'l1.png'))
    run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', str(video), '-vf', f'{sc},select=lt(n\\,2)', '-vsync', '0', os.path.join(tmp, 'a%d.png')])
    run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-sseof', '-0.5', '-i', str(video), '-vf', sc, '-vsync', '0', os.path.join(tmp, 'z%03d.png')])
    zs = sorted(Path(tmp).glob('z*.png'))
    if len(zs) < 2 or not (Path(tmp) / 'a1.png').exists():
        return None
    first, second, prev, last = Path(tmp) / 'a1.png', Path(tmp) / 'a2.png', zs[-2], zs[-1]
    ss = lambda x, y: ssim_all(['ffmpeg', '-nostdin', '-hide_banner', '-i', str(x), '-i', str(y), '-lavfi', 'ssim', '-f', 'null', '-'])
    seam, step_start, step_end = ss(last, first), ss(first, second), ss(prev, last)
    cmd = f'ffmpeg -i last.png -i first.png -lavfi ssim -f null -   (frames at {ANALYSIS_W} px wide; steps: first to second, second-to-last to last)'
    return {'cmd': cmd, 'seam': seam, 'step_first': step_start, 'step_last': step_end}


def contact_sheet(video, dur, out_jpg):
    fps = SHEET_TILES / max(dur, 0.1)
    vf = f'fps={fps:.6f},scale={SHEET_W}:-2,tile={SHEET_COLS}x{SHEET_ROWS}:padding=4:margin=4:color=black'
    cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', str(video), '-an', '-vf', vf, '-frames:v', '1', '-q:v', '3', str(out_jpg)]
    run(cmd)
    return shell(cmd)


# ---------------------------------------------------------------- the judgments
def flicker_metric(ys, cut_times, fps):
    """Brightness (YAVG) shimmer and pops. Cuts, fades and ramps are steps, not flicker: a step moves the brightness and stays.
    pop   = one frame that leaves its neighbours' brightness and comes back (|y[i] - mean(y[i-1], y[i+1])| above FLICKER_POP
            while y[i-1] and y[i+1] agree);
    shimmer = RMS of the second difference over the frames that are not near a cut and not a step (|d2| above FLICKER_STEP)."""
    if len(ys) < 5:
        return None
    bad = set()
    for t in cut_times:
        k = int(round(t * fps))
        bad.update(range(k - 2, k + 3))
    d2, pops = [], []
    for i in range(1, len(ys) - 1):
        if {i - 1, i, i + 1} & bad:
            continue
        r = ys[i] - (ys[i - 1] + ys[i + 1]) / 2
        if abs(r) > FLICKER_POP and abs(ys[i + 1] - ys[i - 1]) < abs(r):
            pops.append((abs(r), i)); continue
        v = abs(2 * r)
        if v <= FLICKER_STEP:
            d2.append(v)
    rms = math.sqrt(sum(v * v for v in d2) / len(d2)) if d2 else 0.0
    worst = max(pops) if pops else None
    return {'rms_d2': round(rms, 4), 'pops': len(pops), 'worst_pop': round(worst[0], 2) if worst else 0, 'worst_pop_at_s': round(worst[1] / fps, 2) if worst else None,
            'pop_times_s': [round(i / fps, 2) for _, i in sorted(pops, key=lambda x: x[1])][:20], 'frames': len(ys)}


def judge(info, film, flags, ap, vp, seam):
    C = {}
    dur, fps = info['duration'], info['fps']
    if film:
        want = float(film['duration'])
        tol = 1.0 / float(film.get('fps', fps) or fps)
        ok = abs(dur - want) <= tol
        C['duration'] = result('pass' if ok else 'fail', f'{dur:.3f} s vs film.json {want:.3f} s (tolerance one frame, {tol:.3f} s)', measured=round(dur, 3), expected=want)
        ok = (info['w'], info['h']) == (film['w'], film['h'])
        C['resolution'] = result('pass' if ok else 'fail', f"{info['w']}x{info['h']} vs film.json {film['w']}x{film['h']}", measured=[info['w'], info['h']], expected=[film['w'], film['h']])
        if 'fps' in film:
            ok = abs(fps - float(film['fps'])) < 0.01
            C['fps'] = result('pass' if ok else 'fail', f"{fps:.3f} fps vs film.json {film['fps']}", measured=round(fps, 3), expected=film['fps'])
        if film.get('audio') and not info['has_audio']:
            C['audio_track'] = result('fail', 'film.json lists audio but the file has no audio stream')
    else:
        C['duration'] = result('info', f'{dur:.3f} s (no film.json given, nothing to compare)', measured=round(dur, 3))
        C['resolution'] = result('info', f"{info['w']}x{info['h']} (no film.json given)", measured=[info['w'], info['h']])

    # loudness and true peak
    if not info['has_audio']:
        C['loudness'] = result('skip', 'no audio stream')
        C['true_peak'] = result('skip', 'no audio stream')
        C['dead_air'] = result('skip', 'no audio stream')
    else:
        t = flags['lufs']
        I, TP = ap['I'], ap['TP']
        if I is None:
            C['loudness'] = result('fail', 'integrated loudness could not be measured (silent file?)')
        else:
            ok = abs(I - t) <= LUFS_TOL
            C['loudness'] = result('pass' if ok else 'fail', f"{I:.1f} LUFS, target {t:g} +/- {LUFS_TOL:g} ({flags['why_lufs']}); LRA {ap['LRA']} LU", measured=I, target=t, lra=ap['LRA'])
        if TP is None:
            C['true_peak'] = result('fail', 'true peak could not be measured')
        else:
            C['true_peak'] = result('pass' if TP <= TP_MAX else 'fail', f'{TP:.1f} dBTP, must be at or below {TP_MAX:g}', measured=TP, max=TP_MAX)
        body = []
        for s, e in ap['silences']:
            lo, hi = max(s, EDGE), min(dur if e is None else e, dur - EDGE)  # the first and last half second are not counted
            if hi - lo >= SILENCE_MIN:
                body.append([s, e])
        C['dead_air'] = result('fail' if body else 'pass', (f'{len(body)} silent stretch(es) of {SILENCE_MIN:g} s or more below {SILENCE_DB} dB: ' + ', '.join(f'{s}-{e}' for s, e in body)) if body else f'no silence of {SILENCE_MIN:g} s or more below {SILENCE_DB} dB inside the film', stretches=body, all_silences=ap['silences'])

    # frozen frames
    if flags['loop'] or flags['still']:
        C['frozen_frames'] = result('skip', 'film.json says loop or still')
    else:
        fr = vp['freezes']
        C['frozen_frames'] = result('fail' if fr else 'pass', (f'{len(fr)} frozen stretch(es) of {FREEZE_D} s or more: ' + ', '.join(f'{s}-{e}' for s, e in fr)) if fr else f'no frozen stretch of {FREEZE_D} s or more', stretches=fr)

    # black frames: a fade from or to black at the edges is allowed
    bad = []
    for s, e in vp['blacks']:
        edge = (s <= 0.05 or e >= dur - 0.1) and (e - s) <= FADE_MAX
        if not edge:
            bad.append([s, e])
    C['black_frames'] = result('fail' if bad else 'pass', (f'{len(bad)} black stretch(es): ' + ', '.join(f'{s}-{e}' for s, e in bad)) if bad else (f'{len(vp["blacks"])} edge fade(s) of black, allowed' if vp['blacks'] else 'no black frames'), stretches=bad, all_black=vp['blacks'])

    # hard cuts
    cuts = vp['cuts']
    lst = ', '.join(f"{c['time']:g}s ({c['score']:g})" for c in cuts)
    if flags['no_cuts']:
        C['hard_cuts'] = result('fail' if cuts else 'pass', (f'{len(cuts)} hard cut(s) in a film that must have none ({flags["why_cuts"]}): {lst}') if cuts else f'no hard cut (scdet above {SCD_T}); {flags["why_cuts"]}', count=len(cuts), cuts=cuts)
    else:
        C['hard_cuts'] = result('info', f'{len(cuts)} hard cut(s) (scdet above {SCD_T}); {flags["why_cuts"]}' + (f': {lst}' if cuts and len(cuts) <= 12 else ''), count=len(cuts), cuts=cuts)

    # flicker
    fm = flicker_metric(vp['yavg'], [c['time'] for c in cuts], fps)
    if fm is None:
        C['flicker'] = result('skip', 'too few frames')
    else:
        ok = fm['rms_d2'] <= FLICKER_RMS_MAX and fm['pops'] == 0
        C['flicker'] = result('pass' if ok else 'fail', f"brightness shimmer RMS {fm['rms_d2']} (max {FLICKER_RMS_MAX}), {fm['pops']} single-frame pop(s) above {FLICKER_POP}" + (f"; worst {fm['worst_pop']} at {fm['worst_pop_at_s']} s" if fm['pops'] else ''), **fm)

    # loop seam
    if flags['loop']:
        if not seam or seam['seam'] is None:
            C['loop_seam'] = result('fail', 'could not measure the seam')
        else:
            steps = [s for s in (seam['step_first'], seam['step_last']) if s is not None]
            ref = min(steps)
            ok = seam['seam'] >= ref - SEAM_SLACK
            C['loop_seam'] = result('pass' if ok else 'fail', f"seam SSIM {seam['seam']:.4f} vs ordinary step {ref:.4f} (slack {SEAM_SLACK})", **{k: v for k, v in seam.items() if k != 'cmd'})
    else:
        C['loop_seam'] = result('skip', 'not a loop')
    return C


def main():
    ap = argparse.ArgumentParser(description='Automatic quality gate for a finished film file.')
    ap.add_argument('video'); ap.add_argument('--film', help='film folder (reads film.json)'); ap.add_argument('--out', default='qc.json')
    a = ap.parse_args()
    video = Path(a.video)
    if not video.exists():
        sys.exit(f'qc: no such file: {video}')
    for tool in ('ffmpeg', 'ffprobe'):
        if run([tool, '-version'], check=False).returncode != 0:
            sys.exit(f'qc: {tool} is needed')
    film, film_dir = None, None
    if a.film:
        film_dir = Path(a.film)
        fj = film_dir / 'film.json'
        if not fj.exists():
            sys.exit(f'qc: {fj} not found')
        film = json.load(open(fj))
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    info = probe(video)
    flags = kind_flags(film, film_dir)
    with tempfile.TemporaryDirectory() as tmp:
        apass = audio_pass(video) if info['has_audio'] else None
        vpass = video_pass(video, tmp)
        seam = seam_pass(video, info['fps'], tmp) if flags['loop'] else None
        sheet = out.with_name(out.stem + '-sheet.jpg')
        sheet_cmd = contact_sheet(video, info['duration'], sheet)
    checks = judge(info, film, flags, apass or {'I': None, 'LRA': None, 'TP': None, 'silences': []}, vpass, seam)
    fails = [k for k, c in checks.items() if c['status'] == 'fail']
    commands = {'ffprobe': info['cmd'], 'video_pass': vpass['cmd'], 'contact_sheet': sheet_cmd}
    if apass: commands['audio_pass'] = apass['cmd']
    if seam: commands['loop_seam'] = seam['cmd']
    report = {'file': str(video), 'film': str(film_dir) if film_dir else None, 'verdict': 'fail' if fails else 'pass', 'failed': fails,
              'video': {k: info[k] for k in ('duration', 'w', 'h', 'fps', 'video_codec', 'audio_codec')},
              'judged_as': {'target_lufs': flags['lufs'], 'why_lufs': flags['why_lufs'], 'no_cuts_expected': flags['no_cuts'], 'why_cuts': flags['why_cuts'], 'loop': flags['loop'], 'still': flags['still']},
              'thresholds': {'lufs_tol': LUFS_TOL, 'true_peak_max': TP_MAX, 'silence': f'{SILENCE_DB} dB for {SILENCE_MIN} s', 'freeze': f'n={FREEZE_N} d={FREEZE_D}', 'black': f'd={BLACK_D}', 'scdet': SCD_T, 'flicker_rms_max': FLICKER_RMS_MAX, 'flicker_pop': FLICKER_POP, 'flicker_step': FLICKER_STEP, 'seam_slack': SEAM_SLACK},
              'checks': checks, 'contact_sheet': str(sheet), 'commands': commands}
    json.dump(report, open(out, 'w'), indent=1)
    mark = {'pass': 'PASS', 'fail': 'FAIL', 'info': 'info', 'skip': 'skip'}
    print(f"qc: {video.name}: {report['verdict'].upper()}" + (f"  (failed: {', '.join(fails)})" if fails else ''))
    for k, c in checks.items():
        print(f"  {mark[c['status']]:4}  {k:13} {c['detail']}")
    print(f'  report: {out}\n  sheet:  {sheet}  (look at all of it)')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
