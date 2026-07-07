"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const acts = [
  { href: "/act/1", num: "I" },
  { href: "/act/2", num: "II" },
  { href: "/act/3", num: "III" },
  { href: "/act/4", num: "IV" },
  { href: "/act/5", num: "V" },
];

export default function Nav() {
  const pathname = usePathname();
  const isTop = pathname === "/";

  return (
    <nav
      className={`no-print fixed top-0 left-0 right-0 z-50 transition-colors duration-500 ${
        isTop ? "bg-transparent" : "bg-paper/90 backdrop-blur-sm border-b border-hairline/60"
      }`}
    >
      <div className="max-w-wide mx-auto px-6 sm:px-10 flex items-center justify-between h-14">
        <Link
          href="/"
          className={`font-serif text-sm tracking-[0.1em] transition-colors ${
            isTop ? "text-on-night-soft hover:text-on-night" : "text-ink-soft hover:text-ink"
          }`}
        >
          サーモンは遡上する
        </Link>
        <div className="hidden sm:flex items-center gap-6">
          {acts.map((act) => {
            const active = pathname === act.href;
            return (
              <Link
                key={act.href}
                href={act.href}
                className={`font-garamond text-xs tracking-[0.22em] transition-colors ${
                  isTop
                    ? active
                      ? "text-on-night"
                      : "text-on-night-soft/70 hover:text-on-night"
                    : active
                    ? "text-rust"
                    : "text-ink-soft hover:text-ink"
                }`}
              >
                {act.num}
              </Link>
            );
          })}
          <Link
            href="/fieldwork"
            className={`font-serif text-xs tracking-[0.04em] transition-colors ${
              isTop ? "text-on-night-soft/70 hover:text-on-night" : "text-ink-soft hover:text-ink"
            }`}
          >
            フィールドワーク
          </Link>
        </div>
      </div>
    </nav>
  );
}
