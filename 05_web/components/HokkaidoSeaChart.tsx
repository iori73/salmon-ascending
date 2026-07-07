import Figure from "./Figure";

const data = [
  { year: 2022, count: 607 },
  { year: 2023, count: 202 },
  { year: 2024, count: 119, isLowest: true },
];

const W = 560;
const H = 280;
const PAD = { top: 30, right: 40, bottom: 56, left: 64 };
const innerW = W - PAD.left - PAD.right;
const innerH = H - PAD.top - PAD.bottom;
const barW = 78;
const maxVal = 650;

const barX = (i: number) => PAD.left + (i * innerW) / data.length + (innerW / data.length - barW) / 2;
const barH = (v: number) => (v / maxVal) * innerH;
const barY = (v: number) => PAD.top + innerH - barH(v);

export default function HokkaidoSeaChart({ num = 3 }: { num?: number }) {
  return (
    <Figure
      num={num}
      title="北海道日本海地区サケ来遊数の推移（万尾）"
      source={<>水産研究・教育機構「令和7年度サケ来遊状況報告」（2025年8月公表）</>}
    >
      <svg
        viewBox={`0 0 ${W} ${H}`}
        width={W}
        height={H}
        className="w-full h-auto min-w-[440px]"
        role="img"
        aria-label="北海道日本海地区のサケ来遊数は2022年607万尾から2024年119万尾へ減少し、1990年以降で最低。"
      >
        <defs>
          <filter id="inkBar" x="-10%" y="-6%" width="120%" height="112%">
            <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves={2} seed={9} result="n" />
            <feDisplacementMap in="SourceGraphic" in2="n" scale={1.8} xChannelSelector="R" yChannelSelector="G" />
          </filter>
        </defs>

        {/* 目盛り */}
        {[0, 200, 400, 600].map((v) => {
          const y = barY(v);
          return (
            <g key={v}>
              <line x1={PAD.left} y1={y} x2={PAD.left + innerW} y2={y} stroke="#D4D0C8" strokeWidth={0.5} strokeDasharray="2,4" />
              <text x={PAD.left - 10} y={y + 4} textAnchor="end" className="chart-label-muted">{v}</text>
            </g>
          );
        })}

        {/* 棒 */}
        {data.map((d, i) => {
          const x = barX(i);
          const y = barY(d.count);
          const h = barH(d.count);
          const fill = d.isLowest ? "#A83232" : "#2E6E8E";
          return (
            <g key={d.year}>
              <rect x={x} y={y} width={barW} height={h} fill={fill} opacity={d.isLowest ? 0.82 : 0.68} filter="url(#inkBar)" />
              <text x={x + barW / 2} y={y - 9} textAnchor="middle" className="chart-label" style={{ fontWeight: 600 }}>{d.count}万尾</text>
              <text x={x + barW / 2} y={PAD.top + innerH + 20} textAnchor="middle" className="chart-label">{d.year}</text>
              {d.isLowest && (
                <text x={x + barW / 2} y={PAD.top + innerH + 36} textAnchor="middle" className="chart-label-muted" style={{ fill: "#A83232" }}>
                  1990年以降で最低
                </text>
              )}
            </g>
          );
        })}

        <line x1={PAD.left} y1={PAD.top + innerH} x2={PAD.left + innerW} y2={PAD.top + innerH} stroke="#2A2A2A" strokeWidth={0.6} />
      </svg>
    </Figure>
  );
}
