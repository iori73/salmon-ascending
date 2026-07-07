import Nav from "@/components/Nav";
import Footer from "@/components/Footer";
import Link from "next/link";

export default function AboutPage() {
  return (
    <>
      <Nav />
      <main className="pt-36 pb-24 px-6 sm:px-10">
        <div className="max-w-article mx-auto">
          <p className="act-number mb-8">このプロジェクトについて</p>
          <h1 className="h-display font-serif text-[2.5rem] sm:text-[3rem] mb-12">
            サーモンは遡上する
          </h1>

          <div className="prose-editorial">
            <p>
              このプロジェクトは、一尾の魚——「サーモン」——をめぐる、三層の関係史を描くグラフィックエディトリアルです。
            </p>

            <p>
              参照軸としたのは、Context Design Instituteの「和食人類学」（ctxt.jp/washoku）の編集・グラフィッククオリティです。食を「ロゼッタストーン」として読む方法論——地質・歴史・文化を横断するシステム思考——を、サーモン×日本という題材に応用することを試みています。
            </p>

            <p>
              五つの章は、「遡上」という構造的メタファーを共有しています。読者は現代の消費（表層）から始まり、渡来の歴史、生態の論理、アイヌの記憶（深層）へと時間を遡ります。そして最後に、最初の問い——「これは何の魚か」——に戻ります。
            </p>

            <hr className="section-rule" />

            <h2>編集方針</h2>

            <p>
              このプロジェクトは、検証可能な事実のみを本文に用いることを原則としています。Project Japanの詳細（具体的な主導者名・開始年・輸出量推移）については、信頼できる一次情報源の確認が現時点で完了しておらず、Act IIでその旨を明示しています。
            </p>

            <p>
              アイヌ文化に関する記述は、公的機関（国立アイヌ民族博物館・札幌市・アイヌ文化振興・研究推進機構）の資料を参照しています。現在も生きている文化への記述として、誤りや不適切な表現へのご指摘を歓迎します。
            </p>

            <hr className="section-rule" />

            <h2>主要参照資料</h2>

            <ul className="text-sm space-y-2 text-text-muted leading-relaxed list-none">
              <li>千歳水族館（サケのふるさと千歳水族館）公式捕獲統計</li>
              <li>水産研究・教育機構「令和7年度サケ来遊状況報告」（2025年8月）</li>
              <li>Seafood Norway（ノルウェー水産物審議会）公式資料</li>
              <li>ノルウェー大使館プレスリリース（2023年）</li>
              <li>国立アイヌ民族博物館（ウポポイ）公式サイト</li>
              <li>札幌市「アシリチェプノミ」文化財ページ</li>
              <li>アイヌ文化振興・研究推進機構 文化マニュアル</li>
              <li>日本弁護士連合会「アイヌ民族の権利に関する決議」（2022年）</li>
              <li>ラポロアイヌネイション訴訟 札幌地裁判決（2024年）</li>
            </ul>

            <hr className="section-rule" />

            <p className="editorial-note">
              制作：川野いおり　2026<br />
              ディレクトリ：<code className="text-xs bg-[#F0EDE8] px-1 py-0.5">/anthropology-of-japanese-food</code>
            </p>
          </div>

          <div className="mt-12">
            <Link href="/" className="text-sm font-serif text-warm-rust border-b border-warm-rust/60 pb-0.5 hover:border-warm-rust transition-colors">
              ← トップに戻る
            </Link>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
