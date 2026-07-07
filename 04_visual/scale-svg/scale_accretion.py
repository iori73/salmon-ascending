#!/usr/bin/env python3
"""
scale_accretion.py — シロザケの鱗を「実証済みの成長＋辺縁付加モデル」で手続き生成する。

恣意的ノイズでなく、査読論文ベースのモデルに準拠（[[scale-formation-models]]）:
  - circuli = 偏心 focus から「成長する縁(margin)に平行」に内側付加
    （marginal accretion; de Vrieze 2012 / Iwasaki elasmoid review）。
    実装 = 実物の鱗輪郭(source_dense.png 由来)を focus へ相似縮小したもの。
  - 半径方向の位置/間隔 = 体成長 von Bertalanffy × 季節変調 → 鱗半径∝体長
    （body–scale proportionality; Peterson 2021）。circulus 沈着率 RCF∝成長速度
    （Fisher & Pearcy 1990）。夏=広い / 冬=密集=年輪(annulus)。
  - 後方野(focus 下)= circuli 乏しく globular reticulation（粒状）。
  ※ チューリング反応拡散は色素パターン専用で circuli には使わない。

出力: scale-accretion.svg / -preview.png(白地) / -hires.png(透過, Figma取込用)
"""

import numpy as np
from scipy import ndimage
from skimage import measure
from PIL import Image, ImageDraw

SEED = 20260614
VIEW_W, VIEW_H = 1314, 1198
SRC = "source_dense.png"

# --- 焦点(偏心・下寄り。輪郭bbox比) ---
FX_FRAC, FY_FRAC = 0.50, 0.70

# --- von Bertalanffy 体成長 (cm) ---
LINF, K_VB, L0 = 78.0, 0.48, 9.0      # L∞, k, 海洋進入時体長
T_END = 3.4                            # 回帰(年) 4年魚相当・海洋年輪3本
WINTER_PHASE = 0.75                    # 季節最小成長(冬)の位相
WMIN = 0.06                            # 冬の成長率の下限係数
N_TARGET = 52                          # 海洋 circuli 目標数(簡略化)
N_FRESH = 3                            # focus 近傍の淡水/初期 circuli

# --- 配色(半径比で 暖focus→寒margin、紙へ淡色化) ---
PAPER = np.array([0xFA, 0xFA, 0xF6], float)
WARM = np.array([0xC4, 0x72, 0x2A], float)
COOL = np.array([0x2E, 0x6E, 0x8E], float)
PALE = 0.42

STROKE_W = 1.6


def fractal_noise(shape, rng, base_sigma=40.0, octaves=5, persistence=0.55):
    acc = np.zeros(shape, np.float32); amp, sig, tot = 1.0, base_sigma, 0.0
    for _ in range(octaves):
        n = rng.standard_normal(shape).astype(np.float32)
        acc += amp * ndimage.gaussian_filter(n, sig); tot += amp
        amp *= persistence; sig *= 0.5
    acc /= tot; acc -= acc.min(); acc /= (acc.max() + 1e-9)
    return acc


