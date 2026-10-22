'use client';
export const ease = [0.22, 1, 0.36, 1];
export const appear = (i = 0) => ({ initial: { opacity: 0, y: 14, filter: 'blur(8px)' }, animate: { opacity: 1, y: 0, filter: 'blur(0px)' }, transition: { duration: 0.9, delay: 0.25 + i * 0.08, ease } });
export const mins = (s) => (s ? `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, '0')}` : '');
export const mb = (n) => (n ? (n >= 1e9 ? `${(n / 1e9).toFixed(1)} GB` : `${Math.round(n / 1e6)} MB`) : '');
