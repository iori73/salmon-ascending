import ArticleLayout from "@/components/ArticleLayout";
import PullQuote from "@/components/PullQuote";
import StrataSynthesis from "@/components/StrataSynthesis";
import Link from "next/link";

const act = {
  num: "V",
  numJa: "ご",
  title: "帰着",
  subtitle: "Return",
  lead: "皿が流れてくる。オレンジ色の切り身が、白い米の上に乗っている。今度は、少し違って見えるかもしれない。",
  tone: "return" as const,
  prevHref: "/act/4",
};

export default function Act5() {
  return (
    <ArticleLayout act={act}>
      <p>
        「これは何の魚か」という問いに、今ならいくつかの答えが言える。
      </p>

      <div className="my-12 space-y-8">
        {[
          {
            label: "生態学として答えるなら",
            body: "アトランティックサーモン（Salmo salar）。ノルウェーまたはチリのフィヨルドで養殖された個体。大西洋原産の種だが、太平洋には自然分布しない。閉鎖系の養殖環境で育てられたため、日本近海のシロザケとは異なり寄生虫リスクが低い。",
            color: "#2E6E8E",
          },
          {
            label: "食文化史として答えるなら",
            body: "1980年代にノルウェーの対日マーケティング活動によって日本の食卓に導入された外来の食体験。「シャケは焼くもの」という長年の食文化的禁忌を、40年かけて塗り替えた存在。",
            color: "#C4722A",
          },
          {
            label: "生態系として答えるなら",
            body: "千歳川、石狩川、標津川を秋に遡上するシロザケ（Oncorhynchus keta）の記憶。産卵後に死んで森の土壌となり、木を育て、熊を養い、川の生態系を維持してきた存在。そして今、急速に数を減らしている存在。",
            color: "#6EB0C4",
          },
          {
            label: "アイヌの世界観として答えるなら",
            body: "カムイチェップ——神の魚。人間に食べられることで神の世界へと帰り、再び人間のもとへ戻ってくる存在。シペ——真の食べ物。その文化的権利は、2024年の時点でまだ法的に認められていない。",
            color: "#8B6E47",
          },
        ].map((item) => (
          <div key={item.label} className="border-l-2 pl-6" style={{ borderColor: item.color }}>
            <p className="text-xs tracking-[0.2em] mb-2.5 font-serif" style={{ color: item.color }}>
              {item.label}
            </p>
            <p className="text-[0.9rem] font-serif leading-[1.9] tracking-[0.03em] text-text-primary">{item.body}</p>
          </div>
        ))}
      </div>

      <p>
        四つの答えは矛盾しない。それらは同じ存在の、異なる時間における、異なる側面だ。
      </p>

      <p>
        「サーモン」はカタカナで書かれる。それは外来語であり、外来の文化であり、外来の魚だ。しかし今では、日本の「当たり前」の中に深く埋め込まれている。一方で、「シャケ」は今も北海道の川を遡上している——ただし、数は急速に減っている。そして「カムイチェップ」は今も秋の川に帰ってくる——ただし、それを「神の魚として」迎える権利は、まだ制度的に保証されていない。
      </p>

      <PullQuote>
        シャケは川を遡って生まれた。<br />
        サーモンは海を渡ってやってきた。<br />
        どちらも今、同じ皿の上にある。
      </PullQuote>

      <p>
        この一文が、プロジェクトの核心だ。「同じ皿の上にある」という事実は、それだけで複数の物語の交差点になっている。
      </p>

      <p>
        遡上とは、来た道を戻ることだ。産卵床へと向かうサケは、孵化した場所へ帰る。このプロジェクトが辿ったのも、消費の現在から始まり、渡来の歴史、生態の論理、文化の記憶へと——過去へ向けた遡上だった。
      </p>

      <p>
        そして魚と同じように、このプロジェクトも帰着する。最初の皿へ。今度は、少し違う見え方で。
      </p>

      <hr className="section-rule" />

      <StrataSynthesis num={1} />

      <div className="mt-16 pt-10 border-t border-[color:var(--rule)]">
        <p className="act-number mb-6">この物語の続きへ</p>
        <div className="flex flex-wrap gap-8">
          <Link
            href="/fieldwork"
            className="text-sm font-serif text-warm-rust border-b border-warm-rust/60 pb-0.5 hover:border-warm-rust transition-colors"
          >
            フィールドワーク記録を見る →
          </Link>
          <Link
            href="/act/1"
            className="text-sm font-serif text-text-muted border-b border-[color:var(--rule)] pb-0.5 hover:text-text-primary transition-colors"
          >
            最初から読む
          </Link>
        </div>
      </div>
    </ArticleLayout>
  );
}
