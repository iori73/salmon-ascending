import type { Metadata } from "next";
import "./fonts.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "サーモンは遡上する — Salmon Ascending",
  description: "日本とサーモンの三層の関係史。消費・生態・文化をめぐる編集的探究。",
  openGraph: {
    title: "サーモンは遡上する",
    description: "日本とサーモンの三層の関係史。消費・生態・文化をめぐる編集的探究。",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <body className="bg-[#FAFAF6] text-[#2A2A2A] antialiased">
        {children}
      </body>
    </html>
  );
}
