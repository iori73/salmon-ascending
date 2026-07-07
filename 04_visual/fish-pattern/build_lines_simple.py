#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scale-lineart.png の circuli を「揃った流れの均一細線」に変換する。
パイプライン:
  1) 2値化 → 微小ノイズ除去
  2) skeletonize で 1px 中心線
  3) 中心線をポリライン群にトレース
  4) 短い破片を捨て、各線を弧長方向に強くスムージング(=流れの統一感)
  5) 等幅・丸キャップの細線として SVG + PNG@2x で出力
出力: scale-lines.svg / scale-lines@2x.png / scale-lines-white@2x.png
"""
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import convolve, gaussian_filter1d, binary_closing
from skimage.morphology import skeletonize, remove_small_objects
import pathlib

from _paths import asset, out
HERE = pathlib.Path(__file__).parent
SRC = asset("scale-lineart.png")

# ===== ノブ =====
VBW, VBH = 1335, 1247          # viewBox(元アセットと同一)
PROC_W = 1335                  # 処理解像度(横)。skeleton 精度と速度の両立
THRESH = 0.55                  # ink 判定(これより暗い=線)。0..1
MIN_SPECK = 40                 # この px 未満の連結塊はノイズとして除去
CLOSE = True                   # skeletonize 前に微小ギャップを橋渡し(流麗さ↑)
MIN_LEN = 24                   # この点数未満のポリラインは捨てる(破片掃除)
SMOOTH_SIGMA = 6.0             # 弧長方向ガウスσ(大きいほど流れが滑らか・統一的)
RESAMPLE_STEP = 3.5            # ポリライン再サンプル間隔(px)。粗いほど滑らか
STROKE_W = 1.6                 # viewBox 座標での線幅
SUPERSAMPLE = 2                # PNG はこの倍率で描いて縮小(AA)。出力は @2x 相当
PNG_SCALE = 2                  # @2x


def load_binary():
    im = Image.open(SRC).convert("L")
    W0, H0 = im.size
    H = int(PROC_W * H0 / W0)
    im = im.resize((PROC_W, H), Image.BILINEAR)
    g = np.asarray(im, float) / 255.0
    binary = g < THRESH
    binary = remove_small_objects(binary, MIN_SPECK)
    if CLOSE:
        # 十字3x3・1回: 線方向の1〜2px欠けを橋渡し。隣接年輪(gap≥3px)は融合しない
        cross = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)
        binary = binary_closing(binary, structure=cross, iterations=1)
    return binary, (PROC_W, H)


DIRS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def trace(skel):
    H, W = skel.shape
    k = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]], np.uint8)
    deg = convolve(skel.astype(np.uint8), k, mode="constant") * skel
    is_node = skel & ((deg == 1) | (deg >= 3))
    used = np.zeros_like(skel, bool)        # 辺として消費済みの非ノード画素
    polylines = []

    def step_neighbors(y, x):
        out = []
        for dy, dx in DIRS:
            ay, ax = y + dy, x + dx
            if 0 <= ay < H and 0 <= ax < W and skel[ay, ax]:
                out.append((ay, ax))
        return out

    def walk(start, first):
        path = [start, first]
        prev, cur = start, first
        while not is_node[cur]:
            used[cur] = True
            nxt = None
            for ny, nx in step_neighbors(*cur):
                if (ny, nx) == prev:
                    continue
                if used[ny, nx]:
                    continue
                nxt = (ny, nx)
                break
            if nxt is None:
                break
            prev, cur = cur, nxt
            path.append(cur)
        return path

    # 1) ノード起点の辺
    nodes = list(zip(*np.where(is_node)))
    for (y, x) in nodes:
        for (ny, nx) in step_neighbors(y, x):
            if is_node[ny, nx]:
                # ノード同士の直接隣接は短すぎるので無視
                continue
            if used[ny, nx]:
                continue
            polylines.append(walk((y, x), (ny, nx)))

    # 2) ノードを持たない閉ループ(全 deg2)
    loop_px = skel & ~is_node & ~used
    ys, xs = np.where(loop_px)
    for (y, x) in zip(ys, xs):
        if used[y, x]:
            continue
        nb = [p for p in step_neighbors(y, x) if not used[p[0], p[1]]]
        if not nb:
            used[y, x] = True
            continue
        path = walk((y, x), nb[0])
        path.append((y, x))     # 閉じる
        polylines.append(path)

    return polylines


def smooth_resample(path):
    p = np.asarray(path, float)              # (N,2) = (y,x)
    if len(p) < 3:
        return None
    # 弧長
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
    if d[-1] < MIN_LEN * 0.5:
        return None
    closed = np.allclose(p[0], p[-1])
    mode = "wrap" if closed else "reflect"
    ys = gaussian_filter1d(p[:, 0], SMOOTH_SIGMA, mode=mode)
    xs = gaussian_filter1d(p[:, 1], SMOOTH_SIGMA, mode=mode)
    # 再サンプル
    n = max(2, int(d[-1] / RESAMPLE_STEP))
    t = np.linspace(0, d[-1], n)
    ry = np.interp(t, d, ys)
    rx = np.interp(t, d, xs)
    return np.column_stack([rx, ry])         # (n,2) = (x,y)


def to_viewbox(poly, sz):
    sx = VBW / sz[0]
    sy = VBH / sz[1]
    return poly * np.array([sx, sy])


def write_svg(polys, out, bg=None):
    parts = [f'<svg width="{VBW}" height="{VBH}" viewBox="0 0 {VBW} {VBH}" '
             f'xmlns="http://www.w3.org/2000/svg">']
    if bg:
        parts.append(f'<rect width="{VBW}" height="{VBH}" fill="{bg}"/>')
    parts.append(f'<g fill="none" stroke="#111111" stroke-width="{STROKE_W}" '
                 f'stroke-linecap="round" stroke-linejoin="round">')
    for poly in polys:
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in poly)
        parts.append(f'<path d="{d}"/>')
    parts.append("</g></svg>")
    out.write_text("\n".join(parts))
    print(f"written {out.name}  ({len(polys)} lines)")


def render_png(polys, out, bg):
    S = SUPERSAMPLE * PNG_SCALE
    W, H = VBW * S, VBH * S
    img = Image.new("RGBA", (W, H), bg)
    dr = ImageDraw.Draw(img)
    w = max(1, int(round(STROKE_W * S)))
    r = w / 2.0
    col = (17, 17, 17, 255)
    for poly in polys:
        pts = [(x * S, y * S) for x, y in poly]
        dr.line(pts, fill=col, width=w, joint="curve")
        for (px, py) in (pts[0], pts[-1]):     # 丸キャップ
            dr.ellipse([px - r, py - r, px + r, py + r], fill=col)
    img = img.resize((VBW * PNG_SCALE, VBH * PNG_SCALE), Image.LANCZOS)
    img.save(out)
    print(f"written {out.name}  {img.size}")


def build_polys(verbose=True):
    """中心線抽出→スムージング→viewBox座標のポリライン群 (list of (n,2) x,y) を返す。"""
    binary, sz = load_binary()
    if verbose:
        print("binary", sz, "ink px", int(binary.sum()))
    skel = skeletonize(binary)
    if verbose:
        print("skeleton px", int(skel.sum()))
    raw = trace(skel)
    if verbose:
        print("raw polylines", len(raw))
    polys = []
    for path in raw:
        if len(path) < MIN_LEN:
            continue
        rp = smooth_resample(path)
        if rp is None:
            continue
        polys.append(to_viewbox(rp, sz))
    if verbose:
        print("kept polylines", len(polys))
    return polys


def main():
    polys = build_polys()
    write_svg(polys, out("lines", "scale-lines.svg"), bg=None)
    write_svg(polys, out("lines", "scale-lines-white.svg"), bg="#FFFFFF")
    render_png(polys, out("lines", "scale-lines@2x.png"), (0, 0, 0, 0))
    render_png(polys, out("lines", "scale-lines-white@2x.png"), (255, 255, 255, 255))


if __name__ == "__main__":
    main()
