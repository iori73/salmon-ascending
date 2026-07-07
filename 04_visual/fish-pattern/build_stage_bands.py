#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""均一細線(build_lines_simple)を focus 中心の半径で 7 つの生活史段階の帯に分割する。
各帯は境界半径で線を正確に切断して切り出すので、7枚を重ねると元の1枚の鱗に戻る。
帯ごとに色分け(暖→寒の水温配色)し、検証用の合成図(境界円＋凡例)も出力。

stage 境界半径(Figma node 6573:223440 stages テンプレより。最大半径=712.205 に対する割合):
  1 仔魚     0      –  6.67%
  2 稚魚     6.67%  – 10.67%
  3 スモルト 10.67% – 16.00%
  4 海洋回遊期16.00% – 93.33%   ← 成長の主舞台(大半)
  5 沿岸回帰期93.33% – 94.67%
  6 河川遡上期94.67% – 96.00%
  7 産卵後   96.00% –100.00%
出力: scale-stage-{k}-{slug}@2x.png / .svg (透過) と scale-stages-combined@2x.png
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pathlib
from build_lines_simple import build_polys, VBW, VBH, SUPERSAMPLE, PNG_SCALE
from _paths import out

HERE = pathlib.Path(__file__).parent

# 生命感: 仔魚(誕生)を太く → 産卵後(終焉)へ細く、段階ごとに線幅をテーパ
STROKE_MAX, STROKE_MIN = 4.0, 1.0
STROKE_BY_STAGE = list(np.linspace(STROKE_MAX, STROKE_MIN, 7))

# ===== ノブ =====
# focus(年輪の収束核)= scale-ink-kasure-grad の inkgrad 中心と同じ
FOCUS = (706.0, 795.0)
# stage 境界(最大半径に対する割合)。0 と 1.0 を含む 8 値 = 7 帯
FRACS = [0.0, 0.0667, 0.1067, 0.1600, 0.9333, 0.9467, 0.9600, 1.0]

STAGES = [
    ("仔魚",       "shigyo",  "#E8B84B"),  # 暖・金(誕生・淡水)
    ("稚魚",       "chigyo",  "#C9A86A"),  # 黄褐
    ("スモルト",   "smolt",   "#8FA98C"),  # セージ(降海)
    ("海洋回遊期", "ocean",   "#4E8E9E"),  # ティール(冷たい外洋・最長)
    ("沿岸回帰期", "coastal", "#4A6E96"),  # スティールブルー
    ("河川遡上期", "river",   "#4C5A82"),  # スレート藍
    ("産卵後",     "spawn",   "#3A3F5C"),  # 濃紺(終焉)
]

FONT_PATH = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def build_outline(polys, focus, nbins=180, pct=92, smooth=6):
    """角度ごとの輪郭半径 outline(θ) を作る。鱗のドーム形に沿った正規化に使う。
    戻り値: angle(rad,-pi..pi)→radius を返す関数。"""
    fx, fy = focus
    pts = np.vstack(polys)
    ang = np.arctan2(pts[:, 1] - fy, pts[:, 0] - fx)
    rad = np.hypot(pts[:, 0] - fx, pts[:, 1] - fy)
    bins = np.linspace(-np.pi, np.pi, nbins + 1)
    idx = np.clip(np.digitize(ang, bins) - 1, 0, nbins - 1)
    out = np.full(nbins, np.nan)
    for k in range(nbins):
        rk = rad[idx == k]
        if len(rk) >= 3:
            out[k] = np.percentile(rk, pct)
    # 空ビンを円環補間
    good = ~np.isnan(out)
    centers = (bins[:-1] + bins[1:]) / 2
    if not good.all():
        ext_c = np.concatenate([centers[good] - 2*np.pi, centers[good], centers[good] + 2*np.pi])
        ext_v = np.tile(out[good], 3)
        out = np.interp(centers, ext_c, ext_v)
    # 円環ガウス平滑
    pad = np.concatenate([out[-smooth*3:], out, out[:smooth*3]])
    ker = np.exp(-0.5*(np.arange(-smooth*3, smooth*3+1)/smooth)**2); ker /= ker.sum()
    sm = np.convolve(pad, ker, mode="same")[smooth*3:-smooth*3]

    def f(a):
        return np.interp(a, centers, sm, period=2*np.pi)
    return f


def band_of(rn, edges):
    b = int(np.searchsorted(edges, rn, side="right") - 1)
    return min(max(b, 0), len(edges) - 2)


def split_by_band(poly, rn, edges):
    """正規化半径 rn(各点) を境界 edges で切断し、(band, points) のラン列に分ける。"""
    runs = []
    cur = [poly[0]]
    cur_band = band_of(rn[0], edges)
    interior = edges[1:-1]
    for i in range(1, len(poly)):
        A, B = poly[i - 1], poly[i]
        rA, rB = rn[i - 1], rn[i]
        bA, bB = band_of(rA, edges), band_of(rB, edges)
        if bA == bB:
            cur.append(B)
            continue
        lo, hi = (rA, rB) if rA < rB else (rB, rA)
        cand = sorted([e for e in interior if lo < e < hi], reverse=(rB < rA))
        seg_band = bA
        for e in cand:
            t = (e - rA) / (rB - rA)
            X = A + t * (B - A)
            cur.append(X)
            runs.append((seg_band, cur))
            cur = [X]
            seg_band += 1 if bB > bA else -1
        cur.append(B)
        cur_band = bB
    runs.append((cur_band, cur))
    return runs


