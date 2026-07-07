import Figure from "./Figure";

/**
 * 図（Act4-2）　余すところなく — サケの全身利用
 * アイヌはサケを頭から目まで余さず使った。皮は靴・衣服に、焼いた身は供物に。
 * 「廃棄する部位なし」という関係の哲学を、部位と用途の対応で示す。
 *
 * 出典: 千歳水族館展示、アイヌ文化振興・研究推進機構マニュアル。模式図。
 */
export default function SalmonUtilization({ num = 2 }: { num?: number }) {
  const W = 960;
  const H = 440;

  return (
    <Figure
      num={num}
      title="余すところなく — サケの全身利用"
      source={<>千歳水族館展示、アイヌ文化振興・研究推進機構マニュアル。部位と用途の模式図。</>}
    >
      <svg
        viewBox={`0 0 ${W} ${H}`}
        width={W}
        height={H}
        className="w-full h-auto min-w-[620px]"
        role="img"
        aria-label="サケの側面図と、頭・目・皮・身・卵・白子・骨・内臓・胃袋それぞれの利用法を示す全身利用図。皮はチェップケリ（靴）に、焼いた身はチマチェップ（供物）に。"
      >
        <defs>
          <filter id="inkU" x="-4%" y="-8%" width="108%" height="116%">
            <feTurbulence type="fractalNoise" baseFrequency="0.014" numOctaves={2} seed={6} result="n" />
            <feDisplacementMap in="SourceGraphic" in2="n" scale={2.2} xChannelSelector="R" yChannelSelector="G" />
          </filter>
        </defs>

        {/* サケ（側面・頭は左） */}
        <g transform="translate(190,150)" filter="url(#inkU)">
          <path
            d="M40,120 C 80,72 170,58 300,62 C 380,64 430,74 470,86 L560,66 L528,120 L560,174 C 430,166 380,176 300,178 C 170,182 80,168 40,120 Z"
            fill="#C79A66"
            stroke="#8B6E47"
            strokeWidth={1.2}
          />
          <path d="M300,62 L330,34 L364,64 Z" fill="#C79A66" stroke="#8B6E47" strokeWidth={1} />
          <path d="M444,80 L460,64 L468,82 Z" fill="#C79A66" />
          <path d="M300,178 L320,202 L346,178 Z" fill="#C79A66" stroke="#8B6E47" strokeWidth={0.8} />
          <path d="M120,150 L150,178 L170,150 Z" fill="#B98C57" />
          {/* 婚姻色のまだら */}
          <path d="M150,118 C 230,104 320,104 420,118 C 320,132 230,132 150,118 Z" fill="#A83232" opacity={0.28} />
          {/* 鰓 */}
          <path d="M92,86 C 104,110 104,132 92,154" fill="none" stroke="#8B6E47" strokeWidth={1} opacity={0.7} />
          {/* 目 */}
          <circle cx={70} cy={108} r={5.5} fill="#fafaf6" stroke="#8B6E47" strokeWidth={1} />
          <circle cx={70} cy={108} r={2.4} fill="#2a2a2a" />
        </g>

        {/* 注記（leader line + label）。座標は translate(190,150) 後の絶対値で */}
        {/* 頭・目 */}
        <line x1={250} y1={250} x2={210} y2={300} stroke="#8B6E47" strokeWidth={0.8} />
        <text x={150} y={314} className="chart-label" style={{ fill: "#2A2A2A" }}>頭・目</text>
        <text x={150} y={330} className="chart-label-muted">煮る・出汁・余さず</text>

        {/* 皮 → チェップケリ */}
        <line x1={420} y1={210} x2={420} y2={86} stroke="#8B6E47" strokeWidth={0.8} />
        <text x={420} y={74} textAnchor="middle" className="chart-label" style={{ fill: "#8B6E47" }}>皮 → チェップケリ（皮の靴）</text>
        <text x={420} y={58} textAnchor="middle" className="chart-label-muted">衣服・帽子にも加工</text>

        {/* 身 → 焼く・干す／チマチェップ */}
        <line x1={520} y1={250} x2={560} y2={300} stroke="#8B6E47" strokeWidth={0.8} />
        <text x={566} y={304} className="chart-label" style={{ fill: "#A83232" }}>身 → 焼く・干す</text>
        <text x={566} y={320} className="chart-label-muted">チマチェップ＝イチャルパ（供養）の供物</text>

        {/* 卵・白子 */}
        <line x1={470} y1={330} x2={470} y2={372} stroke="#8B6E47" strokeWidth={0.8} />
        <text x={470} y={388} textAnchor="middle" className="chart-label" style={{ fill: "#2A2A2A" }}>卵（イクラ）・白子 → 食</text>

        {/* 骨・内臓・胃袋 */}
        <line x1={300} y1={210} x2={300} y2={372} stroke="#8B6E47" strokeWidth={0.8} />
        <text x={300} y={388} textAnchor="middle" className="chart-label" style={{ fill: "#2A2A2A" }}>骨・内臓・胃袋 → 余さず利用</text>

        {/* 哲学 */}
        <text x={W / 2} y={420} textAnchor="middle" className="chart-label" style={{ fill: "#8B6E47" }}>
          廃棄する部位なし — 食べることは、関係を結ぶこと
        </text>
      </svg>
    </Figure>
  );
}
