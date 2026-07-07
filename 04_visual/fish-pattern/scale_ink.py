#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鱗パターン5「水彩インクのにじみ/広がり」— 参照(藍の絞り染め/放射状フィラメント滲み, CHINA/DNA2725)に寄せる。
実circuli line-art を土台に、**focus中心の極座標で放射方向に滲ませ**、角度方向の繊維ノイズで
放射状スパイク(芯→外へ染み出す筋)を作る。藍・紙地・粒状。
出力: scale-ink-v2.png
"""
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, gaussian_filter1d, map_coordinates
from _paths import asset, out as _OUT

SEED = 20260618
PAPER = np.array([248, 247, 242], float)
LINEART = asset("scale-lineart.png")
PROC_W = 1500
FOCUS = (0.50, 0.71)


def _hex(h): return np.array([int(h[i:i+2],16) for i in (1,3,5)], float)


def fnoise(n, octaves=5, seed=0, periodic=False):
    rng = np.random.default_rng(SEED + seed)
    out = np.zeros(n); amp = 1.0; tot = 0
    for o in range(octaves):
        k = max(2, 4 * (2 ** o))
        base = rng.standard_normal(k)
        if periodic: base[-1] = base[0]
        x = np.linspace(0, k - 1, n)
        out += amp * np.interp(x, np.arange(k), base); tot += amp; amp *= 0.55
    out = (out - out.min()) / (np.ptp(out) + 1e-9)
    return out


def load_line():
    im = Image.open(LINEART).convert("RGBA")
    W0, H0 = im.size; H = int(PROC_W * H0 / W0)
    im = im.resize((PROC_W, H), Image.BILINEAR)
    a = np.asarray(im, float) / 255
    lum = 0.299*a[...,0]+0.587*a[...,1]+0.114*a[...,2]
    L = np.clip(a[...,3]*(1-lum), 0, 1)
    return gaussian_filter(L, 0.6), (PROC_W, H)


def main():
    L, (W, H) = load_line()
    fx, fy = FOCUS[0]*W, FOCUS[1]*H
    # 半径最大 = focusから四隅までの最大
    Rmax = max(np.hypot(fx, fy), np.hypot(W-fx, fy), np.hypot(fx, H-fy), np.hypot(W-fx, H-fy))
    NTH, NR = 1600, 1000
    th = np.linspace(0, 2*np.pi, NTH, endpoint=False)
    rr = np.linspace(0, Rmax, NR)
    TH, RR = np.meshgrid(th, rr)                       # (NR, NTH)
    xs = fx + RR*np.cos(TH); ys = fy + RR*np.sin(TH)
    P = map_coordinates(L, [ys, xs], order=1, mode="constant", cval=0.0)  # polar line density

    # 角度方向の繊維(放射スパイクの強弱): 高周波1Dノイズ
    fiber = fnoise(NTH, octaves=6, seed=1, periodic=True)        # 0..1
    fiber = 0.25 + 0.95 * (fiber ** 1.4)                         # コントラスト
    fiber2 = fnoise(NTH, octaves=7, seed=5, periodic=True)
    P = P * fiber[None, :]

    # 放射方向の滲み(外向き wick・短め=芯から少し染み出す程度)。累積が長すぎると solid 化するので decay短く
    bleed = np.zeros_like(P)
    acc = np.zeros(NTH)
    decay = 0.86                                                # 短いwick(circuli構造を残す)
    grow = (rr / Rmax)
    for i in range(NR):
        acc = acc * decay + P[i] * (0.5 + 0.5*grow[i])
        bleed[i] = acc
    bleed = gaussian_filter1d(bleed, 4, axis=0)                 # 放射方向に柔らかく(円輪は残す)
    bleed = gaussian_filter1d(bleed, 1.5, axis=1)
    # circuli(P)を主役に・bleedは縁の染み出しとして加える
    field = np.clip(0.95*P + 0.45*bleed, 0, 1.4)
    # 角度高周波の細い筋(繊維)
    field *= (0.72 + 0.5*fiber2[None, :])

    # unwarp 極→直交
    ys2, xs2 = np.mgrid[0:H, 0:W].astype(float)
    dx, dy = xs2 - fx, ys2 - fy
    rad = np.hypot(dx, dy); ang = (np.arctan2(dy, dx)) % (2*np.pi)
    ri = rad / Rmax * (NR - 1)
    ti = ang / (2*np.pi) * NTH
    ink = map_coordinates(field, [ri, ti], order=1, mode="grid-wrap")
    ink = gaussian_filter(ink, 1.0)
    # 正規化・芯を濃く
    ink = np.clip(ink / (np.percentile(ink, 99.5) + 1e-6), 0, 1) ** 0.85

    # 粒状(紙の繊維)
    grain = gaussian_filter(np.random.default_rng(SEED+9).standard_normal((H, W)), 1.0)
    grain = (grain - grain.min())/(np.ptp(grain)+1e-9)
    ink = np.clip(ink * (0.85 + 0.3*grain), 0, 1)

    # 着色: 紙→藍→濃藍
    indigo = _hex("#2F62A0"); deep = _hex("#16335C")
    t = ink[..., None]
    col = PAPER[None,None]*(1-np.clip(t*1.5,0,1)) + indigo[None,None]*np.clip(t*1.5,0,1)
    col = col + (deep-indigo)[None,None]*np.clip((ink-0.55)/0.45,0,1)[...,None]
    out = np.clip(col, 0, 255).astype(np.uint8)
    Image.fromarray(out).save(_OUT("scale-bg", "scale-ink-v2.png"))
    print("saved scale-ink-v2.png", (W, H))


if __name__ == "__main__":
    main()
