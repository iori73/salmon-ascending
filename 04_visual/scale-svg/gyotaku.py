#!/usr/bin/env python3
"""
gyotaku.py — シロザケの鱗(同心円トレース)に魚拓・墨の質感を与える。

入力 : source_dense.png (Figma node 6084:242498 書出し / 白地・濃灰線)
出力 : gyotaku-{wet,dry,balanced}.png  (透過背景・墨のみ RGBA)
       gyotaku-montage.png            (3案ヨコ並びプレビュー)

表現する3要素:
  払い harai   = 筆のスイープ方向に沿った微細な streak と、縁/末端のテーパー(筆の抜け)
  にじみ nijimi = 墨の溜まり(濃)と紙への淡いハロー滲み出し、線の柔らかいエッジ
  掠れ kasure  = 乾いた筆が紙目に擦れて線が確率的に途切れる(外周ほど強い)

墨はモノクロ一本。濃= #2A2A2A(深炭) / 淡= #6B6B5F(淡墨)。背景は透過。
"""

import numpy as np
from scipy import ndimage
from PIL import Image

SRC = "source_dense.png"
WORK_LONG = 3000          # 処理解像度(長辺px)
SEED = 20260613

# 墨の階調 (visual-language-concept.md)
INK_DARK = np.array([0x2A, 0x2A, 0x2A], float) / 255.0   # 深炭(溜まり)
INK_PALE = np.array([0x6B, 0x6B, 0x5F], float) / 255.0   # 淡墨(乾き縁)


# ---------------------------------------------------------------- ノイズ場
def fractal_noise(shape, rng, base_sigma=40.0, octaves=5, persistence=0.55):
    """gaussian平滑した白色雑音を周波数別に重畳した値ノイズ [0,1]。"""
    acc = np.zeros(shape, np.float32)
    amp, sig, tot = 1.0, base_sigma, 0.0
    for _ in range(octaves):
        n = rng.standard_normal(shape).astype(np.float32)
        acc += amp * ndimage.gaussian_filter(n, sig)
        tot += amp
        amp *= persistence
        sig *= 0.5
    acc /= tot
    acc -= acc.min()
    acc /= (acc.max() + 1e-9)
    return acc


def streak_noise(shape, rng, sigma_along=26.0, sigma_perp=1.4, angle_deg=-28.0):
    """一方向に引き伸ばした筆スジ風ノイズ [0,1]。angleは筆のスイープ方向。"""
    n = rng.standard_normal(shape).astype(np.float32)
    n = ndimage.gaussian_filter(n, (sigma_perp, sigma_along))   # 横長にスジ化
    n = ndimage.rotate(n, angle_deg, reshape=False, order=1, mode="reflect")
    n -= n.min()
    n /= (n.max() + 1e-9)
    return n


def smoothstep(lo, hi, x):
    t = np.clip((x - lo) / (hi - lo + 1e-9), 0.0, 1.0)
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- 本体
def load_ink():
    im = Image.open(SRC).convert("L")
    w, h = im.size
    s = WORK_LONG / max(w, h)
    im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    g = np.asarray(im, np.float32) / 255.0
    ink = np.clip((1.0 - g) / 0.80, 0.0, 1.0)        # 濃灰線→1, 紙→0 に正規化
    # 白抜けの小穴を軽く補完(注記「AEAAFFが無いところをblackで補完」)
    closed = ndimage.grey_closing(ink, size=5)
    ink = np.maximum(ink, closed * 0.6)
    return ink


def radial_field(ink):
    """ink重心を中心とした正規化半径 r∈[0,1] (掠れの外周強調に使う)。"""
    h, w = ink.shape
    ys, xs = np.nonzero(ink > 0.25)
    cy, cx = (ys.mean(), xs.mean()) if len(ys) else (h / 2, w / 2)
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
    return r / (r.max() + 1e-9)


