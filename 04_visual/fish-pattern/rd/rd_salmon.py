#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rd_salmon.py — シロザケ7段階の体模様を Gierer–Meinhardt 反応拡散で生成(側面ビュー)。

各段階 = 同一 Turing エンジンの「パラメータ集合」(科学的に正確: 遷移は発生・ホルモンの
スイッチ)。Turing が各段階の空間パターン(縦バー間隔=波長/斑点/一様)を生成。
バー間隔は線形安定性解析の予測波長 λ_T を実バー数(parr~10-11, 婚姻色~8)へ較正し、
シミュレーション後に FFT 実測波長で検証する。

側面シルエット = fish_geom(既存・側面プロファイル)を再利用。体軸=x。縦バーは x 方向に
変化 → 抑制因子の x拡散(Dx_h)を大きく(検証済の向き制御)。
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter, zoom
import rd_engine as E
import rd_stability as S
import fish_geom as G

CALP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "calibration.json")
CAL = json.load(open(CALP)) if os.path.exists(CALP) else {}
_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "salmon")
os.makedirs(_OUT, exist_ok=True)
PAPER = np.array([250, 250, 246], float)


def hexc(s):
    s = s.lstrip("#"); return np.array([int(s[i:i+2], 16) for i in (0, 2, 4)], float)


def calibrate_Dh(kin, p, Da, target_lambda, lo=2.0, hi=400.0):
    """λ_T ≈ target になる Dh を二分探索(λ_T は Dh とともに増加)。"""
    for _ in range(34):
        mid = 0.5 * (lo + hi)
        lam = S.turing_analysis(kin, p, Da, mid)["lambda_T"]
        if not (lam == lam):  # nan
            lo = mid; continue
        if lam < target_lambda:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def side_mask(W, H):
    """側面シルエット + 体内座標。body=胴(RD領域), full=胴+ひれ+尾(表示シルエット)。"""
    t, n, body, tr = G.build_fields(W, H, pad=0.08)
    im = Image.new("L", (W, H), 0); d = ImageDraw.Draw(im)
    for p in [G.tail_polygon(tr)] + G.fin_polygons(tr):
        d.polygon([(float(x), float(y)) for x, y in p], fill=255)
    fins = (np.array(im) > 128)
    full = body | fins
    for m in (body, full):
        m[0, :] = m[-1, :] = m[:, 0] = m[:, -1] = False
    return t, n, body, full, tr


# 段階定義: GM rate + 目標バー数(λ_T較正用) + 異方比 + regime + 配色キー
# regime: "bars"=異方縦バー, "speckle"=等方微細斑, "none"=一様(銀化/未形成)
STAGES = [
    dict(n=1, jp="1 仔魚",   regime="none",    base_dark=0.18, calkey="1", yolk=True),
    dict(n=2, jp="2 稚魚",   regime="bars",    bars=10, aniso=11.0, amp=0.95, base_dark=0.42, calkey="2"),
    dict(n=3, jp="3 スモルト", regime="none",   base_dark=0.30, calkey="3"),
    # 海洋: 実物はほぼ無地の銀。シロザケは大きな黒点を持たない種 → 斑点格子は禁。
    # ごく微細・低振幅のスペックルのみ(amp を強く落とし銀地に寄せる)。
    dict(n=4, jp="4 海洋",   regime="speckle", lam=3.0, Da=0.35, amp=0.05, base_dark=0.55, calkey="4"),
    dict(n=5, jp="5 沿岸",   regime="bars",    bars=10, aniso=7.0, amp=0.5, base_dark=0.5, calkey="5"),
    dict(n=6, jp="6 遡上",   regime="bars",    bars=8,  aniso=6.0, amp=1.0, base_dark=0.55, nuptial=True, calkey="6"),
    dict(n=7, jp="7 産卵後", regime="bars",    bars=8,  aniso=6.0, amp=0.8,  base_dark=0.62, nuptial=True, wear=True, calkey="7"),
]

# GM 基本(均一安定&Turing可能域)。kappa=0 で安定性解析が解析的に有効(検証済 λ_T=10.8@Dh20)。
GM = dict(rho=1.0, mu_a=1.0, rho_h=1.0, mu_h=2.0, kappa=0.0, a0=0.0)


