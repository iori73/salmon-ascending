#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fish_top_soft.py — 真上(背側)から見たサケ7段階を「やわらかいグラデーション」で描く(点描でない最終形)。
fish_top の幾何(build/bend/幅プロファイル)を流用。段階別に: 姿勢(bend)・幅(wscale)・背側配色ランプ・
背正中線・横帯(パー/カリコ鞍)・微細点(海洋)・卵黄嚢(仔魚)・カイプ(遡上/産卵後)・ひれ侵食(産卵後)。
出力: out/top/soft-<n>-<slug>.png(透過RGBA) と soft-top-montage.png。SVG は make_top_svg.py。
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
import fish_top as FT

_DIR = os.path.dirname(os.path.abspath(__file__))
_OUT = os.path.join(_DIR, "out", "top")
os.makedirs(_OUT, exist_ok=True)
PAPER = (250, 250, 246)


def hx(s):
    s = s.lstrip("#"); return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], float)


def ramp3(c0, c1, c2, f):
    f = np.clip(f, 0, 1)[..., None]
    lo = c0[None, None] * (1 - 2 * f) + c1[None, None] * (2 * f)
    hi = c1[None, None] * (1 - (2 * f - 1)) + c2[None, None] * (2 * f - 1)
    return np.where(f < 0.5, lo, hi)


# 真上(背側)の段階仕様。c0=稜線(中央) c1=中間 c2=側縁。bend=遊泳姿勢, wscale=幅。
# bartype: none/parr/calico。bar_col=帯色。実物基準(真上では銀腹/赤紫flankは不可視→背の暗色が主役)。
SOFT = [
    dict(n=1, slug="alevin", jp="①仔魚", bend=(0, 0, 0, 0), wscale=0.70,
         c0="#EEF2F6", c1="#DCE3EA", c2="#BFC9D3", mid=None, bartype="none",
         yolk=True, tail=True, head_bulb=True, eye_t=0.045, eye_sep=0.020),
    dict(n=2, slug="parr", jp="②稚魚", bend=(0, 0.04, 0.04, 0), wscale=0.80,
         c0="#B3B79C", c1="#8C9270", c2="#5C6446", mid="#343C2C", bartype="parr",
         barcount=9, baramp=0.55, bar_col="#2E3727", tail=True, eye_t=0.05, eye_sep=0.026),
    dict(n=3, slug="smolt", jp="③スモルト", bend=(0, 0.10, 0.10, 0), wscale=0.84,
         c0="#C9CFD4", c1="#9AA6B1", c2="#566B76", mid="#3C4C58",
         bartype="none", speckle=0.04, tail=True, eye_t=0.05, eye_sep=0.028),
    dict(n=4, slug="ocean", jp="④海洋", bend=(0, 0.08, 0.08, 0), wscale=1.0,
         c0="#C2CBCC", c1="#7E9193", c2="#39535B", mid="#22302A", bartype="none",
         speckle=0.03, tail=True, eye_t=0.05, eye_sep=0.030),
    dict(n=5, slug="coastal", jp="⑤沿岸", bend=(0.04, 0.20, -0.11, 0.04), wscale=0.98,
         c0="#ACB096", c1="#7D8160", c2="#454D34", mid="#2C3422", bartype="parr",
         barcount=9, baramp=0.22, bar_col="#3A4230", tail=True, eye_t=0.05, eye_sep=0.030),
    dict(n=6, slug="river", jp="⑥遡上", bend=(0.057, 0.25, -0.14, 0.057), wscale=0.92,
         c0="#9AA158", c1="#6E7740", c2="#33401F", mid="#26301D", bartype="calico",
         barcount=8, baramp=0.6, bar_col="#5A3A4E", bar_dark="#26301D",
         kype=True, tail=True, eye_t=0.05, eye_sep=0.030),
    dict(n=7, slug="postspawn", jp="⑦産卵後", bend=(0, 0.09, 0.05, 0), wscale=0.84,
         c0="#8C8C76", c1="#65654E", c2="#3A3A28", mid="#2A2A1C", bartype="calico",
         barcount=8, baramp=0.45, bar_col="#6A4B41", bar_dark="#2A2A1C",
         kype=True, erode=True, tail=True, eye_t=0.05, eye_sep=0.030),
]
BY_N = {s["n"]: s for s in SOFT}


