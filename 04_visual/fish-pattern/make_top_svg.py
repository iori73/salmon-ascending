#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_top_svg.py — 真上(背側)7段階のソフト表現を「ベクターSVG」で出力(縦・頭=下)。
fish_top_soft.SOFT の段階仕様を流用し、体シルエットを path、縁ぼかしを feGaussianBlur、
体色を linearGradient、卵黄嚢を radialGradient、横帯(パー/カリコ)を blur 付き line、目を circle で構成。
出力: out/top/soft-<n>-<slug>.svg と soft-top-montage.svg。
"""
import os
import numpy as np
import fish_top as FT
from fish_top_soft import SOFT

_DIR = os.path.dirname(os.path.abspath(__file__))
_OUT = os.path.join(_DIR, "out", "top")
os.makedirs(_OUT, exist_ok=True)

CW, CH = 280, 680          # 1段階のキャンバス
CX = CW * 0.5              # 体軸の中央x
TOP = CH * 0.06
LPX = CH * 0.86            # 体軸の画素長(頭t=0が下、尾t=1が上)
PAD = 0.06                 # 体側の左右マージン比(未使用予備)


def _w(t, ws):
    return FT._w(np.array([t]))[0] * LPX * ws


def _ctr(t, bend):
    return FT._center(np.array([t]), bend)[0] * LPX


def _xy(t, edge, bend, ws):
    """体内パラメータ t(0頭→尾) と edge(-1左/+1右) を 縦・頭下 の画素(x,y)へ。"""
    cx = CX + _ctr(t, bend)
    x = cx + edge * _w(t, ws)
    y = TOP + (1.0 - t / 0.885) * LPX        # t=0→下, t=0.885→上(尾柄)
    return x, y


def body_path(bend, ws):
    ts = np.linspace(0.0, 0.885, 60)
    top = [_xy(t, -1, bend, ws) for t in ts]            # 左縁(頭→尾)
    bot = [_xy(t, +1, bend, ws) for t in ts][::-1]      # 右縁(尾→頭)
    pts = top + bot
    d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
    return d


def tail_path(bend, ws):
    # 尾扇(t=0.885 から少し上へ二叉)
    bx, by = _xy(0.885, 0, bend, ws)
    cx = CX + _ctr(1.0, bend)
    ty = TOP + (1.0 - 1.02 / 0.885) * LPX
    spread = 0.10 * LPX
    notchy = TOP + (1.0 - 0.96 / 0.885) * LPX
    w0 = _w(0.885, ws)
    return (f"M {bx - w0:.1f},{by:.1f} L {cx - spread:.1f},{ty:.1f} "
            f"L {cx:.1f},{notchy:.1f} L {cx + spread:.1f},{ty:.1f} L {bx + w0:.1f},{by:.1f} Z")


def stage_svg(sp, x0=0, defs_id="", bar_ts=None):
    """bar_ts: 帯を置く体軸位置t のリスト。与えると等間隔でなくその位置(=本物RD場のピーク)に置く。"""
    bend = sp["bend"]; ws = sp.get("wscale", 1.0)
    c0, c1, c2 = sp["c0"], sp["c1"], sp["c2"]
    uid = f"{defs_id}{sp['n']}"
    g = []
    defs = []
    # 体色: 横方向(x)の対称グラデ c2→c0→c2
    defs.append(
        f'<linearGradient id="bg{uid}" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{c2}"/><stop offset="0.5" stop-color="{c0}"/>'
        f'<stop offset="1" stop-color="{c2}"/></linearGradient>')
    defs.append(f'<filter id="sb{uid}" x="-20%" y="-20%" width="140%" height="140%">'
                f'<feGaussianBlur stdDeviation="2.2"/></filter>')
    grp = [f'<g transform="translate({x0},0)">']
    # 体(ぼかしフィルタで縁を柔らかく)
    grp.append(f'<path d="{body_path(bend, ws)}" fill="url(#bg{uid})" filter="url(#sb{uid})"/>')
    grp.append(f'<path d="{tail_path(bend, ws)}" fill="{c1}" filter="url(#sb{uid})" opacity="0.92"/>')
    # 背正中線(暗・細・ぼかし)
    if sp.get("mid"):
        midpts = [_xy(t, 0, bend, ws) for t in np.linspace(0.04, 0.86, 40)]
        dmid = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in midpts)
        grp.append(f'<path d="{dmid}" fill="none" stroke="{sp["mid"]}" stroke-width="{0.10*LPX:.1f}" '
                   f'stroke-linecap="round" opacity="0.5" filter="url(#sb{uid})"/>')
    # 横帯(パー/カリコ): t沿いに暗帯
    bt = sp.get("bartype", "none")
    if bt in ("parr", "calico"):
        nb = sp.get("barcount", 8); amp = sp.get("baramp", 0.4)
        bc = sp.get("bar_col", "#333"); op = min(0.85, amp + 0.2)
        tlist = bar_ts if bar_ts is not None else [0.14 + 0.70 * (i + 0.5) / nb for i in range(nb)]
        for tb in tlist:
            xl, yl = _xy(tb, -0.92, bend, ws); xr, yr = _xy(tb, +0.92, bend, ws)
            grp.append(f'<line x1="{xl:.1f}" y1="{yl:.1f}" x2="{xr:.1f}" y2="{yr:.1f}" '
                       f'stroke="{bc}" stroke-width="{0.022*LPX:.1f}" stroke-linecap="round" '
                       f'opacity="{op:.2f}" filter="url(#sb{uid})"/>')
    # 卵黄嚢(放射グラデ)
    if sp.get("yolk"):
        defs.append(f'<radialGradient id="yk{uid}"><stop offset="0" stop-color="#F6A766"/>'
                    f'<stop offset="0.6" stop-color="#EE7A38"/><stop offset="1" stop-color="#EE7A38" stop-opacity="0"/></radialGradient>')
        yx, yy = _xy(0.16, 0, bend, ws)
        grp.append(f'<ellipse cx="{yx:.1f}" cy="{yy:.1f}" rx="{0.075*LPX:.1f}" ry="{0.058*LPX:.1f}" '
                   f'fill="url(#yk{uid})"/>')
    # 目(左右2点)
    et = sp.get("eye_t", 0.05); es = sp.get("eye_sep", 0.026) * LPX
    ex, ey = _xy(et, 0, bend, ws)
    for s in (+1, -1):
        grp.append(f'<circle cx="{ex + s*es:.1f}" cy="{ey:.1f}" r="{0.0135*LPX:.1f}" fill="#282A2E"/>')
    grp.append('</g>')
    return "".join(defs), "".join(grp)


def main():
    # 個別
    for sp in SOFT:
        defs, grp = stage_svg(sp, x0=0, defs_id="s")
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{CW}" height="{CH}" '
               f'viewBox="0 0 {CW} {CH}"><defs>{defs}</defs>{grp}</svg>')
        p = os.path.join(_OUT, f"soft-{sp['n']}-{sp['slug']}.svg")
        open(p, "w").write(svg); print("saved", os.path.basename(p))
    # montage
    pad = 18
    MW = pad + len(SOFT) * (CW + pad); MH = CH + 2 * pad
    alld, allg = [], []
    for i, sp in enumerate(SOFT):
        defs, grp = stage_svg(sp, x0=pad + i * (CW + pad), defs_id="m")
        alld.append(defs); allg.append(grp)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{MW}" height="{MH}" viewBox="0 0 {MW} {MH}">'
           f'<rect width="{MW}" height="{MH}" fill="#FAFAF6"/><defs>{"".join(alld)}</defs>'
           f'<g transform="translate(0,{pad})">{"".join(allg)}</g></svg>')
    p = os.path.join(_OUT, "soft-top-montage.svg")
    open(p, "w").write(svg); print("saved", p)


if __name__ == "__main__":
    main()
