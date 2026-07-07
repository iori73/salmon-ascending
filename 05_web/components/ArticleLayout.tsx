import Link from "next/link";
import Nav from "./Nav";
import Footer from "./Footer";

type Tone = "surface" | "shallow" | "water" | "earth" | "return";

interface ActMeta {
  num: string;
  numJa: string;
  title: string;
  subtitle: string;
  lead: string;
  tone?: Tone;
  prevHref?: string;
  nextHref?: string;
  nextLabel?: string;
}

const ROMAN: Record<string, string> = { "1": "I", "2": "II", "3": "III", "4": "IV", "5": "V" };

export default function ArticleLayout({
  children,
  act,
}: {
  children: React.ReactNode;
  act: ActMeta;
}) {
  const next =
    act.nextHref && act.nextLabel
      ? { href: act.nextHref, label: act.nextLabel, num: ROMAN[act.nextHref.split("/").pop() ?? ""] ?? "" }
      : undefined;

  return (
    <>
      <Nav />
      <main className="bg-paper">
        {/* Act header */}
        <header className="pt-36 pb-16 px-6 sm:px-10 max-w-wide mx-auto">
          {act.prevHref && (
            <Link
              href={act.prevHref}
              className="label hover:text-ink transition-colors no-print inline-block mb-10"
            >
              ← 前の章
            </Link>
          )}
          <p className="label block mb-7">
            Act {act.num} — {act.subtitle}
          </p>
          <h1 className="font-serif text-display font-light tracking-[0.08em] leading-[1.28] text-ink mb-7 max-w-[15em]">
            {act.title}
          </h1>
          <hr className="section-rule max-w-article !ml-0" />
          <p className="mt-10 font-serif font-light text-lead tracking-[0.04em] text-ink max-w-article">
            {act.lead}
          </p>
        </header>

        {/* Article body */}
        <div className="px-6 sm:px-10 max-w-article mx-auto prose-editorial pb-8">
          {children}
        </div>
      </main>
      <Footer next={next} />
    </>
  );
}
