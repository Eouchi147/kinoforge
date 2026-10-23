#!/usr/bin/env python3
"""Estimated cues for a Cutaway film that has no narration yet (layout, tests, the line's example).

    python3 films/lib/cutaway/tools/cues_estimate.py <film dir> [--wps 2.7] [--title-line l01] [--hold 3.2] [--outro 4.2]

Reads <film dir>/script.json ({"title", "lines": [{"text"}...]}) or script.md (one narration line per non-empty line,
lines starting with # skipped) and writes cues.json in the director's format (lines with word times, title_line,
outro_s, duration) with "estimated": true. Real narration (films/director/sound.py or .github/workflows/sound.yml)
replaces it with measured times; specs keep working because they refer to words, not seconds.
"""
import argparse
import json
import os


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('film'); ap.add_argument('--wps', type=float, default=2.7)
    ap.add_argument('--title-line', default='l01'); ap.add_argument('--hold', type=float, default=3.2); ap.add_argument('--outro', type=float, default=4.2)
    ap.add_argument('--lead', type=float, default=1.2); ap.add_argument('--gap', type=float, default=0.7)
    a = ap.parse_args(); d = a.film
    if os.path.exists(os.path.join(d, 'script.json')):
        s = json.load(open(os.path.join(d, 'script.json'))); title = s.get('title', ''); texts = [l['text'] for l in s['lines']]
    else:
        raw = [x.strip() for x in open(os.path.join(d, 'script.md')).read().splitlines()]; title = ''
        texts = [x for x in raw if x and not x.startswith('#')]
    t = a.lead; lines = []
    for k, text in enumerate(texts):
        words = text.split(); dur = len(words) / a.wps + 0.2 * sum(text.count(c) for c in '.,;:'); w = []
        for j, x in enumerate(words):
            w.append([x, round(t + dur * j / len(words), 3), round(t + dur * (j + 1) / len(words) - 0.04, 3)])
        lid = f'l{k:02d}'; lines.append({'id': lid, 'text': text, 'start': round(t, 3), 'end': round(t + dur, 3), 'words': w})
        t += dur + (a.hold if lid == a.title_line else a.gap)
    dur = round(t - a.gap + a.outro, 3)
    cues = {'id': os.path.basename(os.path.abspath(d)), 'title': title, 'duration': dur, 'outro_s': a.outro, 'title_line': a.title_line,
            'lines': lines, 'estimated': True, 'note': f'Estimated at {a.wps} words per second (no narration yet): tools/cues_estimate.py.'}
    json.dump(cues, open(os.path.join(d, 'cues.json'), 'w'), indent=1)
    print(f'{len(lines)} lines, {dur} s')


if __name__ == '__main__':
    main()
