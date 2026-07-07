import Link from "next/link";

interface FooterProps {
  /** 記事ページで「次の章」を出す場合に渡す */
  next?: { href: string; label: string; num: string };
}

const acts: [string, string, string][] = [
  ["I", "消費の現在", "/act/1"],
  ["II", "渡来の物語", "/act/2"],
  ["III", "川に戻る論理", "/act/3"],
  ["IV", "神の魚", "/act/4"],
  ["V", "帰着", "/act/5"],
];

export default function Footer({ next }: FooterProps) {
  return (
    <footer className="bg-night text-on-night mt-28">
      {next && (
        <div className="nav-section border-b border-white/10">
          <Link
            href={next.href}
            className="group max-w-wide mx-auto px-6 sm:px-10 py-10 flex items-baseline justify-between gap-6"
          >
            <span className="flex items-baseline gap-4">
              <span className="label text-on-night-soft">次の章 · Next</span>
              <span className="font-garamond italic text-teal-mid">Act {next.num}</span>
              <span className="font-serif text-2xl sm:text-3xl text-on-night group-hover:text-rust transition-colors">
                {next.label}
              </span>
            </span>
            <span className="text-on-night-soft group-hover:text-rust transition-colors text-lg">→</span>
          </Link>
        </div>
      )}

      <div className="max-w-wide mx-auto px-6 sm:px-10 py-16 grid sm:grid-cols-3 gap-12">
        <div>
          <p className="font-garamond text-lg italic text-rust mb-2">Salmon Ascending</p>
          <p className="font-serif text-xl mb-4 tracking-[0.05em]">サーモンは遡上する</p>
          <p className="text-sm text-on-night-soft leading-relaxed">
            日本とサーモンの三層の関係史。<br />
            消費・生態・文化をめぐる編集的探究。
          </p>
        </div>
        <div className="nav-section">
          <p className="label mb-4">Acts</p>
          <ul className="space-y-2">
            {acts.map(([num, label, href]) => (
              <li key={href}>
                <Link
                  href={href}
                  className="flex items-baseline gap-3 text-sm text-on-night-soft hover:text-on-night transition-colors"
                >
                  <span className="font-garamond italic w-5 text-teal-mid">{num}</span>
                  <span className="font-serif">{label}</span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <p className="label mb-4">Sources</p>
          <ul className="space-y-1 text-xs text-on-night-soft leading-relaxed">
            <li>千歳水族館 捕獲統計（2022〜2025）</li>
            <li>水産研究・教育機構 令和7年サケ報告書</li>
            <li>Seafood Norway 対日輸出統計</li>
            <li>国立アイヌ民族博物館（ウポポイ）</li>
            <li>札幌市文化財ページ（アシリチェプノミ）</li>
            <li>日本弁護士連合会 2022年決議</li>
          </ul>
        </div>
      </div>

      <div className="max-w-wide mx-auto px-6 sm:px-10 pb-12">
        <p className="text-xs text-on-night-soft/80 tracking-wide">
          編集・図版　川野いおり · 2026　／　本文：源ノ明朝　欧文：EB Garamond
        </p>
      </div>
    </footer>
  );
}
