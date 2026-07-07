"use client";
import Link from "next/link";
import { useEffect, useRef } from "react";
import Nav from "@/components/Nav";
import Footer from "@/components/Footer";

const acts = [
  {
    num: "I",
    href: "/act/1",
    titleJa: "消費の現在",
    titleEn: "The Present of Consumption",
    desc: "回転寿司のサーモン。それはいつから当たり前になったのか。",
  },
  {
    num: "II",
    href: "/act/2",
    titleJa: "渡来の物語",
    titleEn: "The Story of Arrival",
    desc: "ノルウェーが日本の食卓を変えた四十年。なぜ日本人は生サーモンを食べなかったのか。",
  },
  {
    num: "III",
    href: "/act/3",
    titleJa: "川に戻る論理",
    titleEn: "The Logic of Return",
    desc: "千歳川、二年で七割減。サケはなぜ、生まれた川に戻るのか。",
  },
  {
    num: "IV",
    href: "/act/4",
    titleJa: "神の魚",
    titleEn: "The Sacred Fish",
    desc: "カムイチェップ——アイヌが「神の魚」と呼んだ存在と、奪われた漁の権利。",
  },
  {
    num: "V",
    href: "/act/5",
    titleJa: "帰着",
    titleEn: "Return",
    desc: "「これは何の魚か」。問いには、複数の答えがある。",
  },
];

export default function Home() {
  const heroRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onScroll = () => {
      if (!heroRef.current) return;
      const y = window.scrollY;
      heroRef.current.style.transform = `translateY(${y * 0.25}px)`;
      heroRef.current.style.opacity = String(Math.max(0, 1 - y / 560));
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <>
      <Nav />
      <main>
        {/* ── Hero ── */}
        <section className="relative min-h-screen flex flex-col justify-center bg-night overflow-hidden">
          {/* 微かな水の層 */}
          <svg className="absolute inset-0 w-full h-full opacity-[0.07]" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
            {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
              <line key={i} x1="0" y1={`${12 + i * 11}%`} x2="100%" y2={`${12 + i * 11}%`} stroke="#6EB0C4" strokeWidth="0.5" strokeDasharray="2,56" />
            ))}
          </svg>

          <div ref={heroRef} className="relative z-10 px-8 max-w-3xl mx-auto text-center">
            <p className="label text-on-night-soft mb-10">
              Salmon Ascending&nbsp;·&nbsp;A Graphic Editorial
            </p>
            <h1 className="font-serif font-light text-hero tracking-[0.1em] text-on-night">
              サーモンは
              <br />
              遡上する
            </h1>
            <p className="font-serif font-light text-base sm:text-lg text-teal-pale/85 leading-[2] tracking-[0.08em] mt-12 mb-14">
              一尾の魚をめぐる、三層の時間。
              <br className="hidden sm:block" />
              消費・生態・文化——日本とサーモンの関係史。
            </p>
            <div className="w-px h-14 bg-gradient-to-b from-teal-mid/60 to-transparent mx-auto" />
          </div>

          <div className="absolute bottom-12 left-1/2 -translate-x-1/2 z-10 no-print">
            <svg width="16" height="26" viewBox="0 0 16 26" className="opacity-30">
              <line x1="8" y1="0" x2="8" y2="20" stroke="#C8E0E8" strokeWidth="1" />
              <polyline points="3,15 8,22 13,15" fill="none" stroke="#C8E0E8" strokeWidth="1" />
            </svg>
          </div>
        </section>

        {/* ── 章ナビ ── */}
        <section className="py-28 px-6 sm:px-10 bg-bg">
          <div className="max-w-wide mx-auto">
            <p className="act-number mb-14">五つの章、一つの遡上</p>
            <div className="divide-y divide-[color:var(--rule)]">
              {acts.map((act) => (
                <Link
                  key={act.num}
                  href={act.href}
                  className="group grid grid-cols-[3rem_1fr_auto] sm:grid-cols-[4.5rem_1fr_auto] items-baseline gap-x-5 sm:gap-x-8 py-9 transition-colors"
                >
                  <span className="font-garamond text-[2rem] sm:text-[2.6rem] leading-none text-warm-ochre/70 group-hover:text-warm-rust transition-colors">
                    {act.num}
                  </span>
                  <span>
                    <span className="block font-serif text-xl sm:text-[1.6rem] font-normal tracking-[0.05em] text-text-primary group-hover:text-warm-rust transition-colors mb-1.5">
                      {act.titleJa}
                    </span>
                    <span className="block font-garamond italic text-sm text-warm-ochre mb-3 tracking-wide">
                      {act.titleEn}
                    </span>
                    <span className="block text-[0.875rem] font-serif text-text-muted leading-[1.85] tracking-[0.03em] max-w-[34em]">
                      {act.desc}
                    </span>
                  </span>
                  <span className="self-center text-[color:var(--rule)] group-hover:text-warm-rust transition-colors text-lg">
                    →
                  </span>
                </Link>
              ))}
            </div>
          </div>
        </section>

        {/* ── フィールドワーク ── */}
        <section className="py-20 px-6 sm:px-10 tone-earth border-t border-[color:var(--rule)]">
          <div className="max-w-wide mx-auto flex flex-col sm:flex-row gap-10 items-start">
            <div className="flex-1">
              <p className="act-number mb-5">フィールドワーク</p>
              <h2 className="font-serif text-2xl font-normal tracking-[0.05em] mb-5">現場の記録</h2>
              <p className="text-[0.9rem] font-serif text-text-muted leading-[1.95] tracking-[0.03em] mb-7 max-w-[32em]">
                調査は続いている。北海道の川、アイヌの記憶の場所、消費の現場。
                フィールドワークの記録は、随時更新する。
              </p>
              <Link
                href="/fieldwork"
                className="inline-block text-sm font-serif text-warm-rust border-b border-warm-rust/60 pb-0.5 hover:border-warm-rust transition-colors"
              >
                記録を見る →
              </Link>
            </div>
            <div className="sm:w-72 shrink-0">
              <div className="bg-[#D8C7A6] h-48 flex items-center justify-center">
                <p className="text-xs text-warm-ochre font-serif tracking-wide">フィールドワーク写真（予定）</p>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
