#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_stage_vectors.py — 仔魚ベクターと同じ「Figmaで操作できる細密ベクター」を残り6段階
(②稚魚parr ③スモルト ④海洋 ⑤沿岸 ⑥遡上calico ⑦産卵後)で生成する。

形は fish_geom（パラメトリック側面プロファイル）から Catmull-Rom→ベジェで滑らかに起こす
＝「計算で導いた形」。各パーツ(body/fins/tail/back/markings/eye…)を個別 <path> にして
SVGに出力するので、Figma取り込み後もアンカー単位で編集できる。

色は calibration.json の flank/bar を基準に、背=暗化・腹=明化で countershade を付与。
段階で変えるのは「色・縦バー(parrマーク/婚姻色)・銀化/摩耗」だけ。

出力: stage-vec-{n}-{slug}.svg ×6 ＋ stage-vec-montage.svg(横一列)
"""
import os, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.insert(0, HERE)
import fish_geom as G   # _TOP/_BOT プロファイル・eye 位置を共有
from _paths import out as _OUT

SLUG = {1: "alevin", 2: "parr", 3: "smolt", 4: "ocean", 5: "coastal", 6: "river", 7: "postspawn"}

# ---- キャンバス・体格 ----
W, H = 360.0, 140.0
PAD = 16.0
L = W - 2 * PAD          # 体長(px)
CY = H * 0.5
OX = PAD


def hx(s):
    s = s.lstrip("#")
    return np.array([int(s[i:i+2], 16) for i in (0, 2, 4)], float)


def to_hex(c):
    c = np.clip(c, 0, 255).astype(int)
    return "#%02x%02x%02x" % (c[0], c[1], c[2])


def darken(c, f):
    return c * f


def lighten(c, f):
    return c + (255 - c) * (f - 1.0)


def desat(c, f):
    lum = 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    return c * (1 - f) + lum * f


# ---- calibration.json から段階色 ----
CAL = json.load(open(os.path.join(HERE, "calibration.json")))


# 銀化段階は実測色が紫/緑に寄るため銀方向へ脱彩度
DESAT = {3: 0.45, 4: 0.25}


def stage_palette(n):
    c = CAL.get(str(n), {})
    flank = hx(c.get("flank", "#8E8971"))
    if n in DESAT:
        flank = desat(flank, DESAT[n])
    back = darken(flank, 0.60)
    belly = lighten(flank, 1.20)
    if c.get("bar_red"):
        bar = hx(c["bar_red"]); bar2 = hx(c.get("bar_dark", "#4D4934"))
    elif c.get("bar_dark"):
        bar = hx(c["bar_dark"]); bar2 = darken(hx(c["bar_dark"]), 0.8)
    else:
        bar = darken(flank, 0.62); bar2 = darken(flank, 0.5)
    yolk = hx(c["yolk"]) if c.get("yolk") else None
    return dict(flank=flank, back=back, belly=belly, bar=bar, bar2=bar2, yolk=yolk)


# ---- 幾何ヘルパ ----
def htop(t, prof=None):
    return float(G._interp(prof if prof is not None else G._TOP, t))


def hbot(t, prof=None):
    return float(G._interp(prof if prof is not None else G._BOT, t))


def PX(t, sign_h):
    """t と 半高さの符号付き比 sign_h(+上は負y) -> svg座標。sign_h は L単位の符号付きn。"""
    return (OX + t * L, CY - sign_h * L)


def catmull(points, closed=False):
    """点列を通る滑らかな三次ベジェの d 片(先頭Mは付けない)。points: [(x,y),...]"""
    pts = list(points)
    n = len(pts)
    if n < 2:
        return ""
    segs = []
    for i in range(n - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1 = pts[i]
        p2 = pts[i + 1]
        p3 = pts[i + 2] if i + 2 < n else pts[i + 1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        segs.append("C %.2f %.2f %.2f %.2f %.2f %.2f" % (c1[0], c1[1], c2[0], c2[1], p2[0], p2[1]))
    return " ".join(segs)


def body_path(top_prof=None, bot_prof=None):
    top_prof = top_prof if top_prof is not None else G._TOP
    bot_prof = bot_prof if bot_prof is not None else G._BOT
    top = [PX(t, h) for (t, h) in top_prof]              # 背側(上,負y側)
    bot = [PX(t, -h) for (t, h) in bot_prof]             # 腹側(下)
    d = "M %.2f %.2f " % top[0]
    d += catmull(top)
    d += " L %.2f %.2f " % bot[-1]                      # 尾柄で上→下
    d += catmull(list(reversed(bot)))
    d += " Z"
    return d


def back_band_path(depth=0.40, top_prof=None):
    """背の countershade 帯: 背プロファイル → 内側(半高 depth)で戻る。"""
    top_prof = top_prof if top_prof is not None else G._TOP
    top = [PX(t, h) for (t, h) in top_prof]
    inner = [PX(t, h * (1 - depth)) for (t, h) in top_prof]   # 内側= 背半高の depth ぶん下げ
    d = "M %.2f %.2f " % top[0]
    d += catmull(top)
    d += " L %.2f %.2f " % inner[-1]
    d += catmull(list(reversed(inner)))
    d += " Z"
    return d


def belly_band_path(depth=0.45, bot_prof=None):
    bot_prof = bot_prof if bot_prof is not None else G._BOT
    bot = [PX(t, -h) for (t, h) in bot_prof]
    inner = [PX(t, -h * (1 - depth)) for (t, h) in bot_prof]
    d = "M %.2f %.2f " % bot[0]
    d += catmull(bot)
    d += " L %.2f %.2f " % inner[-1]
    d += catmull(list(reversed(inner)))
    d += " Z"
    return d


def fin_fold_path(t0=0.55, t1=0.94, fold_h_max=0.034):
    """仔魚の連続した膜状ひれ(fin fold): 体プロファイルの少し外側を一周する薄い帯。
    個別の背びれ/尻びれの代わりに、背側外縁(t0→t1)→腹側外縁(t1→t0)をたどるリング状の輪郭にする。
    高さはt0/t1で0まで滑らかにテーパーし、中央付近で最大(実際の連続fin foldの盛り上がりを模す)。
    body_path()と同じ構成(t1端は直線で閉じる)にして、閉ループのcatmullシーム歪みを避ける。"""
    ts = np.linspace(t0, t1, 24)

    def taper(t):
        frac = (t - t0) / (t1 - t0)
        return fold_h_max * np.sin(np.pi * frac) ** 0.6

    top = [PX(t, htop(t, G._TOP_ALEVIN) + taper(t)) for t in ts]
    bot = [PX(t, -(hbot(t, G._BOT_ALEVIN) + taper(t))) for t in ts]
    d = "M %.2f %.2f " % top[0]
    d += catmull(top)
    d += " L %.2f %.2f " % bot[-1]
    d += catmull(list(reversed(bot)))
    d += " Z"
    return d


# 卵黄嚢の位置・大きさ(体の輪郭そのものに組み込む膨らみとして共有するパラメータ)
YOLK_CENTER_T = 0.32
YOLK_HALF_WIDTH = 0.17
YOLK_HEIGHT = 0.135


def _yolk_bump(t_array, center=YOLK_CENTER_T, half_width=YOLK_HALF_WIDTH, height=YOLK_HEIGHT):
    """中心からhalf_width以内で滑らかに0→height→0と盛り上がるコサイン型の膨らみ。"""
    d = np.abs(np.asarray(t_array, dtype=float) - center)
    bump = np.zeros_like(d)
    within = d < half_width
    bump[within] = height * np.cos((d[within] / half_width) * (np.pi / 2)) ** 2
    return bump


def alevin_bot_profile_with_yolk(n_pts=60):
    """腹側プロファイル(仔魚)に卵黄嚢の膨らみを足した、密にサンプリングした点列。
    体の輪郭(body_path/belly_band_path)にこれを渡すことで、卵黄嚢を「別パーツの楕円」
    ではなく「体の輪郭そのものが膨らんだ一続きの形」として描ける(体と分離して見える問題の対策)。"""
    ts = np.linspace(0.0, 0.94, n_pts)
    base = np.array([hbot(t, G._BOT_ALEVIN) for t in ts])
    bump = _yolk_bump(ts)
    return list(zip(ts, base + bump))


def yolk_fill_path():
    """卵黄嚢の色だけを塗る内部パス。輪郭線には一切触れず(体の輪郭は既に膨らみ込みで
    一体化しているため)、通常の腹ライン〜膨らんだ腹ラインの間の「膨らんだ分」だけを塗る。"""
    ts = np.linspace(YOLK_CENTER_T - YOLK_HALF_WIDTH * 0.9, YOLK_CENTER_T + YOLK_HALF_WIDTH * 0.9, 28)
    base = np.array([hbot(t, G._BOT_ALEVIN) for t in ts])
    bump = _yolk_bump(ts)
    inner = [PX(t, -h) for t, h in zip(ts, base)]          # 通常の腹ライン(内側)
    outer = [PX(t, -h) for t, h in zip(ts, base + bump)]   # 膨らんだ腹ライン(外側=体の輪郭と一致)
    d = "M %.2f %.2f " % inner[0]
    d += catmull(inner)
    d += " L %.2f %.2f " % outer[-1]
    d += catmull(list(reversed(outer)))
    d += " Z"
    return d


def tail_path():
    x0 = OX + 0.882 * L
    xt = OX + 1.02 * L
    notch = OX + 0.93 * L
    spread = 0.16 * L
    p = [(x0, CY - 0.038 * L), (xt, CY - spread), (notch, CY), (xt, CY + spread), (x0, CY + 0.038 * L)]
    d = "M %.2f %.2f " % p[0]
    for q in p[1:]:
        d += "L %.2f %.2f " % q
    return d + "Z"


def fin_path(nodes, smooth=True):
    pts = [PX(t, h) for (t, h) in nodes]
    if smooth and len(pts) >= 3:
        d = "M %.2f %.2f " % pts[0] + catmull(pts) + " Z"
    else:
        d = "M %.2f %.2f " % pts[0] + " ".join("L %.2f %.2f" % q for q in pts[1:]) + " Z"
    return d


# 各ひれ(背・脂・尻・腹・胸): (t, 符号付き半高比)。+上(背), -下(腹)
FIN_DORSAL = [(0.40, 0.128), (0.45, 0.150), (0.50, 0.215), (0.55, 0.140), (0.55, 0.118)]
FIN_ADIPOSE = [(0.745, 0.066), (0.775, 0.108), (0.805, 0.060)]
FIN_ANAL = [(0.58, -0.100), (0.62, -0.150), (0.66, -0.190), (0.685, -0.095)]
FIN_PELVIC = [(0.48, -0.090), (0.515, -0.165), (0.55, -0.085)]
FIN_PECT = [(0.205, -0.058), (0.245, -0.140), (0.295, -0.165), (0.30, -0.050)]


def eye_xy(prof=None):
    t = 0.062
    return PX(t, 0.33 * htop(t, prof))


def gill_path(top_prof=None, bot_prof=None):
    t = 0.175
    a = PX(t, htop(t, top_prof) * 0.92)
    b = PX(t + 0.02, -hbot(t, bot_prof) * 0.9)
    mid = PX(t - 0.03, 0.0)
    return "M %.2f %.2f Q %.2f %.2f %.2f %.2f" % (a[0], a[1], mid[0], mid[1], b[0], b[1])


def lateral_line_path():
    pts = [PX(t, 0.0) for t in [0.20, 0.35, 0.5, 0.65, 0.85]]
    return "M %.2f %.2f " % pts[0] + catmull(pts)


def kype_path():
    """婚姻色♂の鉤鼻(下顎の張り出し)。"""
    nose = PX(0.0, 0.0)
    p1 = (nose[0] - 0.02 * L, CY + 0.02 * L)
    p2 = (nose[0] + 0.06 * L, CY + 0.075 * L)
    p3 = PX(0.10, -hbot(0.10) * 0.55)
    return "M %.2f %.2f Q %.2f %.2f %.2f %.2f L %.2f %.2f Z" % (
        nose[0], nose[1], p1[0], p1[1], p2[0], p2[1], p3[0], p3[1])


def rrect(x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    return ("M %.2f %.2f H %.2f A %.2f %.2f 0 0 1 %.2f %.2f V %.2f A %.2f %.2f 0 0 1 %.2f %.2f "
            "H %.2f A %.2f %.2f 0 0 1 %.2f %.2f V %.2f A %.2f %.2f 0 0 1 %.2f %.2f Z") % (
        x + r, y, x + w - r, r, r, x + w, y + r, y + h - r, r, r, x + w - r, y + h,
        x + r, r, r, x, y + h - r, y + r, r, r, x + r, y)


def bar_shapes(tc_list, wfrac, top_frac, bot_frac, irregular, rng):
    out = []
    for tc in tc_list:
        tcj = float(np.clip(tc + (rng.uniform(-irregular, irregular) if irregular else 0), 0.12, 0.84))
        ht = htop(tcj) * L; hb = hbot(tcj) * L
        ytop = CY - ht * top_frac
        ybot = CY + hb * bot_frac
        bw = wfrac * L * (1 + (rng.uniform(-0.2, 0.45) if irregular else 0))
        x = OX + tcj * L - bw / 2
        out.append(rrect(x, ytop, bw, ybot - ytop, bw * 0.45))
    return out


# ---- 段階仕様 ----
def stage_spec(n):
    rng = np.random.default_rng(20260621 + n)
    pal = stage_palette(n)
    spec = dict(pal=pal, bars=[], bar_color=pal["bar"], bar_op=0.0,
                back_op=0.55, belly_op=0.0, sheen=0.0, wear=0.0, kype=(n in (6, 7)), yolk=(n == 1))
    if n == 1:      # 仔魚 alevin: 半透明の体＋腹に卵黄嚢、模様なし
        spec["back_op"] = 0.25; spec["belly_op"] = 0.15; spec["sheen"] = 0.15
    elif n == 2:      # 稚魚 parr: 等間隔の縦バー約10本
        tcs = list(np.linspace(0.17, 0.80, 10))
        spec["bars"] = bar_shapes(tcs, 0.028, 0.55, 0.42, 0.0, rng)
        spec["bar_op"] = 0.85; spec["back_op"] = 0.5
    elif n == 3:    # スモルト 銀化: 模様抑制・銀の艶
        spec["sheen"] = 0.55; spec["back_op"] = 0.4; spec["belly_op"] = 0.5
    elif n == 4:    # 海洋: ほぼ無地の銀・強い countershade(黒点なし)
        spec["sheen"] = 0.45; spec["back_op"] = 0.85; spec["belly_op"] = 0.55
    elif n == 5:    # 沿岸: 弱い縦縞が再出現
        tcs = list(np.linspace(0.18, 0.80, 10))
        spec["bars"] = bar_shapes(tcs, 0.024, 0.45, 0.30, 0.0, rng)
        spec["bar_op"] = 0.35; spec["back_op"] = 0.55
    elif n == 6:    # 遡上 calico: 太い不規則縦バー＋婚姻色(赤紫)
        tcs = list(np.linspace(0.20, 0.78, 8))
        spec["bars"] = bar_shapes(tcs, 0.05, 0.6, 0.5, 0.03, rng)
        spec["bar_op"] = 0.8; spec["back_op"] = 0.6
        spec["bar_color"] = pal["bar"]   # bar_red
    elif n == 7:    # 産卵後: calico退色＋摩耗(白抜け斑)
        tcs = list(np.linspace(0.20, 0.78, 8))
        spec["bars"] = bar_shapes(tcs, 0.05, 0.6, 0.5, 0.03, rng)
        spec["bar_op"] = 0.45; spec["back_op"] = 0.6; spec["wear"] = 0.5
    return spec


def wear_blobs(rng, k=7):
    out = []
    for _ in range(k):
        t = rng.uniform(0.25, 0.8); s = rng.uniform(-0.35, 0.35)
        cx, cy = PX(t, s * htop(t))
        rx = rng.uniform(0.03, 0.06) * L; ry = rng.uniform(0.012, 0.028) * L
        out.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#D9D2C4" fill-opacity="0.28"/>' % (cx, cy, rx, ry))
    return out


def render_stage_svg(n, standalone=True):
    sp = stage_spec(n)
    pal = sp["pal"]
    rng = np.random.default_rng(20260621 + n)
    g = []
    g.append('<g data-name="stage-%d-%s">' % (n, SLUG[n]))

    if n == 1:
        # 仔魚(alevin): 成魚シルエットは使わず、薄いリボン状の幼生体形+連続fin foldで描く。
        # 卵黄嚢は体の輪郭(bot_prof)そのものに膨らみとして組み込み、別パーツの楕円にはしない
        # (体と分離して見える問題への対策。yolk_fill_pathは色だけを塗る内部パスで輪郭には触れない)。
        top_prof = G._TOP_ALEVIN
        bot_prof = alevin_bot_profile_with_yolk()
        g.append('  <path data-name="fin-fold" d="%s" fill="%s" fill-opacity="0.85"/>' % (
            fin_fold_path(), to_hex(darken(pal["flank"], 0.85))))
        g.append('  <path data-name="body" d="%s" fill="%s"/>' % (
            body_path(top_prof, bot_prof), to_hex(pal["flank"])))
        g.append('  <path data-name="back" d="%s" fill="%s" fill-opacity="%.2f"/>' % (
            back_band_path(0.42, top_prof), to_hex(pal["back"]), sp["back_op"]))
        if sp["belly_op"] > 0:
            g.append('  <path data-name="belly" d="%s" fill="%s" fill-opacity="%.2f"/>' % (
                belly_band_path(0.5, bot_prof), to_hex(pal["belly"]), sp["belly_op"]))
        if pal.get("yolk") is not None:
            g.append('  <path data-name="yolk-sac" d="%s" fill="%s" fill-opacity="0.92"/>' % (
                yolk_fill_path(), to_hex(pal["yolk"])))
        # 胸びれのみ(対になって早期発達。他の鰭は未分化のためfin foldに含まれる)
        finfill = to_hex(darken(pal["back"], 1.05))
        pect_small = [(t, h * 0.6) for (t, h) in FIN_PECT]
        g.append('  <path data-name="fin-pectoral" d="%s" fill="%s" fill-opacity="0.9"/>' % (
            fin_path(pect_small, True), finfill))
        g.append('  <path data-name="gill" d="%s" fill="none" stroke="%s" stroke-opacity="0.5" stroke-width="1"/>' % (
            gill_path(top_prof, bot_prof), to_hex(darken(pal["back"], 0.8))))
        ex, ey = eye_xy(top_prof)
        g.append('  <circle data-name="eye" cx="%.2f" cy="%.2f" r="%.2f" fill="#F2EEE6"/>' % (ex, ey, 0.024 * L))
        g.append('  <circle data-name="pupil" cx="%.2f" cy="%.2f" r="%.2f" fill="#1E1E22"/>' % (ex, ey, 0.015 * L))
        g.append('</g>')
        inner = "\n".join(g)
        if standalone:
            return ('<svg xmlns="http://www.w3.org/2000/svg" width="%g" height="%g" viewBox="0 0 %g %g">\n%s\n</svg>'
                    % (W, H, W, H, inner))
        return inner

    # tail (背後)
    g.append('  <path data-name="tail" d="%s" fill="%s"/>' % (tail_path(), to_hex(darken(pal["back"], 0.95))))
    # body
    g.append('  <path data-name="body" d="%s" fill="%s"/>' % (body_path(), to_hex(pal["flank"])))
    # countershade 背
    g.append('  <path data-name="back" d="%s" fill="%s" fill-opacity="%.2f"/>' % (
        back_band_path(0.42), to_hex(pal["back"]), sp["back_op"]))
    # 腹の明部 / 銀の艶
    if sp["belly_op"] > 0:
        g.append('  <path data-name="belly" d="%s" fill="%s" fill-opacity="%.2f"/>' % (
            belly_band_path(0.5), to_hex(pal["belly"]), sp["belly_op"]))
    if sp["sheen"] > 0:
        g.append('  <path data-name="sheen" d="%s" fill="#FFFFFF" fill-opacity="%.2f"/>' % (
            belly_band_path(0.7), sp["sheen"] * 0.6))
    # markings 縦バー
    if sp["bars"]:
        g.append('  <g data-name="markings" fill="%s" fill-opacity="%.2f">' % (to_hex(sp["bar_color"]), sp["bar_op"]))
        for i, d in enumerate(sp["bars"]):
            # calico は赤紫と暗色を交互
            if n in (6, 7) and i % 2 == 1:
                g.append('    <path d="%s" fill="%s"/>' % (d, to_hex(pal["bar2"])))
            else:
                g.append('    <path d="%s"/>' % d)
        g.append('  </g>')
    # 摩耗(産卵後)
    if sp["wear"] > 0:
        g.append('  <g data-name="wear">')
        for b in wear_blobs(rng):
            g.append('    ' + b)
        g.append('  </g>')
    # fins
    finfill = to_hex(darken(pal["back"], 1.05))
    for nm, nodes, sm in [("dorsal", FIN_DORSAL, True), ("adipose", FIN_ADIPOSE, True),
                          ("anal", FIN_ANAL, True), ("pelvic", FIN_PELVIC, True), ("pectoral", FIN_PECT, True)]:
        g.append('  <path data-name="fin-%s" d="%s" fill="%s" fill-opacity="0.92"/>' % (nm, fin_path(nodes, sm), finfill))
    # 婚姻色♂の鉤鼻
    if sp["kype"]:
        g.append('  <path data-name="kype" d="%s" fill="%s"/>' % (kype_path(), to_hex(pal["flank"])))
    # gill / lateral line
    g.append('  <path data-name="gill" d="%s" fill="none" stroke="%s" stroke-opacity="0.5" stroke-width="1"/>' % (
        gill_path(), to_hex(darken(pal["back"], 0.8))))
    g.append('  <path data-name="lateral" d="%s" fill="none" stroke="%s" stroke-opacity="0.45" stroke-width="0.8"/>' % (
        lateral_line_path(), to_hex(darken(pal["back"], 0.85))))
    # eye
    ex, ey = eye_xy()
    g.append('  <circle data-name="eye" cx="%.2f" cy="%.2f" r="%.2f" fill="#F2EEE6"/>' % (ex, ey, 0.026 * L))
    g.append('  <circle data-name="pupil" cx="%.2f" cy="%.2f" r="%.2f" fill="#1E1E22"/>' % (ex, ey, 0.016 * L))
    g.append('</g>')
    inner = "\n".join(g)
    if standalone:
        return ('<svg xmlns="http://www.w3.org/2000/svg" width="%g" height="%g" viewBox="0 0 %g %g">\n%s\n</svg>'
                % (W, H, W, H, inner))
    return inner


def main():
    for n in SLUG:
        svg = render_stage_svg(n, standalone=True)
        path = _OUT("stage-vec", "stage-vec-%d-%s.svg" % (n, SLUG[n]))
        with open(path, "w") as fp:
            fp.write(svg)
        print("saved", os.path.basename(path))
    # montage 横一列
    gap = 14
    ns = list(SLUG)
    MW = PAD + len(ns) * (W + gap)
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="%g" height="%g" viewBox="0 0 %g %g">'
             % (MW, H + 28, MW, H + 28)]
    parts.append('<rect width="%g" height="%g" fill="#FAF6EE"/>' % (MW, H + 28))
    for i, n in enumerate(ns):
        x = PAD + i * (W + gap)
        parts.append('<g transform="translate(%.1f,0)">%s</g>' % (x, render_stage_svg(n, standalone=False)))
        parts.append('<text x="%.1f" y="%g" font-family="Hiragino Sans, sans-serif" font-size="14" fill="#555">%d %s</text>'
                     % (x + 8, H + 20, n, SLUG[n]))
    parts.append('</svg>')
    with open(_OUT("stage-vec", "stage-vec-montage.svg"), "w") as fp:
        fp.write("\n".join(parts))
    print("saved stage-vec-montage.svg")


if __name__ == "__main__":
    main()
