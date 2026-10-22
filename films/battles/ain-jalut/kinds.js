// Ain Jalut: the one symbol the engine does not have, built film-side (no engine change). Import before startBattleMap.
//  - glyph 'u-horse-archers': the legend's unit symbol for the Mongol horse archers (cavalry sign with a bow), drawn like the engine's unit frames.
import { registerIcon, TEAM_RGB, INK } from '/films/lib/battlemap/icons.js';

const rgb = (c, k = 1) => `rgb(${Math.round(Math.min(1, c[0] * k) * 255)},${Math.round(Math.min(1, c[1] * k) * 255)},${Math.round(Math.min(1, c[2] * k) * 255)})`;
const pale = (c, k) => [c[0] + (1 - c[0]) * k, c[1] + (1 - c[1]) * k, c[2] + (1 - c[2]) * k];
registerIcon('u-horse-archers', (g, o) => {
  const team = o.team || TEAM_RGB.carthage; g.lineJoin = 'round'; g.lineCap = 'round';
  g.beginPath(); g.rect(12, 34, 76, 50); g.fillStyle = rgb(pale(team, 0.62)); g.fill();
  g.save(); g.clip(); g.beginPath(); g.rect(12, 34, 76, 6); g.fillStyle = rgb(team); g.fill(); g.restore();
  g.beginPath(); g.rect(12, 34, 76, 50); g.lineWidth = 3; g.strokeStyle = INK; g.stroke();
  g.strokeStyle = INK; g.fillStyle = INK; g.lineWidth = 3; g.beginPath(); g.moveTo(12, 84); g.lineTo(88, 40); g.stroke();
  g.lineWidth = 2.6; g.beginPath(); g.arc(42, 66, 11, -1.25, 1.25); g.stroke(); g.beginPath(); g.moveTo(46, 66); g.lineTo(64, 66); g.stroke();
  g.beginPath(); g.moveTo(66, 66); g.lineTo(60, 62); g.lineTo(60, 70); g.closePath(); g.fill();
});
