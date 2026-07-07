#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fish_top_rd.py — トップビュー(背側)の柄を「本物の反応拡散(Gierer–Meinhardt, λ_T較正済)」で描く版。
rd_salmon.simulate_stage() のGM活性場 A を体軸プロファイル a1d(u) に集約し、cosine擬似縞の代わりに使う。
ソフト版は fish_top_soft.render_soft(bar1d=) を流用、点描版はRD場プロファイルで濃度を作る。
今の cosine 版(soft-*/stip-*)はそのまま。本版の出力: out/top/softrd-* / stiprd-* / *-montage。
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "rd"))
import rd_salmon as RS
import fish_top as FT
import fish_top_soft as STS
import make_top_svg as MSV

_DIR = os.path.dirname(os.path.abspath(__file__))
_OUT = os.path.join(_DIR, "out", "top")
os.makedirs(_OUT, exist_ok=True)
PAPER = (250, 250, 246)
SLUG = {s["n"]: s["slug"] for s in STS.SOFT}
RS_BY_N = {s["n"]: s for s in RS.STAGES}
YOLK = (238, 122, 56)


def rd_profile(n):
    """段階nの本物RD場 A を体軸 u(0頭..1尾) のプロファイル prof(0..1) に集約。bars系のみ意味を持つ。"""
    A, geo, info = RS.simulate_stage(RS_BY_N[n])
    t, nn, body, full, tr = geo
    cols = np.where(body.any(0))[0]
    if cols.size == 0 or np.ptp(A[body]) < 1e-6:
        return None, info
    prof = np.array([A[body[:, c], c].mean() if body[:, c].any() else 0.0 for c in cols])
    prof = (prof - prof.min()) / (np.ptp(prof) + 1e-9)
    u = (cols - cols.min()) / (max(cols.max() - cols.min(), 1))
    return (u.astype(float), prof.astype(float)), info


# ---------- 点描(stipple) RD ----------
def density_rd(W, H, sp, bar1d):
    t, m, body, tr = FT.build(W, H, bend=sp["bend"], wscale=sp.get("wscale", 1.0))
    floor = 0.26
    D = floor + 0.22 * np.ones((H, W)); D[~body] = 0
    stripe = np.exp(-(m ** 2) / (2 * 0.13 ** 2))
    D += 0.34 * stripe * body
    D += 0.08 * (np.abs(m) ** 2) * body
    bt = sp.get("bartype", "none")
    if bt in ("parr", "calico") and bar1d is not None:
        uu, pp = bar1d
        prof = np.interp(np.clip(t / 0.885, 0, 1), uu, pp)
        if bt == "parr":
            bars = np.clip((prof - 0.5) / 0.5, 0, 1) * np.clip(0.35 + 0.65 * np.abs(m), 0, 1)
        else:
            bars = np.clip(prof, 0, 1) ** 1.1
        D += sp.get("baramp", 0.5) * bars * body
    caud = FT._raster(W, H, [FT.caudal_poly(tr)])
    full = body | caud
    D[caud & ~body] = floor * 0.8
    D = np.clip(D, 0, 1); D[~full] = 0
    soft = gaussian_filter(full.astype(float), W * 0.005)
    D *= np.clip(soft, 0, 1) ** 0.6
    return D, full, tr


def prof_peaks(bar1d, thr=0.55):
    """RDプロファイルの極大(=バー位置)を体軸t のリストに。"""
    if bar1d is None:
        return None
    u, p = bar1d; ts = []
    for i in range(1, len(p) - 1):
        if p[i] >= thr and p[i] >= p[i - 1] and p[i] >= p[i + 1]:
            tb = float(np.clip(u[i] * 0.885, 0.10, 0.85))
            if not ts or abs(tb - ts[-1]) > 0.04:
                ts.append(tb)
    return ts or None


def to_vertical(x, y, Wc):
    return y, Wc - x


