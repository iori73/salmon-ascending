import Nav from "@/components/Nav";
import Footer from "@/components/Footer";

const planned = [
  {
    title: "千歳川の十月",
    place: "北海道千歳市",
    season: "2026年10〜11月",
    desc: "シロザケの遡上最盛期。インディアン水車と千歳水族館での観察・撮影記録。",
    status: "planned",
  },
  {
    title: "神の魚を祀る村",
    place: "北海道沙流郡平取町二風谷",
    season: "2026年秋",
    desc: "アイヌ文化の中心地・二風谷での調査。二風谷アイヌ文化博物館、萱野茂コレクション。",
    status: "planned",
  },
  {
    title: "水面下で見るサケ",
    place: "北海道千歳市 サーモンパーク千歳",
    season: "2026年10〜11月",
    desc: "世界唯一の川中水中観察施設。水面下からの遡上観察。",
    status: "planned",
  },
  {
    title: "消費の現場",
    place: "豊洲市場・都内回転寿司",
    season: "2026年通年",
    desc: "Act 1の「消費の現在」を視覚的に記録する。流通の現場と消費の日常性。",
    status: "planned",
  },
];

export default function FieldworkPage() {
  return (
    <>
      <Nav />
      <main className="pt-36 pb-24 px-6 sm:px-10 tone-earth">
        <div className="max-w-wide mx-auto">
          <p className="act-number mb-8">フィールドワーク記録</p>
          <h1 className="h-display font-serif text-[2.5rem] sm:text-[3rem] mb-6">現場の記録</h1>
          <p className="font-serif font-light text-lg text-text-muted leading-[1.95] tracking-[0.04em] max-w-article mb-16">
            このプロジェクトは、デスクリサーチだけでは完結しない。北海道の川、アイヌの記憶の場所、消費の現場——それぞれの場所で、文章と数字を補完する一次的な記録を収集する。
          </p>

          <div className="mb-10">
            <p className="act-number mb-7">計画中のフィールドワーク</p>
            <div className="grid sm:grid-cols-2 gap-px bg-[color:var(--rule)] border border-[color:var(--rule)]">
              {planned.map((fw) => (
                <div key={fw.title} className="bg-bg p-7">
                  <div className="flex justify-between items-baseline mb-4">
                    <p className="font-garamond italic text-sm text-warm-ochre">{fw.season}</p>
                    <span className="fig-num">計画中</span>
                  </div>
                  <h3 className="font-serif text-lg font-normal tracking-[0.04em] mb-1.5">{fw.title}</h3>
                  <p className="text-sm text-warm-ochre font-serif mb-3 tracking-wide">{fw.place}</p>
                  <p className="text-sm text-text-muted font-serif leading-[1.85] tracking-[0.03em]">{fw.desc}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-16 py-6 pl-6 border-l-2 border-warm-ochre/50">
            <p className="editorial-note">
              フィールドワーク記録はこのページで随時更新する。写真・観察ノート・インタビュー（許諾を得たもの）を掲載予定。
            </p>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
