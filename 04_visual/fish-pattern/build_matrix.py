#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
組み合わせマトリクス: 鱗5(背景) × 魚4(前景の7匹スパイラル)。
各セル = 鱗パターン背景 に 7匹の生活史スパイラルを重ねる。
fish styles: stipple(点描・真上) / outline(アウトライン無し) / turing(反応拡散) / watercolor(Gemini)
出力: matrix-<style>-row.png (検証用) / combo-matrix.png (全体)
"""
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
import fish_top as T
import pattern_form as F
from turing_zoo import gray_scott
from _paths import out as _OUT

SEED = 20260621
PAPER = (250, 250, 246)

# 背景は scale_patterns.py / scale_ink.py の出力(out/scale-bg/)を入力に取る
SCALE_BGS = [
    ("radial", _OUT("scale-bg", "scale-bg-radial.png")),
    ("brush",  _OUT("scale-bg", "scale-bg-brush.png")),
    ("ukiyo",  _OUT("scale-bg", "scale-bg-ukiyo.png")),
    ("wa",     _OUT("scale-bg", "scale-bg-wa.png")),
    ("ink",    _OUT("scale-bg", "scale-ink-v2.png")),
]

# 7匹スパイラル配置(compose_radial と同じ)
LAYOUT = [
    (1,  12, 0.130, 5), (2, 62, 0.225, 8), (3, 112, 0.330, 12), (4, 168, 0.500, 42),
    (5, 228, 0.680, 62), (6, 292, 0.825, 65), (7, 346, 0.945, 70),
]


def fish_stipple(st, fw, fh):
    im, _ = T.render_top(fw, fh, st, dot_k=0.05, colored=True, supersample=2)
    return im


def fish_outline(st, fw, fh):
    # pattern_form は横向き・1尾(scale-scallop線画)。stに応じ体高/密度は固定でOK
    return F.render(fw, fh, arc=0.0, density=1.0, n_rows=14, supersample=2)


def fish_turing(st, fw, fh):
    """背側シルエットに反応拡散(Gray-Scott)を充填した魚。実測色で2トーン。"""
    t, m, body, tr = T.build(fw, fh, bend=st.get("bend", (0, 0, 0, 0)))
    caud = T._raster(fw, fh, [T.caudal_poly(tr)])
    pect = T._raster(fw, fh, T.pectoral_polys(tr))
    full = body | caud | pect
    # Gray-Scott(縦バイアス=婚姻色/パー段階は縞、他は斑)
    bt = st.get("bartype", "none")
    ax, ay = (0.5, 1.6) if bt in ("parr", "nuptial") else (1.0, 1.0)
    V = gray_scott(110, 230, 0.038, 0.061, 0.14, 0.07, ax=ax, ay=ay, steps=4500, salt=st["n"])
    Vu = np.asarray(Image.fromarray((np.clip(V, 0, 1) * 255).astype(np.uint8)).resize((fw, fh), Image.BILINEAR)) / 255.0
    two = (Vu > np.median(Vu[full])).astype(float)
    # 色: stageのdorsal ramp(暗/明)
    stops = T.color_ramp(st["n"])
    dark = stops[-1][1]; light = stops[0][1]
    img = np.zeros((fh, fw, 4))
    img[..., :3] = light[None, None] * (1 - two[..., None]) + dark[None, None] * two[..., None]
    soft = gaussian_filter(full.astype(float), fw * 0.004)
    img[..., 3] = np.clip(soft, 0, 1) * 255
    return Image.fromarray(img.astype(np.uint8), "RGBA")


FISH_FNS = {"stipple": fish_stipple, "outline": fish_outline, "turing": fish_turing}


def spiral_layer(style, S=1500):
    """透明キャンバスに7匹スパイラルを配置して返す(背景なし)。"""
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cx = cy = S / 2
    Rmax = S * 0.44
    fn = FISH_FNS[style]
    for n, ang, rfrac, lcm in LAYOUT:
        st = [s for s in T.STAGES if s["n"] == n][0]
        Lpx = int(40 + lcm * 7.6)                     # 魚を拡大
        fw = int(Lpx / (1 - 2 * 0.07)); fh = int(fw * 0.42)
        im = fn(st, fw, fh)
        th = np.radians(ang); r = Rmax * rfrac
        px = cx + r * np.sin(th); py = cy - r * np.cos(th)
        tang = np.degrees(np.arctan2(np.sin(th), np.cos(th)))
        rim = im.rotate(-(tang + 180), expand=True, resample=Image.BICUBIC)
        layer.alpha_composite(rim, (int(px - rim.width / 2), int(py - rim.height / 2)))
    return layer


def cell(bg_path, style, S=1500):
    bg = Image.open(bg_path).convert("RGB")
    # 正方キャンバスに中央寄せでbgを敷く
    c = Image.new("RGB", (S, S), PAPER)
    bw, bh = bg.size; sc = S / max(bw, bh); bg = bg.resize((int(bw*sc), int(bh*sc)))
    c.paste(bg, ((S - bg.width)//2, (S - bg.height)//2))
    c = c.convert("RGBA")
    c.alpha_composite(spiral_layer(style, S))
    return c.convert("RGB")


def row(style):
    from PIL import ImageFont
    S = 1100; pad = 16; lab = 30
    try: f = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 22)
    except: f = ImageFont.load_default()
    cols = len(SCALE_BGS)
    MW = pad + cols * (S + pad); MH = pad + lab + S + pad
    cv = Image.new("RGB", (MW, MH), (255, 255, 255)); dr = ImageDraw.Draw(cv)
    for i, (name, path) in enumerate(SCALE_BGS):
        im = cell(path, style, S=S)
        x = pad + i*(S+pad); y = pad+lab
        cv.paste(im, (x, y)); dr.text((x+4, pad), f"{style} × {name}", fill=(30,30,30), font=f)
    out = _OUT("matrix", f"matrix-{style}-row.png"); cv.save(out); print("saved", out, cv.size)


def build_all(styles, S=1000):
    from PIL import ImageFont
    pad = 18; labw = 150; topb = 34
    try:
        f = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 26)
        fs = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 22)
    except Exception:
        f = fs = ImageFont.load_default()
    cols = len(SCALE_BGS); rows = len(styles)
    MW = labw + pad + cols * (S + pad)
    MH = topb + pad + rows * (S + pad)
    cv = Image.new("RGB", (MW, MH), (255, 255, 255)); dr = ImageDraw.Draw(cv)
    for ci, (name, _) in enumerate(SCALE_BGS):
        dr.text((labw + pad + ci * (S + pad) + 6, 6), name, fill=(20, 20, 20), font=fs)
    for ri, style in enumerate(styles):
        y = topb + pad + ri * (S + pad)
        dr.text((6, y + S // 2), style, fill=(20, 20, 20), font=f)
        for ci, (name, path) in enumerate(SCALE_BGS):
            im = cell(path, style, S=S)
            cv.paste(im, (labw + pad + ci * (S + pad), y))
            print("  cell", style, name, "done")
    cv.save(_OUT("matrix", "combo-matrix.png")); print("saved combo-matrix.png", cv.size)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        build_all(["stipple", "outline", "turing"])
    else:
        row(sys.argv[1] if len(sys.argv) > 1 else "stipple")