def stroke_polys(dr, polys, color, S, sw):
    w = max(1, int(round(sw * S)))
    rcap = w / 2.0
    col = color + (255,)
    for poly in polys:
        if len(poly) < 2:
            continue
        pts = [(float(x) * S, float(y) * S) for x, y in poly]
        dr.line(pts, fill=col, width=w, joint="curve")
        for (px, py) in (pts[0], pts[-1]):
            dr.ellipse([px - rcap, py - rcap, px + rcap, py + rcap], fill=col)


def render_band(polys, color, out, sw):
    S = SUPERSAMPLE * PNG_SCALE
    img = Image.new("RGBA", (VBW * S, VBH * S), (0, 0, 0, 0))
    stroke_polys(ImageDraw.Draw(img), polys, color, S, sw)
    img = img.resize((VBW * PNG_SCALE, VBH * PNG_SCALE), Image.LANCZOS)
    img.save(out)


def write_band_svg(polys, color, out, sw):
    hexc = "#%02X%02X%02X" % color
    parts = [f'<svg width="{VBW}" height="{VBH}" viewBox="0 0 {VBW} {VBH}" '
             f'xmlns="http://www.w3.org/2000/svg">',
             f'<g fill="none" stroke="{hexc}" stroke-width="{sw:.2f}" '
             f'stroke-linecap="round" stroke-linejoin="round">']
    for poly in polys:
        if len(poly) < 2:
            continue
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in poly)
        parts.append(f'<path d="{d}"/>')
    parts.append("</g></svg>")
    out.write_text("\n".join(parts))


def write_combined_svg(bands, out):
    """全7帯を色分けして1枚にまとめたベクター(透過)。Figmaに直接ドラッグ可。"""
    parts = [f'<svg width="{VBW}" height="{VBH}" viewBox="0 0 {VBW} {VBH}" '
             f'xmlns="http://www.w3.org/2000/svg">']
    for k, (name, slug, hexc) in enumerate(STAGES):
        parts.append(f'<g id="stage-{k+1}-{slug}" fill="none" stroke="{hexc}" '
                     f'stroke-width="{STROKE_BY_STAGE[k]:.2f}" stroke-linecap="round" stroke-linejoin="round">')
        for poly in bands[k]:
            if len(poly) < 2:
                continue
            d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in poly)
            parts.append(f'<path d="{d}"/>')
        parts.append("</g>")
    parts.append("</svg>")
    out.write_text("\n".join(parts))


def render_combined(bands, outline, out):
    """全帯を色付きで重ね、境界輪郭＋凡例を描いた検証用(白地)。"""
    S = SUPERSAMPLE * PNG_SCALE
    img = Image.new("RGBA", (VBW * S, VBH * S), (255, 255, 255, 255))
    dr = ImageDraw.Draw(img)
    for k, (name, slug, hexc) in enumerate(STAGES):
        stroke_polys(dr, bands[k], hex2rgb(hexc), S, STROKE_BY_STAGE[k])
    # 境界輪郭(鱗形に沿う・細い灰): r = frac*outline(θ)
    fx, fy = FOCUS
    th = np.linspace(-np.pi, np.pi, 361)
    for frac in FRACS[1:]:
        rr = frac * outline(th)
        xs = (fx + rr * np.cos(th)) * S
        ys = (fy + rr * np.sin(th)) * S
        dr.line(list(zip(xs, ys)), fill=(120, 120, 120, 150), width=max(1, int(round(1.0 * S))))
    img = img.resize((VBW * PNG_SCALE, VBH * PNG_SCALE), Image.LANCZOS)
    # 凡例(色スウォッチ＋段階名)
    dr2 = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT_PATH, 30)
    except Exception:
        font = ImageFont.load_default()
    x0, y0, dy = 40, 40, 56
    for k, (name, slug, hexc) in enumerate(STAGES):
        y = y0 + k * dy
        dr2.rectangle([x0, y, x0 + 40, y + 40], fill=hex2rgb(hexc))
        pct = f"{FRACS[k]*100:.0f}–{FRACS[k+1]*100:.0f}%"
        dr2.text((x0 + 54, y + 4), f"{k+1}. {name}  ({pct})", fill=(40, 40, 40), font=font)
    img.save(out)


def main():
    polys = build_polys()
    fx, fy = FOCUS
    outline = build_outline(polys, FOCUS)
    edges = list(FRACS)                      # 正規化空間 [0..1]
    print(f"focus={FOCUS}  normalize=angular-outline")

    bands = [[] for _ in STAGES]
    for poly in polys:
        ang = np.arctan2(poly[:, 1] - fy, poly[:, 0] - fx)
        rad = np.hypot(poly[:, 0] - fx, poly[:, 1] - fy)
        rn = rad / np.maximum(outline(ang), 1e-6)
        for b, pts in split_by_band(poly, rn, edges):
            if len(pts) >= 2:
                bands[b].append(np.asarray(pts))
    for k, (name, slug, hexc) in enumerate(STAGES):
        seg = sum(len(p) for p in bands[k])
        sw = STROKE_BY_STAGE[k]
        print(f"  stage {k+1} {name:6} runs={len(bands[k]):4d} pts={seg} sw={sw:.2f}")
        col = hex2rgb(hexc)
        render_band(bands[k], col, out("stage-scale", f"scale-stage-{k+1}-{slug}@2x.png"), sw)
        write_band_svg(bands[k], col, out("stage-scale", f"scale-stage-{k+1}-{slug}.svg"), sw)

    render_combined(bands, outline, out("stage-scale", "scale-stages-combined@2x.png"))
    write_combined_svg(bands, out("stage-scale", "scale-stages-combined.svg"))
    print("done. combined -> scale-stages-combined@2x.png / scale-stages-combined.svg")


if __name__ == "__main__":
    main()
