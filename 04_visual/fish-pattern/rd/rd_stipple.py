#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rd_stipple.py — 「RD（近藤先生方式の Gierer–Meinhardt）× 点描」で7段階シロザケを描く。

設計の核:
  生成エンジン = rd_salmon.simulate_stage() が返す *本物の* Turing 場 A（λ_T 較正・FFT検証済み）。
  幾何        = fish_geom（側面シルエット）。輪郭線は一切描かず、点の疎密だけで体形と模様を立てる。
  仕上げ      = 点描（stippling, グリッド+ジッタ・密度∝暗さ・半径∝√暗さ・色=局所RGB）。
  色          = rd_salmon.colorize() の段階別ロジックをそのまま再利用（calibration.json 由来色を保持）。

  ※ 既存 fish_stipple.py は pattern.py の cosine 擬似縞を食べていた。本スクリプトは RD 場へ配線し直す。

1技法（点描）で統一し、段階で変えるのは「RDパラメータ・色・点間隔」のみ:
  ①仔魚 none(一様) / ②稚魚 parr縦バー10 / ③スモルト 銀化 / ④海洋 微細斑(黒点なし) /
  ⑤沿岸 弱縦縞 / ⑥遡上 calico 太バー+婚姻色+水飛沫 / ⑦産卵後 退色+摩耗

出力:
  rd-stipple-stage-{n}-{slug}.png   透過@高解像（Figma配置用）
  rd-stipple-montage.png            1行×7段階（紙地, 確認用）
  rd-stipple-hero-river.png         遡上(⑥)大判 + 水飛沫
  rd-stipple-hero-river.svg         遡上 編集可能版（各点=<circle>, 粗め間引き, Figma操作用）
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 親(04_visual/fish-pattern)
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import rd_salmon as RS       # simulate_stage / STAGES / colorize / stage_colors / side_mask
import fish_geom as G        # build_fields / eye_xy / tr=(ox,oy,L,arc)

SEED = 20260621
PAPER = (250, 250, 246)
INK = (52, 50, 46)
SLUG = {1: "larva", 2: "parr", 3: "smolt", 4: "ocean", 5: "coastal", 6: "river", 7: "postspawn"}

# 段階ごとの点間隔（小=密）。仔魚=まばら → 遡上=密（fish_stipple の値を踏襲）
SPACING = {1: 5.2, 2: 4.4, 3: 4.8, 4: 4.4, 5: 4.4, 6: 3.8, 7: 4.0}


