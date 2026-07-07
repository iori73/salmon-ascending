#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
赤枠1「アウトラインは描かずに、模様で」(蛇の骨格タトゥーの原理)の計算実装。
魚の輪郭線・塗り・目を一切描かず、鱗列(scale rows)+側線(lateral line)という
"構造の模様" の配置だけで体の形・うねり・量感を立ち上げる。
鱗=後縁の弧(クレッセント)。体側で大きく密、背腹・頭尾で小さく疎 → envelope が魚形。
出力: form-hero.png (1尾) / form-reduction.png (密→疎で形がどこまで残るか)
"""
import numpy as np
from PIL import Image, ImageDraw
import fish_geom as G
from _paths import out as _OUT

SEED = 20260615
PAPER = (250, 250, 246)
INK = (44, 42, 38)
TEAL = (46, 110, 142)


def _arc_crescent(dr, x, y, r, ang, col, w, span=120):
    """後縁の弧(scallop) ")"。開口は頭側、弧は尾側へ膨らむ。接線angで回転。"""
    dr.arc([x - r, y - r, x + r, y + r],
           start=ang - span / 2, end=ang + span / 2, fill=col, width=w)


def draw_scales(dr, tr, n_rows=20, scale_dt=0.022, density=1.0, taper=1.0,
                col=INK, line_w=2.0, jitter=0.45):
    """鱗を (t,n) 格子に scallop で配置。鱗が後方へ重なる列を成し、envelope が魚形。
    輪郭・塗りは一切描かない。"""
    rng = np.random.default_rng(SEED)
    ox, oy, L, arc = tr
    a = col + (235,)
    t = 0.02
    ci = 0
    while t <= 0.872:
        hu, hd = G.half_height(t)
        hh = hu + hd
        if hh < 0.012:
            t += scale_dt; ci += 1; continue
        ang = G.body_tangent(tr, t, taper)
        offset = (ci % 2) * 0.5
        # 頭(t<0.1)と尾柄(t>0.8)で体高方向の鱗を間引かず、サイズで絞る
        head_fac = min(1.0, (t - 0.005) / 0.07)
        tail_fac = min(1.0, (0.875 - t) / 0.05)
        for j in range(n_rows + 1):
            nn = -0.95 + (j + offset) * (1.90 / n_rows)
            if abs(nn) > 0.96:
                continue
            x, y = G.pos(tr, t, nn, taper)
            x += rng.uniform(-jitter, jitter) * 2
            y += rng.uniform(-jitter, jitter) * 2
            # 鱗サイズ: 体側中央で最大、背腹端で小、頭尾で縮小
            flank = 1 - 0.42 * abs(nn) ** 1.4
            r = (hh * L) / n_rows * (1.05 * flank * head_fac * (0.45 + 0.55 * tail_fac) + 0.22)
            if r < 1.0:
                continue
            if rng.random() > density:
                continue
            # scallop の丸い縁を尾側へ(後縁が後方に重なる) → 中心 ang(尾方向)に膨らむ ")"
            _arc_crescent(dr, x, y, r, ang, a, max(1, int(line_w)), span=150)
        t += scale_dt
        ci += 1


def draw_tail(dr, tr, taper=1.0, col=INK, line_w=2.0, density=1.0):
    """尾びれ = 尾柄から放射する条(rays)。輪郭は描かない。"""
    rng = np.random.default_rng(SEED + 5)
    ox, oy, L, arc = tr
    bx, by = G.pos(tr, 0.872, 0.0, taper)
    tipx = ox + 1.0 * L
    cy_t = oy - (arc * np.sin(np.pi)) * L
    spread = 0.150 * L * taper
    nr = 16
    for i in range(nr + 1):
        if rng.random() > density:
            continue
        f = i / nr
        ty = (cy_t - spread) + f * (2 * spread)
        # 二叉: 中央(f~0.5)は短く窪む
        notch = 1 - 0.45 * np.exp(-((f - 0.5) ** 2) / (2 * 0.12 ** 2))
        ex = bx + (tipx - bx) * notch
        dr.line([(bx, by + (ty - cy_t) * 0.12), (ex, ty)], fill=col + (210,),
                width=max(1, int(line_w * 0.8)))


def draw_lateral_line(dr, tr, taper=1.0, col=TEAL):
    """側線 = 蛇の背骨にあたる構造軸。ゆるい弧。"""
    pts = []
    for k in range(0, 101):
        t = k / 100 * 0.875
        x, y = G.pos(tr, t, 0.06, taper)   # 側線は中心やや上
        pts.append((x, y))
    dr.line(pts, fill=col + (220,), width=3, joint="curve")


def render(W, H, arc=0.0, density=1.0, n_rows=22, taper=1.0, lateral=True,
           supersample=2):
    SS = supersample
    img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img, "RGBA")
    _, _, _, tr0 = G.build_fields(W, H, arc=arc, taper=taper)
    # transform を SS スケールへ
    ox, oy, L, a = tr0
    tr = (ox * SS, oy * SS, L * SS, a)
    if lateral:
        draw_lateral_line(dr, tr, taper, col=TEAL)
    draw_scales(dr, tr, n_rows=n_rows, density=density, taper=taper,
                col=INK, line_w=2.0 * SS)
    draw_tail(dr, tr, taper=taper, col=INK, line_w=2.0 * SS, density=density)
    img = img.resize((W, H), Image.LANCZOS)
    return img


def main():
    from PIL import ImageFont
    try:
        f_title = ImageFont.truetype("/System/Library/Fonts/ヒラギノ明朝 ProN.ttc", 46)
        f_lab = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 24)
        f_en = ImageFont.truetype("/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf", 24)
    except Exception:
        f_title = f_lab = f_en = ImageFont.load_default()

    # hero: 鱗列だけで立つ1尾
    HW, HH = 1900, 760
    hero = Image.new("RGB", (HW, HH), PAPER)
    im = render(int(HW * 0.94), int(HH * 0.9), arc=0.03, density=1.0, n_rows=14)
    hero.paste(im, ((HW - im.width) // 2, (HH - im.height) // 2), im)
    hd = ImageDraw.Draw(hero)
    hd.line([(54, 54), (354, 54)], fill=TEAL, width=3)
    hd.text((54, 64), "アウトラインを描かず、鱗の列だけで形を立てる", fill=INK, font=f_title)
    en = "no outline · no fill · "
    hd.text((54, HH - 54), en, fill=(110, 104, 92), font=f_en)
    ew = hd.textlength(en, font=f_en)
    hd.text((54 + ew, HH - 54), "鱗(後縁の弧)の疎密と側線だけで魚形が立ち上がる — 蛇骨タトゥーの原理",
            fill=(110, 104, 92), font=f_lab)
    hero.save(_OUT("pattern", "form-hero.png"))
    print("saved form-hero.png", hero.size)

    # reduction: 密→疎。どこまで間引いても魚に見えるか(蛇骨の最小性)
    densities = [1.0, 0.55, 0.28, 0.14]
    labels = ["full", "1/2", "1/4", "1/8 (最小)"]
    FW, FH = 1500, 560
    pad = 24; top = 96; labelh = 40
    MW = pad + 2 * FW + pad * 2
    MH = top + 2 * (FH + labelh) + pad * 2
    cv = Image.new("RGB", (MW, MH), PAPER)
    dr = ImageDraw.Draw(cv)
    dr.line([(pad, 32), (pad + 320, 32)], fill=TEAL, width=3)
    dr.text((pad, 44), "模様をどこまで間引いても「魚」は残るか", fill=INK, font=f_title)
    for i, (d, lab) in enumerate(zip(densities, labels)):
        im = render(int(FW * 0.96), int(FH * 0.92), arc=0.0, density=d, n_rows=14)
        r = i // 2; c = i % 2
        x = pad + c * (FW + pad); y = top + r * (FH + labelh)
        cv.paste(im, (x, y), im)
        dr.text((x + 6, y + FH + 2), lab, fill=(70, 70, 70), font=f_lab)
    cv.save(_OUT("pattern", "form-reduction.png"))
    print("saved form-reduction.png", cv.size)


if __name__ == "__main__":
    main()
