// Kinetic card registry: type name -> builder, plus each type's default background.
import { statement, slam, record, strike, list, count, title, end } from './text.js';
import { letter, quote } from './hand.js';
import { stamp, drawer } from './objects.js';
import { map } from './map.js';

export const CARDS = { statement, slam, record, strike, list, count, title, end, letter, quote, stamp, drawer, map };
export const DEFAULT_BG = { record: 'paper', letter: 'parchment' };
