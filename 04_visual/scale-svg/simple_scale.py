#!/usr/bin/env python3
"""
simple_scale.py — シロザケの鱗を「簡略化＋有機的」に手描き直しする。

ねらい : 完全な同心円の入れ子(生物的にありえない)を避け、適度なランダム性を
         残したまま、密な自動トレースより簡潔な circuli を生成する。

方式   : 焦点からの距離場を低周波 fractal ノイズで歪ませ、その「等高線」を
         circuli にする。1つの歪み場由来なので線はほぼ平行・所々で寄り集まり、
         完全同心円にならない(=自然)。年輪は等高線間隔を詰めて表現。

生物構造: 焦点を下寄り(posterior)にオフセット / 焦点直下は circuli ほぼ無し /
          海洋年輪3〜4本で密集 / 成長期は疎。

配色   : 半径比で 暖(焦点 #C4722A 系) → 寒(外周 #2E6E8E 系) の淡い放射グラデ。

出力   : simple-scale.svg          (本番・ベクター線、stroke のみ)
         simple-scale-preview.png  (ローカル目視確認・白地)
"""

import numpy as np
from scipy import ndimage
from skimage import measure
from PIL import Image, ImageDraw

SEED = 20260614
VIEW_W, VIEW_H = 1314, 1198      # 既存 scale frame 6229:208850 に一致
SS = 2                            # supersample(処理解像度倍率)
W, H = VIEW_W * SS, VIEW_H * SS

# 焦点(下寄り) と 展開半径 (work-grid px)
FX, FY = int(0.500 * W), int(0.660 * H)
MAXR = int(0.75 * H)              # 上方へ展開する最大半径(輪郭楕円に合わせる)

# 鱗の輪郭(非対称な卵型) — 上に大きく/下は焦点の少し下で丸く閉じる(few circuli below focus)
SIL_CX = W // 2
SIL_CY = int(FY - 0.04 * MAXR)
RY_UP = SIL_CY - int(0.03 * H)    # 上方(dome)…キャンバス上端近くまで
RY_DN = int(0.13 * MAXR)          # 下方…焦点の少し下で丸く閉じる
RX = int(0.46 * W)                # 左右幅

# 歪み(完全同心円を崩す)
A_WARP_BIG = 26 * SS              # ゆるい大波
A_WARP_MIC = 6 * SS               # 微揺れ

# 配色 (visual-language-concept.md / 淡色化)
PAPER = np.array([0xFA, 0xFA, 0xF6], float)
WARM = np.array([0xC4, 0x72, 0x2A], float)   # 鉄錆(焦点)
COOL = np.array([0x2E, 0x6E, 0x8E], float)   # 北の深海色(外周)
PALE = 0.42                                   # 紙へ寄せる割合(淡さ)

STROKE_W = 1.8                                # SVG線幅(viewBox px)
MIN_SEG = 14                                  # 短い破片の除去(viewBox px)


def fractal_noise(shape, rng, base_sigma=40.0, octaves=5, persistence=0.55):
    """gaussian平滑した白色雑音を周波数別に重畳した値ノイズ [0,1]。(gyotaku.py 流用)"""
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


def radius_schedule():
    """淡水帯3本 → 海洋4年(成長期=疎 + 年輪=密集) の半径列(work-grid px)。"""
    sched = [0.016 * MAXR, 0.027 * MAXR, 0.040 * MAXR]          # 淡水帯(疎)
    annuli = [0.45, 0.62, 0.80, 0.93]                          # 年輪(外周ほど密)
    prev = 0.050 * MAXR
    for k, af in enumerate(annuli):
        ann = af * MAXR
        ann_start = ann - 0.040 * MAXR                         # 年輪バンド幅
        n_summer = 9                                           # 成長期(夏)
        for j in range(n_summer):
            f = (j + 1) / (n_summer + 1)
            sched.append(prev + (ann_start - prev) * (f ** 0.85))
        n_ann = 4 if k < 2 else 3                              # 年輪(冬)の密集
        for j in range(n_ann):
            sched.append(ann_start + (ann - ann_start) * (j + 1) / n_ann)
        prev = ann + 0.015 * MAXR
    sched.append(0.965 * MAXR)                                 # 最外
    sched.append(0.995 * MAXR)
    return sched


def color_for(t):
    """t=r/MAXR (0..1) で 暖→寒、紙へ淡色化した RGB hex。"""
    base = WARM * (1 - t) + COOL * t
    rgb = base * (1 - PALE) + PAPER * PALE
    return "#%02X%02X%02X" % tuple(int(round(c)) for c in np.clip(rgb, 0, 255))


def split_by_mask(pts, keep):
    """keep(bool配列)で連続Trueの区間ごとに polyline を分割。"""
    segs, cur = [], []
    for p, k in zip(pts, keep):
        if k:
            cur.append(p)
        elif cur:
            segs.append(cur); cur = []
    if cur:
        segs.append(cur)
    return segs


