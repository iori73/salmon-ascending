#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終ビジョンのプレビュー(非破壊): 放射状の鱗(circuli)=波の上を、真上から見た点描サケ7匹が
泳ぐ。merge all `6184:216434` の Group 62 は壊さず、別途モックを生成して見え方を確認する。
配置規則は採用版に準拠: 半径=体長比 / 12時スタート一周 / 接線向き(泳ぐ方向) / 生物学準拠サイズ。
出力: radial-swim-mock.png (墨) / radial-swim-mock-color.png (実測色)
"""
import numpy as np
from PIL import Image, ImageDraw
import fish_top as T
from _paths import out as _OUT

SEED = 20260615
PAPER = (250, 250, 246)
WAVE = (150, 170, 184)   # 淡い藍鼠=水の波

# プレビュー用=スパイラルに均等配置(各魚が波の上を泳ぐのを見せる)。
# 本番 merge all は採用版の 12時起点・生死が頂点で揃う角度を使う(別途)。
STAGES_LAYOUT = [
    # n, angle_deg(from top, cw), radius_frac(0..1), length_cm
    (1,  12, 0.130, 5),
    (2,  62, 0.225, 8),
    (3, 112, 0.330, 12),
    (4, 168, 0.500, 42),
    (5, 228, 0.680, 62),
    (6, 292, 0.825, 65),
    (7, 346, 0.945, 70),
]


def draw_circuli(dr, cx, cy, Rmax, n_rings=70, col=WAVE):
    """放射状の同心円 circuli=波。わずかに有機的にうねらせる。年輪3本は密。"""
    rng = np.random.default_rng(SEED)
    # 半径スケジュール: 中心密→外で年輪(annulus)3本の密集帯
    rs = []
    r = Rmax * 0.04
    annuli = [Rmax * 0.56, Rmax * 0.80, Rmax * 0.93]
    while r < Rmax:
        rs.append(r)
        # 年輪近傍は間隔を詰める
        near = min(abs(r - a) for a in annuli)
        step = Rmax * (0.006 + 0.012 * np.clip(near / (Rmax * 0.12), 0, 1))
        r += step
    for i, r in enumerate(rs):
        amp = r * 0.012 * (0.5 + rng.random())
        ph = rng.uniform(0, 6.28)
        k = rng.integers(3, 7)
        pts = []
        for a in np.linspace(0, 2 * np.pi, 240):
            rr = r + amp * np.sin(k * a + ph)
            pts.append((cx + rr * np.cos(a), cy + rr * np.sin(a)))
        near = min(abs(r - aa) for aa in annuli)
        al = 150 if near < Rmax * 0.02 else 70
        dr.line(pts + [pts[0]], fill=col + (al,), width=2)


def place_fish(canvas, cx, cy, Rmax, colored):
    for n, ang_deg, rfrac, lcm in STAGES_LAYOUT:
        st = [s for s in T.STAGES if s["n"] == n][0]
        # 魚画像(横長)を生成。length_px は体長比
        Lpx = int(28 + lcm * 5.4)
        fw = int(Lpx / (1 - 2 * 0.07))           # build の pad 分を補正
        fh = int(fw * 0.42)
        ph = (n * 0.7) % 6.28
        im, _ = T.render_top(fw, fh, st, amp=0.11, freq=1.2, phase=ph,
                             dot_k=0.05, colored=colored, supersample=2)
        # 位置: 12時起点(up), clockwise
        th = np.radians(ang_deg)
        r = Rmax * rfrac
        px = cx + r * np.sin(th)
        py = cy - r * np.cos(th)
        # 接線(clockwise で進む)方向 = d/dth (sin,-cos)→(cos, sin)。頭をそちらへ。
        tang = np.degrees(np.arctan2(np.sin(th), np.cos(th)))
        # 画像の頭は -x(左)。頭を tang 方向へ → 回転角 = -(tang+180) (PILはCCW正)
        rot = -(tang + 180)
        rim = im.rotate(rot, expand=True, resample=Image.BICUBIC)
        canvas.alpha_composite(rim, (int(px - rim.width / 2), int(py - rim.height / 2)))


def build(colored):
    S = 2000
    cx = cy = S // 2
    Rmax = S * 0.46
    base = Image.new("RGBA", (S, S), PAPER + (255,))
    dr = ImageDraw.Draw(base, "RGBA")
    draw_circuli(dr, cx, cy, Rmax)
    place_fish(base, cx, cy, Rmax, colored)
    out = _OUT("radial", "radial-swim-mock-color.png" if colored else "radial-swim-mock.png")
    base.convert("RGB").save(out)
    print("saved", out, base.size)


if __name__ == "__main__":
    build(False)
    build(True)