def render(ink, r, rng, p):
    h, w = ink.shape

    # 筆の太み: 線をわずかに肥らせて墨のストローク幅に寄せる
    if p["weight"] > 1:
        ink = np.maximum(ink, ndimage.grey_dilation(ink, size=p["weight"]))

    # --- にじみ: 弱ブラーで線を柔らかく、密度から溜まりを作る ---
    soft = ndimage.gaussian_filter(ink, p["blur"])
    density = ndimage.gaussian_filter(ink, p["pool_sigma"])
    density /= (density.max() + 1e-9)
    pool = smoothstep(0.35, 0.85, density)                       # 線が密な所=溜まり

    # --- 掠れ: 値ノイズ×筆スジ を閾値処理で線を途切れさせる(外周ほど強い) ---
    nz = fractal_noise((h, w), rng, base_sigma=p["kasure_sigma"], octaves=5)
    st = streak_noise((h, w), rng, sigma_along=p["streak_len"],
                      angle_deg=p["sweep_angle"])
    field = 0.55 * nz + 0.45 * st
    thr = p["kasure_thr"] + p["edge_kasure"] * r                 # 外周で閾値↑=掠れ↑
    keep = smoothstep(thr - 0.16, thr + 0.16, field)             # ソフトに保持率
    dry = 1.0 - keep                                             # 乾き具合(淡墨寄せ用)

    # --- 払い: 縁/末端のテーパー(筆の抜け) ---
    edge_taper = smoothstep(0.96, p["edge_fade"], r)             # 最外周を細らせる
    edge_taper = 1.0 - edge_taper
    # スイープ方向の片側フェード(筆を払う向きで薄れる)
    a = np.deg2rad(p["sweep_angle"])
    yy, xx = np.mgrid[0:h, 0:w]
    proj = (np.cos(a) * xx + np.sin(a) * yy)
    proj = (proj - proj.min()) / (np.ptp(proj) + 1e-9)
    sweep_fade = 1.0 - p["sweep_fade"] * smoothstep(0.70, 1.0, proj)  # 端だけ控えめに

    # --- 被覆(alpha)合成 ---
    cover = soft * keep
    cover = cover * (1.0 - p["pool_lift"]) + np.maximum(cover, ink * keep) * p["pool_lift"]
    cover = cover * (0.95 + 0.65 * pool)                         # 溜まりは濃く
    cover = cover * edge_taper * sweep_fade

    # 和紙グレイン(乾筆が紙目に噛む)
    grain = fractal_noise((h, w), rng, base_sigma=2.2, octaves=2)
    cover = cover * (1.0 - p["grain"] * (1.0 - grain))

    # ハロー滲み出し(紙側へ淡く)
    halo = ndimage.gaussian_filter(cover, p["halo_sigma"]) * p["halo"]
    alpha = np.clip(np.maximum(cover, halo), 0.0, 1.0)
    alpha = alpha ** p["alpha_gamma"]

    # --- 墨の階調: 溜まり=深炭 / 乾き=淡墨 ---
    paleness = np.clip(0.55 * dry + 0.35 * (1.0 - pool) +
                       0.30 * smoothstep(0.6, 1.0, r), 0.0, 1.0)
    paleness *= p["pale_amt"]
    rgb = INK_DARK[None, None, :] * (1 - paleness[..., None]) + \
        INK_PALE[None, None, :] * paleness[..., None]

    out = np.zeros((h, w, 4), np.float32)
    out[..., :3] = rgb
    out[..., 3] = alpha
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)


# ---------------------------------------------------------------- パラメータ3案
PRESETS = {
    "wet": dict(            # にじみ強(湿)
        weight=3, blur=2.3, pool_sigma=26, kasure_sigma=46, kasure_thr=0.24,
        edge_kasure=0.12, streak_len=20, sweep_angle=-28, edge_fade=1.18,
        sweep_fade=0.10, pool_lift=0.7, grain=0.08, halo=0.50, halo_sigma=7,
        alpha_gamma=0.72, pale_amt=0.30),
    "dry": dict(            # 掠れ強(乾)
        weight=1, blur=1.0, pool_sigma=20, kasure_sigma=24, kasure_thr=0.37,
        edge_kasure=0.18, streak_len=38, sweep_angle=-28, edge_fade=1.10,
        sweep_fade=0.16, pool_lift=0.3, grain=0.20, halo=0.14, halo_sigma=4,
        alpha_gamma=0.86, pale_amt=0.66),
    "balanced": dict(       # バランス
        weight=2, blur=1.5, pool_sigma=23, kasure_sigma=32, kasure_thr=0.30,
        edge_kasure=0.15, streak_len=28, sweep_angle=-28, edge_fade=1.14,
        sweep_fade=0.12, pool_lift=0.5, grain=0.13, halo=0.32, halo_sigma=5,
        alpha_gamma=0.80, pale_amt=0.48),
}


def main():
    ink = load_ink()
    r = radial_field(ink)
    print(f"working size: {ink.shape[1]}x{ink.shape[0]}")
    imgs = {}
    for name, p in PRESETS.items():
        rng = np.random.default_rng(SEED + hash(name) % 1000)
        arr = render(ink, r, rng, p)
        Image.fromarray(arr, "RGBA").save(f"gyotaku-{name}.png")
        imgs[name] = arr
        cov = arr[..., 3].mean() / 255
        print(f"  gyotaku-{name}.png  coverage={cov:.3f}")

    # montage (紙色 #FAFAF6 背景にコンポジットして並べる)
    pad, h = 40, ink.shape[0]
    paper = np.array([0xFA, 0xFA, 0xF6], np.uint8)
    tiles = []
    for name in ("wet", "dry", "balanced"):
        a = imgs[name].astype(np.float32) / 255
        comp = paper[None, None, :] * (1 - a[..., 3:]) + a[..., :3] * 255 * a[..., 3:]
        tiles.append(comp.astype(np.uint8))
    W = sum(t.shape[1] for t in tiles) + pad * (len(tiles) + 1)
    canvas = np.full((h + 2 * pad, W, 3), paper, np.uint8)
    x = pad
    for t in tiles:
        canvas[pad:pad + h, x:x + t.shape[1]] = t
        x += t.shape[1] + pad
    Image.fromarray(canvas).save("gyotaku-montage.png")
    print("  gyotaku-montage.png")


if __name__ == "__main__":
    main()
