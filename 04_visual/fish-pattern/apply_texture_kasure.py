#!/usr/bin/env python3
"""クリーン年輪マスク(_rings_mask.png)を、実物グランジ素材で侵食(かすれマスク)して
年輪プリント風のラスタ画像を生成する。テクスチャ/ドロップ率/濃さを引数で調整。"""
import sys, numpy as np
from PIL import Image, ImageFile
from _paths import asset, out as _out, BASE
ImageFile.LOAD_TRUNCATED_IMAGES = True

# ---- ノブ ----
TEXTURE   = sys.argv[1] if len(sys.argv)>1 else str(BASE / "_grunge_src/Resource Boy - Grunge Textures/013.jpg")
DROPOUT   = float(sys.argv[2]) if len(sys.argv)>2 else 0.35   # かすれで抜く面積比(0-1)
SOFT      = float(sys.argv[3]) if len(sys.argv)>3 else 0.14   # 抜けの境界の柔らかさ(luminance)
INK_GAMMA = float(sys.argv[4]) if len(sys.argv)>4 else 0.80   # 墨の濃さ(<1で濃く)
OUT       = sys.argv[5] if len(sys.argv)>5 else str(_out("kasure", "texkasure.png"))
PAPER = np.array([242,238,230], np.float32)
INK   = np.array([18,16,15],  np.float32)

rings = Image.open(asset("_rings_mask.png")).convert("RGBA")
W,H = rings.size
R = np.asarray(rings)[:,:,3].astype(np.float32)/255.0           # 年輪インク被覆(濃淡含む)

g = Image.open(TEXTURE).convert("L").resize((W,H), Image.LANCZOS)
G = np.asarray(g).astype(np.float32)/255.0                       # グランジ輝度

thr  = float(np.quantile(G, 1.0 - DROPOUT))                      # 明るい上位DROPOUTを抜く
keep = np.clip((thr - G)/max(SOFT,1e-3) + 0.5, 0.0, 1.0)         # 暗部=墨残す, 明部=抜く

A = np.clip(R*keep, 0, 1) ** INK_GAMMA                           # 最終インクα
out = PAPER[None,None,:]*(1-A[:,:,None]) + INK[None,None,:]*A[:,:,None]
Image.fromarray(out.astype("uint8")).save(OUT)
# クイック確認用に1/2プレビュー
import os as _os
_prev = _os.path.join(_os.path.dirname(OUT), "_preview_" + _os.path.basename(OUT))
Image.fromarray(out.astype("uint8")).resize((W//2,H//2), Image.LANCZOS).save(_prev)
print(f"{OUT}: {W}x{H} tex={TEXTURE.split('/')[-1]} drop={DROPOUT} soft={SOFT} gamma={INK_GAMMA} thr={thr:.3f}")
