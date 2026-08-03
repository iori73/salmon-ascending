#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
outline_remove.py — outline_check.py が検出した「線状の暗い構造(キーライン)」を、
生成のやり直しに頼らず、確定的な後処理で除去する。

プロンプトだけでhanga-v1の「輪郭線ゼロ」を達成しようとする試みは複数回失敗した
(モデル自体に「魚イラスト=輪郭線あり」という強い先行傾向があるらしい)。
そこで方針転換: 生成はそのまま行い、outline_check.py と同じblack top-hat検出で
線状画素を特定した後、各線状画素を「最も近い非線状画素の色」で塗り替える
(最近傍インペインティング)。線は数px幅の細い構造なので、この手法で
不自然な穴を残さず自然に周囲の色に置き換えられる。

使い方:
    python3 outline_remove.py <in.png> <out.png>
"""
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

import outline_check as oc


def remove_outline(in_path: str, out_path: str) -> dict:
    im = np.array(Image.open(in_path).convert("RGB")).astype(np.uint8)
    L = oc._luminance(im.astype(float))

    closing_L = ndimage.grey_closing(L, size=(oc.SE_SIZE, oc.SE_SIZE))
    tophat = closing_L - L
    stroke_mask = (tophat > oc.TOPHAT_THRESH) & (L < oc.ABS_DARK_THRESH)

    # 最近傍インペインティングは曲線境界でギザギザ(階段状)の継ぎ目を生むため使わない。
    # 代わりに各RGBチャンネルをそれぞれclosingし、その結果(=線を周囲の色で滑らかに埋めた値)を
    # stroke_mask部分にだけ採用する。closingはモルフォロジー的に形状を保ったまま細い暗線だけ除去する
    # ための演算なので、境界の滑らかさが自然に保たれる。
    closed_channels = [
        ndimage.grey_closing(im[..., c].astype(float), size=(oc.SE_SIZE, oc.SE_SIZE))
        for c in range(3)
    ]
    filled = im.astype(float).copy()
    for c in range(3):
        filled[..., c] = np.where(stroke_mask, closed_channels[c], im[..., c])
    filled = np.clip(filled, 0, 255).astype(np.uint8)

    Image.fromarray(filled).save(out_path)

    before_frac = float(stroke_mask.sum()) / L.size
    after = oc.outline_score(out_path)
    return {
        "input": in_path,
        "output": out_path,
        "stroke_fraction_before": round(before_frac, 5),
        "stroke_fraction_after": after["outline_fraction"],
        "has_outline_after": after["has_outline"],
    }


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    result = remove_outline(sys.argv[1], sys.argv[2])
    for k, v in result.items():
        print("%s: %s" % (k, v))


if __name__ == "__main__":
    main()
