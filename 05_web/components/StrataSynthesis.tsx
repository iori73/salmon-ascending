import Figure from "./Figure";

/**
 * 図（Act5）　三層の時間構造
 * ひとつの皿の上で出会う二尾（在来のシロザケ／渡来のアトランティックサーモン）を起点に、
 * 表層＝消費・渡来（40年）／中層＝生態・回帰（数百万年）／深層＝アイヌ・神の魚（数千年）
 * を、地層のように下へ深まる時間として統合する総括図。
 */
function Fish({ x, y, s = 1, dir = 1, color }: { x: number; y: number; s?: number; dir?: 1 | -1; color: string }) {
  return (
    <g transform={`translate(${x},${y}) scale(${dir * s},${s})`} filter="url(#inkS)">
      <path d="M2,9 C6,4 15,2 26,3 C34,3 41,5 48,7 L56,1 L51,9 L56,17 C43,13 34,14 26,15 C15,16 6,14 2,9 Z" fill={color} />
      <path d="M26,3 L31,-2 L36,4 Z" fill={color} />
      <circle cx={7} cy={8} r={1} fill="#fafaf6" />
    </g>
  );
}

export default function StrataSynthesis({ num = 1 }: { num?: number }) {
  const W = 940;
  const H = 640;
  const axX = 72;

  return (
    <Figure
      num={num}
      title="三層の時間構造 — ひとつの魚をめぐる、消費・生態・文化"
      source={<>本作の編集構造を要約した模式図。各層の事実は Act I〜IV の出典に拠る。</>}
    >
      <svg
        viewBox={`0 0 ${W} ${H}`}
        width={W}
        height={H}
        className="w-full h-auto min-w-[620px]"
        role="img"
        aria-label="一つの皿で出会う二尾の魚を起点に、表層=消費・渡来の40年、中層=生態・回帰の数百万年、深層=アイヌ・神の魚の数千年が、地層のように下へ深まる時間として重なる総括図。"
      >
        <defs>
          <filter id="inkS" x="-5%" y="-5%" width="110%" height="110%">
            <feTurbulence type="fractalNoise" baseFrequency="0.015" numOctaves={2} seed={8} result="n" />
            <feDisplacementMap in="SourceGraphic" in2="n" scale={2} xChannelSelector="R" yChannelSelector="G" />
          </filter>
          <marker id="sT" markerWidth={8} markerHeight={8} refX={6} refY={3.5} orient="auto"><path d="M0,0 L7,3.5 L0,7 Z" fill="#2E6E8E" /></marker>
          <marker id="sG" markerWidth={8} markerHeight={8} refX={6} refY={3.5} orient="auto"><path d="M0,0 L7,3.5 L0,7 Z" fill="#B8902F" /></marker>
        </defs>

        {/* 地層の帯 */}
        <rect x={axX + 28} y={48} width={W - axX - 76} height={168} fill="#F4F0E6" />
        <rect x={axX + 28} y={216} width={W - axX - 76} height={176} fill="#E2EEF2" />
        <rect x={axX + 28} y={392} width={W - axX - 76} height={184} fill="#EFEADD" />
        {[216, 392].map((y) => (
          <line key={y} x1={axX + 28} y1={y} x2={W - 48} y2={y} stroke="#DAD4C6" strokeWidth={1} strokeDasharray="3,4" />
        ))}

        {/* 時間・深さの軸 */}
        <line x1={axX} y1={56} x2={axX} y2={568} stroke="#8B6E47" strokeWidth={1} markerEnd="url(#sG)" opacity={0.7} />
        <text x={axX} y={44} textAnchor="middle" className="chart-label-muted" style={{ fill: "#8B6E47" }}>現在 / 浅</text>
        <text x={axX} y={590} textAnchor="middle" className="chart-label-muted" style={{ fill: "#8B6E47" }}>過去 / 深</text>

        {/* ── 表層：皿の上で出会う二尾 ── */}
        <g>
          <ellipse cx={560} cy={132} rx={150} ry={40} fill="#fafaf6" stroke="#DAD4C6" strokeWidth={1.2} />
          {/* 渡来（金）左から */}
          <path d="M430,108 C 470,112 500,124 524,130" fill="none" stroke="#B8902F" strokeWidth={1.4} strokeDasharray="6,4" markerEnd="url(#sG)" opacity={0.8} />
          <Fish x={486} y={120} s={1.15} dir={1} color="#D4A847" />
          {/* 在来（青）右から */}
          <path d="M690,108 C 650,112 620,124 596,130" fill="none" stroke="#2E6E8E" strokeWidth={1.4} strokeDasharray="6,4" markerEnd="url(#sT)" opacity={0.8} />
          <Fish x={636} y={120} s={1.15} dir={-1} color="#2E6E8E" />
          <text x={560} y={186} textAnchor="middle" className="chart-label-muted">同じ皿の上の二尾 — シロザケ（在来）と アトランティックサーモン（渡来）</text>
        </g>
        <g>
          <text x={axX + 48} y={96} className="chart-label" style={{ fill: "#C4722A" }}>表層 — 文化変容</text>
          <text x={axX + 48} y={114} className="chart-label-muted">「サーモン」渡来・消費</text>
          <text x={axX + 48} y={132} className="chart-label-muted" style={{ fontStyle: "italic", fontFamily: "EB Garamond, serif" }}>1985–present · 40 yrs</text>
        </g>

        {/* ── 中層：回帰する論理 ── */}
        <g>
          <path d="M470,300 C 600,288 760,300 860,330" fill="none" stroke="#2E6E8E" strokeWidth={1.6} opacity={0.7} filter="url(#inkS)" />
          <Fish x={690} y={300} s={1.3} dir={-1} color="#6EB0C4" />
          <text x={700} y={356} textAnchor="middle" className="chart-label-muted">生まれた川へ回帰する</text>
        </g>
        <g>
          <text x={axX + 48} y={270} className="chart-label" style={{ fill: "#2E6E8E" }}>中層 — 生態</text>
          <text x={axX + 48} y={288} className="chart-label-muted">回帰する論理</text>
          <text x={axX + 48} y={306} className="chart-label-muted" style={{ fontStyle: "italic", fontFamily: "EB Garamond, serif" }}>millions of years</text>
        </g>

        {/* ── 深層：神の魚 ── */}
        <g>
          {/* 抽象的な渦（往還） */}
          <path d="M700,486 C 672,486 672,520 706,520 C 734,520 734,492 712,492 C 698,492 698,506 712,506" fill="none" stroke="#8B6E47" strokeWidth={1.6} opacity={0.55} filter="url(#inkS)" />
          <Fish x={620} y={486} s={1.15} dir={-1} color="#A83232" />
          <text x={700} y={548} textAnchor="middle" className="chart-label-muted">食べられ、神の世界へ帰り、また戻る</text>
        </g>
        <g>
          <text x={axX + 48} y={452} className="chart-label" style={{ fill: "#8B6E47" }}>深層 — 文化</text>
          <text x={axX + 48} y={470} className="chart-label-muted">カムイチェップ（神の魚）</text>
          <text x={axX + 48} y={488} className="chart-label-muted" style={{ fontStyle: "italic", fontFamily: "EB Garamond, serif" }}>thousands of years</text>
        </g>
      </svg>
    </Figure>
  );
}
