// P12 TERRAIN — the camera plan (pure data + easing; imported by scene.js and by the Node planning tools).
// S1 top-down locked-off, S2 ONE eased tilt + descent (top-down -> ~35 deg oblique, the look target riding ahead of the pen),
// S3 locked-off low oblique. Heights are world units (the relief is 2x exaggerated); x east, z south, y up.
export const LENS = { s1: 35, s2: 35, s3: 28 };
export const POSE = {
  s1: { pos: [-6, 197, 2], look: [-6, 0, 1.6], mm: LENS.s1 },                    // 89.9 deg: image-up is north
  s2a: { pos: [-6, 197, 2], look: [-6, 0, 1.6], mm: LENS.s2 },                    // identical to S1: the tilt starts from rest on the same frame
  s2b: { pos: [30, 131, -44], look: [8, 48, -165], mm: LENS.s2 },                 // 34 deg oblique from the east bank: the route funnels up to the tarn, the pass on the skyline
  s3: { pos: [-34, 72, -52], look: [8, 46, -190], mm: LENS.s3 },                  // low oblique from the valley axis (62 units west + 54 lower than S2's last frame), peaks against the sky
};
const ss5 = (u) => u * u * u * (u * (u * 6 - 15) + 10);
// smootherstep from rest to rest with a tiny pre-move settle (anticipation: the camera eases back ~2 % before it commits)
export function kS2(u) { const k = ss5(Math.min(1, Math.max(0, u))); return u < 0.3 ? k - 0.022 * Math.pow(Math.sin(Math.PI * u / 0.3), 2) : k; }
