#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
点描(stippling)を芸術的に作り直す — 参考「鯨の模様と水飛沫」に倣う。
核: 輪郭を描かず、点の疎密だけで「量感(立体)」と「模様」を立ち上げる。
手法: 重み付きボロノイ・スティップリング(Secord 2002 / Lloyd 緩和)で
      濃度場 D に点を分布させる。D = カウンターシェーディングの立体陰影
      + 婚姻色/パーマークの縦バー + 縁のフェード。墨モノクロ。
出力: stipple-hero.png (遡上・跳躍+水飛沫) / stipple-montage.png (7段階)
"""
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
from scipy.spatial import cKDTree

import fish_geom as G
from _paths import out as _OUT

SEED = 20260615
PAPER = (250, 250, 246)
SUMI = (38, 36, 33)


def _raster_polys(W, H, polys):
    im = Image.new("L", (W, H), 0); d = ImageDraw.Draw(im)
    for p in polys:
        d.polygon([(float(x), float(y)) for x, y in p], fill=255)
    return np.array(im) > 128


def density_field(W, H, st, arc=0.0):
    """段階stの濃度場 D(0..1, 1=濃) と full mask, transform を返す。"""
    t, n, body, tr = G.build_fields(W, H, arc=arc)
    rng = np.random.default_rng(SEED + st["n"] * 7)

    # ひれ・尾を含む全身マスク
    tailm = _raster_polys(W, H, [G.tail_polygon(tr)])
    finm = _raster_polys(W, H, G.fin_polygons(tr))
    full = body | tailm | finm

    # --- 立体(カウンターシェーディング): 体全体を点で作り、背=暗/腹=明の勾配で量感 ---
    back = np.clip((n + 1) / 2, 0, 1)            # 0腹..1背
    floor = st.get("floor", 0.26)                # 全身の下地密度(これで全形が点で立つ)
    volume = back ** 1.6
    sheen = np.exp(-((n - 0.15) ** 2) / (2 * 0.18 ** 2))   # 側面の銀の反射(明)
    base_dark = st.get("base_dark", 0.55)
    silver = st.get("silver", 0.35)
    D = floor + base_dark * volume - silver * sheen * 0.45
    D = np.maximum(D, floor * 0.55)              # 腹も完全には消さない(形を残す)
    D[~body] = 0
    # ひれ・尾: 下地より薄く、外へフェード
    fin_only = (tailm | finm) & (~body)
    D[fin_only] = floor * 0.85
    # 頭部: 鰓蓋の縁と口を締める
    head = np.clip(1 - t / 0.16, 0, 1) * body
    D += 0.16 * head * (0.45 + 0.55 * back)

    # --- 模様(縦バー): 濃度として乗せる ---
    bt = st["bartype"]; amp = st.get("baramp", 0.0)
    if bt in ("parr", "nuptial"):
        nb = st.get("barcount", 8)
        phase = rng.uniform(0, 2 * np.pi)
        bars = 0.5 + 0.5 * np.cos(2 * np.pi * nb * np.clip(t / 0.88, 0, 1) + phase)
        if bt == "parr":
            bars = (bars > 0.62).astype(float)    # 細い斑
            bars *= np.clip((n + 0.1), 0, 1)      # 上半身中心
        else:
            bars = np.clip((bars - 0.30) / 0.70, 0, 1) ** 1.3  # 太いバー
            bars *= np.clip((n + 0.55), 0, 1)     # 側線より上で強い
        D += amp * gaussian_filter(bars * body, 1.5)
    if st["n"] == 7:   # 産卵後: 退色の白抜け斑
        wear = gaussian_filter(rng.standard_normal((H, W)), 11)
        wear = (wear - wear.min()) / (np.ptp(wear) + 1e-9)
        D -= 0.45 * np.clip(wear - 0.55, 0, None) * body

    # --- 目: 明るく抜いて、瞳を濃点リングで ---
    ex, ey = G.eye_xy(tr)
    ys, xs = np.mgrid[0:H, 0:W]
    er = max(6, W * 0.012)
    eye_d = np.sqrt((xs - ex) ** 2 + (ys - ey) ** 2)
    D = np.where(eye_d < er * 1.4, D * 0.15, D)          # 眼窩を白く
    D += np.where((eye_d > er * 0.55) & (eye_d < er * 1.05), 0.9, 0)  # 瞳の輪

    D = np.clip(D, 0, 1)
    D[~full] = 0
    # --- 縁フェード: マスクをぼかして縁で点を薄く(ハード境界を消す) ---
    soft = gaussian_filter(full.astype(float), W * 0.005)
    D *= np.clip(soft, 0, 1) ** 0.6
    return D, full, tr


def weighted_voronoi(D, n_points, iters=26, seed=0):
    """重み付きボロノイ・スティップリング。点座標(x,y)と各点の局所密度を返す。"""
    H, W = D.shape
    rng = np.random.default_rng(SEED + seed)
    rho = np.clip(D, 0, 1) ** 1.15
    ys, xs = np.where(rho > 0.015)
    w = rho[ys, xs]
    fg = np.stack([xs, ys], 1).astype(float)
    # 初期点: 密度に比例してサンプル
    p = w / w.sum()
    idx = rng.choice(len(xs), size=n_points, p=p)
    pts = fg[idx] + rng.uniform(-0.5, 0.5, (n_points, 2))
    for it in range(iters):
        tree = cKDTree(pts)
        _, lbl = tree.query(fg, workers=-1)
        wsum = np.bincount(lbl, weights=w, minlength=n_points)
        xsum = np.bincount(lbl, weights=w * fg[:, 0], minlength=n_points)
        ysum = np.bincount(lbl, weights=w * fg[:, 1], minlength=n_points)
        nz = wsum > 1e-9
        pts[nz, 0] = xsum[nz] / wsum[nz]
        pts[nz, 1] = ysum[nz] / wsum[nz]
        if (~nz).any():                       # 空セルは密度に応じ再配置
            k = int((~nz).sum())
            ridx = rng.choice(len(xs), size=k, p=p)
            pts[~nz] = fg[ridx] + rng.uniform(-0.5, 0.5, (k, 2))
    # 局所密度(点サイズ用)
    di = np.clip(D[np.clip(pts[:, 1].astype(int), 0, H - 1),
                   np.clip(pts[:, 0].astype(int), 0, W - 1)], 0, 1)
    return pts, di


def water_spray(tr, rng, n=520):
    ox, oy, L, arc = tr
    hx, hy = ox + 0.02 * L, oy - (arc * 0) * L
    out = []
    for _ in range(n):
        ang = rng.uniform(-2.5, -0.35)
        dist = abs(rng.normal(0, 0.26)) * L
        px = hx + np.cos(ang) * dist * rng.uniform(0.5, 1.4)
        py = (oy - 0.05 * L) + np.sin(ang) * dist
        out.append((px, py, dist / L))
    return out


def render(W, H, st, arc=0.0, dot_k=0.011, spray=False, supersample=2):
    D, body, tr = density_field(W, H, st, arc=arc)
    SS = supersample
    cw, ch = W * SS, H * SS
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img, "RGBA")
    rng = np.random.default_rng(SEED + st["n"] * 13)

    # 水飛沫(背面に薄く先打ち)
    if spray:
        for px, py, dr_ in water_spray(tr, rng, n=int(W * 0.6)):
            if not (0 <= px < W and 0 <= py < H):
                continue
            r = rng.uniform(0.5, 2.0) * max(0.2, 1 - dr_) * SS
            a = int(np.clip(150 - 120 * dr_, 35, 175))
            dr.ellipse([px * SS - r, py * SS - r, px * SS + r, py * SS + r],
                       fill=(56, 70, 82, a))      # 藍墨のしぶき

    # 本体の点描
    n_points = int(D.sum() * dot_k)
    pts, di = weighted_voronoi(D, n_points, seed=st["n"])
    for (x, y), d in zip(pts, di):
        r = (0.55 + 1.7 * np.sqrt(d)) * SS
        v = int(np.clip(120 - 70 * d, 30, 130))   # 濃い所ほど黒く
        col = (SUMI[0] + v // 6, SUMI[1] + v // 6, SUMI[2] + v // 6,
               int(np.clip(140 + 115 * d, 140, 255)))
        dr.ellipse([x * SS - r, y * SS - r, x * SS + r, y * SS + r], fill=col)

    img = img.resize((W, H), Image.LANCZOS)
    return img, n_points


# stage 定義(立体・銀・模様パラメータ。色は使わず墨)
STAGES = [
    dict(n=1, jp="1 仔魚",   bartype="none",    baramp=0.0, base_dark=0.30, silver=0.10),
    dict(n=2, jp="2 稚魚",   bartype="parr",    baramp=0.55, barcount=11, base_dark=0.50, silver=0.15),
    dict(n=3, jp="3 スモルト", bartype="parr",   baramp=0.16, barcount=11, base_dark=0.42, silver=0.45),
    dict(n=4, jp="4 海洋",   bartype="none",    baramp=0.0, base_dark=0.62, silver=0.55),
    dict(n=5, jp="5 沿岸",   bartype="none",    baramp=0.0, base_dark=0.58, silver=0.45),
    dict(n=6, jp="6 遡上",   bartype="nuptial", baramp=0.60, barcount=8, base_dark=0.66, silver=0.18),
    dict(n=7, jp="7 産卵後", bartype="nuptial", baramp=0.85, barcount=8, base_dark=0.70, silver=0.08),
]


def main():
    from PIL import ImageFont
    try:
        f_title = ImageFont.truetype("/System/Library/Fonts/ヒラギノ明朝 ProN.ttc", 46)
        f_lab = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 22)
    except Exception:
        f_title = f_lab = ImageFont.load_default()

    # hero: 遡上(跳躍の弧 + 水飛沫)
    HW, HH = 1900, 980
    hero = Image.new("RGB", (HW, HH), PAPER)
    st6 = [s for s in STAGES if s["n"] == 6][0]
    im, npt = render(int(HW * 0.92), int(HH * 0.9), st6, arc=0.075, dot_k=0.05, spray=True)
    hero.paste(im, ((HW - im.width) // 2, (HH - im.height) // 2), im)
    hd = ImageDraw.Draw(hero)
    hd.line([(54, 54), (54 + 300, 54)], fill=(46, 110, 142), width=3)
    hd.text((54, 64), "点描 — 遡上。輪郭を描かず、点が体をつくる。", fill=SUMI, font=f_title)
    hero.save(_OUT("stipple", "stipple-hero.png"))
    print("saved stipple-hero.png", hero.size, "points=", npt)

    # 7段階 montage
    FW, FH = 900, 380
    pad = 20; labelh = 40; top = 92
    nS = len(STAGES)
    MW = pad + nS * FW + nS * pad
    MH = top + FH + labelh + pad
    cv = Image.new("RGB", (MW, MH), PAPER)
    dr = ImageDraw.Draw(cv)
    dr.line([(pad, 30), (pad + 300, 30)], fill=(46, 110, 142), width=3)
    dr.text((pad, 42), "点描 7段階 — 点の疎密が立体と模様をつくる(輪郭なし)", fill=SUMI, font=f_title)
    for i, st in enumerate(STAGES):
        im, _ = render(int(FW * 0.98), int(FH * 0.95), st, arc=0.0, dot_k=0.045, spray=(st["n"] == 6))
        x = pad + i * (FW + pad); y = top + (FH - im.height) // 2
        cv.paste(im, (x, y), im)
        dr.text((x + 4, top + FH + 4), st["jp"], fill=(60, 60, 60), font=f_lab)
    cv.save(_OUT("stipple", "stipple-montage.png"))
    print("saved stipple-montage.png", cv.size)


if __name__ == "__main__":
    main()
