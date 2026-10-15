import localFont from 'next/font/local';
import './globals.css';

const bricolage = localFont({ src: '../node_modules/@fontsource-variable/bricolage-grotesque/files/bricolage-grotesque-latin-standard-normal.woff2', variable: '--font-bricolage', weight: '200 800', display: 'swap' });

export const metadata = { title: 'KINOFORGE Studio', description: 'Talk to the director, approve, watch the film.' };
export const viewport = { themeColor: '#0d1430', width: 'device-width', initialScale: 1, viewportFit: 'cover' };

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={bricolage.variable}>
      <body>{children}</body>
    </html>
  );
}
