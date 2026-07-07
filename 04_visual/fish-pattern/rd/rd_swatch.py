#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rd_swatch.py — 魚形なし。各段階の Turing 模様だけを正方形スウォッチに(タイル状=周期境界)。
シミュレータと同じ Gray–Scott パラメータで計算し、段階色で着色。出力: swatch-<stage>.png + montage。
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "swatches")
os.makedirs(_OUT, exist_ok=True)
SEED = 20260620


def gray_scott(G, F, k, ax=1.0, ay=1.0, Du=0.16, Dv=0.08, steps=9000, salt=0):
    rng = np.random.default_rng(SEED + salt * 7)
    U = np.ones((G, G)); V = np.zeros((G, G))
    rr = rng.random((G, G)); V[rr < 0.06] = 0.5; U[rr < 0.06] = 0.25
    for _ in range(steps):
        lu = ax * (np.roll(U, 1, 1) + np.roll(U, -1, 1) - 2 * U) + ay * (np.roll(U, 1, 0) + np.roll(U, -1, 0) - 2 * U)
        lv = ax * (np.roll(V, 1, 1) + np.roll(V, -1, 1) - 2 * V) + ay * (np.roll(V, 1, 0) + np.roll(V, -1, 0) - 2 * V)
        uvv = U * V * V
        U += Du * lu - uvv + F * (1 - U)
        V += Dv * lv + uvv - (F + k) * V
    v = (V - V.min()) / (np.ptp(V) + 1e-9)
    return v


# レジーム指針(GS, Du:Dv=0.16:0.08):
#  - parr/calico の実物は「離散した縦バー」。これは連続ストライプ(=迷路, worm域)ではなく
#    spot域(高め k・低め F)で離散斑を出し、強い縦異方(ay≫ax)で縦に伸ばして得る。
#  - 海洋期の実物は「ほぼ無地の銀」。シロザケは大きな黒点を持たない種なので斑点格子は禁。
#    → 微細パターンを生成しても amp を強く落として銀地に寄せる。
#  - 太い少数バー(calico)は G を小さくして特徴サイズ/タイルを相対的に大きくする。


def hexc(s): return np.array([int(s[i:i+2], 16) for i in (1, 3, 5)], float)


# 模様だけ: base色 + bar色(+calicoは赤)。G=グリッド(小→太い少数バー), amp=模様の濃さ。
# 配色: parr mark=スレート青灰 / calico=高彩度マゼンタ赤紫(緑黒の暗核と2色) / ocean=冷たい銀。
SW = [
    dict(key="parr",   jp="②稚魚 parr",      F=.026, k=.0610, ax=.14, ay=1.86, G=170, amp=1.0,
         base="#AEB2A6", bar="#39433C"),
    dict(key="coastal",jp="⑤沿岸(弱バー)",   F=.028, k=.0615, ax=.16, ay=1.84, G=170, amp=0.45,
         base="#A6A892", bar="#3D4636"),
    dict(key="calico", jp="⑥遡上 calico",    F=.026, k=.0610, ax=.16, ay=1.84, G=115, amp=1.0,
         base="#C3C2A6", bar="#A03E55", bar2="#283021", red=True),
    dict(key="postspawn", jp="⑦産卵後",      F=.026, k=.0610, ax=.16, ay=1.84, G=115, amp=0.85,
         base="#75745E", bar="#7E4654", bar2="#2A2A1C", red=True),
    dict(key="ocean",  jp="④海洋(ほぼ無地)",  F=.038, k=.0650, ax=1.0, ay=1.0, G=200, amp=0.12,
         base="#C8CDD2", bar="#9DAEB6"),
]


def colorize(v, st):
    base = hexc(st["base"]); bar = hexc(st["bar"]); bar2 = hexc(st.get("bar2", st["bar"]))
    amp = st.get("amp", 1.0)
    m = (np.clip((v - 0.5) * 2, 0, 1) * amp)[..., None]  # 模様の強さ(amp で減衰)
    if st.get("red"):
        # 強い所=赤紫(婚姻色), 最強核=緑黒 の2段
        col = base[None, None] * (1 - m) + bar[None, None] * m
        m2 = (np.clip((v - 0.78) / 0.22, 0, 1) * amp)[..., None]
        col = col * (1 - m2) + bar2[None, None] * m2
    else:
        col = base[None, None] * (1 - m) + bar[None, None] * m
    return np.clip(col, 0, 255).astype(np.uint8)


def main():
    for st in SW:
        G = st.get("G", 200)
        v = gray_scott(G, st["F"], st["k"], st["ax"], st["ay"], salt=hash(st["key"]) % 97)
        img = Image.fromarray(colorize(v, st))
        img.resize((500, 500), Image.NEAREST).save(os.path.join(_OUT, f"swatch-{st['key']}.png"))
        print("saved swatch-%s.png" % st["key"])
    # montage
    th = 300; pad = 20; lab = 30
    try: f = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 22)
    except: f = ImageFont.load_default()
    cols = len(SW); W = pad + cols * (th + pad); H = pad + lab + th + lab
    cv = Image.new("RGB", (W, H), (255, 255, 255)); dr = ImageDraw.Draw(cv)
    dr.line([(pad, 8), (pad + 360, 8)], fill=(46, 110, 142), width=3)
    dr.text((pad, 14), "模様だけ swatch — 反応拡散の計算結果(魚形なし・タイル状)", fill=(30, 30, 30), font=f)
    for i, st in enumerate(SW):
        im = Image.open(os.path.join(_OUT, f"swatch-{st['key']}.png")).resize((th, th), Image.NEAREST)
        x = pad + i * (th + pad)
        cv.paste(im, (x, pad + lab)); dr.text((x + 4, pad + lab + th + 2), st["jp"], fill=(60, 60, 60), font=f)
    p = os.path.join(_OUT, "rd-swatches.png"); cv.save(p); print("saved", p, cv.size)


if __name__ == "__main__":
    main()
