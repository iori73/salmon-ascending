#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
outline_check.py — hanga-v1の必須ルール「輪郭線(キーライン)が一切ない」を、
目視ではなくピクセル解析で客観的に判定する。

目視判定は本パイプラインの過程で複数回誤り(anchor画像を「輪郭線なし」と誤判定)を
起こしたため、この一項目だけは機械的な指標に置き換える。

原理: モルフォロジーのblack top-hat変換(closing(輝度) - 輝度)を使う。
  closingは「構造要素(SE)より細い暗い構造」を周囲の明るさで埋めてしまう一方、
  SEより太い暗い領域(瞳孔・パーマークなど正当な塗りの暗色)はほぼそのまま残す。
  よって tophat = closing - 輝度 が大きい画素は「SEより細い暗い線状構造」＝輪郭線の
  可能性が高い。単純な勾配ベースの検出だと「大きな暗い塗り領域の縁」も誤検出したが、
  この手法ならパーマークや瞳孔のような正当な大きい暗色塗りを誤検出しにくい。

使い方:
    python3 outline_check.py <image.png> [image2.png ...]
    python3 outline_check.py --all   # attempts/配下の *hanga-v1*.png + style/anchor-hanga-v1.png を一括判定
"""
import glob
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
PIPELINE_ROOT = os.path.dirname(HERE)

# 較正済みパラメータ:
# - 確定has_outlineサンプル 6/01-hanga-v1.png(ユーザー確認済みの太い輪郭線あり)が高スコアになること
# - 確定has_outlineサンプル 6/02-hanga-v1.png(旧anchor、ユーザーが目視で輪郭線ありと訂正)も
#   6/01よりは低くとも明確にOUTLINE側に分類されること
# の2点で較正した。
SE_SIZE = 7             # 構造要素のサイズ(px)。想定される輪郭線の太さ(~3-6px)より大きく、
                        # 瞳孔・パーマークなど正当な暗色塗り(数十px)より小さく設定。
                        # 11だと歯のような微細な形状(数px幅)まで歪めてしまうため7に縮小。
TOPHAT_THRESH = 18      # tophat値がこれを超えたら「線」画素とみなす(0-255輝度スケール)
ABS_DARK_THRESH = 130   # かつ元の輝度がこれより暗い画素のみ対象(明るい塗りの微小ムラを除外)
OUTLINE_FRAC_THRESH = 0.006  # 全画素中「線」画素の割合がこれを超えたら has_outline=True


def _luminance(arr: np.ndarray) -> np.ndarray:
    return 0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]


def outline_score(path: str) -> dict:
    im = np.array(Image.open(path).convert("RGB")).astype(float)
    L = _luminance(im)

    closing = ndimage.grey_closing(L, size=(SE_SIZE, SE_SIZE))
    tophat = closing - L

    stroke_mask = (tophat > TOPHAT_THRESH) & (L < ABS_DARK_THRESH)
    frac = float(stroke_mask.sum()) / L.size

    return {
        "image": path,
        "stroke_pixels": int(stroke_mask.sum()),
        "total_pixels": int(L.size),
        "outline_fraction": round(frac, 5),
        "has_outline": bool(frac > OUTLINE_FRAC_THRESH),
    }


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    if args == ["--all"]:
        paths = sorted(glob.glob(os.path.join(PIPELINE_ROOT, "attempts", "**", "*hanga-v1*.png"), recursive=True))
        paths += sorted(glob.glob(os.path.join(PIPELINE_ROOT, "style", "*hanga-v1*.png")))
    else:
        paths = args

    results = [outline_score(p) for p in paths]
    results.sort(key=lambda r: -r["outline_fraction"])
    for r in results:
        flag = "OUTLINE" if r["has_outline"] else "clean  "
        print("%s  %.5f  %s" % (flag, r["outline_fraction"], os.path.relpath(r["image"], PIPELINE_ROOT)))
    return results


if __name__ == "__main__":
    main()
