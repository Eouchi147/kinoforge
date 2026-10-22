// node films/lib/battlemap/tools/worldtest.mjs films/battles/cannae/spec.json  -> timing + a height/feature summary
import fs from 'fs'; import { buildWorldData } from '../worldgen.js';
const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf8')); const t0 = Date.now();
const w = buildWorldData(spec.world); let lo = 1e9, hi = -1e9; for (const h of w.H) { lo = Math.min(lo, h); hi = Math.max(hi, h); }
console.log('world built in', Date.now() - t0, 'ms', w.nx, 'x', w.nz, 'height', lo.toFixed(1), hi.toFixed(1));
