#!/usr/bin/env python3
"""年輪(merged=1335x1247)の木目に、中心(stage1)→外周(stage7)へ向け段階的に強くなる
「かすれの質感」を与える。★線は消さない★: インクを抜くのではなく、線の全長を保ったまま
インク濃度を微細テクスチャで変調し、外側ほど枯れた(かすれた)筆致にする。最低濃度に床を設け、
どんなに掠れても線が消えないようにする。"""
import sys, numpy as np
from PIL import Image, ImageFile
from _paths import asset, out, BASE
from scipy.ndimage import gaussian_filter
ImageFile.LOAD_TRUNCATED_IMAGES = True

# ---- ノブ ----
TEXTURE   = sys.argv[1] if len(sys.argv)>1 else str(BASE / "_grunge_src/Resource Boy - Grunge Textures/004.jpg")
MAX_DRY   = float(sys.argv[2]) if len(sys.argv)>2 else 0.72  # 外周での最大かすれ(濃度の減り幅; 1=ほぼ消える手前)
RAD_GAMMA = float(sys.argv[3]) if len(sys.argv)>3 else 1.35  # 放射ランプ曲率(>1で中心側を長くクリーンに)
INK_GAMMA = float(sys.argv[4]) if len(sys.argv)>4 else 0.92  # 全体の濃さ(線を残すため<1控えめ)
OUT       = sys.argv[5] if len(sys.argv)>5 else str(out("kasure", "radial_kasure.png"))
REAL_W    = float(sys.argv[6]) if len(sys.argv)>6 else 0.30  # 実グランジの質感ブレンド比(0=純手続き)
FLOOR     = float(sys.argv[7]) if len(sys.argv)>7 else 0.18  # 最暗かすれでも残すインク濃度の床(線を消さない)
CONTRAST  = 1.7                                              # かすれスジのコントラスト

SCALE = 2
CX, CY = 698*SCALE, 815*SCALE     # stage1収束点
R0, R1 = 150*SCALE, 712*SCALE     # クリーン半径 / stage7外周(最大かすれ)
PAPER = np.array([242,238,230], np.float32)
INK   = np.array([18,16,15],  np.float32)

rings = Image.open(asset("_rings_mask.png")).convert("RGBA")
W,H = rings.size
R = np.asarray(rings)[:,:,3].astype(np.float32)/255.0       # 線の被覆(これは保持する)

# --- かすれ質感フィールド: 等方性フラクタルノイズ(密度均一)＋任意で実グランジ ---
def fractal(W,H, base=16, octaves=6, seed=7, persist=0.55):
    rng = np.random.default_rng(seed)
    out = np.zeros((H,W), np.float32); amp=1.0; norm=0.0
    for o in range(octaves):
        gh = max(2,int(base*(2**o))); gw = max(2,int(gh*W/H))
        n = rng.standard_normal((gh,gw)).astype(np.float32)
        n = np.asarray(Image.fromarray(n, mode='F').resize((W,H), Image.BILINEAR))
        out += amp*n; norm += amp; amp *= persist
    out /= norm
    return (out-out.min())/(np.ptp(out)+1e-6)
field = fractal(W,H)                                         # 0..1 高=枯れ(インク薄)
if REAL_W > 0:
    g = np.asarray(Image.open(TEXTURE).convert("L").resize((W,H),Image.LANCZOS)).astype(np.float32)/255.0
    hp = g - gaussian_filter(g, max(W,H)/50.0)
    hp = hp/np.sqrt(gaussian_filter(hp*hp, max(W,H)/50.0)+1e-4)
    hp = np.clip(0.5+hp*0.25,0,1)
    field = (1-REAL_W)*field + REAL_W*hp
field = np.clip((field-0.5)*CONTRAST+0.5, 0, 1)              # スジを際立たせる

# --- 放射ランプ: 中心0 → 外周1 ---
yy,xx = np.mgrid[0:H,0:W]
dist = np.sqrt((xx-CX)**2 + (yy-CY)**2)
radial = np.clip((dist - R0)/(R1 - R0), 0, 1) ** RAD_GAMMA

# --- ★インク濃度を変調(線は消さない)★ ---
# dry: 外側かつfield高で大きい枯れ。inkdark: 線内のインク濃さ(FLOOR以上を保証)
dry = MAX_DRY * radial * field
inkdark = np.clip(1.0 - dry, FLOOR, 1.0)                     # 床で線の連続性を担保
cov = np.clip(R * inkdark, 0, 1) ** INK_GAMMA               # 被覆Rは保持、濃さだけ変調
out = PAPER[None,None,:]*(1-cov[:,:,None]) + INK[None,None,:]*cov[:,:,None]
Image.fromarray(out.astype("uint8")).save(OUT)
import os as _os
_prev = _os.path.join(_os.path.dirname(OUT), "_preview_" + _os.path.basename(OUT))
Image.fromarray(out.astype("uint8")).resize((W//2,H//2), Image.LANCZOS).save(_prev)
print(f"{OUT}: {W}x{H} maxDry={MAX_DRY} radGamma={RAD_GAMMA} inkGamma={INK_GAMMA} realW={REAL_W} floor={FLOOR}")
