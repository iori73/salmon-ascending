#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鱗(背景)パターン5種を **実トレース vector の line-art** から生成。
(合成同心円は誤り。Figma 6402:513456 を書き出した scale-lineart.png を共通幾何に使う)
focus(核)は OFF-CENTER(下中央付近・circuliの収束点)。全treatmentは line_alpha + focus距離場 で駆動。
  1 radial : focus距離で暖→寒の放射グラデ、実circuli線を着色
  2 brush  : 実線を掠れ/ドライブラシ化(墨)
  3 ukiyo  : focus距離の藍ぼかし帯 + 実線
  4 wa     : focus距離の淡い和色グラデ + 実線
  5 ink    : 実線に沿う藍インク + 滲み + 粒状
出力: scale-patterns-montage.png + scale-bg-<name>.png
"""
import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import gaussian_filter, binary_closing, binary_fill_holes
from _paths import asset, out as _OUT

SEED = 20260616
PAPER = np.array([250, 250, 246], float)
LINEART = asset("scale-lineart.png")
PROC_W = 1500            # 処理解像度(横)
FOCUS_RATIO = (0.50, 0.71)   # line-art 上の focus 位置(下中央寄り・要視認調整)


def _hex(h): return np.array([int(h[i:i+2], 16) for i in (1, 3, 5)], float)


def fractal_noise(h, w, octaves=5, seed=0):
    rng = np.random.default_rng(SEED + seed)
    out = np.zeros((h, w)); amp = 1.0; tot = 0.0
    for o in range(octaves):
        base = max(2, (8 << o))
        n = rng.standard_normal((max(2, h * base // w if False else max(2, h // (64 // (o + 1) + 1))),
                                 max(2, w // (64 // (o + 1) + 1))))
        n = np.asarray(Image.fromarray(((n - n.min()) / (np.ptp(n) + 1e-9) * 255).astype(np.uint8))
                       .resize((w, h), Image.BILINEAR)) / 255.0
        out += amp * n; tot += amp; amp *= 0.5
    return out / tot


def load_geometry():
    im = Image.open(LINEART).convert("RGBA")
    W0, H0 = im.size
    H = int(PROC_W * H0 / W0)
    im = im.resize((PROC_W, H), Image.BILINEAR)
    arr = np.asarray(im, float) / 255.0
    alpha = arr[..., 3]
    rgb = arr[..., :3]
    lum = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    line = np.clip(alpha * (1 - lum), 0, 1)          # 線の濃さ(0..1)
    line = gaussian_filter(line, 0.6)
    # dome mask: 線領域を閉じて穴埋め
    dome = binary_fill_holes(binary_closing(line > 0.15, np.ones((9, 9))))
    # focus & 距離場
    fx, fy = FOCUS_RATIO[0] * PROC_W, FOCUS_RATIO[1] * H
    ys, xs = np.mgrid[0:H, 0:PROC_W].astype(float)
    dist = np.sqrt((xs - fx) ** 2 + (ys - fy) ** 2)
    dmax = np.percentile(dist[dome], 98) if dome.any() else dist.max()
    D = np.clip(dist / (dmax + 1e-6), 0, 1)          # focus距離 0..1
    return line, dome, D, (PROC_W, H)


def ramp(stops, t):
    st = [(s[0], _hex(s[1])) for s in stops]
    out = np.zeros((*t.shape, 3))
    for i in range(len(st) - 1):
        t0, c0 = st[i]; t1, c1 = st[i + 1]
        m = (t >= t0) & (t <= t1)
        f = ((t[m] - t0) / max(t1 - t0, 1e-6))[:, None]
        out[m] = c0 * (1 - f) + c1 * f
    out[t > st[-1][0]] = st[-1][1]
    out[t < st[0][0]] = st[0][1]
    return out


def compose(field_rgb, field_a, line_rgb, line_a):
    """paper←field←line を合成。field_a/line_a は 0..1。"""
    H, W = line_a.shape
    out = np.ones((H, W, 3)) * PAPER
    out = out * (1 - field_a[..., None]) + field_rgb * field_a[..., None]
    out = out * (1 - line_a[..., None]) + line_rgb * line_a[..., None]
    return np.clip(out, 0, 255)


def p_radial(line, dome, D, sz):
    col = ramp([(0.0, "#E0A24E"), (0.28, "#D9C9A0"), (0.55, "#7FA8C4"),
                (0.80, "#5E7E96"), (1.0, "#33505C")], D)
    field_a = dome.astype(float) * 0.18                       # 淡い地
    line_rgb = col * 0.78                                      # 線は濃いめの同色
    return compose(col, field_a, line_rgb, line * 0.95)


def p_brush(line, dome, D, sz):
    H, W = sz[1], sz[0]
    nz = fractal_noise(H, W, octaves=5, seed=2)
    # かすれ: focus遠いほど掠れやすく(閾値上げ)、払い:太み
    thr = 0.34 + 0.18 * D
    keep = (nz > thr) & (line > 0.12)
    la = np.where(keep, np.clip(line * (0.5 + 1.4 * (nz - thr)), 0, 1), 0.0)
    la = gaussian_filter(la, 0.5)
    sumi = np.zeros((H, W, 3)) + _hex("#26241F")
    return compose(np.zeros((H, W, 3)), np.zeros((H, W)), sumi, la)


def p_ukiyo(line, dome, D, sz):
    # 藍のぼかし帯(smoothstep bands)
    bands = [(0.0, "#ECE7DA"), (0.20, "#9DBBD0"), (0.38, "#3E6E93"), (0.54, "#CFD9DD"),
             (0.70, "#27506E"), (0.86, "#9AAAB4"), (1.0, "#1C3A54")]
    f = D * D * (3 - 2 * D)
    col = ramp(bands, f)
    field_a = dome.astype(float) * 0.92
    line_rgb = col * 0.6
    return compose(col, field_a, line_rgb, line * 0.6)


def p_wa(line, dome, D, sz):
    col = ramp([(0.0, "#ECE6D6"), (0.28, "#C3BE94"), (0.5, "#A6BBA8"),
                (0.7, "#7FA8AE"), (0.86, "#6F7E8E"), (1.0, "#4A5763")], D)
    col = gaussian_filter(col, (8, 8, 0))                     # 穏やかに
    field_a = dome.astype(float) * 0.85
    line_rgb = col * 0.72
    return compose(col, field_a, line_rgb, line * 0.5)


def p_ink(line, dome, D, sz):
    H, W = sz[1], sz[0]
    nz = fractal_noise(H, W, octaves=6, seed=5)
    bleed = gaussian_filter(line, 3.0)                        # にじみ
    ink = np.clip(line * 1.1 + 0.5 * bleed, 0, 1) * (0.7 + 0.6 * nz)
    ink = np.clip(ink, 0, 1) * dome
    indigo = _hex("#2E5E80"); deep = _hex("#16304A")
    line_rgb = indigo[None, None] + (deep - indigo)[None, None] * D[..., None]
    field_a = (gaussian_filter(line, 6) * dome) * 0.25        # 淡い藍地
    field_rgb = indigo[None, None] * np.ones((H, W, 1))
    return compose(field_rgb, field_a, line_rgb, np.clip(ink, 0, 1))


PATTERNS = [("radial", p_radial), ("brush", p_brush), ("ukiyo", p_ukiyo), ("wa", p_wa), ("ink", p_ink)]


def main():
    from PIL import ImageDraw, ImageFont
    line, dome, D, sz = load_geometry()
    print("geometry", sz, "dome px", int(dome.sum()))
    ims = []
    for name, fn in PATTERNS:
        rgb = fn(line, dome, D, sz).astype(np.uint8)
        im = Image.fromarray(rgb); im.save(_OUT("scale-bg", f"scale-bg-{name}.png")); ims.append((name, im))
        print("saved scale-bg-%s.png" % name)
    th = 520; pad = 24; lab = 34
    try: f = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 22)
    except: f = ImageFont.load_default()
    titles = {"radial": "1 radial gradient", "brush": "2 ブラシ線(かすり/払い)", "ukiyo": "3 浮世絵ぼかし",
              "wa": "4 静かな和グラデ", "ink": "5 水彩インクにじみ"}
    cols = 5; MW = pad + cols * (th + pad); MH = pad + lab + th + pad
    cv = Image.new("RGB", (MW, MH), (255, 255, 255)); dr = ImageDraw.Draw(cv)
    for i, (name, im) in enumerate(ims):
        t = im.resize((th, int(th * im.height / im.width))); x = pad + i * (th + pad); y = pad + lab
        cv.paste(t, (x, y)); dr.text((x, pad), titles[name], fill=(30, 30, 30), font=f)
    cv.save(_OUT("scale-bg", "scale-patterns-montage.png")); print("saved montage", cv.size)


if __name__ == "__main__":
    main()
