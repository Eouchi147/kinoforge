'use client';
// Line icons, 1.6 px strokes on a 24 grid: plain geometry, no pictograms of characters or emoji.
const S = ({ children, size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false">{children}</svg>
);
export const Icon = {
  desk: (p) => <S {...p}><rect x="3.5" y="4.5" width="17" height="15" rx="1.5" /><path d="M3.5 9.5h17M9 9.5v10" /></S>,
  library: (p) => <S {...p}><rect x="3.5" y="5" width="17" height="14" rx="1.5" /><path d="M7 5v14M17 5v14M3.5 9h3.5M3.5 15h3.5M17 9h3.5M17 15h3.5" /></S>,
  create: (p) => <S {...p}><path d="M4 9.5h16v9a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 18.5z" /><path d="m4 9.5-.6-3 15.5-3 .6 3M8 6l2.2 2.8M12.5 5.2l2.2 2.8" /></S>,
  styles: (p) => <S {...p}><rect x="3.5" y="3.5" width="7.5" height="7.5" rx="1" /><rect x="13" y="3.5" width="7.5" height="7.5" rx="1" /><rect x="3.5" y="13" width="7.5" height="7.5" rx="1" /><rect x="13" y="13" width="7.5" height="7.5" rx="1" /></S>,
  jobs: (p) => <S {...p}><path d="M4 6.5h9M4 12h13M4 17.5h6" /><circle cx="18" cy="6.5" r="2" /><circle cx="14" cy="17.5" r="2" /></S>,
  sound: (p) => <S {...p}><path d="M4 10v4M8 7v10M12 4v16M16 8v8M20 11v2" /></S>,
  manual: (p) => <S {...p}><path d="M12 6.5c-2-1.6-4.6-2-8-2v14c3.4 0 6 .4 8 2 2-1.6 4.6-2 8-2v-14c-3.4 0-6 .4-8 2zM12 6.5v14" /></S>,
  settings: (p) => <S {...p}><path d="M4 7h10M18 7h2M4 17h2M10 17h10" /><circle cx="16" cy="7" r="2" /><circle cx="8" cy="17" r="2" /></S>,
  spend: (p) => <S {...p}><path d="M6 3.5h12v17l-2-1.4-2 1.4-2-1.4-2 1.4-2-1.4-2 1.4z" /><path d="M9 8.5h6M9 12h6M9 15.5h3.5" /></S>,
  more: (p) => <S {...p}><circle cx="6" cy="12" r="1.2" /><circle cx="12" cy="12" r="1.2" /><circle cx="18" cy="12" r="1.2" /></S>,
  search: (p) => <S {...p}><circle cx="10.5" cy="10.5" r="6" /><path d="m15 15 5 5" /></S>,
  play: (p) => <S {...p}><path d="M8 5.5v13l10.5-6.5z" fill="currentColor" stroke="none" /></S>,
  close: (p) => <S {...p}><path d="M6 6l12 12M18 6 6 18" /></S>,
  back: (p) => <S {...p}><path d="M14.5 6 8.5 12l6 6" /></S>,
  next: (p) => <S {...p}><path d="m9.5 6 6 6-6 6" /></S>,
  send: (p) => <S {...p}><path d="M5 12h13M13 6l6 6-6 6" /></S>,
  download: (p) => <S {...p}><path d="M12 4v11M7 10.5l5 5 5-5M5 19.5h14" /></S>,
  external: (p) => <S {...p}><path d="M14 4.5h5.5V10M19.5 4.5 11 13M17 13.5v5a1 1 0 0 1-1 1H5.5a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1h5" /></S>,
  check: (p) => <S {...p}><path d="m5 12.5 4.5 4.5L19 7.5" /></S>,
  pin: (p) => <S {...p}><path d="M12 21v-6M7 4.5h10l-1.5 5 2.5 3H6l2.5-3z" /></S>,
  lock: (p) => <S {...p}><rect x="5" y="10.5" width="14" height="9.5" rx="1.5" /><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5" /></S>,
  unlock: (p) => <S {...p}><rect x="5" y="10.5" width="14" height="9.5" rx="1.5" /><path d="M8 10.5V8a4 4 0 0 1 7.7-1.5" /></S>,
};
export const APP_ICON = { desk: Icon.desk, library: Icon.library, create: Icon.create, styles: Icon.styles, jobs: Icon.jobs, sound: Icon.sound, spend: Icon.spend, manual: Icon.manual, settings: Icon.settings };
