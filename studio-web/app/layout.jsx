import localFont from 'next/font/local';
import './globals.css';

const bricolage = localFont({ src: '../node_modules/@fontsource-variable/bricolage-grotesque/files/bricolage-grotesque-latin-standard-normal.woff2', variable: '--font-bricolage', weight: '200 800', display: 'swap' });

export const metadata = { title: 'KINOFORGE Studio', description: 'The studio operating system: watch, review, create, and follow every build.' };
export const viewport = { themeColor: '#0b0c10', width: 'device-width', initialScale: 1, viewportFit: 'cover', colorScheme: 'dark' };

export default function RootLayout({ children }) {
  return (
    <html lang="en" dir="ltr" className={bricolage.variable}>
      <body>{children}</body>
    </html>
  );
}
