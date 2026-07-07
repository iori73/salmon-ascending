#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
点描(stippling)レンダラ — リファレンス「鯨の模様と水飛沫」(点描画)に倣う。
pattern.py の模様フィールド+実画像キャリブレーション色を流用し、
体の濃淡を「点の密度・大きさ」で表現。色は段階ごとの実測色を保持(モノクロ墨でない)。
遡上(段階6)は跳躍の水飛沫を周囲に散らす。
出力: fish-stipple-montage.png (1行×7段階) + fish-stipple-hero.png (遡上の大判)
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

import pattern as P   # build_mask, pattern_field, colorize, STAGES, salmon_polygon ...
from _paths import out as _OUT

SEED = 20260615
PAPER = (250, 250, 246)
INK = (52, 50, 46)


def darkness_and_color(W, H, st):
    """段階stの体について、暗さ場 D(0..1) と各画素のRGB色を返す。"""
    body, full, tr = P.build_mask(W, H)
    field, cs = P.pattern_field(W, H, body, tr, st)
    rgba = P.colorize(st, field, cs, full)        # (H,W,4)
    rgb = rgba[..., :3].astype(float)
    alpha = rgba[..., 3] > 0
    # 暗さ = 1 - 相対輝度(紙地比)。模様の濃い所・背側ほど高い
    lum = (0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]) / 255.0
    D = np.clip(1.0 - lum, 0, 1)
    # コントラストを点描向けに少し持ち上げ
    D = np.clip((D - 0.12) / 0.78, 0, 1)
    D[~alpha] = 0.0
    return D, rgb, alpha, full, tr


def stipple(draw, D, rgb, alpha, rng, spacing=4.2, jitter=0.9, rmax=2.4, gamma=0.85):
    """グリッド+ジッタの加重点描。密度∝D, 半径∝sqrt(D)。色=局所RGB。"""
    H, W = D.shape
    gy = np.arange(spacing * 0.5, H, spacing)
    gx = np.arange(spacing * 0.5, W, spacing)
    for cy in gy:
        for cx in gx:
            jx = cx + rng.uniform(-jitter, jitter) * spacing
            jy = cy + rng.uniform(-jitter, jitter) * spacing
            ix = int(np.clip(jx, 0, W - 1)); iy = int(np.clip(jy, 0, H - 1))
            if not alpha[iy, ix]:
                continue
            d = D[iy, ix]
            if d <= 0.02:
                continue
            # 点を打つ確率(淡い所は間引く)
            if rng.random() > d ** gamma * 1.15:
                continue
            r = 0.6 + rmax * (d ** 0.5)
            c = rgb[iy, ix]
            col = (int(c[0]), int(c[1]), int(c[2]), int(np.clip(150 + 105 * d, 150, 255)))
            draw.ellipse([jx - r, jy - r, jx + r, jy + r], fill=col)


def water_spray(draw, tr, W, H, rng, n=420):
    """遡上の跳躍水飛沫 — 頭部前方〜上方に飛沫の点を散らす。"""
    ox, oy, sx = tr
    head = (ox + 0.05 * sx, oy)
    for _ in range(n):
        ang = rng.uniform(-2.4, -0.5)          # 上前方向
        dist = abs(rng.normal(0, 0.22)) * sx
        px = head[0] + np.cos(ang) * dist * rng.uniform(0.4, 1.3)
        py = head[1] + np.sin(ang) * dist
        if not (0 <= px < W and 0 <= py < H):
            continue
        r = rng.uniform(0.5, 2.2) * (1.0 - dist / (sx + 1e-6)) ** 0.5
        a = int(np.clip(150 - 120 * dist / (sx + 1e-6), 40, 180))
        draw.ellipse([px - r, py - r, px + r, py + r], fill=(70, 96, 110, a))  # teal-ish しぶき


def render_stage(W, H, st, spray=False):
    D, rgb, alpha, full, tr = darkness_and_color(W, H, st)
    rng = np.random.default_rng(SEED + st["n"] * 17)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img, "RGBA")
    if spray:
        water_spray(dr, tr, W, H, rng, n=int(W * 0.5))
    # 段階で点の密度を変える(仔魚=まばら→婚姻色=密)
    spc = {1: 5.2, 2: 4.4, 3: 4.8, 4: 4.4, 5: 4.4, 6: 3.8, 7: 4.0}.get(st["n"], 4.2)
    stipple(dr, D, rgb, alpha, rng, spacing=spc)
    # 目(濃点)
    ox, oy, sx = tr
    ex, ey = ox + 0.07 * sx, oy - 0.02 * sx
    dr.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=(30, 30, 34, 255))
    return img


def main():
    STAGES = P.STAGES
    FW, FH = 880, 380
    pad = 20; labelh = 40; top = 92
    n = len(STAGES)
    MW = pad + n * FW + n * pad
    MH = top + FH + labelh + pad
    cv = Image.new("RGB", (MW, MH), PAPER)
    dr = ImageDraw.Draw(cv)
    try:
        f_title = ImageFont.truetype("/System/Library/Fonts/ヒラギノ明朝 ProN.ttc", 46)
        f_lab = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 22)
        f_en = ImageFont.truetype("/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf", 22)
    except Exception:
        f_title = f_lab = f_en = ImageFont.load_default()
    dr.line([(pad, 28), (pad + 300, 28)], fill=(46, 110, 142), width=3)
    dr.text((pad, 40), "点描 — 鯨の模様と水飛沫に倣う / 計算した模様を点で打つ", fill=INK, font=f_title)

    for i, st in enumerate(STAGES):
        w, h = int(FW * 0.98), int(FH * 0.96)
        im = render_stage(w, h, st, spray=(st["n"] == 6))
        x = pad + i * (FW + pad); y = top + (FH - h) // 2
        cv.paste(im, (x, y), im)
        dr.text((x + 4, top + FH + 4), st["jp"], fill=(60, 60, 60), font=f_lab)
    cv.save(_OUT("stipple", "fish-stipple-montage.png"))
    print("saved fish-stipple-montage.png", cv.size)

    # hero: 遡上(段階6)の大判 + 水飛沫
    HW, HH = 1900, 900
    hero = Image.new("RGB", (HW, HH), PAPER)
    st6 = [s for s in STAGES if s["n"] == 6][0]
    im = render_stage(int(HW * 0.92), int(HH * 0.86), st6, spray=True)
    hero.paste(im, ((HW - im.width) // 2, (HH - im.height) // 2), im)
    hd = ImageDraw.Draw(hero)
    hd.text((54, 40), "遡上 — 跳ねる。", fill=INK, font=f_title)
    hero.save(_OUT("stipple", "fish-stipple-hero.png"))
    print("saved fish-stipple-hero.png", hero.size)


if __name__ == "__main__":
    main()
