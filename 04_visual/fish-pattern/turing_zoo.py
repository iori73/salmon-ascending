#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
近藤滋「チューリングの仮説はいろいろな模様を作り出せる」の計算再現パネル。
1つの Gray-Scott 反応拡散モデルが、(F,k) と異方性を変えるだけで模様の家族を生むことを示す。
最後の1枚=サケ婚姻色の縦バー(異方性縞)で、手法Bの科学的根拠に接続する。
出力: turing-zoo.png (ctxt.jp エディトリアル様式・紙地+teal罫)
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from _paths import out as _OUT

SEED = 20260615

# ---- 配色(ctxt.jp/Suisai 系) ----
PAPER  = (244, 240, 230)   # warm paper #F4F0E6
INK    = (42, 42, 42)      # 墨
TEAL   = (46, 110, 142)    # #2E6E8E
SUB    = (110, 104, 92)    # gloss gray
PATDARK= (38, 44, 52)      # 模様の濃 (藍墨)
PATLITE= (236, 232, 222)   # 模様の淡 (紙白)


def gray_scott(gh, gw, F, k, Du=0.16, Dv=0.08, ax=1.0, ay=1.0, steps=14000, salt=0):
    rng = np.random.default_rng(SEED + salt * 101)
    U = np.ones((gh, gw)); V = np.zeros((gh, gw))
    rr = rng.random((gh, gw)); V[rr < 0.05] = 0.5; U[rr < 0.05] = 0.25
    def lap(Z):
        return (ax * (np.roll(Z, 1, 1) + np.roll(Z, -1, 1) - 2 * Z) +
                ay * (np.roll(Z, 1, 0) + np.roll(Z, -1, 0) - 2 * Z))
    for _ in range(steps):
        uvv = U * V * V
        U += (Du * lap(U) - uvv + F * (1 - U))
        V += (Dv * lap(V) + uvv - (F + k) * V)
    V = (V - V.min()) / (np.ptp(V) + 1e-9)
    return V


# (jp_title, en_gloss, animal, F, k, ax, ay, invert)
PANELS = [
    ("斑点",       "spots",      "チーターの斑",      0.030, 0.062, 1.0, 1.0, False),
    ("多孔・大斑", "holes",      "ヒョウのロゼット風", 0.018, 0.050, 1.0, 1.0, False),
    ("網目",       "polygons",   "キリンの網目",       0.029, 0.057, 1.0, 1.0, True),
    ("迷路・縞",   "labyrinth",  "シマウマ・熱帯魚",   0.029, 0.057, 1.0, 1.0, False),
    ("異方性縦縞", "anisotropic","サケ婚姻色の縦バー", 0.029, 0.057, 0.45, 1.7, False),
]


def two_tone(V, invert=False):
    """中央値で二値化し、淡墨/濃墨の二色へ(近藤の simulator 風クリスプ)。"""
    thr = np.median(V)
    m = V > thr
    if invert:
        m = ~m
    out = np.zeros((*V.shape, 3), np.uint8)
    out[m]  = PATDARK
    out[~m] = PATLITE
    return out


def font(path, size):
    try: return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()

MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
GOTHIC = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
SERIF  = "/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf"


def main():
    n = len(PANELS)
    TILE = 360
    gap = 28
    margin = 70
    top = 230
    capH = 96
    footer = 150
    W = margin * 2 + n * TILE + (n - 1) * gap
    H = top + TILE + capH + footer

    cv = Image.new("RGB", (W, H), PAPER)
    dr = ImageDraw.Draw(cv)

    f_label = font(SERIF, 26)
    f_title = font(MINCHO, 52)
    f_lead  = font(MINCHO, 26)
    f_cap_jp = font(GOTHIC, 28)
    f_cap_en = font(SERIF, 23)
    f_animal = font(MINCHO, 25)
    f_param  = font(SERIF, 21)
    f_foot   = font(MINCHO, 24)

    # masthead
    dr.line([(margin, 60), (margin + 360, 60)], fill=TEAL, width=3)
    dr.text((margin, 74), "REACTION-DIFFUSION", fill=TEAL, font=f_label)
    dr.text((margin, 112), "1つの式が、模様の家族を生む", fill=INK, font=f_title)
    dr.text((margin, 184),
            "近藤滋のチューリング・モデル — 反応拡散方程式の F・k と異方性を変えるだけで、斑点も縞も網目も同じ計算から現れる。",
            fill=SUB, font=f_lead)

    x = margin
    for i, (jp, en, animal, F, k, ax, ay, inv) in enumerate(PANELS):
        salmon = (i == n - 1)
        V = gray_scott(200, 200, F, k, ax=ax, ay=ay, salt=i)
        tile = Image.fromarray(two_tone(V, inv)).resize((TILE, TILE), Image.NEAREST)
        cv.paste(tile, (x, top))
        # frame — salmon panel gets teal frame
        fc = TEAL if salmon else (200, 194, 182)
        fw = 4 if salmon else 1
        dr.rectangle([x - fw, top - fw, x + TILE + fw - 1, top + TILE + fw - 1], outline=fc, width=fw)
        # caption
        cy = top + TILE + 16
        dr.text((x, cy), jp, fill=(TEAL if salmon else INK), font=f_cap_jp)
        dr.text((x, cy + 36), en, fill=SUB, font=f_cap_en)
        # animal + params under tile, small
        dr.text((x, cy + 64), animal, fill=INK, font=f_animal)
        x += TILE + gap

    # footer note
    fy = top + TILE + capH + 30
    dr.line([(margin, fy - 14), (W - margin, fy - 14)], fill=(210, 204, 190), width=1)
    dr.text((margin, fy),
            "右端=サケの体側。同じ反応拡散に異方性(縦方向の拡散を強める)を与えると、婚姻色の縦バーが立ち上がる。",
            fill=INK, font=f_foot)
    en_part = "Gray-Scott model · F,k = feed / kill rate · 200×200 grid · 14,000 steps · seed 20260615   ｜   "
    dr.text((margin, fy + 40), en_part, fill=SUB, font=f_param)
    en_w = dr.textlength(en_part, font=f_param)
    f_ref_jp = font(GOTHIC, 21)
    dr.text((margin + en_w, fy + 40),
            "ref: 近藤滋「チューリングの仮説はいろいろな模様を作り出せる」",
            fill=SUB, font=f_ref_jp)

    cv.save(_OUT("turing", "turing-zoo.png"))
    print("saved turing-zoo.png", cv.size)


if __name__ == "__main__":
    main()
