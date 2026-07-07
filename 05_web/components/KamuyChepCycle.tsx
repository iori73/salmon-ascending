import Figure from "./Figure";

/**
 * 図（Act4-1）　カムイチェップ — 神と人の往還
 * サケはカムイ（神）が魚の姿で人間の世界を訪れたもの。人に食べられることで
 * 魂は神の世界へ帰り、再び魚となって戻る——という相互的な贈与の循環を示す。
 *
 * 倫理的配慮:
 *  - 用語は公的機関で確認済みのもの（カムイチェップ／シペ／アシリチェプノミ）のみ。
 *  - アイヌの文様・祭具を具体的に再現しない（抽象的な渦線にとどめる）。模式図。
 */
function Salmon({ x, y, s = 1, dir = 1, color = "#A83232" }: { x: number; y: number; s?: number; dir?: 1 | -1; color?: string }) {
  return (
    <g transform={`translate(${x},${y}) scale(${dir * s},${s})`} filter="url(#inkK)">
      <path d="M2,10 C6,4 16,2 28,3 C37,3 45,5 52,7 L60,1 L55,9 L60,18 C46,14 37,15 28,16 C16,17 7,15 2,10 Z" fill={color} />
      <path d="M28,3 L33,-3 L38,3 Z" fill={color} />
      <circle cx={8} cy={8} r={1.1} fill="#fafaf6" />
    </g>
  );
}

export default function KamuyChepCycle({ num = 1 }: { num?: number }) {
  const W = 940;
  const H = 540;

  return (
    <Figure
      num={num}
      title="カムイチェップ — 神と人の往還"
      source={
        <>
          用語・概念は国立アイヌ民族博物館（ウポポイ）、札幌市文化財ページ、千歳水族館の記述に拠る。
          模式図であり、アイヌの文様・祭具を再現したものではない。
        </>
      }
    >
      <svg
        viewBox={`0 0 ${W} ${H}`}
        width={W}
        height={H}
        className="w-full h-auto min-w-[620px]"
        role="img"
        aria-label="神の世界と人間の世界のあいだを、サケが往還する循環図。秋に魚の姿で訪れ、人に食べられ、魂は神の世界へ送られ、再び戻る。"
      >
        <defs>
          <filter id="inkK" x="-6%" y="-6%" width="112%" height="112%">
            <feTurbulence type="fractalNoise" baseFrequency="0.015" numOctaves={2} seed={3} result="n" />
            <feDisplacementMap in="SourceGraphic" in2="n" scale={2} xChannelSelector="R" yChannelSelector="G" />
          </filter>
          <marker id="kR" markerWidth={9} markerHeight={9} refX={6.5} refY={4} orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#A83232" /></marker>
          <marker id="kO" markerWidth={9} markerHeight={9} refX={6.5} refY={4} orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#8B6E47" /></marker>
        </defs>

        {/* 神の世界（上） */}
        <rect x={0} y={0} width={W} height={188} fill="#F4ECE0" />
        <text x={W / 2} y={44} textAnchor="middle" className="chart-label" style={{ fill: "#8B6E47", letterSpacing: "0.2em" }}>カムイモシリ — 神の世界</text>
        {/* 抽象的な渦（具体的文様の再現は避ける） */}
        <path d="M470,96 C 452,96 452,116 470,116 C 484,116 484,102 472,102" fill="none" stroke="#8B6E47" strokeWidth={1.4} opacity={0.5} filter="url(#inkK)" />

        {/* 境界 */}
        <line x1={60} y1={196} x2={W - 60} y2={196} stroke="#DAD4C6" strokeWidth={1} strokeDasharray="3,4" />

        {/* 人間の世界（下）＝川 */}
        <text x={W / 2} y={236} textAnchor="middle" className="chart-label" style={{ fill: "#2E6E8E", letterSpacing: "0.2em" }}>アイヌモシリ — 人間の世界（川）</text>
        <path d="M80,300 C 280,288 660,288 860,300 L860,316 C 660,304 280,304 80,316 Z" fill="#C8E0E8" opacity={0.6} />

        {/* 循環：右で来訪（下降）、左で送り（上昇） */}
        <path d="M610,150 C 700,180 720,300 640,360" fill="none" stroke="#A83232" strokeWidth={2} markerEnd="url(#kR)" opacity={0.85} filter="url(#inkK)" />
        <path d="M300,360 C 220,300 240,180 330,150" fill="none" stroke="#8B6E47" strokeWidth={2} strokeDasharray="6,5" markerEnd="url(#kO)" opacity={0.8} filter="url(#inkK)" />

        {/* 来訪するサケ（婚姻色・秋の遡上） */}
        <Salmon x={648} y={250} s={1.5} dir={-1} color="#A83232" />
        <text x={690} y={210} textAnchor="middle" className="chart-label" style={{ fill: "#A83232" }}>来訪（秋の遡上）</text>
        <text x={690} y={224} textAnchor="middle" className="chart-label-muted">魚の姿で人の世界へ</text>

        {/* 送り（魂が神の世界へ帰る） */}
        <text x={250} y={210} textAnchor="middle" className="chart-label" style={{ fill: "#8B6E47" }}>送り</text>
        <text x={250} y={224} textAnchor="middle" className="chart-label-muted">魂は神の世界へ帰る</text>

        {/* 中央：人に食べられる＝儀礼 */}
        <g>
          <circle cx={470} cy={360} r={5} fill="#A83232" />
          <text x={470} y={392} textAnchor="middle" className="chart-label" style={{ fill: "#2A2A2A" }}>人に食べられ、もてなされる</text>
          <text x={470} y={408} textAnchor="middle" className="chart-label-muted">アシリチェプノミ＝初遡上を迎える感謝の儀礼</text>
        </g>

        {/* 二つの名 */}
        <text x={W / 2} y={466} textAnchor="middle" className="chart-label" style={{ fill: "#A83232" }}>カムイチェップ（神の魚）　／　シペ（真の食べ物）</text>
        <text x={W / 2} y={486} textAnchor="middle" className="chart-label-muted">食べられることは尽きることではなく、再び戻るための往還</text>
      </svg>
    </Figure>
  );
}