def stage_colors(st):
    """calibration から flank/dorsal/bar 色を取得(無ければ既定)。"""
    c = CAL.get(st["calkey"], {})
    flank = hexc(c.get("flank", "#9A9A82")); dorsal = hexc(c.get("dorsal", "#5E6B52"))
    if st.get("nuptial"):
        bar = hexc(c.get("bar_red", "#B57657")); bar2 = hexc(c.get("bar_dark", "#4D4934"))
    else:
        bar = hexc(c.get("bar_dark", "#3A3D28")); bar2 = bar
    return flank, dorsal, bar, bar2


def simulate_stage(st, W=120, H=60, steps=26000, seed=1):
    t, n, body, full, tr = side_mask(W, H)
    L = body.sum(0).astype(bool).sum()          # body length in px (cols spanned)
    A = np.zeros((H, W))
    info = {"lambda_pred": None, "lambda_meas": None}
    Da = st.get("Da", 1.0)
    if st["regime"] == "none":
        A[body] = 0.0
    elif st["regime"] in ("bars", "speckle"):
        if st["regime"] == "bars":
            target = L / st["bars"]
            Dxh = calibrate_Dh("gm", GM, Da, target)
            D = dict(Dx_a=Da, Dy_a=Da, Dx_h=Dxh, Dy_h=Dxh / st["aniso"])
        else:                                    # speckle: 等方・短波長(Da小で短く)
            target = st["lam"]
            Dxh = calibrate_Dh("gm", GM, Da, target)
            D = dict(Dx_a=Da, Dy_a=Da, Dx_h=Dxh, Dy_h=Dxh)
        info["lambda_pred"] = S.turing_analysis("gm", GM, Da, Dxh)["lambda_T"]
        dt = E.cfl_dt(D["Dx_a"], D["Dy_a"], D["Dx_h"], D["Dy_h"], margin=0.4)
        a, h, _ = E.simulate(body, "gm", GM, D, steps=steps, dt=dt, seed=seed, noise=0.03)
        A = E.normalize(a, body)
        info["lambda_meas"] = S.measure_wavelength(A, body, axis="x")
    return A, (t, n, body, full, tr), info


def colorize(st, A, geo):
    t, n, body, full, tr = geo
    H, W = A.shape
    flank, dorsal, bar, bar2 = stage_colors(st)
    cs = np.clip((n + 1) / 2, 0, 1)                       # 0腹..1背 カウンターシェード
    base = flank[None, None] * (1 - cs[..., None] ** 1.4 * 0.6) + dorsal[None, None] * (cs[..., None] ** 1.4 * 0.6)
    # markings
    amp = st.get("amp", 0.0)
    bars = np.clip((A - 0.5) * 2, 0, 1) * amp
    # parr/nuptial は体側中心〜上に出やすい
    if st["regime"] == "bars":
        bars *= np.clip(0.35 + 0.65 * cs, 0, 1)
    mark = bar[None, None] * (1 - 0.4 * (cs[..., None])) + bar2[None, None] * 0.4 * cs[..., None]
    col = base * (1 - bars[..., None]) + mark * bars[..., None]
    # 背の暗線(dorsal stripe)
    stripe = np.exp(-((n - 0.85) ** 2) / (2 * 0.10 ** 2))
    col = col * (1 - 0.35 * stripe[..., None]) + dorsal[None, None] * 0.35 * stripe[..., None]
    # 海洋: 微細点を少し暗く
    if st["regime"] == "speckle":
        col = col * (1 - 0.25 * bars[..., None])
    # 産卵後: 退色・白抜け
    if st.get("wear"):
        rng = np.random.default_rng(7)
        wsig = max(7.0, H * 0.12)            # 解像度に比例(低解像60→7px相当のブロッチ径を維持)
        w = gaussian_filter(rng.standard_normal((H, W)), wsig); w = (w - w.min()) / (np.ptp(w) + 1e-9)
        bl = np.clip(w - 0.6, 0, None)[..., None] * 2
        col = col * (1 - bl) + PAPER[None, None] * bl
    # 仔魚: 腹下のオレンジ卵黄嚢(実物の決定的特徴。非Turingの解剖要素として加算)
    if st.get("yolk"):
        yc = hexc(CAL.get(st["calkey"], {}).get("yolk", "#EE7A38"))
        ex0, ey0 = G.eye_xy(tr)
        yy0, xx0 = np.mgrid[0:H, 0:W]
        g = np.exp(-((((xx0 - (ex0 + 0.12 * W)) / (0.14 * W)) ** 2)
                     + (((yy0 - (ey0 + 0.18 * H)) / (0.085 * H)) ** 2)))
        g = np.clip(g, 0, 1)[..., None]
        col = col * (1 - g) + yc[None, None] * g
    out = np.ones((H, W, 3)) * PAPER
    out[full] = np.clip(col[full], 0, 255)       # 胴+ひれ+尾(模様は胴のみ・ひれは地色)
    # eye
    ex, ey = G.eye_xy(tr)
    yy, xx = np.mgrid[0:H, 0:W]
    eye = (xx - ex) ** 2 + (yy - ey) ** 2 < (W * 0.013) ** 2
    out[eye & full] = [30, 30, 34]
    return out.astype(np.uint8)