def render_soft(W, H, n, SS=3, bar1d=None):
    """bar1d=(u,prof): 体軸u(0..1)に沿う柄強度プロファイル。与えると cosine 擬似縞の代わりに
    これ(=本物の反応拡散場の沿軸プロファイル)で帯を描く。None なら従来通り cosine。"""
    sp = BY_N[n]
    Ws, Hs = W * SS, H * SS
    t, m, body, tr = FT.build(Ws, Hs, bend=sp["bend"], wscale=sp.get("wscale", 1.0))
    ox, oy, L, bend = tr
    ys, xs = np.mgrid[0:Hs, 0:Ws].astype(float)
    am = np.abs(m)
    rng = np.random.default_rng(7 * n + 3)

    # --- 形状(body + 任意の尾 + 頭丸め + カイプ) ---
    shape = ((t >= 0) & (t <= 0.885) & (am <= 1.0)).astype(float)
    if sp.get("tail"):
        im = Image.new("L", (Ws, Hs), 0); d = ImageDraw.Draw(im)
        d.polygon([(float(x), float(y)) for x, y in FT.caudal_poly(tr)], fill=255)
        shape = np.clip(shape + (np.array(im) > 128), 0, 1)
    if sp.get("head_bulb"):
        hcy = oy - FT._center(np.array([0.035]), bend)[0] * L
        hb = np.exp(-((((xs - (ox + 0.040 * L)) / (0.052 * L)) ** 2) + (((ys - hcy) / (0.030 * L)) ** 2)))
        shape = np.clip(shape + (hb > 0.45), 0, 1)
    if sp.get("kype"):                                   # 鉤状の吻(真上では頭をやや伸ばし尖らす)
        kcy = oy - FT._center(np.array([0.0]), bend)[0] * L
        kp = ((xs < ox + 0.02 * L) & (xs > ox - 0.05 * L)
              & (np.abs(ys - kcy) < 0.018 * L))
        shape = np.clip(shape + kp, 0, 1)
    if sp.get("erode"):                                  # ひれ・尾をボロボロに(縁を虫食い)
        noise = gaussian_filter(rng.standard_normal((Hs, Ws)), Ws * 0.004)
        shape *= (noise > -0.4) | (am < 0.6)
    alpha = gaussian_filter(shape, Ws * 0.006)
    alpha = np.clip(alpha * 1.18, 0, 1)

    # --- 体色(稜線→側縁) + 背正中線 ---
    col = ramp3(hx(sp["c0"]), hx(sp["c1"]), hx(sp["c2"]), am)
    ridge = np.exp(-(m ** 2) / (2 * 0.18 ** 2))
    col = col * (1 - 0.10 * ridge[..., None]) + np.array([255, 255, 255])[None, None] * (0.10 * ridge[..., None])
    if sp.get("mid"):
        mid = hx(sp["mid"]); dm = np.exp(-(m ** 2) / (2 * 0.10 ** 2))
        col = col * (1 - 0.55 * dm[..., None]) + mid[None, None] * (0.55 * dm[..., None])

    # --- 横帯(真上=体軸方向に並ぶ暗帯。パー/カリコ鞍) ---
    bt = sp.get("bartype", "none")
    if bt in ("parr", "calico"):
        nb = sp.get("barcount", 8); amp = sp.get("baramp", 0.4)
        jag = gaussian_filter(rng.standard_normal((Hs, Ws)), (Ws * 0.004, Ws * 0.012))
        jag = jag / (np.abs(jag).max() + 1e-9)
        tt = np.clip(t / 0.86, 0, 1) + 0.03 * jag
        if bar1d is not None:                            # 本物RD場の沿軸プロファイル
            uu, pp = bar1d
            wv = np.interp(np.clip(tt, 0, 1), uu, pp)
        else:                                            # 従来=cosine擬似縞
            wv = 0.5 + 0.5 * np.cos(2 * np.pi * nb * tt)
        if bt == "parr":
            bars = np.clip((wv - 0.55) / 0.45, 0, 1)
            bars *= np.clip(0.30 + 0.70 * am, 0, 1)        # 体側ほど濃い
            bc = hx(sp["bar_col"])
            col = col * (1 - (amp * bars)[..., None]) + bc[None, None] * (amp * bars)[..., None]
        else:  # calico: 赤紫鞍(側) + 暗緑黒核
            bars = np.clip((wv - 0.4) / 0.6, 0, 1) ** 1.1
            bc = hx(sp["bar_col"]); bd = hx(sp.get("bar_dark", sp["bar_col"]))
            flank = np.clip(am - 0.15, 0, 1)               # 真上では鞍は上flankに見える
            col = col * (1 - (amp * bars * flank)[..., None]) + bc[None, None] * (amp * bars * flank)[..., None]
            core = (amp * bars * np.exp(-(m ** 2) / (2 * 0.22 ** 2)))[..., None]
            col = col * (1 - 0.6 * core) + bd[None, None] * (0.6 * core)
    if sp.get("speckle"):
        sp2 = gaussian_filter((rng.random((Hs, Ws)) > 0.992).astype(float), Ws * 0.0016)
        col = col * (1 - (sp.get("speckle") * 4 * sp2)[..., None]) + np.array([40, 60, 70])[None, None] * (sp.get("speckle") * 4 * sp2)[..., None]

    A = alpha.copy(); RGB = np.clip(col, 0, 255)

    # --- 卵黄嚢(仔魚) ---
    if sp.get("yolk"):
        ty = 0.16; cxx = ox + ty * L; cyy = oy - FT._center(np.array([ty]), bend)[0] * L
        g = np.clip(np.exp(-((((xs - cxx) / (0.075 * L)) ** 2) + (((ys - cyy) / (0.058 * L)) ** 2))), 0, 1)
        yc = hx("#EE7A38"); yhi = hx("#F6A766")
        ycol = yhi[None, None] * g[..., None] + yc[None, None] * (1 - g[..., None])
        ya = g * 0.92
        A = np.clip(A + ya * (1 - A), 0, 1)
        RGB = RGB * (1 - ya[..., None]) + ycol * ya[..., None]

    # --- 目(真上=左右2点) ---
    et = sp.get("eye_t", 0.05); ecx = ox + et * L
    ecy = oy - FT._center(np.array([et]), bend)[0] * L
    esep = sp.get("eye_sep", 0.026) * L
    for s in (+1, -1):
        de = (((xs - ecx) ** 2 + (ys - (ecy + s * esep)) ** 2) < (0.0135 * L) ** 2)
        RGB[de] = [40, 42, 46]; A[de] = 1.0

    rgba = np.zeros((Hs, Ws, 4), float); rgba[..., :3] = RGB; rgba[..., 3] = A * 255
    img = Image.fromarray(np.clip(rgba, 0, 255).astype(np.uint8), "RGBA")
    return img.resize((W, H), Image.LANCZOS)