def stage_render(st, W, H):
    """段階 st の高解像レンダー素材を返す: D(暗さ0..1), rgb(float HxWx3), alpha(bool), tr, info。

    RD は低解像(120x60)で解いて A を得て、高解像幾何へ A を双線形拡大 → colorize で着色 →
    輝度から暗さ場 D を作る（色ロジックは rd_salmon を再利用＝重複なし）。
    """
    # 1) 本物のRD場（低解像）
    A_low, geo_low, info = RS.simulate_stage(st)            # A_low: (60,120)
    # 2) 高解像幾何
    t, n, body, full, tr = RS.side_mask(W, H)
    # 3) RD場を高解像へ
    a_im = Image.fromarray((np.clip(A_low, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    A = np.asarray(a_im, float) / 255.0
    A[~body] = 0.0
    # 4) rd_salmon の段階別着色をそのまま利用
    geo = (t, n, body, full, tr)
    rgb = RS.colorize(st, A, geo).astype(float)             # (H,W,3) PAPER背景・full内着色・目つき
    # 5) 暗さ場 D = 輝度(地のトーン/カウンターシェード) + マーキング場(RD由来のバー)を直接加算。
    #    色だけだと parr/沿岸はバー色が体側色と低コントラストで縞が点密度に出ない →
    #    RD活性場 A 由来のバー強度を density に直接効かせる（より忠実・amp由来なので海洋/仔魚は不変）。
    lum = (0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]) / 255.0
    D_lum = np.clip(1.0 - lum, 0, 1)
    mark = _marking(st, A, n)                               # 0..1（none/speckleはほぼ0）
    D = np.clip(0.6 * D_lum + 0.9 * mark, 0, 1)
    D = np.clip((D - 0.08) / 0.84, 0, 1)
    D[~full] = 0.0
    return D, rgb, full, tr, info


def _marking(st, A, n):
    """RD活性場 A から段階のバー/斑マーキング強度(0..1)を再構成（rd_salmon.colorize と同式）。"""
    amp = st.get("amp", 0.0)
    bars = np.clip((A - 0.5) * 2, 0, 1) * amp
    if st["regime"] == "bars":
        cs = np.clip((n + 1) / 2, 0, 1)
        bars = bars * np.clip(0.35 + 0.65 * cs, 0, 1)       # 体側中心〜背に出やすい
    return np.clip(bars, 0, 1)


def _points(D, rgb, alpha, rng, spacing, jitter=0.9, rmax=2.4, gamma=0.85):
    """点描の点を列挙（fish_stipple.stipple と同じ数式・PIL/SVG 共有）。yield (x,y,r,(R,G,B,A))。
    輪郭は描かず、alpha(=full mask)内のみ・密度∝D・半径∝√D・色=局所RGB。"""
    H, W = D.shape
    gy = np.arange(spacing * 0.5, H, spacing)
    gx = np.arange(spacing * 0.5, W, spacing)
    for cy in gy:
        for cx in gx:
            jx = cx + rng.uniform(-jitter, jitter) * spacing
            jy = cy + rng.uniform(-jitter, jitter) * spacing
            ix = int(np.clip(jx, 0, W - 1)); iy = int(np.clip(jy, 0, H - 1))
            if not alpha[iy, ix]:
                continue
            d = D[iy, ix]
            if d <= 0.02:
                continue
            if rng.random() > d ** gamma * 1.15:        # 淡い所は確率的に間引く
                continue
            r = 0.6 + rmax * (d ** 0.5)
            c = rgb[iy, ix]
            a = int(np.clip(150 + 105 * d, 150, 255))
            yield jx, jy, r, (int(c[0]), int(c[1]), int(c[2]), a)


def water_spray(draw, tr, W, H, rng, n=420):
    """遡上の跳躍水飛沫 — 頭部前方〜上方に飛沫の点を散らす（fish_geom 幾何に合わせる）。"""
    ox, oy, L, arc = tr
    cy = oy - (arc * np.sin(np.pi * 0.05)) * L
    head = (ox + 0.05 * L, cy)
    for _ in range(n):
        ang = rng.uniform(-2.4, -0.5)                  # 上前方向
        dist = abs(rng.normal(0, 0.22)) * L
        px = head[0] + np.cos(ang) * dist * rng.uniform(0.4, 1.3)
        py = head[1] + np.sin(ang) * dist
        if not (0 <= px < W and 0 <= py < H):
            continue
        r = rng.uniform(0.5, 2.2) * (1.0 - dist / (L + 1e-6)) ** 0.5
        a = int(np.clip(150 - 120 * dist / (L + 1e-6), 40, 180))
        draw.ellipse([px - r, py - r, px + r, py + r], fill=(70, 96, 110, a))  # teal しぶき


def render_png(st, W, H, spray=False):
    """段階の透過RGBA点描を返す。"""
    D, rgb, full, tr, info = stage_render(st, W, H)
    rng = np.random.default_rng(SEED + st["n"] * 17)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img, "RGBA")
    if spray:
        water_spray(dr, tr, W, H, rng, n=int(W * 0.5))
    spc = SPACING.get(st["n"], 4.4)
    for x, y, r, col in _points(D, rgb, full, rng, spacing=spc):
        dr.ellipse([x - r, y - r, x + r, y + r], fill=col)
    # 目（濃点）
    ex, ey = G.eye_xy(tr)
    dr.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=(30, 30, 34, 255))
    return img, info


