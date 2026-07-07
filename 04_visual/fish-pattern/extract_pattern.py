#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
実写(きれいな図譜/標本)から「背面に見える模様」を抽出 — 推測でなく本物の markings を学習。
方式(堅牢): plain背景の魚を色でセグメント→列ごとにマスクで魚の上端(背の稜線)と中央(側線)を求め、
その背帯(ridge→lateral)を正規化タイル(M行: 0=稜線→側線, T列: 頭→尾)へリサンプル。
真上では |m|=0(稜線)→1(側線・体の縁) に対応。鮮赤紫の下方flankは真上で不可視なので除外。
出力: pattern_top_<st>.png(実RGB) / _dark(濃度) / _debug(マスク&帯) / _preview
"""
import os
import numpy as np
from PIL import Image, ImageDraw
from _paths import out as _OUT
from scipy.ndimage import binary_closing, binary_opening, gaussian_filter1d

# bbox=魚の外接矩形(x0,y0,x1,y1), head_left=頭が左か, band=側線までの体高比(0.5=中央)
SOURCES = {
    6: dict(img="ref/c6male.png", bbox=(16, 32, 478, 182), head_left=True, band=0.62,
            note="婚姻色雄 図譜 Dog Salmon Breeding Male"),
    4: dict(img="ref/c4fda.png",  bbox=(52, 104, 470, 212), head_left=True, band=0.55,
            note="海洋 FDA標本 O. keta(銀・spot無)"),
    2: dict(img="/tmp/plate_fingerling.jpg", bbox=(55, 55, 712, 172), head_left=True, band=0.55,
            note="稚魚 FMIB37734 Dog Salmon Fingerling(パーマーク・種正確)"),
    5: dict(img="/tmp/plate_adult34142.jpg", bbox=(35, 45, 842, 182), head_left=True, band=0.55,
            note="沿岸 FMIB34142 Dog Salmon(銀・engraving=単色)"),
    3: dict(img="/tmp/plate_smolt.jpg", bbox=(30, 40, 305, 112), head_left=True, band=0.55,
            note="スモルト FMIB37731 Dog salmon fry(→銀化変換)"),
}
T_SAMP = 480
M_SAMP = 90


def fish_mask(crop):
    """plain背景(淡色)から魚を分離。魚=暗いor彩度高い。"""
    rgb = crop.astype(float)
    mx = rgb.max(2); mn = rgb.min(2)
    V = mx / 255.0
    S = (mx - mn) / (mx + 1e-6)
    bg = (V > 0.74) & (S < 0.22)          # 淡色・低彩度=背景
    m = ~bg
    m = binary_opening(m, np.ones((3, 3)))
    m = binary_closing(m, np.ones((9, 9)))
    # 最大連結成分だけ残す
    from scipy.ndimage import label
    lab, n = label(m)
    if n > 0:
        sizes = np.bincount(lab.ravel()); sizes[0] = 0
        m = lab == sizes.argmax()
    return m


def extract(stage):
    s = SOURCES[stage]
    im = np.asarray(Image.open(s["img"]).convert("RGB"))
    x0, y0, x1, y1 = s["bbox"]
    crop = im[y0:y1, x0:x1].astype(float)
    H, W = crop.shape[:2]
    mask = fish_mask(crop)
    if not s["head_left"]:
        crop = crop[:, ::-1]; mask = mask[:, ::-1]
    # 列ごとに魚の上端(ridge)と中央(lateral)を求め背帯をサンプル
    tile = np.zeros((M_SAMP, T_SAMP, 3))
    valid = np.zeros(T_SAMP, bool)
    tops = np.full(W, np.nan); mids = np.full(W, np.nan)
    for cx in range(W):
        col = np.where(mask[:, cx])[0]
        if len(col) < 6:
            continue
        top = col.min(); bot = col.max()
        tops[cx] = top; mids[cx] = top + (bot - top) * s["band"]
    # 端の欠損を補間し平滑化
    xs = np.arange(W)
    for arr in (tops, mids):
        ok = ~np.isnan(arr)
        if ok.sum() > 10:
            arr[~ok] = np.interp(xs[~ok], xs[ok], arr[ok])
    tops_s = gaussian_filter1d(tops, 4); mids_s = gaussian_filter1d(mids, 4)
    for ti in range(T_SAMP):
        # t: 0=頭(左) .. 1=尾(右)。head_left済みなので列= t*W
        fx = ti / (T_SAMP - 1) * (W - 1)
        cx = int(round(fx))
        top = tops_s[cx]; mid = mids_s[cx]
        for mi in range(M_SAMP):
            sf = mi / (M_SAMP - 1)            # 0=稜線(top) .. 1=側線(mid)
            yy = top + sf * (mid - top)
            iy = int(np.clip(round(yy), 0, H - 1))
            tile[mi, ti] = crop[iy, cx]
        valid[ti] = True
    out = Image.fromarray(tile.astype(np.uint8))
    out.save(_OUT("pattern", f"pattern_top_{stage}.png"))
    lum = (0.299 * tile[..., 0] + 0.587 * tile[..., 1] + 0.114 * tile[..., 2]) / 255
    dark = 1 - lum
    dark = (dark - dark.min()) / (np.ptp(dark) + 1e-9)
    Image.fromarray((dark * 255).astype(np.uint8)).save(_OUT("pattern", f"pattern_top_{stage}_dark.png"))
    # debug: マスク輪郭 + ridge/mid ライン
    dbgimg = (crop * 0.6 + np.dstack([mask * 255] * 3) * 0.4).astype(np.uint8)
    dbg = Image.fromarray(dbgimg); dd = ImageDraw.Draw(dbg)
    for cx in range(0, W, 4):
        dd.point((cx, tops_s[cx]), fill=(255, 0, 0))
        dd.point((cx, mids_s[cx]), fill=(0, 120, 255))
    dbg.save(_OUT("pattern", f"pattern_top_{stage}_debug.png"))
    out.resize((T_SAMP, M_SAMP * 3), Image.NEAREST).save(_OUT("pattern", f"pattern_top_{stage}_preview.png"))
    print(f"stage {stage}: tile {out.size}  ({s['note']})")


def _lum(t):
    return 0.299 * t[..., 0] + 0.587 * t[..., 1] + 0.114 * t[..., 2]


def derive_smolt():
    """3スモルト=実写の稚魚(fry)を銀化変換(chumは稚魚で降海→smolt=銀化したfry)。
    パーの濃淡は実写由来のまま、彩度を落とし冷たい銀へ寄せる。"""
    p = _OUT("pattern", "pattern_top_3.png")
    if not os.path.exists(p):
        return
    t = np.asarray(Image.open(p).convert("RGB"), float)
    lum = _lum(t)
    silver = np.stack([lum * 0.92 + 18, lum * 0.95 + 22, lum * 1.0 + 30], -1)  # 冷たい銀青
    out = np.clip(0.45 * t + 0.55 * silver, 0, 255)
    Image.fromarray(out.astype(np.uint8)).save(p)
    print("derived 3: 銀化(silvering)適用")


def derive_postspawn():
    """7産卵後=実写の6遡上calicoタイルを暗化・退色・白抜け(wear)。post-spawnは婚姻色の劣化。"""
    src = _OUT("pattern", "pattern_top_6.png")
    if not os.path.exists(src):
        return
    t = np.asarray(Image.open(src).convert("RGB"), float)
    lum = _lum(t)[..., None]
    dark = t * 0.55                                   # 暗く
    faded = 0.55 * dark + 0.45 * (lum * 0.5)          # 退色(灰へ)
    rng = np.random.default_rng(7)
    from scipy.ndimage import gaussian_filter as gf
    wear = gf(rng.standard_normal(t.shape[:2]), 6)
    wear = (wear - wear.min()) / (np.ptp(wear) + 1e-9)
    blotch = np.clip(wear - 0.62, 0, None)[..., None] * 3   # 白抜け斑
    out = np.clip(faded + blotch * 120, 0, 255)
    Image.fromarray(out.astype(np.uint8)).save(_OUT("pattern", "pattern_top_7.png"))
    print("derived 7: 退色+白抜け(post-spawn)適用")


if __name__ == "__main__":
    for st in SOURCES:
        extract(st)
    derive_smolt()
    derive_postspawn()

