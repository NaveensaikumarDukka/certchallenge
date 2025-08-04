import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'Wealth Advisor AI Copilot',
  description: 'AI-powered wealth management platform for financial advisors',
  keywords: ['wealth management', 'AI', 'financial advisor', 'investment', 'portfolio'],
  authors: [{ name: 'Wealth Advisor AI Team' }],
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="font-sans antialiased">
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/50">
          {children}
        </div>
      </body>
    </html>
  );
} 