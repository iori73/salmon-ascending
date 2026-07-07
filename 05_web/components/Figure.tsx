import { ReactNode } from "react";

interface FigureProps {
  /** 図番号（例: 3） */
  num: number;
  /** 図のタイトル */
  title: string;
  /** 凡例（記号の説明）。任意 */
  legend?: ReactNode;
  /** 出典。任意 */
  source?: ReactNode;
  /** 本文カラムを越えて広く展開する（既定: true） */
  bleed?: boolean;
  children: ReactNode;
}

/**
 * 誌面的な図版枠。グラフィックを warm-paper パネル（上辺に teal の罫）に収め、
 * 図番号＋タイトル＋出典をパネル下に置く。
 */
export default function Figure({
  num,
  title,
  legend,
  source,
  bleed = true,
  children,
}: FigureProps) {
  return (
    <figure
      className={`my-16 ${
        bleed ? "relative left-1/2 -translate-x-1/2 w-[min(1040px,94vw)]" : ""
      }`}
    >
      <div className="fig-panel">
        <div className="overflow-x-auto">{children}</div>
      </div>

      <figcaption className="mt-3 flex items-baseline gap-3">
        <span className="fig-num shrink-0">図 {num}</span>
        <span className="fig-caption">{title}</span>
      </figcaption>

      {legend && <p className="fig-caption mt-2">{legend}</p>}
      {source && <p className="fig-source mt-1">出典：{source}</p>}
    </figure>
  );
}
