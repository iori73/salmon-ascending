import Figure from "./Figure";

/**
 * 図（Act2）　ふたつの海
 * 北太平洋を回遊する在来のシロザケ（青）と、北大西洋＝ノルウェーから渡来した
 * 養殖アトランティックサーモン（金）が、日本の食卓で交差する——を北極中心の
 * 正距方位図法の模式図で示す。
 *
 * 事実への配慮:
 *  - シロザケ(O. keta)は北太平洋・オホーツク海・ベーリング海を回遊する在来種。
 *  - アトランティックサーモン(Salmo salar)は大西洋原産で太平洋には自然分布しない。
 *  - 2023年の対日輸出は24,000トン（世界13位・アジア3位）。
 *  - ※輸送手段の内訳・Project Japanの具体的経緯は未検証（継続調査中）。地図は模式。
 */

const cx = 470;
const cy = 320;
const R = 248;
const k = R / 65;

function project(lat: number, lng: number) {
  const r = Math.min(R, k * (90 - lat));
  const a = (lng * Math.PI) / 180;
  return { x: cx + r * Math.sin(a), y: cy - r * Math.cos(a) };
}

export default function TwoOceansMap({ num = 1 }: { num?: number }) {
  const W = 940;
  const H = 660;
  const norway = project(62, 12);
  const japan = project(40, 140);

  return (
    <Figure
      num={num}
      title="ふたつの海 — 北太平洋のシロザケと、北大西洋のアトランティックサーモン"
      legend={
        <span className="inline-flex flex-wrap gap-x-4 gap-y-1">
          <span><span style={{ color: "#2E6E8E" }}>―</span> シロザケの海洋回遊（在来・北太平洋）</span>
          <span><span style={{ color: "#D4A847" }}>―</span> ノルウェーからの輸出（養殖・北大西洋）</span>
        </span>
      }
      source={
        <>
          2023年の対日輸出24,000トン（世界第13位・アジア第3位）。正距方位図法の模式図。
          ※輸送手段の内訳・Project Japanの具体的経緯は継続調査中。
        </>
      }
    >
      <svg
        viewBox={`0 0 ${W} ${H}`}
        width={W}
        height={H}
        className="w-full h-auto min-w-[640px]"
        role="img"
        aria-label="北極を中心とした北半球の模式地図。北太平洋を回遊する在来のシロザケと、北大西洋のノルウェーから渡来する養殖アトランティックサーモンが、日本で交差することを示す。"
      >
        <defs>
          <filter id="inkMap" x="-5%" y="-5%" width="110%" height="110%">
            <feTurbulence type="fractalNoise" baseFrequency="0.013" numOctaves={2} seed={11} result="n" />
            <feDisplacementMap in="SourceGraphic" in2="n" scale={2.2} xChannelSelector="R" yChannelSelector="G" />
          </filter>
          <radialGradient id="ocean" cx="50%" cy="46%" r="55%">
            <stop offset="0%" stopColor="#E6F0F3" />
            <stop offset="100%" stopColor="#D4E6EC" />
          </radialGradient>
          <clipPath id="hemi"><circle cx={cx} cy={cy} r={R} /></clipPath>
          <marker id="mTeal" markerWidth={8} markerHeight={8} refX={6} refY={3.5} orient="auto">
            <path d="M0,0 L7,3.5 L0,7 Z" fill="#2E6E8E" />
          </marker>
          <marker id="mGold" markerWidth={9} markerHeight={9} refX={6.5} refY={4} orient="auto">
            <path d="M0,0 L8,4 L0,8 Z" fill="#B8902F" />
          </marker>
        </defs>

        {/* 海 */}
        <circle cx={cx} cy={cy} r={R} fill="url(#ocean)" stroke="#8B6E47" strokeWidth={1.1} />

        {/* 経緯線 */}
        <g opacity={0.22}>
          {[60, 35].map((lat) => (
            <circle key={lat} cx={cx} cy={cy} r={k * (90 - lat)} fill="none" stroke="#8B6E47" strokeWidth={0.5} strokeDasharray="2,4" />
          ))}
          {[0, 45, 90, 135, 180, 225, 270, 315].map((lng) => {
            const p = project(25, lng);
            return <line key={lng} x1={cx} y1={cy} x2={p.x} y2={p.y} stroke="#8B6E47" strokeWidth={0.4} strokeDasharray="2,4" />;
          })}
        </g>

        {/* 陸地（背景として淡く） */}
        <g clipPath="url(#hemi)" filter="url(#inkMap)">
          {/* ユーラシア：北欧→シベリア→東アジア */}
          <path
            d="M 470,98 C 500,116 492,142 514,156 C 560,150 556,196 532,214
               C 596,236 636,300 592,356 C 624,398 604,452 566,478
               C 540,460 520,452 504,468 C 486,442 492,408 472,392
               C 462,352 472,304 466,260 C 452,212 456,150 470,110 Z"
            fill="#D8C7A6"
            stroke="#a78f63"
            strokeWidth={0.8}
            opacity={0.5}
          />
          {/* 北米：アラスカ→カナダ→グリーンランド */}
          <path
            d="M 466,300 C 470,338 452,372 430,392 C 446,404 438,424 416,420
               C 388,408 374,372 392,346 C 360,338 350,300 372,278
               C 404,266 430,256 440,276 C 450,244 466,256 466,300 Z"
            fill="#D8C7A6"
            stroke="#a78f63"
            strokeWidth={0.8}
            opacity={0.42}
          />
        </g>

        {/* 日本列島（小さな島群） */}
        <g filter="url(#inkMap)">
          <path d={`M ${japan.x - 4},${japan.y - 14} C ${japan.x + 6},${japan.y - 6} ${japan.x + 8},${japan.y + 6} ${japan.x + 2},${japan.y + 14} C ${japan.x - 4},${japan.y + 6} ${japan.x - 8},${japan.y - 4} ${japan.x - 4},${japan.y - 14} Z`} fill="#8B6E47" opacity={0.6} />
          <ellipse cx={japan.x + 12} cy={japan.y + 20} rx={4} ry={7} fill="#8B6E47" opacity={0.5} transform={`rotate(28 ${japan.x + 12} ${japan.y + 20})`} />
        </g>

        {/* 海域ラベル */}
        <text x={392} y={222} textAnchor="middle" className="chart-label" style={{ fill: "#2E6E8E", fontStyle: "italic" }}>北大西洋</text>
        <text x={486} y={520} textAnchor="middle" className="chart-label" style={{ fill: "#2E6E8E", fontStyle: "italic" }}>北太平洋</text>

        {/* シロザケの海洋回遊ループ（北太平洋・円内） */}
        <path
          d={`M ${japan.x},${japan.y + 2} C 636,512 548,556 472,544 C 406,534 386,498 412,468 C 442,442 470,460 ${japan.x - 6},${japan.y + 6}`}
          fill="none"
          stroke="#2E6E8E"
          strokeWidth={2}
          strokeDasharray="8,5"
          markerEnd="url(#mTeal)"
          opacity={0.85}
          filter="url(#inkMap)"
        />
        <text x={486} y={538} textAnchor="middle" className="chart-label-muted">回遊（2〜5年）</text>

        {/* ノルウェー → 日本 の輸出ルート（金） */}
        <path
          d={`M ${norway.x},${norway.y} C 580,212 668,300 666,372 C 664,428 632,452 ${japan.x + 9},${japan.y - 7}`}
          fill="none"
          stroke="#D4A847"
          strokeWidth={2.2}
          markerEnd="url(#mGold)"
          opacity={0.95}
          filter="url(#inkMap)"
        />

        {/* ノルウェー */}
        <circle cx={norway.x} cy={norway.y} r={4} fill="#B8902F" />
        <text x={norway.x + 9} y={norway.y - 6} className="chart-label" style={{ fill: "#8B6E47" }}>ノルウェー</text>
        <text x={norway.x + 9} y={norway.y + 8} className="chart-label-muted">養殖アトランティックサーモン</text>

        {/* 日本＝交差点 */}
        <g>
          <circle cx={japan.x} cy={japan.y} r={13} fill="none" stroke="#A83232" strokeWidth={1.2} opacity={0.65} />
          <circle cx={japan.x} cy={japan.y} r={4.5} fill="#A83232" />
          <text x={japan.x + 18} y={japan.y - 2} className="chart-label" style={{ fill: "#A83232" }}>日本</text>
          <text x={japan.x + 18} y={japan.y + 12} className="chart-label-muted">同じ皿の上で交差する</text>
        </g>

        {/* 方位（N） */}
        <g opacity={0.6}>
          <line x1={cx} y1={cy - R - 4} x2={cx} y2={cy - R + 14} stroke="#8B6E47" strokeWidth={0.8} />
          <text x={cx} y={cy - R - 8} textAnchor="middle" className="chart-label-muted" style={{ fill: "#8B6E47" }}>N</text>
        </g>
      </svg>
    </Figure>
  );
}