def render_svg(st, W, H, spacing, spray=False):
    """編集可能版: 各点を <circle> にした SVG 文字列（粗め間引きで Figma が扱える点数に）。"""
    D, rgb, full, tr, info = stage_render(st, W, H)
    rng = np.random.default_rng(SEED + st["n"] * 17)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}">']
    cnt = 0
    if spray:
        ox, oy, L, arc = tr
        cy = oy - (arc * np.sin(np.pi * 0.05)) * L
        head = (ox + 0.05 * L, cy)
        for _ in range(int(W * 0.18)):
            ang = rng.uniform(-2.4, -0.5); dist = abs(rng.normal(0, 0.22)) * L
            px = head[0] + np.cos(ang) * dist * rng.uniform(0.4, 1.3); py = head[1] + np.sin(ang) * dist
            if not (0 <= px < W and 0 <= py < H):
                continue
            r = rng.uniform(0.5, 2.2) * (1.0 - dist / (L + 1e-6)) ** 0.5
            parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{max(r,0.4):.2f}" '
                         f'fill="#46606e" fill-opacity="0.5"/>'); cnt += 1
    for x, y, r, col in _points(D, rgb, full, rng, spacing=spacing):
        hexc = '#%02x%02x%02x' % (col[0], col[1], col[2])
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" '
                     f'fill="{hexc}" fill-opacity="{col[3]/255:.2f}"/>'); cnt += 1
    ex, ey = G.eye_xy(tr)
    parts.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="3" fill="#1e1e22"/>'); cnt += 1
    parts.append('</svg>')
    return "\n".join(parts), cnt


def main():
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "stipple")
    os.makedirs(outdir, exist_ok=True)
    try:
        f_title = ImageFont.truetype("/System/Library/Fonts/ヒラギノ明朝 ProN.ttc", 40)
        f_lab = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 22)
    except Exception:
        f_title = f_lab = ImageFont.load_default()

    # --- per-stage 透過PNG + montage ---
    CW, CH = 900, 440
    pad = 20; top = 96; labelh = 40
    n = len(RS.STAGES)
    MW = pad + n * (CW + pad)
    MH = top + CH + labelh + pad
    cv = Image.new("RGB", (MW, MH), PAPER)
    dr = ImageDraw.Draw(cv)
    dr.line([(pad, 30), (pad + 320, 30)], fill=(46, 110, 142), width=3)
    dr.text((pad, 44), "反応拡散 × 点描 — シロザケ7段階（輪郭なし・点の疎密で形）", fill=INK, font=f_title)

    for i, st in enumerate(RS.STAGES):
        im, info = render_png(st, CW, CH, spray=(st["n"] == 6))
        # 透過 per-stage 保存
        im.save(os.path.join(outdir, f"rd-stipple-stage-{st['n']}-{SLUG[st['n']]}.png"))
        # montage へ
        x = pad + i * (CW + pad); y = top
        cv.paste(im, (x, y), im)
        dr.text((x + 4, top + CH + 4), st["jp"], fill=(60, 60, 60), font=f_lab)
        lp, lm = info.get("lambda_pred"), info.get("lambda_meas")
        print(f"{st['jp']}: regime={st['regime']} λ_pred={lp} λ_meas={lm}")
    cv.save(os.path.join(outdir, "rd-stipple-montage.png"))
    print("saved rd-stipple-montage.png", cv.size)

    # --- hero: 遡上(⑥)大判 + 水飛沫 ---
    st6 = [s for s in RS.STAGES if s["n"] == 6][0]
    HW, HH = 1800, 900
    hero = Image.new("RGB", (HW, HH), PAPER)
    im, _ = render_png(st6, int(HW * 0.94), int(HH * 0.9), spray=True)
    hero.paste(im, ((HW - im.width) // 2, (HH - im.height) // 2), im)
    hd = ImageDraw.Draw(hero)
    hd.text((54, 40), "遡上 — 跳ねる。", fill=INK, font=f_title)
    hero.save(os.path.join(outdir, "rd-stipple-hero-river.png"))
    print("saved rd-stipple-hero-river.png", hero.size)

    # --- hero 編集可能SVG（粗め間引き = 点数を抑える） ---
    svg, cnt = render_svg(st6, 1200, 600, spacing=7.5, spray=True)
    with open(os.path.join(outdir, "rd-stipple-hero-river.svg"), "w") as fp:
        fp.write(svg)
    print(f"saved rd-stipple-hero-river.svg  points={cnt}")


if __name__ == "__main__":
    main()
