#!/usr/bin/env node
// Print a film's scene list, shot table and the director's checks (camera speed limits, shot count, short shots, jump cuts) without a browser.
// node films/lib/battlemap/tools/scenes.mjs films/battles/cannae [--w 1280 --h 720]
import fs from 'fs'; import path from 'path'; import { pathToFileURL } from 'url';
import { Clock } from '../timeline.js'; import { compileScenes, reportText } from '../scenes.js';
const dir = process.argv[2]; const a = process.argv.slice(3); const W = +(a[a.indexOf('--w') + 1] || 1280) || 1280, H = +(a[a.indexOf('--h') + 1] || 720) || 720;
const spec = (await import(pathToFileURL(path.resolve(dir, 'spec.js')).href)).default; const cues = JSON.parse(fs.readFileSync(path.resolve(dir, 'cues.json'), 'utf8'));
const clock = new Clock(cues, spec.marks || {}); const R = compileScenes(spec, clock, W / H, { duration: cues.duration });
console.log(reportText(R)); process.exit(R.errors.length ? 1 : 0);
