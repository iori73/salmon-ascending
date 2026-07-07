#!/usr/bin/env python3
"""scale-ink.svg(inkgradグラデ塗り)に「外周ほど強い」掠れを適用 → scale-ink-kasure.svg。

設計: 同じパス群を <use> で2レイヤー重ね、放射状マスクでクロスフェードする。
  - レイヤー1: クリーンなインク(掠れなし)。中央で不透明・外周で透明 (mask=mCenter)
  - レイヤー2: kasure(erosion)適用インク。中央で透明・外周で不透明 (mask=mEdge)
  中間半径で両者が混ざり、掠れ(穴)が外へ向かって徐々に立ち上がる。
パスは複製せず id 参照なのでファイルはほぼ太らない。"""
import re, pathlib

from _paths import asset, out
HERE = pathlib.Path(__file__).parent
SRC = asset("scale-ink.svg")
OUT = out("kasure", "scale-ink-kasure.svg")

# --- 掠れノブ(密度・濃さ) ---
GRAIN_FREQ    = "0.04 0.8"
GRAIN_ALPHA   = "16 -5.6"
BLOTCH_FREQ   = "0.012 0.03"
BLOTCH_ALPHA  = "6 -1.6"
WARP_FREQ     = "0.018"
WARP_SCALE    = "3.2"
INK_GAMMA_AMP = "1.7"
INK_GAMMA_EXP = "0.65"

# --- 放射状ランプ(掠れの効き方)ノブ ---
RAMP_CX, RAMP_CY, RAMP_R = "50%", "68%", "62%"  # 起点=鱗中心(inkgradと同心)
CORE_STOP  = "22%"   # ここまでは完全クリーン(掠れ0の起点)
MID_STOP   = "55%"   # 中間: 掠れ立ち上がり
# offset 100% で掠れ最大

KASURE = f'''<filter id="kasure" x="-6%" y="-6%" width="112%" height="112%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="{GRAIN_FREQ}" numOctaves="2" seed="11" result="grain"/>
    <feColorMatrix in="grain" type="matrix"
       values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 {GRAIN_ALPHA}" result="grainMask"/>
    <feTurbulence type="fractalNoise" baseFrequency="{BLOTCH_FREQ}" numOctaves="3" seed="4" result="blotch"/>
    <feColorMatrix in="blotch" type="matrix"
       values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 {BLOTCH_ALPHA}" result="blotchMask"/>
    <feComposite in="grainMask" in2="blotchMask" operator="in" result="mask"/>
    <feComposite in="SourceGraphic" in2="mask" operator="in" result="eroded"/>
    <feTurbulence type="fractalNoise" baseFrequency="{WARP_FREQ}" numOctaves="2" seed="9" result="warp"/>
    <feDisplacementMap in="eroded" in2="warp" scale="{WARP_SCALE}" xChannelSelector="R" yChannelSelector="G" result="warped"/>
    <feComponentTransfer in="warped">
      <feFuncA type="gamma" amplitude="{INK_GAMMA_AMP}" exponent="{INK_GAMMA_EXP}" offset="0"/>
    </feComponentTransfer>
  </filter>'''

# mEdge = 掠れレイヤーの可視量(中央黒=隠す, 外白=見せる)
# mCenter = クリーンレイヤーの可視量(mEdgeの反転)
RAMPS = f'''<radialGradient id="kEdge" cx="{RAMP_CX}" cy="{RAMP_CY}" r="{RAMP_R}">
    <stop offset="0%"  stop-color="#000"/>
    <stop offset="{CORE_STOP}" stop-color="#000"/>
    <stop offset="{MID_STOP}" stop-color="#808080"/>
    <stop offset="100%" stop-color="#fff"/>
  </radialGradient>
  <radialGradient id="kCenter" cx="{RAMP_CX}" cy="{RAMP_CY}" r="{RAMP_R}">
    <stop offset="0%"  stop-color="#fff"/>
    <stop offset="{CORE_STOP}" stop-color="#fff"/>
    <stop offset="{MID_STOP}" stop-color="#808080"/>
    <stop offset="100%" stop-color="#000"/>
  </radialGradient>
  <mask id="mEdge"><rect width="100%" height="100%" fill="url(#kEdge)"/></mask>
  <mask id="mCenter"><rect width="100%" height="100%" fill="url(#kCenter)"/></mask>'''

USES = '''<use href="#inkpaths" mask="url(#mCenter)"/>
<use href="#inkpaths" filter="url(#kasure)" mask="url(#mEdge)"/>'''

src = SRC.read_text()

# 1) defsを開いたまま: kasure/ramps/masks を足し、描画groupを id付きでdefs内に取り込む
open_marker = '</defs>\n<g filter="url(#nijimi)">'
assert src.count(open_marker) == 1, "open boundary not found"
src = src.replace(open_marker,
    f'{KASURE}\n  {RAMPS}\n  <g id="inkpaths">', 1)

# 2) 末尾: パスgroupを閉じ→defsを閉じ→2レイヤーをuseで配置
close_marker = '</g>\n</svg>'
assert src.count(close_marker) == 1, "close boundary not found"
src = src.replace(close_marker, f'</g>\n</defs>\n{USES}\n</svg>', 1)

OUT.write_text(src)
print(f"written {OUT.name}: {len(src)} bytes")
