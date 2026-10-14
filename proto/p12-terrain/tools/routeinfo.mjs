import { makeTerrain, makeRoute, makeRiver } from '../terrain.js';
const T = makeTerrain({ res: 1.0 }); const R = makeRoute(T); const V = makeRiver(T);
console.log('route L', R.L.toFixed(1), 'n', R.n);
for (let s = 0; s <= R.L + 0.1; s += 10) { const [x, y, z] = R.at(s); console.log('s', String(Math.round(s)).padStart(4), 'x', x.toFixed(1).padStart(7), 'y', y.toFixed(1).padStart(6), 'z', z.toFixed(1).padStart(7), 'slope', T.slopeAt(x, z).toFixed(2)); }
const e = R.at(R.L); console.log('end', e.map(v => v.toFixed(1)), 'camp', T.camp, 'campY', T.sample(...T.camp).toFixed(1), 'saddle', T.saddle, 'saddleY', T.sample(...T.saddle).toFixed(1), 'tarn level', T.lake.level);
// peak heights
for (const [px, pz] of T.layout.peaks) console.log('peak', px, pz, T.sample(px, pz).toFixed(1));
