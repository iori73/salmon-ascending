import Figure from "./Figure";

type TLEvent = { year: number; label: string; side: "top" | "bottom"; color: string; major?: boolean };

const events: TLEvent[] = [
  { year: 1970, label: "日本に生サーモン食なし", side: "top", color: "#8B6E47" },
  { year: 1985, label: "ノルウェー、対日マーケティング開始", side: "bottom", color: "#C4722A", major: true },
  { year: 1991, label: "大手スーパーに生サーモン定着", side: "top", color: "#C4722A" },
  { year: 2000, label: "回転寿司に広がる", side: "bottom", color: "#2E6E8E" },
  { year: 2013, label: "寿司ネタ人気No.1に", side: "top", color: "#2E6E8E", major: true },
  { year: 2023, label: "対日輸出 24,000トン", side: "bottom", color: "#2E6E8E" },
];

const W = 760;
const H = 220;
const PAD = { left: 48, right: 48 };
const axisY = H / 2;
const startYear = 1966;
const endYear = 2028;
const span = endYear - startYear;
const innerW = W - PAD.left - PAD.right;
const xPos = (year: number) => PAD.left + ((year - startYear) / span) * innerW;

export default function ConsumptionTimeline({ num = 1 }: { num?: number }) {
  return (
    <Figure
      num={num}
      title="日本におけるサーモン消費の変遷"
      source={<>Seafood Norway公開情報および各種報道をもとに作成。1985年前後の具体的経緯（Project Japan）の一次資料は継続調査中。</>}
    >
      <svg
        viewBox={`0 0 ${W} ${H}`}
        width={W}
        height={H}
        className="w-full h-auto min-w-[560px]"
        role="img"
        aria-label="1970年に生サーモン食がなかった日本で、1985年のノルウェーのマーケティング開始を経て、2013年に寿司ネタ人気1位、2023年に対日輸出24,000トンへと至る変遷。"
      >
        <defs>
          <filter id="inkTl" x="-2%" y="-30%" width="104%" height="160%">
            <feTurbulence type="fractalNoise" baseFrequency="0.015" numOctaves={2} seed={5} result="n" />
            <feDisplacementMap in="SourceGraphic" in2="n" scale={2} xChannelSelector="R" yChannelSelector="G" />
          </filter>
        </defs>

        {/* 時間軸（手描き質感） */}
        <line x1={PAD.left} y1={axisY} x2={W - PAD.right} y2={axisY} stroke="#C9BFA8" strokeWidth={1.4} filter="url(#inkTl)" />

        {/* 年目盛り */}
        {[1970, 1980, 1990, 2000, 2010, 2020].map((y) => (
          <g key={y}>
            <line x1={xPos(y)} y1={axisY - 4} x2={xPos(y)} y2={axisY + 4} stroke="#8B6E47" strokeWidth={0.8} opacity={0.7} />
            <text x={xPos(y)} y={axisY + 18} textAnchor="middle" className="chart-label-muted">{y}</text>
          </g>
        ))}

        {/* 出来事 */}
        {events.map((ev) => {
          const x = xPos(ev.year);
          const isTop = ev.side === "top";
          const stemEnd = isTop ? axisY - 34 : axisY + 34;
          const yearY = isTop ? stemEnd - 6 : stemEnd + 14;
          const labelY = isTop ? stemEnd - 20 : stemEnd + 28;
          const r = ev.major ? 5 : 3.5;
          return (
            <g key={ev.year}>
              <line x1={x} y1={axisY} x2={x} y2={stemEnd} stroke={ev.color} strokeWidth={0.9} opacity={0.6} />
              {ev.major && <circle cx={x} cy={axisY} r={r + 4} fill={ev.color} opacity={0.12} />}
              <circle cx={x} cy={axisY} r={r} fill={ev.color} />
              <text x={x} y={yearY} textAnchor="middle" className="chart-label" style={{ fill: ev.color, fontWeight: ev.major ? 600 : 400 }}>
                {ev.year}
              </text>
              <text x={x} y={labelY} textAnchor="middle" className="chart-label-muted" style={{ fill: "#2A2A2A" }}>
                {ev.label}
              </text>
            </g>
          );
        })}
      </svg>
    </Figure>
  );
}