def render_hi(st, A_lo, scale=8):
    """低解像でRDを解いた活性場 A_lo を高解像で着色。
    物理(波長較正)は低解像のまま。仕上げのみ高解像化:
      ① 高解像シルエット mask で輪郭をくっきり(NEAREST階段を解消)
      ② 模様場 A を bicubic で滑らかに拡大(ブロックを解消)
    """
    Hlo, Wlo = A_lo.shape
    Wr, Hr = Wlo * scale, Hlo * scale
    geo_hi = side_mask(Wr, Hr)                       # (t,n,body,full,tr) 高解像
    A_hi = zoom(A_lo, (Hr / Hlo, Wr / Wlo), order=3) # bicubic
    A_hi = np.clip(A_hi, 0.0, 1.0)
    A_hi = np.clip((A_hi - 0.5) * 1.5 + 0.5, 0.0, 1.0)  # 平滑化で鈍ったバーのコントラストを回復
    return colorize(st, A_hi, geo_hi)


def main():
    try:
        ft = ImageFont.truetype("/System/Library/Fonts/ヒラギノ明朝 ProN.ttc", 40)
        fl = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 22)
        fs = ImageFont.truetype("/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf", 18)
    except Exception:
        ft = fl = fs = ImageFont.load_default()
    SC = 8                       # 表示拡大
    W, H = 120, 60
    cellw, cellh = W * SC, H * SC
    pad = 24; top = 90; labh = 64
    cv = Image.new("RGB", (pad + len(STAGES) * (cellw + pad), top + cellh + labh), (255, 255, 255))
    dr = ImageDraw.Draw(cv)
    dr.line([(pad, 44), (pad + 460, 44)], fill=(46, 110, 142), width=3)
    dr.text((pad, 52), "反応拡散シミュレーション — シロザケ7段階(Gierer–Meinhardt, 側面)", fill=(30, 30, 30), font=ft)
    rows = []
    for i, st in enumerate(STAGES):
        A, geo, info = simulate_stage(st)        # 低解像でRDを解く(λ較正はここ)
        img = render_hi(st, A, scale=SC)         # 高解像で着色(輪郭・模様ともブロック解消)
        im = Image.fromarray(img)                # すでに cellw×cellh
        x = pad + i * (cellw + pad)
        cv.paste(im, (x, top))
        dr.text((x + 4, top + cellh + 4), st["jp"], fill=(40, 40, 40), font=fl)
        lp = info["lambda_pred"]; lm = info["lambda_meas"]
        note = "" if lp is None else f"λ_T≈{lp:.1f} / FFT {lm:.1f}px" if lm == lm else f"λ_T≈{lp:.1f}px"
        dr.text((x + 4, top + cellh + 34), note, fill=(110, 104, 92), font=fs)
        rows.append((st["jp"], lp, lm))
        print(f"{st['jp']}: regime={st['regime']} λ_pred={lp} λ_meas={lm}")
    cv.save(os.path.join(_OUT, "rd-salmon-montage.png"))
    print("saved", os.path.join(_OUT, "rd-salmon-montage.png"), cv.size)


if __name__ == "__main__":
    main()
