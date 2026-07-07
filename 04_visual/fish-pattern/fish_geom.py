#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
パラメトリックなサケ体形 — 中心線(centerline)＋上下プロファイルで体を定義。
「アウトラインを描かず、模様/点の疎密で形を立ち上げる」ための共有ジオメトリ。
各画素に体内座標 (t: 鼻先0→尾柄1, n: 腹-1→背+1) を割り当てて返す。
"""
import numpy as np

# pattern.py のシルエットに準拠した上下プロファイル(L単位, +上)
_TOP = [(0.00,0.00),(0.03,0.040),(0.08,0.075),(0.15,0.105),(0.25,0.125),(0.36,0.130),
        (0.50,0.122),(0.64,0.100),(0.78,0.066),(0.88,0.038)]
_BOT = [(0.00,0.00),(0.04,0.045),(0.10,0.085),(0.20,0.115),(0.32,0.125),(0.46,0.122),
        (0.60,0.100),(0.74,0.070),(0.85,0.042),(0.88,0.036)]   # 正の半高(下方向)


def _interp(prof, t):
    ts = np.array([p[0] for p in prof]); hs = np.array([p[1] for p in prof])
    return np.interp(np.clip(t, 0, ts[-1]), ts, hs)


def build_fields(W, H, pad=0.06, arc=0.0, taper=1.0):
    """戻り値: TT, NN, MASK(body), CENTERPX(t->中心y, 配列でなく関数), transform
    arc: 中心線の反り(L単位, 正=中央が上＝跳躍)。taper: 体高倍率。
    """
    ox = W * pad
    L = W * (1 - 2 * pad)
    oy = H * 0.55
    ys, xs = np.mgrid[0:H, 0:W].astype(float)
    t = (xs - ox) / L
    # 中心線(t->世界y, L単位, +上): 跳躍の弧 = sin
    def center(tt):
        return arc * np.sin(np.pi * np.clip(tt, 0, 1))
    wy = (oy - ys) / L                      # 世界y(L単位, +上)
    c = center(t)
    hu = _interp(_TOP, t) * taper           # 背側半高
    hd = _interp(_BOT, t) * taper           # 腹側半高
    d = wy - c
    n = np.where(d >= 0, d / np.maximum(hu, 1e-6), d / np.maximum(hd, 1e-6))
    body = (t >= 0) & (t <= 0.885) & (np.abs(n) <= 1.0)
    return t, n, body, (ox, oy, L, arc)


def tail_polygon(tr, taper=1.0):
    """尾びれ(二叉)ポリゴン画素座標。中心線の尾柄位置に合わせる。"""
    ox, oy, L, arc = tr
    t0 = 0.885
    cy0 = oy - (arc * np.sin(np.pi * t0)) * L
    x0 = ox + t0 * L
    xt = ox + 1.005 * L
    spread = 0.150 * L * taper
    notch = ox + 0.95 * L
    cy_t = oy - (arc * np.sin(np.pi * 1.0)) * L
    return [(x0, cy0 - 0.035 * L), (xt, cy_t - spread), (notch, cy_t),
            (xt, cy_t + spread), (x0, cy0 + 0.035 * L)]


def fin_polygons(tr, taper=1.0):
    """背・脂・尻・胸びれ。中心線に沿って配置。"""
    ox, oy, L, arc = tr
    def P(t, nworld):  # nworld in L-units (+up) relative to center
        cy = oy - (arc * np.sin(np.pi * t)) * L
        return (ox + t * L, cy - nworld * L * taper)
    dorsal = [P(0.40, 0.125), P(0.46, 0.215), P(0.52, 0.118)]
    adipose = [P(0.74, 0.066), P(0.775, 0.105), P(0.81, 0.060)]
    anal = [P(0.58, -0.100), P(0.62, -0.195), P(0.66, -0.095)]
    pect = [P(0.20, -0.055), P(0.27, -0.165), P(0.30, -0.050)]
    return [dorsal, adipose, anal, pect]


def pos(tr, t, nn, taper=1.0):
    """体内座標 (t, n) -> 画素(x,y)。n: 腹-1..背+1。"""
    ox, oy, L, arc = tr
    cy = oy - (arc * np.sin(np.pi * np.clip(t, 0, 1))) * L
    hu = _interp(_TOP, t) * taper
    hd = _interp(_BOT, t) * taper
    h = hu if nn >= 0 else hd
    return (ox + t * L, cy - nn * h * L)


def body_tangent(tr, t, taper=1.0):
    """中心線の接線角(度, 画面座標)。鱗の向き付け用。"""
    dt = 1e-3
    x0, y0 = pos(tr, max(0, t - dt), 0, taper)
    x1, y1 = pos(tr, min(1, t + dt), 0, taper)
    return np.degrees(np.arctan2(y1 - y0, x1 - x0))


def half_height(t):
    return _interp(_TOP, t), _interp(_BOT, t)


def eye_xy(tr):
    ox, oy, L, arc = tr
    t = 0.062
    cy = oy - (arc * np.sin(np.pi * t)) * L
    hu = _interp(_TOP, t)
    return (ox + t * L, cy - 0.33 * hu * L)