def extract_outline():
    """source_dense.png から鱗輪郭を抽出→凸包→focus基準の R(θ) として360点で返す。
    凸包にすることで底の擬似ノッチ(相似縮小で尖る原因)を除去し star-shaped を保証。"""
    from scipy.spatial import ConvexHull
    g = np.asarray(Image.open(SRC).convert("L")); H, W = g.shape
    mask = g < 205
    d = max(2, W // 400)
    mask = ndimage.binary_dilation(mask, iterations=d)
    mask = ndimage.binary_fill_holes(mask)
    lbl, n = ndimage.label(mask)
    sizes = ndimage.sum(np.ones_like(lbl), lbl, range(1, n + 1))
    big = ndimage.binary_erosion(lbl == (np.argmax(sizes) + 1), iterations=d)
    cont = max(measure.find_contours(big.astype(float), 0.5), key=len)   # (y,x)
    pts = cont[:, ::-1].astype(float)                                    # (x,y)
    hull = pts[ConvexHull(pts).vertices]                                 # 凸包頂点(順)
    # viewBox へフィット(余白)
    mn, mx = hull.min(0), hull.max(0); span = mx - mn
    margin = 0.06
    sc = min(VIEW_W * (1 - 2 * margin) / span[0], VIEW_H * (1 - 2 * margin) / span[1])
    off = np.array([VIEW_W, VIEW_H]) / 2 - (mn + span / 2) * sc
    hull = hull * sc + off
    bb_mn, bb_mx = hull.min(0), hull.max(0)
    focus = np.array([bb_mn[0] + FX_FRAC * (bb_mx[0] - bb_mn[0]),
                      bb_mn[1] + FY_FRAC * (bb_mx[1] - bb_mn[1])])
    # focus基準の極座標 → 角度で R(θ) を補間(凸なので単調=star-shaped)
    rel = hull - focus
    a = np.arctan2(rel[:, 1], rel[:, 0]); r = np.hypot(rel[:, 0], rel[:, 1])
    order = np.argsort(a); a, r = a[order], r[order]
    a = np.r_[a[-1] - 2 * np.pi, a, a[0] + 2 * np.pi]
    r = np.r_[r[-1], r, r[0]]                                            # 周期端
    th = np.linspace(-np.pi, np.pi, 360, endpoint=False)
    Rth = np.interp(th, a, r)
    # 軽い円環平滑
    win = 9; k = np.ones(win) / win
    Rth = np.convolve(np.r_[Rth[-win:], Rth, Rth[:win]], k, "same")[win:-win]
    outline = focus + np.c_[np.cos(th), np.sin(th)] * Rth[:, None]
    return outline, focus


def growth_schedule():
    """von Bertalanffy×季節 → RCF積分で circulus 沈着時刻 → 半径比 s_i・年輪フラグ。"""
    t0 = np.log(1 - L0 / LINF) / K_VB
    L = lambda t: LINF * (1 - np.exp(-K_VB * (t - t0)))
    vbrate = lambda t: LINF * K_VB * np.exp(-K_VB * (t - t0))
    season = lambda t: WMIN + (1 - WMIN) * (0.5 + 0.5 * np.cos(2 * np.pi * (t - (WINTER_PHASE + 0.5))))
    g = lambda t: vbrate(t) * season(t)                       # 実効体成長率
    g0 = g(0.0)
    dt = 0.004
    ts = np.arange(0, T_END, dt)
    sgr_norm = g(ts) / g0
    rcf = 0.88 * sgr_norm + 0.12                              # ∝成長率＋床(冬も僅少沈着)
    # 総数 N_TARGET になるよう正規化
    rcf *= N_TARGET / (rcf.sum() * dt)
    cum = np.cumsum(rcf) * dt
    Lend = L(T_END)
    times, svals = [], []
    nxt = 1.0
    for t, c in zip(ts, cum):
        while c >= nxt:
            times.append(t); svals.append(L(t) / Lend); nxt += 1.0
    svals = np.array(svals); times = np.array(times)
    # 年輪 = 季節成長最小(冬)近傍の circuli
    is_ann = np.array([abs(((t - WINTER_PHASE) % 1.0) - 0.0) < 0.10 or
                       abs(((t - WINTER_PHASE) % 1.0) - 1.0) < 0.10 for t in times])
    # 淡水/初期 circuli を focus 近傍に少数
    fresh = np.linspace(0.03, svals.min() * 0.85, N_FRESH)
    svals = np.r_[fresh, svals]
    is_ann = np.r_[np.zeros(N_FRESH, bool), is_ann]
    ann_s = sorted(set(round(float(s), 2) for s, a in zip(svals, is_ann) if a))
    return svals, is_ann, ann_s


def color_for(t):
    rgb = (WARM * (1 - t) + COOL * t) * (1 - PALE) + PAPER * PALE
    return "#%02X%02X%02X" % tuple(int(round(c)) for c in np.clip(rgb, 0, 255))


def main():
    rng = np.random.default_rng(SEED)
    outline, F = extract_outline()
    svals, is_ann, ann_s = growth_schedule()

    rel = outline - F                                   # focus基準ベクトル
    Rout = np.hypot(rel[:, 0], rel[:, 1])
    ang = np.arctan2(rel[:, 1], rel[:, 0])
    unit = rel / (Rout[:, None] + 1e-9)
    Rbar = float(Rout.mean())                           # 平均半径(内側=円に近づける)
    Npt = len(outline)
    ymax = float(outline[:, 1].max())
    ybelow = F[1] + 0.06 * (ymax - F[1])                # 後方野しきい(これより下=reticulation)

    def longest_run(keep):
        """円環bool配列の最長連結Trueセグメントのインデックス列(wrap考慮)。"""
        n = len(keep)
        if keep.all():
            return list(range(n))
        best = (0, 0); cur = []
        for k in list(range(n)) + list(range(n)):       # 2周してwrap拾う
            if keep[k % n]:
                cur.append(k % n)
                if len(cur) > best[1] - best[0]:
                    best = (cur[0], cur[0] + len(cur))
            else:
                cur = []
            if len(cur) >= n:
                break
        a, b = best
        return [i % n for i in range(a, b)]

    def rnd(arr):
        return [(round(float(x), 1), round(float(y), 1)) for x, y in arr]

    import os
    DEBUG = bool(os.environ.get("DBG"))
    paths = []                                          # (color, pts, closed)
    for i, s in enumerate(svals):
        w = min(1.0, s * 1.15)                          # 内側=円, 外側=実輪郭形へ補間(allometry)
        R = s * ((1 - w) * Rbar + w * Rout)
        if not is_ann[i] and not DEBUG:                 # 年輪は素直/夏は僅かに揺らす
            ph = rng.uniform(0, 2 * np.pi, 2)
            R = R + 2.2 * np.sin(2 * ang + ph[0]) + 1.3 * np.sin(3 * ang + ph[1])
        circ = F + unit * R[:, None]
        col = color_for(float(np.clip(s, 0, 1)))
        if DEBUG:
            paths.append((col, rnd(circ), True)); continue
        if s < 0.20:                                    # 初期=小さな丸い閉ループ
            paths.append((col, rnd(circ), True))
        else:                                           # 外側=上側の弧のみ(後方野は除外)
            run = longest_run(circ[:, 1] <= ybelow)
            if len(run) > 6:
                paths.append((col, rnd(circ[run]), False))
    if DEBUG:
        xs = [p[0] for _, pts, _ in paths for p in pts]; ys = [p[1] for _, pts, _ in paths for p in pts]
        print(f"DEBUG path bbox x[{min(xs):.0f},{max(xs):.0f}] y[{min(ys):.0f},{max(ys):.0f}]")

    # 後方野 reticulation(粒状): focus 下〜後方の輪郭内に小点を散布(内側に限定)
    reti = []
    xmin, xmax = float(outline[:, 0].min()), float(outline[:, 0].max())
    for _ in range(1400):
        x = rng.uniform(xmin, xmax); y = rng.uniform(ybelow, ymax)
        inside = False; j = Npt - 1
        for k in range(Npt):
            xi, yi = outline[k]; xj, yj = outline[j]
            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi):
                inside = not inside
            j = k
        if inside and len(reti) < 320:
            reti.append((round(x, 1), round(y, 1)))

    # ---- SVG
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           f'<svg xmlns="http://www.w3.org/2000/svg" width="{VIEW_W}" height="{VIEW_H}" viewBox="0 0 {VIEW_W} {VIEW_H}">',
           f'<g fill="none" stroke-width="{STROKE_W}" stroke-linecap="round" stroke-linejoin="round">']
    for col, pts, closed in paths:
        d = "M " + " L ".join(f"{x} {y}" for x, y in pts) + (" Z" if closed else "")
        out.append(f'<path d="{d}" stroke="{col}"/>')
    out.append('</g>')
    rc = color_for(0.05)
    out.append(f'<g fill="{rc}">')
    for x, y in reti:
        out.append(f'<circle cx="{x}" cy="{y}" r="1.5"/>')
    out.append('</g></svg>')
    open("scale-accretion.svg", "w").write("\n".join(out))

    # ---- PNG (PIL, 4x→縮小AA)
    def render(scale, bg, fn, ss=4):
        big = Image.new("RGBA", (VIEW_W * scale * ss, VIEW_H * scale * ss),
                        (0, 0, 0, 0) if bg is None else tuple(int(c) for c in bg) + (255,))
        dr = ImageDraw.Draw(big)
        for col, pts, closed in paths:
            rgb = tuple(int(col[i:i + 2], 16) for i in (1, 3, 5))
            ln = [(x * scale * ss, y * scale * ss) for x, y in pts]
            if closed: ln = ln + [ln[0]]
            if len(ln) >= 2:
                dr.line(ln, fill=rgb + (255,), width=max(1, int(STROKE_W * scale * ss)), joint="curve")
        rr = tuple(int(rc[i:i + 2], 16) for i in (1, 3, 5))
        for x, y in reti:
            r = 1.6 * scale * ss
            dr.ellipse([x * scale * ss - r, y * scale * ss - r, x * scale * ss + r, y * scale * ss + r], fill=rr + (255,))
        big.resize((VIEW_W * scale, VIEW_H * scale), Image.LANCZOS).save(fn)

    render(1, PAPER, "scale-accretion-preview.png")
    render(3, None, "scale-accretion-hires.png")

    print(f"circuli={len(svals)} (fresh{N_FRESH}+ocean) paths={len(paths)} reti={len(reti)}")
    print(f"annulus s-values = {ann_s}  (target ~0.60/0.80/0.93)")
    print(f"focus=({F[0]:.0f},{F[1]:.0f})  outline_pts={Npt}")


if __name__ == "__main__":
    main()
