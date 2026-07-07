#!/usr/bin/env python3
"""現Figmaベクター(scale-brush.svg)のフィルタを erosion型(掠れ)に差し替えて scale-kasure.svg を生成。
パラメータを一箇所で管理し、ヘッドレスChromeでの確認→反復チューニングを容易にする。"""
import re, pathlib, sys

from _paths import asset, out
HERE = pathlib.Path(__file__).parent
SRC = asset("scale-brush.svg")
OUT = out("kasure", "scale-kasure.svg")

# --- 掠れノブ（密度・濃さの調整はここだけ） ---
GRAIN_FREQ   = "0.04 0.8"     # 微細ノイズ: X小=線方向に長く連続, Y大=筋
GRAIN_ALPHA  = "16 -5.6"      # 微細マスク閾値(↑残ink多/掠れ弱, ↓掠れ強)
BLOTCH_FREQ  = "0.012 0.03"   # 粗い塊ノイズ
BLOTCH_ALPHA = "6 -1.6"       # 塊抜け閾値
WARP_FREQ    = "0.018"        # 有機的揺らし周波数
WARP_SCALE   = "3.2"          # 揺らし量
INK_GAMMA_AMP = "1.7"         # 低不透明度マークを濃く(参照画像の黒さに寄せる)
INK_GAMMA_EXP = "0.65"
PAPER = None                  # None=背景透過(再利用しやすい/Figmaは下地に乗る)。色文字列で紙地を焼き込む

FILTER = f'''<defs>
  <filter id="kasure" x="-6%" y="-6%" width="112%" height="112%" color-interpolation-filters="sRGB">
    <!-- A. fine anisotropic grain = dry-brush striations -->
    <feTurbulence type="fractalNoise" baseFrequency="{GRAIN_FREQ}" numOctaves="2" seed="11" result="grain"/>
    <feColorMatrix in="grain" type="matrix"
       values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 {GRAIN_ALPHA}" result="grainMask"/>
    <!-- B. coarse blotch dropout -->
    <feTurbulence type="fractalNoise" baseFrequency="{BLOTCH_FREQ}" numOctaves="3" seed="4" result="blotch"/>
    <feColorMatrix in="blotch" type="matrix"
       values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 {BLOTCH_ALPHA}" result="blotchMask"/>
    <!-- C. intersect masks then erode source ink -->
    <feComposite in="grainMask" in2="blotchMask" operator="in" result="mask"/>
    <feComposite in="SourceGraphic" in2="mask" operator="in" result="eroded"/>
    <!-- D. organic edge warp -->
    <feTurbulence type="fractalNoise" baseFrequency="{WARP_FREQ}" numOctaves="2" seed="9" result="warp"/>
    <feDisplacementMap in="eroded" in2="warp" scale="{WARP_SCALE}" xChannelSelector="R" yChannelSelector="G" result="warped"/>
    <!-- E. deepen ink to match reference black -->
    <feComponentTransfer in="warped">
      <feFuncA type="gamma" amplitude="{INK_GAMMA_AMP}" exponent="{INK_GAMMA_EXP}" offset="0"/>
    </feComponentTransfer>
  </filter>
</defs>'''

src = SRC.read_text()
out, n = re.subn(r"<defs>.*?</defs>", FILTER, src, count=1, flags=re.DOTALL)
assert n == 1, f"defs replace count={n}"
if PAPER:
    out = out.replace('<g filter="url(#kasure)">',
                      f'<rect width="100%" height="100%" fill="{PAPER}"/>\n<g filter="url(#kasure)">', 1)
OUT.write_text(out)
print(f"written {OUT.name}: {len(out)} bytes, defs replaced={n}")