def decimate(seg, step_px):
    """点を ~step_px 間隔へ間引き(端点保持)、最大120点。"""
    if len(seg) <= 3:
        return seg
    out = [seg[0]]
    acc = 0.0
    for i in range(1, len(seg)):
        acc += np.hypot(seg[i][0] - seg[i - 1][0], seg[i][1] - seg[i - 1][1])
        if acc >= step_px:
            out.append(seg[i]); acc = 0.0
    if out[-1] is not seg[-1]:
        out.append(seg[-1])
    if len(out) > 120:
        idx = np.linspace(0, len(out) - 1, 120).round().astype(int)
        out = [out[i] for i in idx]
    return out


def main():
    rng = np.random.default_rng(SEED)

    # 距離場 + 歪み
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dist = np.hypot(xx - FX, yy - FY)
    big = fractal_noise((H, W), rng, base_sigma=110.0 * SS / 2, octaves=4, persistence=0.55)
    mic = fractal_noise((H, W), rng, base_sigma=18.0 * SS / 2, octaves=3, persistence=0.5)
    warped = dist + A_WARP_BIG * (big - 0.5) + A_WARP_MIC * (mic - 0.5)
    warped = ndimage.gaussian_filter(warped, 1.0)

    sched = radius_schedule()
    step_px = 9 * SS

    paths = []          # (color_hex, [(x,y)..viewBox], closed)
    preview = []        # (color, [(x,y)..viewBox], closed) 同じ
    for r in sched:
        t = float(np.clip(r / MAXR, 0, 1))
        col = color_for(t)
        for contour in measure.find_contours(warped, r):
            # contour: (row=y, col=x) work-grid
            orig_closed = bool(np.allclose(contour[0], contour[-1]))
            pts_w = [(c[1], c[0]) for c in contour]
            # マスク = 非対称卵型シルエットの内側
            keep = []
            for (x, y) in pts_w:
                ry = RY_UP if y < SIL_CY else RY_DN
                inside = (((x - SIL_CX) / RX) ** 2 + ((y - SIL_CY) / ry) ** 2) <= 1.0
                keep.append(inside)
            kept_all = all(keep)
            segs = [pts_w] if kept_all else split_by_mask(pts_w, keep)
            for seg in segs:
                # viewBox 座標へ(整数丸めでデータ圧縮)
                vb = [(int(round(x / SS)), int(round(y / SS))) for (x, y) in seg]
                # 長さフィルタ
                L = sum(np.hypot(vb[i][0] - vb[i - 1][0], vb[i][1] - vb[i - 1][1])
                        for i in range(1, len(vb)))
                if L < MIN_SEG:
                    continue
                vb = decimate(vb, step_px / SS)
                is_closed = orig_closed and kept_all
                paths.append((col, vb, is_closed))

    # ---- SVG 出力
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           f'<svg xmlns="http://www.w3.org/2000/svg" width="{VIEW_W}" height="{VIEW_H}" '
           f'viewBox="0 0 {VIEW_W} {VIEW_H}">',
           f'<g fill="none" stroke-width="{STROKE_W}" stroke-linecap="round" stroke-linejoin="round">']
    for col, vb, closed in paths:
        d = "M " + " L ".join(f"{x} {y}" for x, y in vb) + (" Z" if closed else "")
        out.append(f'<path d="{d}" stroke="{col}"/>')
    out.append('</g></svg>')
    svg = "\n".join(out)
    with open("simple-scale.svg", "w") as f:
        f.write(svg)

    # ---- PNG レンダリング(PIL, supersample→縮小でAA)
    def render(scale, bg, out, ss=4, lw=2.0):
        big = Image.new("RGBA", (VIEW_W * scale * ss, VIEW_H * scale * ss),
                        (0, 0, 0, 0) if bg is None else tuple(int(c) for c in bg) + (255,))
        dr = ImageDraw.Draw(big)
        for col, vb, closed in paths:
            rgb = tuple(int(col[i:i + 2], 16) for i in (1, 3, 5))
            line = [(x * scale * ss, y * scale * ss) for x, y in vb]
            if closed:
                line = line + [line[0]]
            if len(line) >= 2:
                dr.line(line, fill=rgb + (255,), width=max(1, int(lw * scale * ss)), joint="curve")
        big = big.resize((VIEW_W * scale, VIEW_H * scale), Image.LANCZOS)
        big.save(out)

    render(1, PAPER, "simple-scale-preview.png")          # 白地・確認用
    render(3, None, "simple-scale-hires.png")              # 透過・高解像(Figma取込用)

    nseg = len(paths)
    nbytes = len(svg.encode())
    print(f"paths(segments)={nseg}  schedule_rings={len(sched)}  "
          f"svg_bytes={nbytes} ({nbytes/1024:.1f}KB)  focus=({FX//SS},{FY//SS}) maxR={MAXR//SS}")


if __name__ == "__main__":
    main()
