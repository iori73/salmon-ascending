#!/usr/bin/env python3
"""scale-lines.svg(stroke線画)に水温グラデ＋kasureを適用。
 ① scale-lines-kasure-grad.svg = カラー + エフェクト(両方)
 ② scale-lines-grad.svg        = カラーのみ(全線クリーン)
色は scale-ink-kasure-grad と同一の userSpaceOnUse 水温グラデを共有。"""
import re, pathlib

from _paths import out
HERE = pathlib.Path(__file__).parent
SRC = out("lines", "scale-lines.svg")   # build_lines_simple.py の出力を入力に取る
OUT_BOTH = out("lines", "scale-lines-kasure-grad.svg")
OUT_COLOR = out("lines", "scale-lines-grad.svg")

# --- 水温グラデ(scale-ink-kasure-grad.py と同値) ---
CX, CY, R = 668, 855, 1010
STOPS = [
    (0.00, "#F0E8C4"), (0.10, "#DAC988"), (0.22, "#BBBB86"), (0.36, "#86AC93"),
    (0.50, "#5F9CA0"), (0.64, "#56849D"), (0.78, "#566E92"), (0.90, "#45506F"),
    (1.00, "#313752"),
]
stops_xml = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in STOPS)
INKGRAD = (f'<radialGradient id="inkgrad" gradientUnits="userSpaceOnUse" '
           f'cx="{CX}" cy="{CY}" r="{R}">{stops_xml}</radialGradient>')

# --- 掠れノブ ---
GRAIN_FREQ, GRAIN_ALPHA = "0.04 0.8", "16 -5.6"
BLOTCH_FREQ, BLOTCH_ALPHA = "0.012 0.03", "6 -1.6"
WARP_FREQ, WARP_SCALE = "0.018", "3.2"
INK_GAMMA_AMP, INK_GAMMA_EXP = "1.7", "0.65"
KASURE = f'''<filter id="kasure" x="-6%" y="-6%" width="112%" height="112%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="{GRAIN_FREQ}" numOctaves="2" seed="11" result="grain"/>
    <feColorMatrix in="grain" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 {GRAIN_ALPHA}" result="grainMask"/>
    <feTurbulence type="fractalNoise" baseFrequency="{BLOTCH_FREQ}" numOctaves="3" seed="4" result="blotch"/>
    <feColorMatrix in="blotch" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 {BLOTCH_ALPHA}" result="blotchMask"/>
    <feComposite in="grainMask" in2="blotchMask" operator="in" result="mask"/>
    <feComposite in="SourceGraphic" in2="mask" operator="in" result="eroded"/>
    <feTurbulence type="fractalNoise" baseFrequency="{WARP_FREQ}" numOctaves="2" seed="9" result="warp"/>
    <feDisplacementMap in="eroded" in2="warp" scale="{WARP_SCALE}" xChannelSelector="R" yChannelSelector="G" result="warped"/>
    <feComponentTransfer in="warped"><feFuncA type="gamma" amplitude="{INK_GAMMA_AMP}" exponent="{INK_GAMMA_EXP}" offset="0"/></feComponentTransfer>
  </filter>'''

# --- 放射状ランプ(中央クリーン→外周かすれ) ---
RX, RY, RR = "50%", "68%", "62%"
CORE, MID = "22%", "55%"
RAMPS = f'''<radialGradient id="kEdge" cx="{RX}" cy="{RY}" r="{RR}">
    <stop offset="0%" stop-color="#000"/><stop offset="{CORE}" stop-color="#000"/><stop offset="{MID}" stop-color="#808080"/><stop offset="100%" stop-color="#fff"/></radialGradient>
  <radialGradient id="kCenter" cx="{RX}" cy="{RY}" r="{RR}">
    <stop offset="0%" stop-color="#fff"/><stop offset="{CORE}" stop-color="#fff"/><stop offset="{MID}" stop-color="#808080"/><stop offset="100%" stop-color="#000"/></radialGradient>
  <mask id="mEdge"><rect width="100%" height="100%" fill="url(#kEdge)"/></mask>
  <mask id="mCenter"><rect width="100%" height="100%" fill="url(#kCenter)"/></mask>'''

src = SRC.read_text()
GROUP_OPEN = '<g fill="none" stroke="#111111" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
assert src.count(GROUP_OPEN) == 1, "group open not found"
GROUP_GRAD = GROUP_OPEN.replace('stroke="#111111"', 'stroke="url(#inkgrad)"')

# ① 両方適用: defsに gradient/filter/ramps/線group(id付) を入れ、2レイヤーuse
both = src.replace(
    GROUP_OPEN,
    f'<defs>\n  {INKGRAD}\n  {KASURE}\n  {RAMPS}\n  ' + GROUP_GRAD.replace('<g ', '<g id="linepaths" ', 1),
    1)
CLOSE = '</g></svg>'
assert both.count(CLOSE) == 1, "close marker not found"
both = both.replace(CLOSE,
    '</g>\n</defs>\n<use href="#linepaths" mask="url(#mCenter)"/>\n<use href="#linepaths" filter="url(#kasure)" mask="url(#mEdge)"/>\n</svg>', 1)
OUT_BOTH.write_text(both)

# ② カラーのみ: defsにgradientだけ、strokeをグラデに(全線クリーン)
color = src.replace('<svg ', '<svg ', 1)  # noop anchor
color = color.replace(GROUP_OPEN, f'<defs>{INKGRAD}</defs>\n' + GROUP_GRAD, 1)
OUT_COLOR.write_text(color)

print(f"both : {OUT_BOTH.name} {len(both)} bytes")
print(f"color: {OUT_COLOR.name} {len(color)} bytes")
