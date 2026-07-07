import Figure from "./Figure";

/**
 * 網走川 地形断面図
 *
 * 設計根拠:
 *  - 網走川（116km）はシロザケ捕獲数ランキング1位の河川（2022〜2024年平均）。
 *  - 地形的に「山地→広大な農業盆地→汽水湖→流氷の海」という4帯を持ち、
 *    サケの一生が地形に対応する数少ない河川。
 *  - 北見盆地は日本最大の玉ねぎ産地（人の営みとサケの通り道の交差）。
 *  - 網走湖（汽水）は海水と淡水の境界＝サケが最後に身体を変容させる場。
 *  - オホーツク海の流氷はプランクトン発生に関わり、サケの餌環境と連動する。
 *
 * スタイル参照: ctxt.jp/washoku「春の山地形グラフィック」
 *  - 単一のオーガニックな地形ライン、地面テクスチャ（水平ハッチ）、
 *    手描き感フィルター（feTurbulence）、ガーモンド斜体ラベル。
 */

// ── 針葉樹（トドマツ・エゾマツ）アイコン ──
function Conifer({ x, y, h = 30 }: { x: number; y: number; h?: number }) {
  const w1 = h * 0.26;
  const w2 = h * 0.35;
  return (
    <g filter="url(#inkTerrain)" opacity={0.82}>
      {/* 幹 */}
      <line x1={x} y1={y} x2={x} y2={y - h} stroke="#3D2B1A" strokeWidth={1.1} />
      {/* 上部の葉 */}
      <polygon
        points={`${x},${y - h - 5} ${x - w1},${y - h + h * 0.3} ${x + w1},${y - h + h * 0.3}`}
        fill="#3D2B1A"
        opacity={0.76}
      />
      {/* 下部の葉（広がり） */}
      <polygon
        points={`${x},${y - h + h * 0.15} ${x - w2},${y - h + h * 0.65} ${x + w2},${y - h + h * 0.65}`}
        fill="#3D2B1A"
        opacity={0.60}
      />
    </g>
  );
}

