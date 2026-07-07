import Figure from "./Figure";

const data = [
  { year: 2022, count: 587475, label: "587,475" },
  { year: 2023, count: 328272, label: "328,272" },
  { year: 2024, count: 161276, label: "161,276" },
  { year: 2025, count: 67283, label: "67,283*" },
];

const fiveYearAvg = 346671;

const W = 720;
const H = 320;
const PAD = { top: 36, right: 70, bottom: 56, left: 78 };
const innerW = W - PAD.left - PAD.right;
const innerH = H - PAD.top - PAD.bottom;
const maxVal = 650000;

const scaleX = (i: number) => PAD.left + (i / (data.length - 1)) * innerW;
const scaleY = (v: number) => PAD.top + innerH - (v / maxVal) * innerH;

export default function SalmonRunChart({ num = 2 }: { num?: number }) {
  const points = data.map((d, i) => `${scaleX(i)},${scaleY(d.count)}`).join(" ");
  const avgY = scaleY(fiveYearAvg);
  const gridVals = [0, 200000, 400000, 600000];

  return (
    <Figure
      num={num}
      title="千歳川サケ捕獲数の推移（尾）"
      source={
        <>
          千歳水族館（サケのふるさと千歳水族館）公式捕獲統計。*2025年は12月5日時点の暫定値。
        </>
      }
    >
      <svg
        viewBox={`0 0 ${W} ${H}`}
        width={W}
        height={H}
        className="w-full h-auto min-w-[560px]"
        role="img"
        aria-label="千歳川のサケ捕獲数は2022年の587,475尾から2024年の161,276尾へ72.6%減少し、2025年暫定値は67,283尾とさらに低い。"
      >
        <defs>
          <filter id="inkLine" x="-3%" y="-10%" width="106%" height="120%">
            <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves={2} seed={4} result="n" />
            <feDisplacementMap in="SourceGraphic" in2="n" scale={2.2} xChannelSelector="R" yChannelSelector="G" />
          </filter>
        </defs>

        {/* グリッド（最小限） */}
        {gridVals.map((v) => {
          const y = scaleY(v);
          return (
            <g key={v}>
              <line x1={PAD.left} y1={y} x2={PAD.left + innerW} y2={y} stroke="#D4D0C8" strokeWidth={0.5} strokeDasharray="2,4" />
              <text x={PAD.left - 10} y={y + 4} textAnchor="end" className="chart-label-muted">
                {v === 0 ? "0" : `${v / 10000}万`}
              </text>
            </g>
          );
        })}

        {/* 5年平均 */}
        <line x1={PAD.left} y1={avgY} x2={PAD.left + innerW} y2={avgY} stroke="#8B6E47" strokeWidth={1} strokeDasharray="6,4" opacity={0.6} />
        <text x={PAD.left + innerW + 6} y={avgY + 4} className="chart-label-muted" style={{ fill: "#8B6E47" }}>5年平均</text>

        {/* 面 */}
        <polygon points={`${scaleX(0)},${scaleY(0)} ${points} ${scaleX(data.length - 1)},${scaleY(0)}`} fill="#2E6E8E" opacity={0.06} />

        {/* 折れ線（手描き質感） */}
        <polyline points={points} fill="none" stroke="#2E6E8E" strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round" filter="url(#inkLine)" />

        {/* データ点・値 */}
        {data.map((d, i) => {
          const x = scaleX(i);
          const y = scaleY(d.count);
          return (
            <g key={d.year}>
              <circle cx={x} cy={y} r={4} fill="#2E6E8E" />
              <text x={x} y={y - 14} textAnchor="middle" className="chart-label" style={{ fontWeight: 600 }}>
                {d.label}
              </text>
              <text x={x} y={PAD.top + innerH + 20} textAnchor="middle" className="chart-label">{d.year}</text>
            </g>
          );
        })}

        {/* 72.6%減の注記（2022→2024） */}
        <g>
          <path
            d={`M${scaleX(0)},${scaleY(587475) - 26} C ${scaleX(1)},${scaleY(587475) - 40} ${scaleX(1.6)},${scaleY(161276) - 44} ${scaleX(2)},${scaleY(161276) - 26}`}
            fill="none" stroke="#A83232" strokeWidth={0.9} strokeDasharray="3,3" opacity={0.7}
          />
          <text x={scaleX(1)} y={scaleY(587475) - 44} textAnchor="middle" className="chart-label" style={{ fill: "#A83232", fontWeight: 600 }}>
            2年で −72.6%
          </text>
        </g>

        {/* X軸 */}
        <line x1={PAD.left} y1={PAD.top + innerH} x2={PAD.left + innerW} y2={PAD.top + innerH} stroke="#2A2A2A" strokeWidth={0.6} />
      </svg>
    </Figure>
  );
}
