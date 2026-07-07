"use client";

import { Inter } from "next/font/google";
import "./globals.css";
import { useState, useEffect } from "react";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === 'light' ? 'dark' : 'light');

  return (
    <html lang="en" data-theme={theme}>
      <body className={`${inter.variable} antialiased`}>
        <div className="fixed top-6 right-8 z-50">
            <button 
                onClick={toggleTheme}
                className="glass px-4 py-2 rounded-full text-xs font-bold glow-btn uppercase tracking-tighter"
            >
                {theme === 'light' ? '🌙 Dark Mode' : '☀️ Light Mode'}
            </button>
        </div>
        {children}
      </body>
    </html>
  );
}
