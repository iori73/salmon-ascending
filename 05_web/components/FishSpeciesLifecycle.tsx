import Figure from "./Figure";

/**
 * 図　3種のサケ・マスの生活史 ― 川と海、どこで時を過ごすか
 *
 * 北海道に来るサケ属3種（シロザケ・カラフトマス・サクラマス）の生活史を、
 * 円環の「時計」として並べて比較する。
 *  - リングの大きさ ＝ 寿命（カラフトマス2年 < サクラマス3年 < シロザケ最長）
 *  - 弧の長さ        ＝ その環境（川／海）での滞在時間の比
 *
 * 数値は HRO さけます・内水面水産試験場「3種の生活史」図に拠る:
 *  - シロザケ   : 産卵9–12月 / ふ化・浮上1–4月 / 降海3–6月 / 海洋 1年半〜6年半
 *  - カラフトマス: 産卵8–10月 / ふ化11–1月 / 降海2–4月 / 川 半年・海 1年半（2年で一生）
 *  - サクラマス : 産卵9–10月 / ふ化12–1月 / 浮上3–4月 / 河川 約1年・海 約1年（雄の一部は残留＝ヤマメ）
 */

// ── サケのシルエット（右向き基準）。dir=-1 で反転（RiverCrossSection と共通の体型）──
function Salmon({
  x,
  y,
  s = 1,
  dir = 1,
  color = "#2E6E8E",
  spawning = false,
  opacity = 1,
}: {
  x: number;
  y: number;
  s?: number;
  dir?: 1 | -1;
  color?: string;
  spawning?: boolean;
  opacity?: number;
}) {
  const body =
    "M2,12 C6,5 18,3 30,4 C40,4 49,6 56,8 L66,1 L60,11 L66,21 C50,16 40,17 30,18 C18,19 8,17 2,12 Z";
  const dorsal = "M31,4 L37,-3 L42,4 Z";
  const adipose = "M50,7 L54,3 L56,7 Z";
  const analFin = "M24,18 L27,24 L31,18 Z";
  const kype = "M2,11 C-4,9 -6,13 -1,15 L5,13 C3,12 3,11 2,11 Z";
  return (
    <g
      transform={`translate(${x},${y}) scale(${(dir * s).toFixed(3)},${s})`}
      opacity={opacity}
      filter="url(#ink-life)"
    >
      <path d={body} fill={color} stroke={color} strokeWidth={0.5} />
      <path d={dorsal} fill={color} />
      <path d={adipose} fill={color} />
      <path d={analFin} fill={color} />
      {spawning && (
        <>
          <path d={kype} fill={color} />
          <ellipse cx={28} cy={11} rx={10} ry={3.2} fill="#7a1f1f" opacity={0.4} />
        </>
      )}
      <circle cx={9} cy={10} r={1.3} fill="#fafaf6" />
      <circle cx={9} cy={10} r={0.7} fill="#2a2a2a" />
    </g>
  );
}

// 極座標（deg: 0=東/3時, -90=上/12時, 時計回りに増加）
function pol(cx: number, cy: number, r: number, deg: number): [number, number] {
  const a = (deg * Math.PI) / 180;
  return [cx + r * Math.cos(a), cy + r * Math.sin(a)];
}
// 円弧パス（start→end を時計回り sweep=1）
function arc(cx: number, cy: number, r: number, start: number, end: number) {
  const [x1, y1] = pol(cx, cy, r, start);
  const [x2, y2] = pol(cx, cy, r, end);
  const large = end - start > 180 ? 1 : 0;
  return `M${x1.toFixed(2)},${y1.toFixed(2)} A${r},${r} 0 ${large} 1 ${x2.toFixed(2)},${y2.toFixed(2)}`;
}

const OCHRE = "#8b6e47"; // 川（淡水）
const TEAL = "#2e6e8e"; // 海（海洋）
const TEALMID = "#6eb0c4";
const SPAWN = "#a83232";
const RUST = "#c4722a";

type Stage = { deg: number; main: string; sub?: string };
type Species = {
  key: string;
  cx: number;
  name: string;
  sci: string;
  r: number;
  fr: number; // 川（淡水）が占める弧の比
  stats: string[];
  stages: Stage[];
};