def vertical(n, W=300, Hh=720, bar1d=None):
    """頭=下・尾=上の縦向き透過PNGを返す。bar1d を渡すと本物RD柄で描く。"""
    horiz = render_soft(Hh, W, n, bar1d=bar1d)   # 横(頭=左)
    return horiz.rotate(90, expand=True)         # 頭を下へ


def main():
    try:
        ft = ImageFont.truetype("/System/Library/Fonts/ヒラギノ明朝 ProN.ttc", 40)
        fl = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 22)
    except Exception:
        ft = fl = ImageFont.load_default()
    W, Hh = 280, 680
    for sp in SOFT:
        v = vertical(sp["n"], W, Hh)
        p = os.path.join(_OUT, f"soft-{sp['n']}-{sp['slug']}.png"); v.save(p)
        print("saved", os.path.basename(p), v.size)
    # montage
    cw, ch = W, Hh; pad = 18; top = 84; labh = 34
    MW = pad + len(SOFT) * (cw + pad); MH = top + ch + labh + pad
    cv = Image.new("RGB", (MW, MH), PAPER); dr = ImageDraw.Draw(cv)
    dr.line([(pad, 30), (pad + 300, 30)], fill=(46, 110, 142), width=3)
    dr.text((pad, 42), "ソフト・真上(背側) 7段階 — 泳ぎ上がる姿勢", fill=(40, 40, 36), font=ft)
    for i, sp in enumerate(SOFT):
        v = Image.open(os.path.join(_OUT, f"soft-{sp['n']}-{sp['slug']}.png"))
        x = pad + i * (cw + pad); cv.paste(v, (x, top), v)
        dr.text((x + 4, top + ch + 2), sp["jp"], fill=(60, 60, 60), font=fl)
    p = os.path.join(_OUT, "soft-top-montage.png"); cv.save(p); print("saved", p, cv.size)


if __name__ == "__main__":
    main()
