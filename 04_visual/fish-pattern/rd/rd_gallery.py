#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rd_gallery.py — 静的・高品質な計算出力(有限ステップで完了→CPU常時負荷なし)。
(1) 創発シーケンス: 一様+微小ノイズ → Turing 模様が時間発展で立ち上がる過程(=計算の証拠)。
(2) Turing zoo: 同一 Gray–Scott 式で (F,k,異方) を変えるだけの模様の家族(近藤式ギャラリー)。
出力: rd-emergence.png / rd-zoo.png
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "gallery")
os.makedirs(_OUT, exist_ok=True)
SEED = 20260619
PAPER = (250, 250, 246)


def gray_scott(gh, gw, F, k, Du=0.16, Dv=0.08, ax=1.0, ay=1.0, steps=12000, snaps=None, salt=0):
    """Gray–Scott を steps 回。snaps=[ステップ番号...] でその時点の V を記録して返す。"""
    rng = np.random.default_rng(SEED + salt * 101)
    U = np.ones((gh, gw)); V = np.zeros((gh, gw))
    rr = rng.random((gh, gw)); V[rr < 0.05] = 0.5; U[rr < 0.05] = 0.25
    snaps = set(snaps or []); out = {}
    if 0 in snaps:
        out[0] = V.copy()
    for it in range(1, steps + 1):
        lu = ax * (np.roll(U, 1, 1) + np.roll(U, -1, 1) - 2 * U) + ay * (np.roll(U, 1, 0) + np.roll(U, -1, 0) - 2 * U)
        lv = ax * (np.roll(V, 1, 1) + np.roll(V, -1, 1) - 2 * V) + ay * (np.roll(V, 1, 0) + np.roll(V, -1, 0) - 2 * V)
        uvv = U * V * V
        U += Du * lu - uvv + F * (1 - U)
        V += Dv * lv + uvv - (F + k) * V
        if it in snaps:
            out[it] = V.copy()
    return V, out


def crisp(V):
    """高コントラストな墨-紙(ink on paper)に整え uint8 画像化。"""
    v = (V - V.min()) / (np.ptp(V) + 1e-9)
    v = np.clip((v - 0.35) / 0.4, 0, 1)[..., None]   # コントラスト
    paper = np.array([250.0, 250, 246]); ink = np.array([28.0, 30, 36])
    col = paper * (1 - v) + ink * v
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))


def font(sz):
    for p in ["/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf"]:
        try: return ImageFont.truetype(p, sz)
        except Exception: pass
    return ImageFont.load_default()


def emergence():
    """縦縞パターンの創発: t=0(ノイズ)→収束 を6コマで。"""
    G = 200
    snaps = [0, 300, 900, 2500, 6000, 12000]
    _, frames = gray_scott(G, G, 0.029, 0.057, ax=0.45, ay=1.55, steps=12000, snaps=snaps, salt=1)
    th = 300; pad = 20; lab = 30
    fL = font(26); fS = font(20)
    W = pad + len(snaps) * (th + pad); H = pad + lab + th + lab
    cv = Image.new("RGB", (W, H), (255, 255, 255)); dr = ImageDraw.Draw(cv)
    dr.line([(pad, 8), (pad + 420, 8)], fill=(46, 110, 142), width=3)
    dr.text((pad, 14), "創発シーケンス — 一様+ノイズ から Turing 模様が計算で立ち上がる(縦縞)", fill=(30, 30, 30), font=fL)
    for i, s in enumerate(snaps):
        im = crisp(frames[s]).resize((th, th), Image.NEAREST)
        x = pad + i * (th + pad)
        cv.paste(im, (x, pad + lab))
        dr.text((x + 4, pad + lab + th + 2), f"step {s}", fill=(60, 60, 60), font=fS)
    p = os.path.join(_OUT, "rd-emergence.png"); cv.save(p); print("saved", p, cv.size)


def zoo():
    """同一式・パラメータ違いの模様の家族。"""
    G = 220
    cases = [
        ("斑点 spots", 0.030, 0.062, 1.0, 1.0), ("サンゴ coral", 0.054, 0.063, 1.0, 1.0),
        ("迷路 maze", 0.029, 0.057, 1.0, 1.0), ("多孔 holes", 0.039, 0.058, 1.0, 1.0),
        ("ワーム worms", 0.058, 0.065, 1.0, 1.0), ("分裂 mitosis", 0.026, 0.051, 1.0, 1.0),
        ("縦縞 stripes", 0.029, 0.057, 0.45, 1.55), ("サケ稚魚 parr", 0.038, 0.061, 0.42, 1.6),
    ]
    th = 300; pad = 18; lab = 30; cols = 4
    fL = font(26); fS = font(19)
    rows = (len(cases) + cols - 1) // cols
    W = pad + cols * (th + pad); H = pad + lab + rows * (th + lab)
    cv = Image.new("RGB", (W, H), (255, 255, 255)); dr = ImageDraw.Draw(cv)
    dr.line([(pad, 8), (pad + 420, 8)], fill=(46, 110, 142), width=3)
    dr.text((pad, 14), "Turing zoo — 同一 Gray–Scott 式、(F,k,異方)を変えるだけの模様の家族", fill=(30, 30, 30), font=fL)
    for i, (name, F, k, ax, ay) in enumerate(cases):
        V, _ = gray_scott(G, G, F, k, ax=ax, ay=ay, steps=12000, salt=i + 10)
        im = crisp(V).resize((th, th), Image.NEAREST)
        r = i // cols; c = i % cols
        x = pad + c * (th + pad); y = pad + lab + r * (th + lab)
        cv.paste(im, (x, y))
        dr.text((x + 4, y + th + 2), f"{name}  F={F} k={k}" + ("  異方" if ax != 1 else ""), fill=(60, 60, 60), font=fS)
        print("zoo", name)
    p = os.path.join(_OUT, "rd-zoo.png"); cv.save(p); print("saved", p, cv.size)


if __name__ == "__main__":
    emergence()
    zoo()