export default function FishSpeciesLifecycle({ num = 2 }: { num?: number }) {
  const W = 1020;
  const H = 500;
  const CY = 212;

  const species: Species[] = [
    {
      key: "keta",
      cx: 178,
      name: "シロザケ",
      sci: "O. keta",
      r: 104,
      fr: 0.15,
      stats: ["海 1.5〜6.5 年", "川 数週間", "最も遠く長く回遊"],
      stages: [
        { deg: -90, main: "産卵", sub: "9〜12月" },
        { deg: -63, main: "ふ化", sub: "1〜4月" },
        { deg: -36, main: "降海", sub: "3〜6月" },
        { deg: 145, main: "海洋で成長", sub: "1.5〜6.5年" },
        { deg: 222, main: "回帰", sub: "秋" },
      ],
    },
    {
      key: "gorbuscha",
      cx: 510,
      name: "カラフトマス",
      sci: "O. gorbuscha",
      r: 74,
      fr: 0.25,
      stats: ["2 年で一生", "川 半年 / 海 1年半", "奇数年に多い"],
      stages: [
        { deg: -90, main: "産卵", sub: "8〜10月" },
        { deg: -45, main: "ふ化", sub: "11〜1月" },
        { deg: 0, main: "降海", sub: "2〜4月" },
        { deg: 150, main: "海洋で成長", sub: "1年半" },
        { deg: 224, main: "回帰", sub: "2年目" },
      ],
    },
    {
      key: "masou",
      cx: 842,
      name: "サクラマス",
      sci: "O. masou",
      r: 90,
      fr: 0.5,
      stats: ["河川に 約1年", "海 約1年", "一部はヤマメに"],
      stages: [
        { deg: -90, main: "産卵", sub: "9〜10月" },
        { deg: -36, main: "ふ化・浮上", sub: "12〜4月" },
        { deg: 56, main: "河川生活", sub: "約1年" },
        { deg: 96, main: "降海", sub: "" },
        { deg: 158, main: "海洋で成長", sub: "約1年" },
        { deg: 224, main: "回帰", sub: "春" },
      ],
    },
  ];

  return (
    <Figure
      num={num}
      title="3種のサケ・マスの生活史 ― 川と海、どこで時を過ごすか"
      legend={
        <span className="inline-flex flex-wrap gap-x-4 gap-y-1">
          <span><span style={{ color: OCHRE }}>●</span> 川（淡水）にいる時間</span>
          <span><span style={{ color: TEAL }}>●</span> 海（海洋）にいる時間</span>
          <span style={{ color: "var(--fg-faint)" }}>リングの大きさ＝寿命／弧の長さ＝その環境での滞在</span>
        </span>
      }
      source={
        <>
          北海道立総合研究機構 さけます・内水面水産試験場「サケ・カラフトマス・サクラマスの生活史」図に拠る。
          サクラマスは雄の一部が降海せず河川に残留し（ヤマメ）、産卵に参加する。
        </>
      }
    >
      <svg
        viewBox={`0 0 ${W} ${H}`}
        width={W}
        height={H}
        className="min-w-[760px] w-full h-auto"
        role="img"
        aria-label="サケ属3種（シロザケ・カラフトマス・サクラマス）の生活史を円環で比較した図。リングの大きさが寿命を、弧の長さが川と海それぞれの滞在時間を表す。シロザケは海で1年半から6年半と最も長く広く回遊し、カラフトマスは川半年・海1年半の2年で一生を終え、サクラマスは河川で約1年・海で約1年を過ごし雄の一部は川に残る。"
      >
        <defs>
          <filter id="ink-life" x="-6%" y="-6%" width="112%" height="112%">
            <feTurbulence type="fractalNoise" baseFrequency="0.016" numOctaves={2} seed={5} result="n" />
            <feDisplacementMap in="SourceGraphic" in2="n" scale={2.4} xChannelSelector="R" yChannelSelector="G" />
          </filter>
          <marker id="lifeArrowTeal" markerUnits="userSpaceOnUse" markerWidth={15} markerHeight={13} refX={10} refY={6.5} orient="auto">
            <path d="M0,0 L13,6.5 L0,13 Z" fill={TEAL} />
          </marker>
          <marker id="lifeArrowOchre" markerUnits="userSpaceOnUse" markerWidth={15} markerHeight={13} refX={10} refY={6.5} orient="auto">
            <path d="M0,0 L13,6.5 L0,13 Z" fill={OCHRE} />
          </marker>
        </defs>

        <rect x={0} y={0} width={W} height={H} fill="#F2F7F8" />

        {species.map((sp) => {
          const riverEnd = -90 + sp.fr * 360;
          const oceanEnd = 270; // = -90 + 360
          // 円環の薄い土台
          const baseRing = arc(sp.cx, CY, sp.r, -90, 269.9);
          return (
            <g key={sp.key}>
              {/* 土台リング */}
              <path d={baseRing} fill="none" stroke="#d9d2c4" strokeWidth={11} strokeLinecap="round" opacity={0.5} />
              {/* 川（淡水）弧 */}
              <path
                d={arc(sp.cx, CY, sp.r, -90, riverEnd)}
                fill="none"
                stroke={OCHRE}
                strokeWidth={11}
                strokeLinecap="round"
                markerEnd="url(#lifeArrowOchre)"
                filter="url(#ink-life)"
              />
              {/* 海（海洋）弧 */}
              <path
                d={arc(sp.cx, CY, sp.r, riverEnd, oceanEnd)}
                fill="none"
                stroke={TEAL}
                strokeWidth={11}
                strokeLinecap="round"
                markerEnd="url(#lifeArrowTeal)"
                opacity={0.92}
                filter="url(#ink-life)"
              />

              {/* 段階ラベル */}
              {sp.stages.map((st, i) => {
                const [lx, ly] = pol(sp.cx, CY, sp.r + 26, st.deg);
                const cos = Math.cos((st.deg * Math.PI) / 180);
                const anchor = Math.abs(cos) < 0.34 ? "middle" : cos > 0 ? "start" : "end";
                const onRiver = st.deg <= riverEnd + 0.01;
                return (
                  <g key={i}>
                    <text
                      x={lx}
                      y={ly}
                      textAnchor={anchor}
                      className="chart-label"
                      style={{ fill: onRiver ? "#6b5a3f" : TEAL }}
                    >
                      {st.main}
                    </text>
                    {st.sub && (
                      <text x={lx} y={ly + 13} textAnchor={anchor} className="chart-label-muted">
                        {st.sub}
                      </text>
                    )}
                  </g>
                );
              })}

              {/* 魚シルエット：産卵（上・婚姻色）／降海（小・teal）／海洋（中・teal-mid） */}
              {(() => {
                const [sx, sy] = pol(sp.cx, CY, sp.r, -90);
                const [dx, dy] = pol(sp.cx, CY, sp.r, riverEnd);
                const [ox, oy] = pol(sp.cx, CY, sp.r, 150);
                return (
                  <>
                    <Salmon x={sx - 16} y={sy - 6} s={0.46} dir={-1} color={SPAWN} spawning />
                    <Salmon x={dx - 9} y={dy - 4} s={0.3} dir={1} color={TEAL} opacity={0.85} />
                    <Salmon x={ox - 26} y={oy - 9} s={0.74} dir={-1} color={TEALMID} />
                  </>
                );
              })()}

              {/* 中心：和名＋学名＋キースタッツ */}
              <text x={sp.cx} y={CY - 16} textAnchor="middle" className="chart-label" style={{ fontSize: 15, fontWeight: 600, fill: "#2a2a2a" }}>
                {sp.name}
              </text>
              <text x={sp.cx} y={CY - 1} textAnchor="middle" className="chart-label-muted" style={{ fontStyle: "italic", fontFamily: "var(--garamond)" }}>
                {sp.sci}
              </text>
              {sp.stats.map((s, i) => (
                <text
                  key={i}
                  x={sp.cx}
                  y={CY + 16 + i * 13}
                  textAnchor="middle"
                  className="chart-label-muted"
                  style={{ fill: i === 0 ? RUST : "#6b6b5f" }}
                >
                  {s}
                </text>
              ))}
            </g>
          );
        })}

        {/* 下部の横断サマリ */}
        <g>
          <line x1={70} y1={H - 54} x2={W - 70} y2={H - 54} stroke="var(--hairline)" strokeWidth={1} />
          <text x={70} y={H - 32} className="chart-label" style={{ fill: "#6b5a3f" }}>
            川にいる時間：サクラマス（約1年）≫ カラフトマス（半年）≧ シロザケ（数週間）
          </text>
          <text x={70} y={H - 14} className="chart-label" style={{ fill: TEAL }}>
            海にいる時間・寿命：シロザケ（最長・最も遠く回遊）＞ サクラマス ＞ カラフトマス（2年で一生）
          </text>
        </g>
      </svg>
    </Figure>
  );
}
