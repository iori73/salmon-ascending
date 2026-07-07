#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
出所(provenance)図: 各段階で [実写PD図譜の出所] → [抽出した背帯タイル] → [点描の結果] を並べる。
模様が実画像由来であることを可視化。出力: provenance.png
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import fish_top as T
from _paths import out as _OUT

PAPER = (250, 250, 246); INK = (44, 42, 38); TEAL = (46, 110, 142); SUB = (120, 114, 100)

# stage: (source_img, citation, crop_bbox or None)
SRC = {
 1: ("/tmp/plate_alevinfry.jpg", "PSM 仔魚/稚魚図 (参考・本段は procedural)", (0, 0, 300, 192)),
 2: ("/tmp/plate_fingerling.jpg", "FMIB 37734 Dog Salmon Fingerling (PD)", (40, 40, 720, 180)),
 3: ("/tmp/plate_smolt.jpg", "FMIB 37731 Dog salmon fry → 銀化 (PD)", None),
 4: ("ref/c4fda.png", "FDA 243 Oncorhynchus keta 標本 (PD)", (35, 95, 470, 235)),
 5: ("/tmp/plate_adult34142.jpg", "FMIB 34142 Dog Salmon (PD)", (25, 40, 852, 192)),
 6: ("ref/c6male.png", "Dog Salmon Breeding Male 図譜 (PD)", None),
 7: ("ref/c6male.png", "6 遡上 calico から派生（退色・白抜け）", None),
}


def thumb(path, bbox, box):
    im = Image.open(path).convert("RGB")
    if bbox: im = im.crop(bbox)
    im.thumbnail(box)
    return im


def main():
    try:
        f_t = ImageFont.truetype("/System/Library/Fonts/ヒラギノ明朝 ProN.ttc", 38)
        f_l = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 22)
        f_s = ImageFont.truetype("/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf", 19)
        f_c = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 17)
    except Exception:
        f_t = f_l = f_s = f_c = ImageFont.load_default()

    rowH = 200; pad = 30; top = 120
    colS = 470     # source
    colT = 470     # tile
    colF = 560     # fish
    arrow = 56
    x_lab = pad
    x_src = x_lab + 250
    x_tile = x_src + colS + arrow
    x_fish = x_tile + colT + arrow
    W = x_fish + colF + pad
    H = top + 7 * rowH + pad

    cv = Image.new("RGB", (W, H), PAPER); dr = ImageDraw.Draw(cv)
    dr.line([(pad, 50), (pad + 360, 50)], fill=TEAL, width=3)
    dr.text((pad, 60), "模様の出所 — 実写PD図譜 → 抽出 → 点描", fill=INK, font=f_t)
    # column headers
    hy = top - 34
    dr.text((x_src, hy), "① 実写の出所 (PD)", fill=SUB, font=f_s)
    dr.text((x_tile, hy), "② 抽出した背帯", fill=SUB, font=f_s)
    dr.text((x_fish, hy), "③ 点描の結果", fill=SUB, font=f_s)

    for i, st in enumerate(T.STAGES):
        n = st["n"]; y = top + i * rowH
        # ラベル
        dr.text((x_lab, y + 30), st["jp"], fill=INK, font=f_l)
        src, cite, bbox = SRC[n]
        dr.text((x_lab, y + 64), "", fill=SUB, font=f_c)
        # ① source
        try:
            s = thumb(src, bbox, (colS, rowH - 70))
            cv.paste(s, (x_src, y + 12))
        except Exception:
            dr.text((x_src, y + 60), "(no source)", fill=SUB, font=f_c)
        dr.text((x_src, y + rowH - 50), cite, fill=SUB, font=f_c)
        # ② tile
        tp = f"pattern_top_{n}.png"
        if os.path.exists(tp):
            til = Image.open(tp).convert("RGB").resize((colT, rowH - 90), Image.NEAREST)
            cv.paste(til, (x_tile, y + 22))
            dr.text((x_tile, y + rowH - 50), "稜線→側線 を正規化", fill=SUB, font=f_c)
        else:
            dr.text((x_tile, y + 70), "— (procedural)", fill=SUB, font=f_c)
        # ③ fish
        im, _ = T.render_top(colF, rowH - 30, st, dot_k=0.055, colored=True)
        cv.paste(im, (x_fish, y), im)
        # arrows
        dr.text((x_src + colS + 14, y + rowH // 2 - 16), "→", fill=(170, 164, 150), font=f_t)
        dr.text((x_tile + colT + 14, y + rowH // 2 - 16), "→", fill=(170, 164, 150), font=f_t)

    cv.save(_OUT("provenance", "provenance.png"))
    print("saved provenance.png", cv.size)


if __name__ == "__main__":
    main()