def render_stip_rd(sp, bar1d, Wc=900, Hc=300, SS=2, dot_k=0.05):
    D, full, tr = density_rd(Wc, Hc, sp, bar1d)
    ox, oy, L, _ = tr
    n = sp["n"]
    pts, di = FT.weighted_voronoi(D, int(D.sum() * dot_k), seed=n + 70)
    stops = FT.color_ramp(n)
    Wv, Hv = Hc, Wc
    img = Image.new("RGBA", (Wv * SS, Hv * SS), (0, 0, 0, 0)); dr = ImageDraw.Draw(img, "RGBA")
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wv}" height="{Hv}" viewBox="0 0 {Wv} {Hv}">']
    for (x, y), d in zip(pts, di):
        r = 0.55 + 1.7 * np.sqrt(max(d, 0))
        c = FT.ramp_color(stops, d)
        if n == 1:
            tt = (x - ox) / L
            if 0.10 < tt < 0.225 and abs(y - oy) < 0.075 * L:
                c = np.array(YOLK, float)
        vx, vy = to_vertical(x, y, Wc)
        ci = (int(c[0]), int(c[1]), int(c[2]))
        dr.ellipse([(vx - r) * SS, (vy - r) * SS, (vx + r) * SS, (vy + r) * SS], fill=(ci[0], ci[1], ci[2], 200))
        svg.append(f'<circle cx="{vx:.1f}" cy="{vy:.1f}" r="{r:.2f}" fill="rgb({ci[0]},{ci[1]},{ci[2]})" fill-opacity="0.8"/>')
    if n == 1:
        for s in (+1, -1):
            ey = oy + s * 0.020 * L; vx, vy = to_vertical(ox + 0.05 * L, ey, Wc); rr = 0.018 * L
            dr.ellipse([(vx - rr) * SS, (vy - rr) * SS, (vx + rr) * SS, (vy + rr) * SS], fill=(40, 42, 46, 255))
            svg.append(f'<circle cx="{vx:.1f}" cy="{vy:.1f}" r="{rr:.1f}" fill="#282A2E"/>')
    svg.append('</svg>')
    return img.resize((Wv, Hv), Image.LANCZOS), "".join(svg)


def main():
    try:
        ft = ImageFont.truetype("/System/Library/Fonts/ヒラギノ明朝 ProN.ttc", 38)
        fl = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 22)
    except Exception:
        ft = fl = ImageFont.load_default()

    profiles = {}
    print("— 本物RD場(GM)を解いて体軸プロファイルに集約 —")
    for sp in STS.SOFT:
        n = sp["n"]
        if sp["bartype"] in ("parr", "calico"):
            b, info = rd_profile(n)
            profiles[n] = b
            print(f"  段階{n} {sp['slug']}: λ_pred={info.get('lambda_pred')} λ_meas={info.get('lambda_meas')}")
        else:
            profiles[n] = None

    W, Hh = 280, 680
    soft_v, stip_v = [], []
    for sp in STS.SOFT:
        n = sp["n"]; slug = sp["slug"]
        # soft-rd (PNG + ベクターSVG: バーは本物RD場のピーク位置に)
        v = STS.vertical(n, W, Hh, bar1d=profiles[n])
        v.save(os.path.join(_OUT, f"softrd-{n}-{slug}.png")); soft_v.append((sp, v))
        bts = prof_peaks(profiles[n])
        defs, grp = MSV.stage_svg(sp, x0=0, defs_id="rd", bar_ts=bts)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{MSV.CW}" height="{MSV.CH}" '
               f'viewBox="0 0 {MSV.CW} {MSV.CH}"><defs>{defs}</defs>{grp}</svg>')
        open(os.path.join(_OUT, f"softrd-{n}-{slug}.svg"), "w").write(svg)
        # stip-rd
        png, svg = render_stip_rd(sp, profiles[n])
        png.save(os.path.join(_OUT, f"stiprd-{n}-{slug}.png"))
        open(os.path.join(_OUT, f"stiprd-{n}-{slug}.svg"), "w").write(svg)
        stip_v.append((sp, png))
        print("saved softrd/stiprd -%d-%s" % (n, slug))

    def montage(items, title, fn):
        cw, ch = items[0][1].size; pad = 18; top = 84; labh = 34
        MW = pad + len(items) * (cw + pad); MH = top + ch + labh + pad
        cv = Image.new("RGB", (MW, MH), PAPER); dr = ImageDraw.Draw(cv)
        dr.line([(pad, 30), (pad + 340, 30)], fill=(46, 110, 142), width=3)
        dr.text((pad, 42), title, fill=(40, 40, 36), font=ft)
        for i, (sp, im) in enumerate(items):
            x = pad + i * (cw + pad); cv.paste(im, (x, top), im)
            dr.text((x + 4, top + ch + 2), sp["jp"], fill=(60, 60, 60), font=fl)
        p = os.path.join(_OUT, fn); cv.save(p); print("saved", p, cv.size)

    montage(soft_v, "ソフト・真上 7段階 — 本物の反応拡散(GM, λ_T較正)で柄を生成", "softrd-top-montage.png")
    montage(stip_v, "点描・真上 7段階 — 本物の反応拡散(GM, λ_T較正)で柄を生成", "stiprd-top-montage.png")


if __name__ == "__main__":
    main()
