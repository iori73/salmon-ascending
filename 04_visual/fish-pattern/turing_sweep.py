#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gray-Scott 反応拡散の (F,k) 掃引 — 近藤滋「チューリングの仮説はいろいろな模様を作り出せる」の再現確認用。
発火する模様(spots/rings/polygon/labyrinth/stripes)を実出力で見てから本パネルを作る。
出力: turing-sweep.png (グレースケール contact sheet, 各タイルに F,k ラベル)
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from _paths import out as _OUT

SEED = 20260615

def gray_scott(gh, gw, F, k, Du=0.16, Dv=0.08, ax=1.0, ay=1.0, steps=12000, salt=0):
    rng = np.random.default_rng(SEED + salt * 101)
    U = np.ones((gh, gw)); V = np.zeros((gh, gw))
    # 複数の核から発火(乱数1点だと消えることがある)
    rr = rng.random((gh, gw))
    V[rr < 0.05] = 0.5; U[rr < 0.05] = 0.25
    def lap(Z):
        return (ax * (np.roll(Z, 1, 1) + np.roll(Z, -1, 1) - 2 * Z) +
                ay * (np.roll(Z, 1, 0) + np.roll(Z, -1, 0) - 2 * Z))
    for _ in range(steps):
        uvv = U * V * V
        U += (Du * lap(U) - uvv + F * (1 - U))
        V += (Dv * lap(V) + uvv - (F + k) * V)
    V = (V - V.min()) / (np.ptp(V) + 1e-9)
    return V

# Pearson/Sims 既知の安定領域を中心に掃引
GRID = [
    # (label, F, k, ax, ay)
    ("spots .030/.062",  0.030, 0.062, 1.0, 1.0),
    ("spots .025/.060",  0.025, 0.060, 1.0, 1.0),
    ("holes .039/.058",  0.039, 0.058, 1.0, 1.0),
    ("rings .030/.057",  0.030, 0.057, 1.0, 1.0),
    ("maze  .029/.057",  0.029, 0.057, 1.0, 1.0),
    ("worms .058/.065",  0.058, 0.065, 1.0, 1.0),
    ("coral .054/.063",  0.054, 0.063, 1.0, 1.0),
    ("chaos .026/.051",  0.026, 0.051, 1.0, 1.0),
    ("ufuji .018/.051",  0.018, 0.051, 1.0, 1.0),
    ("polyA .034/.0618", 0.034, 0.0618, 1.0, 1.0),
    ("stripeV .029/.057 ay", 0.029, 0.057, 0.45, 1.7),
    ("stripeV .030/.062 ay", 0.030, 0.062, 0.45, 1.7),
]

def main():
    gh, gw = 160, 160
    tile = 200
    cols = 4
    rows = (len(GRID) + cols - 1) // cols
    pad = 10; labelh = 22
    MW = cols * tile + (cols + 1) * pad
    MH = rows * (tile + labelh) + (rows + 1) * pad
    canvas = Image.new("RGB", (MW, MH), (250, 250, 248))
    dr = ImageDraw.Draw(canvas)
    try: font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 14)
    except: font = ImageFont.load_default()
    for idx, (label, F, k, ax, ay) in enumerate(GRID):
        V = gray_scott(gh, gw, F, k, ax=ax, ay=ay, salt=idx)
        std = float(V.std())
        img = Image.fromarray((np.clip(V, 0, 1) * 255).astype(np.uint8)).resize((tile, tile), Image.NEAREST)
        r = idx // cols; c = idx % cols
        x = pad + c * (tile + pad); y = pad + r * (tile + labelh + pad)
        canvas.paste(img, (x, y))
        dr.text((x + 2, y + tile + 2), "%s s=%.2f" % (label, std), fill=(40, 40, 40), font=font)
        print("%-22s F=%.4f k=%.4f std=%.3f" % (label, F, k, std))
    canvas.save(_OUT("turing", "turing-sweep.png"))
    print("saved turing-sweep.png", canvas.size)

if __name__ == "__main__":
    main()
