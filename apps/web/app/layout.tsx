import type { Metadata } from "next";
import { Manrope, Space_Grotesk, IBM_Plex_Mono } from "next/font/google";
import Link from "next/link";

import "./globals.css";

const sans = Manrope({ subsets: ["latin"], variable: "--font-sans" });
const display = Space_Grotesk({ subsets: ["latin"], variable: "--font-display" });
const mono = IBM_Plex_Mono({ subsets: ["latin"], weight: ["400", "500"], variable: "--font-mono" });

export const metadata: Metadata = {
  title: "OpsCentreDan",
  description: "Incident management workspace with AI-assisted investigation",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${sans.variable} ${display.variable} ${mono.variable}`}>
      <body>
        <div className="app-shell">
          <aside className="sidebar">
            <h1>OpsCentreDan</h1>
            <Link href="/incidents" className="nav-link">
              Incidents
            </Link>
            <Link href="/onboarding" className="nav-link">
              Onboarding
            </Link>
            <Link href="/knowledge" className="nav-link">
              Knowledge
            </Link>
            <Link href="/settings/connectors" className="nav-link">
              Connectors
            </Link>
            <Link href="/login" className="nav-link">
              Login
            </Link>
          </aside>
          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}
