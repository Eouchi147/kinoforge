// writes ../timing.json for audio.py (pen speed envelope sampled at 200 Hz + all cue times)
import fs from 'node:fs';
import * as TM from '../timing.js';
const env = []; for (let t = 0; t <= 10.0001; t += 0.005) env.push([+t.toFixed(3), +TM.speedRaw(t).toFixed(5)]);
const out = { fps: TM.FPS, cutS2: TM.CUT_S2, cutS3: TM.CUT_S3, shotDur: TM.SHOT_DUR, times: TM.TIMES, penSpeed: env, penPeak: Math.max(...env.map((e) => e[1])) };
fs.writeFileSync(new URL('../timing.json', import.meta.url), JSON.stringify(out));
console.log('timing.json written; penPeak', out.penPeak.toFixed(3));
for (const t of [0.6, 1.0, 2.0, 3.0, 3.625, 4.5, 5.5, 6.5, 7.0, 7.625, 7.875, 8.0, 8.2, 8.375]) console.log('t', t.toFixed(3), 'p', TM.progress(t).toFixed(3), 'v', TM.speedNorm(t).toFixed(3), '/s');