export default function AbashiriTerrainMap({ num = 1 }: { num?: number }) {
  const W = 960;
  const H = 480;

  // ────────────────────────────────────────────────────────────────
  // 地形プロフィールライン
  //   左（西）= 北見山地 源流 ≈ 500m
  //   右（東）= オホーツク海 ≈ 0m
  //   縦スケールは約8倍に誇張（視覚的強調）
  // ────────────────────────────────────────────────────────────────
  const terrainLine = [
    "M 0,75",
    "C 44,74 82,96 122,126",       // 山頂部（北見山地）
    "C 162,156 204,212 246,249",   // 急傾斜・下降
    "C 276,263 296,269 314,272",   // 盆地入口
    "C 412,278 518,282 612,285",   // 北見盆地（広大な平坦部）
    "C 646,289 664,297 678,302",   // 低湿地への緩降
    "C 700,308 716,294 726,292",   // 浜堤（微地形の盛り上がり）
    "C 738,291 748,308 760,315",   // 浜堤を越えて網走湖へ
    "C 774,317 808,317 840,315",   // 網走湖面（ほぼ水平）
    "C 852,314 860,308 870,307",   // 湖東岸・海側の浜堤
    "C 894,308 918,313 942,314",   // 海岸線
    "C 952,315 957,320 960,326",   // オホーツク海
  ].join(" ");

  const terrainFill = terrainLine + " L 960,480 L 0,480 Z";

  // 水域（網走湖〜オホーツク海）
  const waterFill = [
    "M 726,292",
    "C 738,291 748,308 760,315",
    "C 774,317 808,317 840,315",
    "C 852,314 860,308 870,307",
    "C 894,308 918,313 942,314",
    "C 952,315 957,320 960,326",
    "L 960,480 L 726,480 Z",
  ].join(" ");

  return (
    <Figure
      num={num}
      title="網走川 地形断面 — 北見山地 · 北見盆地 · 網走湖 · オホーツク海"
      legend={
        <span className="inline-flex flex-wrap gap-x-4 gap-y-0.5">
          <span><span style={{ color: "#A83232" }}>●</span> 遡上するサケ（秋）</span>
          <span><span style={{ color: "#2E6E8E" }}>■</span> 水域（網走湖・オホーツク海）</span>
          <span><span style={{ color: "#8B6E47" }}>—</span> 農地テクスチャ（北見盆地）</span>
        </span>
      }
      source={
        <>
          国土地理院・河川情報をもとに模式化。縦スケールは約8倍に誇張。
          左（西）＝源流・産卵場、右（東）＝河口・外洋回遊域。
        </>
      }
    >
      <svg
        viewBox={`0 0 ${W} ${H}`}
        width={W}
        height={H}
        className="w-full h-auto min-w-[640px]"
        role="img"
        aria-label="網走川の地形断面図。左の北見山地（産卵場）から右のオホーツク海まで、山地・北見盆地の農業平野・汽水湖の網走湖・流氷の海を一望する。サケは海から上流の産卵場へ向けて遡上する。"
      >
        <defs>
          {/* 手描き感フィルター（強め）*/}
          <filter id="inkTerrain" x="-5%" y="-5%" width="110%" height="110%">
            <feTurbulence
              type="fractalNoise"
              baseFrequency="0.016"
              numOctaves={3}
              seed={7}
              result="n"
            />
            <feDisplacementMap
              in="SourceGraphic"
              in2="n"
              scale={2.5}
              xChannelSelector="R"
              yChannelSelector="G"
            />
          </filter>
          {/* 手描き感フィルター（弱め・細部用）*/}
          <filter id="inkTerrainSoft" x="-3%" y="-3%" width="106%" height="106%">
            <feTurbulence type="fractalNoise" baseFrequency="0.022" numOctaves={2} seed={11} result="n" />
            <feDisplacementMap in="SourceGraphic" in2="n" scale={1.3} xChannelSelector="R" yChannelSelector="G" />
          </filter>

          {/* 大地グラデーション（黄土色系） */}
          <linearGradient id="terrainGradAb" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%"   stopColor="#C8B082" />
            <stop offset="45%"  stopColor="#BA9E68" />
            <stop offset="100%" stopColor="#A68A50" />
          </linearGradient>

          {/* 水域グラデーション（teal系） */}
          <linearGradient id="waterGradAb" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%"   stopColor="#C8E0E8" stopOpacity={0.74} />
            <stop offset="55%"  stopColor="#6EB0C4" stopOpacity={0.60} />
            <stop offset="100%" stopColor="#2E6E8E" stopOpacity={0.54} />
          </linearGradient>

          {/* 空グラデーション（オホーツクの冷気を帯びた白） */}
          <linearGradient id="skyGradAb" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%"   stopColor="#E6EDE8" />
            <stop offset="100%" stopColor="#ECE8E0" />
          </linearGradient>

          {/* 遡上矢印マーカー（左向き） */}
          <marker id="arUpstreamAb" markerWidth={7} markerHeight={7} refX={3} refY={3.5} orient="auto">
            <path d="M 7,1 L 1,3.5 L 7,6 Z" fill="#A83232" opacity={0.82} />
          </marker>
        </defs>

        {/* ── 空 ── */}
        <rect x={0} y={0} width={W} height={H} fill="url(#skyGradAb)" />

        {/* ── 山の後景シルエット（奥行き感） ── */}
        <g filter="url(#inkTerrainSoft)" opacity={0.17}>
          <path
            d="M 0,75 C 28,55 60,44 92,62 C 124,80 152,108 194,132 C 222,148 256,198 288,248 L 288,300 L 0,300 Z"
            fill="#8B6E47"
          />
          <path
            d="M 40,105 C 72,85 108,74 142,92 C 174,110 198,135 238,180 C 258,204 278,234 298,264 L 298,300 L 40,300 Z"
            fill="#8B6E47"
          />
        </g>

        {/* ── 大地（地形ライン以下の塗りつぶし） ── */}
        <path
          d={terrainFill}
          fill="url(#terrainGradAb)"
          opacity={0.88}
          filter="url(#inkTerrainSoft)"
        />

        {/* ── 水域（網走湖〜オホーツク海） ── */}
        <path d={waterFill} fill="url(#waterGradAb)" />

        {/* ── 農地テクスチャ（北見盆地：水平ハッチ線） ── */}
        {Array.from({ length: 11 }, (_, i) => {
          const y   = 275 + i * 7;
          const x1  = 316 + i * 3.2;
          const x2  = 614 - i * 2.6;
          const op  = 0.30 - i * 0.020;
          return (
            <line
              key={i}
              x1={x1} y1={y} x2={x2} y2={y}
              stroke="#8B6E47"
              strokeWidth={0.55}
              opacity={op > 0 ? op : 0}
              filter="url(#inkTerrainSoft)"
            />
          );
        })}

        {/* ── 地形ライン（メイン・手描き） ── */}
        <path
          d={terrainLine}
          fill="none"
          stroke="#3D2B1A"
          strokeWidth={2.6}
          strokeLinecap="round"
          strokeLinejoin="round"
          filter="url(#inkTerrain)"
        />

        {/* ── 針葉樹（北見山地） ── */}
        {([
          [26,  78, 40],
          [54,  78, 36],
          [80,  87, 32],
          [108, 104, 30],
          [136, 122, 26],
          [160, 144, 22],
        ] as [number, number, number][]).map(([x, y, h], i) => (
          <Conifer key={i} x={x} y={y} h={h} />
        ))}

        {/* ── 流氷のヒント（オホーツク海・白い楕円） ── */}
        {([
          [890, 270, 20, 8],
          [924, 256, 14, 5.5],
          [950, 278, 10, 4],
        ] as [number, number, number, number][]).map(([cx, cy, rx, ry], i) => (
          <ellipse
            key={i}
            cx={cx} cy={cy} rx={rx} ry={ry}
            fill="white"
            stroke="#6EB0C4"
            strokeWidth={0.8}
            opacity={0.70 - i * 0.08}
            filter="url(#inkTerrainSoft)"
          />
        ))}

        {/* ── 波線（オホーツク海） ── */}
        {Array.from({ length: 3 }, (_, i) => (
          <path
            key={i}
            d={`M ${880 + i * 18},${334 + i * 20} Q ${896 + i * 18},${324 + i * 20} ${914 + i * 18},${334 + i * 20} Q ${932 + i * 18},${344 + i * 20} ${950 + i * 18},${334 + i * 20}`}
            fill="none"
            stroke="#2E6E8E"
            strokeWidth={1.2}
            opacity={0.50 - i * 0.10}
            filter="url(#inkTerrainSoft)"
          />
        ))}

        {/* ── サケ2尾（遡上中・左向き） ── */}
        {([
          [408, 275],
          [536, 281],
        ] as [number, number][]).map(([sx, sy], i) => (
          <g
            key={i}
            transform={`translate(${sx},${sy}) scale(-0.38, 0.38)`}
            opacity={0.72}
            filter="url(#inkTerrainSoft)"
          >
            <path
              d="M2,12 C6,5 18,3 30,4 C40,4 49,6 56,8 L66,1 L60,11 L66,21 C50,16 40,17 30,18 C18,19 8,17 2,12 Z"
              fill="#A83232"
              stroke="#A83232"
              strokeWidth={0.4}
            />
            <path d="M31,4 L37,-3 L42,4 Z" fill="#A83232" />
          </g>
        ))}

        {/* ── 遡上の動線（破線アーチ） ── */}
        <path
          d="M 676,262 C 600,248 502,244 400,258"
          fill="none"
          stroke="#A83232"
          strokeWidth={1.2}
          strokeDasharray="6,4"
          markerEnd="url(#arUpstreamAb)"
          opacity={0.66}
          filter="url(#inkTerrainSoft)"
        />

        {/* ── 標高スケール（左端） ── */}
        <g opacity={0.65}>
          <line x1={14} y1={72} x2={14} y2={318} stroke="#8B6E47" strokeWidth={0.7} />
          {([
            [75,  "500m"],
            [128, "200m"],
            [249, "50m"],
            [315, "0m"],
          ] as [number, string][]).map(([y, label]) => (
            <g key={label}>
              <line x1={9} y1={y} x2={19} y2={y} stroke="#8B6E47" strokeWidth={0.7} />
              <text
                x={23} y={y + 4}
                style={{
                  fontFamily: "EB Garamond, Georgia, serif",
                  fontSize: "10px",
                  fill: "#8A847A",
                  letterSpacing: "0.02em",
                }}
              >
                {label}
              </text>
            </g>
          ))}
        </g>

        {/* ── テキストラベル ── */}

        {/* 北見山地 */}
        <text
          x={60} y={40} textAnchor="middle"
          style={{ fontFamily: "Noto Serif JP, serif", fontSize: "15px", fill: "#3D2B1A", fontWeight: 500, letterSpacing: "0.06em" }}
        >
          北見山地
        </text>
        <text
          x={60} y={56} textAnchor="middle"
          style={{ fontFamily: "EB Garamond, Georgia, serif", fontStyle: "italic", fontSize: "10px", fill: "#8A847A", letterSpacing: "0.03em" }}
        >
          Kitami Range
        </text>

        {/* 産卵場（リーダー線付き） */}
        <text
          x={195} y={147} textAnchor="middle"
          style={{ fontFamily: "Noto Serif JP, serif", fontSize: "11px", fill: "#A83232", letterSpacing: "0.05em" }}
        >
          産卵場
        </text>
        <text
          x={195} y={160} textAnchor="middle"
          style={{ fontFamily: "EB Garamond, Georgia, serif", fontStyle: "italic", fontSize: "9px", fill: "#A83232", opacity: 0.75 }}
        >
          湧水のある礫底
        </text>
        <line x1={208} y1={165} x2={228} y2={234} stroke="#A83232" strokeWidth={0.8} opacity={0.55} />

        {/* 北見盆地 */}
        <text
          x={462} y={238} textAnchor="middle"
          style={{ fontFamily: "Noto Serif JP, serif", fontSize: "14px", fill: "#555049", letterSpacing: "0.06em" }}
        >
          北見盆地
        </text>
        <text
          x={462} y={254} textAnchor="middle"
          style={{ fontFamily: "EB Garamond, Georgia, serif", fontStyle: "italic", fontSize: "9.5px", fill: "#8A847A" }}
        >
          Kitami Basin — 日本最大の玉ねぎ産地
        </text>

        {/* 遡上ラベル */}
        <text
          x={526} y={240} textAnchor="middle"
          style={{ fontFamily: "EB Garamond, Georgia, serif", fontStyle: "italic", fontSize: "9.5px", fill: "#A83232", opacity: 0.80 }}
        >
          ← 遡上（秋）
        </text>

        {/* 浜堤（微地形ラベル） */}
        <text
          x={706} y={264} textAnchor="middle"
          style={{ fontFamily: "EB Garamond, Georgia, serif", fontStyle: "italic", fontSize: "9px", fill: "#8A847A" }}
        >
          浜堤
        </text>
        <line x1={720} y1={270} x2={724} y2={287} stroke="#8A847A" strokeWidth={0.65} opacity={0.55} />

        {/* 網走湖 */}
        <text
          x={800} y={294} textAnchor="middle"
          style={{ fontFamily: "Noto Serif JP, serif", fontSize: "12.5px", fill: "#2E6E8E", letterSpacing: "0.06em" }}
        >
          網走湖
        </text>
        <text
          x={800} y={308} textAnchor="middle"
          style={{ fontFamily: "EB Garamond, Georgia, serif", fontStyle: "italic", fontSize: "9.5px", fill: "#6EB0C4" }}
        >
          汽水湖 · brackish lake
        </text>

        {/* オホーツク海 */}
        <text
          x={916} y={246} textAnchor="middle"
          style={{ fontFamily: "Noto Serif JP, serif", fontSize: "13px", fill: "#2E6E8E", letterSpacing: "0.06em" }}
        >
          オホーツク海
        </text>
        <text
          x={916} y={260} textAnchor="middle"
          style={{ fontFamily: "EB Garamond, Georgia, serif", fontStyle: "italic", fontSize: "9.5px", fill: "#6EB0C4" }}
        >
          Sea of Okhotsk
        </text>
        {/* 流氷 */}
        <text
          x={914} y={240} textAnchor="middle"
          style={{ fontFamily: "EB Garamond, Georgia, serif", fontStyle: "italic", fontSize: "8.5px", fill: "#6EB0C4", opacity: 0.72 }}
        >
          流氷（冬）
        </text>

        {/* 方位ラベル */}
        <text x={46} y={468} className="chart-label-muted" style={{ fill: "#8B6E47" }}>
          ← 源流（西）
        </text>
        <text x={858} y={468} className="chart-label-muted" style={{ fill: "#2E6E8E" }}>
          河口（東）→
        </text>
      </svg>
    </Figure>
  );
}
