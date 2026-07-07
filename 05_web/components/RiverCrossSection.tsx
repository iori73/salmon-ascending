import Figure from "./Figure";

/**
 * 図3　川の縦断面とシロザケの一生
 *
 * 事実への配慮（オーナー指摘に対応）:
 *  - シロザケ（Oncorhynchus keta）は高山源流ではなく、湧水のある
 *    下流〜中流の礫底に産卵する。図では産卵床を河口寄りの礫底に置く。
 *  - 稚魚は孵化後まもなく（春）降海する＝淡水滞在が短い。
 *  - 産卵後は死に、その死骸が海由来の栄養（窒素・リン）を森へ還す（MDN）。
 *  位置・段階は 02_research/ の検証済み記述に拠る。
 */

// ── サケのシルエット（右向き基準）。dir=-1 で遡上（左向き）に反転 ──
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
  // 66×22 のサケ体。鼻先(0,12)起点。
  const body =
    "M2,12 C6,5 18,3 30,4 C40,4 49,6 56,8 L66,1 L60,11 L66,21 C50,16 40,17 30,18 C18,19 8,17 2,12 Z";
  const dorsal = "M31,4 L37,-3 L42,4 Z";
  const adipose = "M50,7 L54,3 L56,7 Z";
  const analFin = "M24,18 L27,24 L31,18 Z";
  const kype = "M2,11 C-4,9 -6,13 -1,15 L5,13 C3,12 3,11 2,11 Z"; // 鈎吻（雄）
  return (
    <g
      transform={`translate(${x},${y}) scale(${(dir * s).toFixed(3)},${s})`}
      opacity={opacity}
      filter="url(#ink)"
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

export default function RiverCrossSection({ num = 1 }: { num?: number }) {
  const W = 960;
  const H = 520;

  // 川面（上流で高く、河口で海面へ。以降は外洋＝平らな水面） ───
  const surface =
    "M150,192 C 250,214 360,240 460,253 C 540,263 630,286 700,300 L960,300";
  // 河床（河口の先で外洋床へ落ち込む） ───
  const bed =
    "M150,208 C 250,230 360,256 460,267 C 540,276 630,300 700,312 C 745,316 770,340 805,388 C 850,440 905,464 960,470";
  // 大地（左の谷から右の外洋床まで連続。山もこの上に乗る＝継ぎ目をなくす） ───
  const ground =
    "M0,176 L150,208 C 250,230 360,256 460,267 C 540,276 630,300 700,312 C 745,316 770,340 805,388 C 850,440 905,464 960,470 L960,520 L0,520 Z";
  // 水のかたまり（川＋外洋を一塊で） ───
  const water =
    "M150,192 C 250,214 360,240 460,253 C 540,263 630,286 700,300 L960,300 L960,470 C 905,464 850,440 805,388 C 770,340 745,316 700,312 C 630,300 540,276 460,267 C 360,256 250,230 150,208 Z";

  return (
    <Figure
      num={num}
      title="川の縦断面とシロザケの一生"
      legend={
        <span className="inline-flex flex-wrap gap-x-4 gap-y-1">
          <span><span style={{ color: "#A83232" }}>●</span> 産卵する成魚（婚姻色）</span>
          <span><span style={{ color: "#2E6E8E" }}>●</span> 降海する稚魚</span>
          <span><span style={{ color: "#6EB0C4" }}>●</span> 外洋を回遊する成魚</span>
          <span><span style={{ color: "#C4722A" }}>●</span> 遡上する成魚</span>
        </span>
      }
      source={
        <>
          ライフステージは水産研究・教育機構ほかの記述に拠る。※シロザケは高山源流ではなく、
          湧水のある下流〜中流の礫底に産卵し、稚魚は春に降海する。
        </>
      }
    >
      <svg
        viewBox={`0 0 ${W} ${H}`}
        width={W}
        height={H}
        className="min-w-[680px] w-full h-auto"
        role="img"
        aria-label="川の縦断面図。左の源流の森から右の外洋へと川が下り、下流の湧水礫底の産卵床、稚魚の降海、外洋回遊、秋の産卵遡上、そして死後に栄養が森へ還る循環を示す。"
      >
        <defs>
          <filter id="ink" x="-6%" y="-6%" width="112%" height="112%">
            <feTurbulence type="fractalNoise" baseFrequency="0.016" numOctaves={2} seed={7} result="n" />
            <feDisplacementMap in="SourceGraphic" in2="n" scale={2.6} xChannelSelector="R" yChannelSelector="G" />
          </filter>
          <linearGradient id="waterGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#C8E0E8" stopOpacity={0.5} />
            <stop offset="55%" stopColor="#6EB0C4" stopOpacity={0.5} />
            <stop offset="100%" stopColor="#2E6E8E" stopOpacity={0.72} />
          </linearGradient>
          <marker id="ar" markerWidth={7} markerHeight={7} refX={5} refY={3} orient="auto">
            <path d="M0,0 L6,3 L0,6 Z" fill="#8B6E47" />
          </marker>
          <marker id="arRust" markerWidth={8} markerHeight={8} refX={6} refY={3.5} orient="auto">
            <path d="M0,0 L7,3.5 L0,7 Z" fill="#C4722A" />
          </marker>
        </defs>

        {/* 空 */}
        <rect x={0} y={0} width={W} height={H} fill="#F2F7F8" />

        {/* 遠景の山並み（源流の森。ground の上に乗せて継ぎ目をなくす） */}
        <g filter="url(#ink)">
          <path
            d="M0,176 C 50,108 92,92 132,118 C 168,140 206,92 250,100 C 292,108 322,162 372,252 L372,300 L0,300 Z"
            fill="#8B6E47"
            opacity={0.12}
          />
          <path
            d="M0,176 C 44,128 86,112 124,134 C 162,156 198,116 240,126 C 280,135 312,170 352,246 L352,300 L0,300 Z"
            fill="#8B6E47"
            opacity={0.2}
          />
        </g>

        {/* 大地（連続） */}
        <path d={ground} fill="#D8C7A6" opacity={0.6} />
        <path d={ground} fill="none" stroke="#8B6E47" strokeWidth={1.4} opacity={0.35} filter="url(#ink)" />

        {/* 針葉樹の森 */}
        {[64, 86, 108, 132].map((tx, i) => (
          <g key={i} transform={`translate(${tx},${158 - (i % 2) * 6})`} opacity={0.5} filter="url(#ink)">
            <path d="M0,18 L6,0 L12,18 Z" fill="#3D2B1A" />
            <line x1={6} y1={18} x2={6} y2={22} stroke="#3D2B1A" strokeWidth={1} />
          </g>
        ))}

        {/* ヒグマ（森の縁。死後の栄養を運ぶ生態系の担い手） */}
        <g transform="translate(168,150)" opacity={0.78} filter="url(#ink)">
          <path
            d="M2,30 C0,21 3,14 11,12 C11,6 17,5 19,9 C23,5 29,7 29,13 C39,14 44,20 44,29 L40,30 L38,25 L34,30 L13,30 L11,25 L7,30 Z"
            fill="#3D2B1A"
          />
        </g>

        {/* 水 */}
        <path d={water} fill="url(#waterGrad)" />
        <path d={surface} fill="none" stroke="#6EB0C4" strokeWidth={1.4} opacity={0.7} filter="url(#ink)" />
        <path d={bed} fill="none" stroke="#8B6E47" strokeWidth={1.8} strokeLinecap="round" filter="url(#ink)" />

        {/* 外洋ラベル */}
        <text x={872} y={324} textAnchor="middle" className="chart-label" style={{ fill: "#2E6E8E", fontStyle: "italic" }}>外洋</text>
        <text x={872} y={339} textAnchor="middle" className="chart-label-muted">北太平洋</text>

        {/* ── 産卵床（下流寄りの湧水礫底）── */}
        <g>
          {[
            [432, 270], [447, 273], [462, 270], [477, 274], [492, 271],
            [440, 277], [470, 278], [500, 276], [455, 267], [485, 267],
          ].map(([gx, gy], i) => (
            <circle key={i} cx={gx} cy={gy} r={2.6 + (i % 3)} fill="#9b8a66" opacity={0.75} />
          ))}
          {[[460, 273], [466, 275], [472, 273], [463, 277], [469, 278]].map(([ex, ey], i) => (
            <circle key={`e${i}`} cx={ex} cy={ey} r={1.7} fill="#E8896A" />
          ))}
          {/* 湧水 */}
          {[0, 1, 2].map((i) => (
            <line key={`v${i}`} x1={446 + i * 20} y1={288} x2={446 + i * 20} y2={272}
              stroke="#6EB0C4" strokeWidth={1} strokeDasharray="2,2" markerEnd="url(#ar)" opacity={0.55} />
          ))}
          {/* 産卵する成魚（対） */}
          <Salmon x={416} y={250} s={1.05} dir={-1} color="#A83232" spawning />
          <Salmon x={500} y={256} s={1.0} dir={1} color="#A83232" spawning opacity={0.9} />
          {/* 注記（leader を上の空へ） */}
          <line x1={460} y1={244} x2={460} y2={150} stroke="#6B6B5F" strokeWidth={0.7} />
          <text x={460} y={140} textAnchor="middle" className="chart-label" style={{ fill: "#A83232" }}>産卵床</text>
          <text x={460} y={126} textAnchor="middle" className="chart-label-muted">湧水のある礫底</text>
        </g>

        {/* ── 稚魚の降海（春） ── */}
        <g>
          <Salmon x={566} y={280} s={0.4} dir={1} color="#2E6E8E" opacity={0.85} />
          <Salmon x={590} y={286} s={0.38} dir={1} color="#2E6E8E" opacity={0.68} />
          <Salmon x={613} y={283} s={0.36} dir={1} color="#2E6E8E" opacity={0.52} />
          <text x={592} y={250} textAnchor="middle" className="chart-label" style={{ fill: "#2E6E8E" }}>稚魚・降海（春）</text>
          <line x1={592} y1={256} x2={592} y2={272} stroke="#2E6E8E" strokeWidth={0.7} opacity={0.5} />
        </g>

        {/* ── 産卵遡上（秋）：外洋から産卵床へ ── */}
        <g>
          <path
            d="M812,360 C 720,326 650,318 560,308 C 528,304 505,298 486,290"
            fill="none" stroke="#C4722A" strokeWidth={1.4} strokeDasharray="7,5"
            markerEnd="url(#arRust)" opacity={0.8} filter="url(#ink)"
          />
          <Salmon x={668} y={300} s={1.0} dir={-1} color="#C4722A" />
          <text x={690} y={334} textAnchor="middle" className="chart-label" style={{ fill: "#C4722A" }}>産卵遡上（秋）</text>
        </g>

        {/* ── 外洋回遊（2〜5年） ── */}
        <g>
          <Salmon x={812} y={392} s={1.12} dir={1} color="#6EB0C4" />
          <Salmon x={846} y={416} s={0.95} dir={-1} color="#6EB0C4" opacity={0.78} />
          <text x={846} y={378} textAnchor="middle" className="chart-label" style={{ fill: "#2E6E8E" }}>外洋回遊</text>
          <text x={846} y={392} textAnchor="middle" className="chart-label-muted">2〜5年</text>
        </g>

        {/* ── 死後：森へ栄養（MDN）── */}
        <g>
          {/* 産卵床 → 森への栄養の還流（1本だけ、控えめに） */}
          <path
            d="M424,256 C 360,250 280,220 212,182"
            fill="none" stroke="#8B6E47" strokeWidth={1.1} strokeDasharray="5,4"
            markerEnd="url(#ar)" opacity={0.5} filter="url(#ink)"
          />
          {/* 説明は左下の大地の余白へ */}
          <text x={150} y={430} textAnchor="start" className="chart-label" style={{ fill: "#6b5a3f" }}>
            死後、栄養が森へ還る
          </text>
          <text x={150} y={446} textAnchor="start" className="chart-label-muted" style={{ fill: "#6b5a3f" }}>
            海由来の窒素・リン → 熊・鳥・微生物
          </text>
        </g>

        {/* 方位ラベル */}
        <text x={20} y={508} className="chart-label-muted" style={{ fill: "#8B6E47" }}>← 源流（上流）</text>
        <text x={830} y={508} className="chart-label-muted" style={{ fill: "#2E6E8E" }}>外洋（下流）→</text>
      </svg>
    </Figure>
  );
}
