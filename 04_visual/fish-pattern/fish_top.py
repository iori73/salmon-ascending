#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真上(背側 dorsal view)から見たサケ — 放射状の鱗(circuli=波)の上を泳ぐ最終形用。
横向き(fish_geom)と別ジオメトリ: 左右対称の流線形 + 遊泳のうねり(S字) + 胸びれ張り出し + 水平尾扇。
点描エンジン(重み付きボロノイ stipple_art.weighted_voronoi)を流用し、背側の濃度場を作る。
"""
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter

from stipple_art import weighted_voronoi, PAPER, SUMI
SEED = 20260615

import json, os
from _paths import out as _OUT
_DIR = os.path.dirname(os.path.abspath(__file__))
_CAL = json.load(open(os.path.join(_DIR, "calibration.json")))

# --- 実写抽出パターン(extract_pattern.py 出力)を使う。あれば procedural より優先 ---
_TILE_CACHE = {}
def real_tile(n):
    """段階nの実写背帯タイル(RGB float HxWx3, row0=稜線→側線, col0=頭→尾)。無ければNone。"""
    if n in _TILE_CACHE:
        return _TILE_CACHE[n]
    p = os.path.join(_DIR, f"pattern_top_{n}.png")
    if os.path.exists(p):
        t = np.asarray(Image.open(p).convert("RGB"), float)
        from scipy.ndimage import gaussian_filter as _gf
        for c in range(3):                       # 抽出のストリーク軽減(軽く平滑)
            t[..., c] = _gf(t[..., c], 1.1)
    else:
        t = None
    _TILE_CACHE[n] = t
    return t


def sample_tile(tile, tnorm, mabs):
    """tnorm(0頭..1尾), mabs(0稜線..1側線) で tile を bilinear サンプル → RGB(H,W,3)。"""
    Mh, Tw = tile.shape[:2]
    fx = np.clip(tnorm, 0, 1) * (Tw - 1)
    fy = np.clip(mabs, 0, 1) * (Mh - 1)
    x0 = np.clip(np.floor(fx).astype(int), 0, Tw - 1); x1 = np.clip(x0 + 1, 0, Tw - 1)
    y0 = np.clip(np.floor(fy).astype(int), 0, Mh - 1); y1 = np.clip(y0 + 1, 0, Mh - 1)
    wx = (fx - x0)[..., None]; wy = (fy - y0)[..., None]
    a = tile[y0, x0] * (1 - wx) + tile[y0, x1] * wx
    b = tile[y1, x0] * (1 - wx) + tile[y1, x1] * wx
    return a * (1 - wy) + b * wy


def _hex(s): return np.array([int(s[i:i + 2], 16) for i in (1, 3, 5)], float)


def _mix(a, b, f): return a * (1 - f) + b * f


# 背側(真上)実観察ベースの色ランプ(density 0→1)。実写(Wikimedia chum 真上/婚姻色)＋calibration準拠。
# 真上では: 暗い背の正中線/オリーブ緑が主役、銀の腹は不可視、婚姻色の鮮赤紫は下方flankで真上はくすむ。
_DORSAL_RAMP = {
    1: [(0.0,"#cfcabd"),(0.5,"#9a9788"),(1.0,"#5f5e50")],                       # 仔魚: 半透明オリーブ灰
    2: [(0.0,"#a7a98c"),(0.45,"#83855f"),(0.8,"#5d6340"),(1.0,"#3a3d28")],      # 稚魚: オリーブ緑+暗パー
    3: [(0.0,"#c4c8d3"),(0.5,"#8f93a6"),(1.0,"#4f566a")],                       # スモルト: 銀青+鋼青背線
    4: [(0.0,"#b3bcbb"),(0.5,"#6f8284"),(0.8,"#3f554f"),(1.0,"#243029")],      # 海洋: 銀+暗い青緑の背
    5: [(0.0,"#9a9b80"),(0.5,"#6b6c5b"),(0.8,"#474d38"),(1.0,"#2c3120")],      # 沿岸: オリーブ
    6: [(0.0,"#9a9a72"),(0.4,"#6b6c4a"),(0.72,"#6e4b52"),(1.0,"#2c3124")],      # 遡上: オリーブ緑+くすんだ紫赤鞍+暗
    7: [(0.0,"#75745e"),(0.45,"#565640"),(0.78,"#6a4b41"),(1.0,"#2a2a1c")],     # 産卵後: 暗退色
}


def color_ramp(n):
    return [(d, _hex(h)) for d, h in _DORSAL_RAMP[n]]


def ramp_color(stops, d):
    for i in range(len(stops) - 1):
        d0, c0 = stops[i]; d1, c1 = stops[i + 1]
        if d <= d1:
            f = (d - d0) / max(d1 - d0, 1e-6)
            return _mix(c0, c1, np.clip(f, 0, 1))
    return stops[-1][1]

# 背側半幅プロファイル(t沿軸0鼻先→0.885尾柄, half-width in L単位)
_WID = [(0.00,0.004),(0.04,0.022),(0.09,0.040),(0.15,0.054),(0.22,0.060),
        (0.30,0.061),(0.40,0.056),(0.52,0.046),(0.64,0.035),(0.76,0.024),
        (0.85,0.016),(0.885,0.012)]


def _w(t):
    ts = np.array([p[0] for p in _WID]); hs = np.array([p[1] for p in _WID])
    return np.interp(np.clip(t, 0, ts[-1]), ts, hs)


def _center(t, bend):
    """採用版 Group62 のベジェ反りを再現。bend=(x0,c1,c2,x3) は L に対する横ずれ比。
    1-4,7=ゆるいC弓 / 5,6=S字(c1>0,c2<0)。"""
    x0, c1, c2, x3 = bend
    u = np.clip(t, 0, 1)
    return ((1 - u) ** 3 * x0 + 3 * (1 - u) ** 2 * u * c1
            + 3 * (1 - u) * u ** 2 * c2 + u ** 3 * x3)


def build(W, H, pad=0.07, bend=(0, 0, 0, 0), wscale=1.0):
    ox = W * pad
    L = W * (1 - 2 * pad)
    oy = H * 0.5
    ys, xs = np.mgrid[0:H, 0:W].astype(float)
    t = (xs - ox) / L
    cy = oy - _center(t, bend) * L                 # 遊泳の中心線(y)=ベジェの反り
    hw = _w(t) * L * wscale                         # 半幅(wscale: 段階別の細太)
    m = (ys - cy) / np.maximum(hw, 1e-6)           # 左右 -1..+1
    body = (t >= 0) & (t <= 0.885) & (np.abs(m) <= 1.0)
    return t, m, body, (ox, oy, L, bend)


def _cpx(tr, t):
    ox, oy, L, bend = tr
    return oy - _center(np.array([t]), bend)[0] * L


def caudal_poly(tr):
    ox, oy, L, bend = tr
    t0 = 0.885; cy0 = _cpx(tr, t0); x0 = ox + t0 * L
    xt = ox + 1.02 * L; cyt = _cpx(tr, 1.0)
    spread = 0.088 * L
    notch = ox + 0.95 * L
    return [(x0, cy0 - 0.012 * L), (xt, cyt - spread), (notch, cyt),
            (xt, cyt + spread), (x0, cy0 + 0.012 * L)]


def pectoral_polys(tr):
    ox, oy, L, bend = tr
    t0 = 0.16; cy = _cpx(tr, t0); x0 = ox + t0 * L
    hw = _w(t0) * L
    out = []
    for s in (+1, -1):
        base1 = (x0, cy + s * hw * 0.7)
        base2 = (x0 + 0.04 * L, cy + s * hw)
        tip = (x0 + 0.12 * L, cy + s * 0.115 * L)   # 後方へ張り出す
        out.append([base1, base2, tip])
    return out


def _raster(W, H, polys):
    im = Image.new("L", (W, H), 0); d = ImageDraw.Draw(im)
    for p in polys:
        d.polygon([(float(x), float(y)) for x, y in p], fill=255)
    return np.array(im) > 128


def density_top(W, H, st, bend=None, **_ignore):
    if bend is None:
        bend = st.get("bend", (0, 0, 0, 0))
    t, m, body, tr = build(W, H, bend=bend)
    rng = np.random.default_rng(SEED + st["n"] * 7)
    caud = _raster(W, H, [caudal_poly(tr)])
    pect = _raster(W, H, pectoral_polys(tr))
    full = body | caud | pect
    floor = st.get("floor", 0.30)
    cmap = None
    tile = real_tile(st["n"])

    if tile is not None:
        # === 実写抽出パターン優先: 実際のmarkingsを (t,|m|) に貼る ===
        rgb = sample_tile(tile, np.clip(t / 0.885, 0, 1), np.clip(np.abs(m), 0, 1))
        lum = (0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]) / 255
        Dpat = 1 - lum
        bv = Dpat[body]
        lo, hi = np.percentile(bv, 3), np.percentile(bv, 99)
        Dpat = np.clip((Dpat - lo) / (hi - lo + 1e-6), 0, 1)
        D = 0.34 + 0.72 * Dpat                        # 下地を上げ全身を均等に点で満たす
        D[~body] = 0
        # 単色図譜(engraving)なら実色は使わず ramp。彩度があれば実色をサンプル
        mx = rgb.max(2); mn = rgb.min(2)
        sat = ((mx - mn) / (mx + 1e-6))[body].mean()
        cmap = rgb if sat > 0.10 else None
    else:
        # === procedural fallback(実写未抽出の段階) ===
        base_dark = st.get("base_dark", 0.62)
        D = floor + base_dark * 0.5 * np.ones((H, W))
        D[~body] = 0
        stripe = np.exp(-(m ** 2) / (2 * 0.13 ** 2))
        D += st.get("dorsal_stripe", 0.34) * stripe * body
        D += 0.08 * (np.abs(m) ** 2) * body
        bt = st["bartype"]; ampb = st.get("baramp", 0.0)
        if bt in ("parr", "nuptial"):
            nb = st.get("barcount", 8)
            ph = rng.uniform(0, 2 * np.pi)
            jag = gaussian_filter(rng.standard_normal((H, W)), (5, 14))
            jag = jag / (np.abs(jag).max() + 1e-9)
            tt = np.clip(t / 0.88, 0, 1) + 0.04 * jag
            bars = 0.5 + 0.5 * np.cos(2 * np.pi * nb * tt + ph)
            if bt == "parr":
                bars = (bars > 0.62).astype(float)
                bars *= np.clip(0.35 + 0.65 * np.abs(m), 0, 1)
            else:
                bars = np.clip((bars - 0.32) / 0.68, 0, 1) ** 1.2
            D += ampb * gaussian_filter(bars * body, 1.2)
        if st.get("speckle"):
            sp = (rng.random((H, W)) > 0.986) & body
            D += 0.45 * gaussian_filter(sp.astype(float), 0.6)
        if st["n"] == 7:
            wear = gaussian_filter(rng.standard_normal((H, W)), 11)
            wear = (wear - wear.min()) / (np.ptp(wear) + 1e-9)
            D -= 0.4 * np.clip(wear - 0.55, 0, None) * body

    # --- 共通: 背びれ/脂びれ(正中線の濃点)・胸尾びれ・頭部・縁フェード ---
    dfin = body & (t > 0.42) & (t < 0.55) & (np.abs(m) < 0.08)
    afin = body & (t > 0.74) & (t < 0.79) & (np.abs(m) < 0.05)
    D[dfin] += 0.18; D[afin] += 0.14
    finmask = (caud | pect) & (~body)
    D[finmask] = floor * 0.8
    D += 0.10 * np.clip(1 - t / 0.14, 0, 1) * body

    D = np.clip(D, 0, 1)
    D[~full] = 0
    soft = gaussian_filter(full.astype(float), W * 0.005)
    D *= np.clip(soft, 0, 1) ** 0.6
    return D, full, tr, cmap


def render_top(W, H, st, bend=None, dot_k=0.05, supersample=2,
               colored=False, **_ignore):
    D, full, tr, cmap = density_top(W, H, st, bend=bend)
    SS = supersample
    img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img, "RGBA")
    n_points = int(D.sum() * dot_k)
    pts, di = weighted_voronoi(D, n_points, seed=st["n"] + 50)
    stops = color_ramp(st["n"]) if (colored and cmap is None) else None
    Hh, Ww = D.shape
    for (x, y), d in zip(pts, di):
        r = (0.55 + 1.7 * np.sqrt(d)) * SS
        if colored and cmap is not None:                 # 実写の実色をサンプル
            c = cmap[int(np.clip(y, 0, Hh - 1)), int(np.clip(x, 0, Ww - 1))]
            col = (int(c[0]), int(c[1]), int(c[2]), int(np.clip(150 + 105 * d, 150, 255)))
        elif colored:
            c = ramp_color(stops, d)
            col = (int(c[0]), int(c[1]), int(c[2]), int(np.clip(150 + 105 * d, 150, 255)))
        else:
            col = (SUMI[0], SUMI[1], SUMI[2], int(np.clip(140 + 115 * d, 140, 255)))
        dr.ellipse([x * SS - r, y * SS - r, x * SS + r, y * SS + r], fill=col)
    return img.resize((W, H), Image.LANCZOS), n_points


# 段階(背側・真上)。dorsal_stripe=暗い背の正中線, speckle=海洋の微細点
STAGES = [
    dict(n=1, jp="1 仔魚",   bartype="none",    baramp=0.0, base_dark=0.32, floor=0.18, dorsal_stripe=0.24, bend=(0, 0.209, 0.209, 0)),
    dict(n=2, jp="2 稚魚",   bartype="parr",    baramp=0.42, barcount=10, base_dark=0.48, floor=0.26, dorsal_stripe=0.32, bend=(0, 0.168, 0.168, 0)),
    dict(n=3, jp="3 スモルト", bartype="none",   baramp=0.0, base_dark=0.42, floor=0.24, dorsal_stripe=0.36, speckle=True, bend=(0, 0.173, 0.173, 0)),
    dict(n=4, jp="4 海洋",   bartype="none",    baramp=0.0, base_dark=0.60, floor=0.30, dorsal_stripe=0.42, speckle=True, bend=(0, 0.110, 0.110, 0)),
    dict(n=5, jp="5 沿岸",   bartype="none",    baramp=0.0, base_dark=0.58, floor=0.30, dorsal_stripe=0.38, bend=(0.046, 0.207, -0.114, 0.046)),
    dict(n=6, jp="6 遡上",   bartype="nuptial", baramp=0.55, barcount=8, base_dark=0.62, floor=0.32, dorsal_stripe=0.34, bend=(0.057, 0.253, -0.140, 0.057)),
    dict(n=7, jp="7 産卵後", bartype="nuptial", baramp=0.78, barcount=8, base_dark=0.70, floor=0.32, dorsal_stripe=0.30, bend=(0, 0.073, 0.073, 0)),
]


def main():
    from PIL import ImageFont
    try:
        f_title = ImageFont.truetype("/System/Library/Fonts/ヒラギノ明朝 ProN.ttc", 44)
        f_lab = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 22)
    except Exception:
        f_title = f_lab = ImageFont.load_default()

    # hero: 真上から泳ぐ遡上のサケ
    HW, HH = 1500, 900
    hero = Image.new("RGB", (HW, HH), PAPER)
    st6 = [s for s in STAGES if s["n"] == 6][0]
    im, npt = render_top(int(HW * 0.9), int(HH * 0.92), st6, amp=0.12, freq=1.2, dot_k=0.055)
    hero.paste(im, ((HW - im.width) // 2, (HH - im.height) // 2), im)
    hd = ImageDraw.Draw(hero)
    hd.line([(50, 50), (350, 50)], fill=(46, 110, 142), width=3)
    hd.text((50, 60), "点描・真上から — 泳ぐサケ(背側)", fill=SUMI, font=f_title)
    hero.save(_OUT("stipple", "stipple-top-hero.png"))
    print("saved stipple-top-hero.png", hero.size, "points=", npt)

    # 7段階(背側, 真上)
    FW, FH = 560, 760
    pad = 18; top = 86; labelh = 36
    nS = len(STAGES)
    MW = pad + nS * FW + nS * pad
    MH = top + FH + labelh + pad
    cv = Image.new("RGB", (MW, MH), PAPER)
    dr = ImageDraw.Draw(cv)
    dr.line([(pad, 28), (pad + 300, 28)], fill=(46, 110, 142), width=3)
    dr.text((pad, 40), "点描 7段階・真上(背側) — 泳ぐ姿勢", fill=SUMI, font=f_title)
    phases = [0.6, 1.2, 2.0, 0.3, 1.6, 0.9, 2.4]
    for i, st in enumerate(STAGES):
        im, _ = render_top(int(FW * 0.95), int(FH * 0.95), st, amp=0.11, freq=1.2,
                           phase=phases[i], dot_k=0.05)
        x = pad + i * (FW + pad); y = top + (FH - im.height) // 2
        cv.paste(im, (x, y), im)
        dr.text((x + 4, top + FH + 2), st["jp"], fill=(60, 60, 60), font=f_lab)
    cv.save(_OUT("stipple", "stipple-top-montage.png"))
    print("saved stipple-top-montage.png", cv.size)


if __name__ == "__main__":
    main()
