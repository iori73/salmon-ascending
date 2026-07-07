#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_top_stipple.py — 真上(背側)7段階の点描(stipple)版。fish_top の濃度場+重み付きボロノイ点を流用。
縦・頭=下に揃え(soft版と同じ向き)、仔魚は直線(bend=0)+卵黄嚢+目。各点= PNG(円) と SVG(<circle>)。
出力: out/top/stip-<n>-<slug>.png / .svg と stip-top-montage.png。
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import fish_top as FT

_DIR = os.path.dirname(os.path.abspath(__file__))
_OUT = os.path.join(_DIR, "out", "top")
os.makedirs(_OUT, exist_ok=True)
PAPER = (250, 250, 246)
SLUG = {1: "alevin", 2: "parr", 3: "smolt", 4: "ocean", 5: "coastal", 6: "river", 7: "postspawn"}
YOLK = (238, 122, 56)


def stage_points(st, Wc=900, Hc=300, dot_k=0.05):
    """horizontal 濃度場→点。返り: pts[(x,y)], rad[], rgb[](0-255), tr, (Wc,Hc)。縦変換は呼び出し側。"""
    bend = (0, 0, 0, 0) if st["n"] == 1 else st.get("bend", (0, 0, 0, 0))
    D, full, tr, cmap = FT.density_top(Wc, Hc, st, bend=bend)
    ox, oy, L, _ = tr
    n_pts = int(D.sum() * dot_k)
    pts, di = FT.weighted_voronoi(D, n_pts, seed=st["n"] + 50)
    stops = FT.color_ramp(st["n"])
    P, R, C = [], [], []
    for (x, y), d in zip(pts, di):
        r = 0.55 + 1.7 * np.sqrt(max(d, 0))
        if cmap is not None:
            c = cmap[int(np.clip(y, 0, Hc - 1)), int(np.clip(x, 0, Wc - 1))]
        else:
            c = FT.ramp_color(stops, d)
        # 仔魚: 卵黄嚢域の点をオレンジに
        if st["n"] == 1:
            t = (x - ox) / L
            if 0.10 < t < 0.225 and abs(y - oy) < 0.075 * L:
                c = np.array(YOLK, float)
        P.append((x, y)); R.append(r); C.append((int(c[0]), int(c[1]), int(c[2])))
    return P, R, C, tr, (Wc, Hc)


def to_vertical(x, y, Wc):
    """horizontal(頭=左,x沿軸) → 縦(頭=下)。新canvas: 幅=Hc, 高=Wc。"""
    return y, Wc - x


def render(st, Wc=900, Hc=300, SS=2, dot_k=0.05):
    P, R, C, tr, _ = stage_points(st, Wc, Hc, dot_k)
    ox, oy, L, _ = tr
    Wv, Hv = Hc, Wc                     # 縦canvas
    # PNG
    img = Image.new("RGBA", (Wv * SS, Hv * SS), (0, 0, 0, 0)); dr = ImageDraw.Draw(img, "RGBA")
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wv}" height="{Hv}" viewBox="0 0 {Wv} {Hv}">']
    for (x, y), r, c in zip(P, R, C):
        vx, vy = to_vertical(x, y, Wc)
        a = 200
        dr.ellipse([(vx - r) * SS, (vy - r) * SS, (vx + r) * SS, (vy + r) * SS],
                   fill=(c[0], c[1], c[2], a))
        svg.append(f'<circle cx="{vx:.1f}" cy="{vy:.1f}" r="{r:.2f}" fill="rgb({c[0]},{c[1]},{c[2]})" fill-opacity="0.8"/>')
    # 目(仔魚: 真上=左右2点)
    if st["n"] == 1:
        et = 0.05; ex = ox + et * L
        for s in (+1, -1):
            ey = oy + s * 0.020 * L
            vx, vy = to_vertical(ex, ey, Wc); rr = 0.018 * L
            dr.ellipse([(vx - rr) * SS, (vy - rr) * SS, (vx + rr) * SS, (vy + rr) * SS], fill=(40, 42, 46, 255))
            svg.append(f'<circle cx="{vx:.1f}" cy="{vy:.1f}" r="{rr:.1f}" fill="#282A2E"/>')
    svg.append('</svg>')
    png = img.resize((Wv, Hv), Image.LANCZOS)
    return png, "".join(svg)


def main():
    try:
        ft = ImageFont.truetype("/System/Library/Fonts/ヒラギノ明朝 ProN.ttc", 40)
        fl = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 22)
    except Exception:
        ft = fl = ImageFont.load_default()
    pngs = []
    for st in FT.STAGES:
        png, svg = render(st)
        slug = SLUG[st["n"]]
        png.save(os.path.join(_OUT, f"stip-{st['n']}-{slug}.png"))
        open(os.path.join(_OUT, f"stip-{st['n']}-{slug}.svg"), "w").write(svg)
        pngs.append((st, png))
        print("saved stip-%d-%s.png/.svg" % (st["n"], slug))
    # montage
    cw, ch = pngs[0][1].size; pad = 18; top = 84; labh = 34
    MW = pad + len(pngs) * (cw + pad); MH = top + ch + labh + pad
    cv = Image.new("RGB", (MW, MH), PAPER); dr = ImageDraw.Draw(cv)
    dr.line([(pad, 30), (pad + 300, 30)], fill=(46, 110, 142), width=3)
    dr.text((pad, 42), "点描・真上(背側) 7段階 — 泳ぎ上がる姿勢", fill=(40, 40, 36), font=ft)
    for i, (st, png) in enumerate(pngs):
        x = pad + i * (cw + pad); cv.paste(png, (x, top), png)
        dr.text((x + 4, top + ch + 2), f"{st['n']} {SLUG[st['n']]}", fill=(60, 60, 60), font=fl)
    p = os.path.join(_OUT, "stip-top-montage.png"); cv.save(p); print("saved", p, cv.size)


if __name__ == "__main__":
    main()
