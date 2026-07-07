#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rd_swatch_uniform.py — 模様が形成されない段階(①仔魚・③スモルト)の swatch。
反応拡散の出力は「一様(亜臨界/銀化で遮蔽)」=空間パターンなし。それを正直に
単色〜縦グラデで表現(微小ノイズの艶のみ)。出力: swatch-larva.png / swatch-smolt.png
"""
import os
import numpy as np
from PIL import Image

_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "swatches")
os.makedirs(_OUT, exist_ok=True)
SEED = 20260620


def hexc(s): return np.array([int(s[i:i+2], 16) for i in (1, 3, 5)], float)


def vgrad(G, top, mid, bot):
    """縦方向 top→mid→bot の3点グラデ。"""
    t = np.linspace(0, 1, G)[:, None]
    top, mid, bot = hexc(top), hexc(mid), hexc(bot)
    out = np.zeros((G, G, 3))
    for c in range(3):
        a = np.where(t[:, 0] < 0.5, top[c] + (mid[c] - top[c]) * (t[:, 0] / 0.5),
                     mid[c] + (bot[c] - mid[c]) * ((t[:, 0] - 0.5) / 0.5))
        out[:, :, c] = a[:, None]
    return out


def main():
    G = 200
    rng = np.random.default_rng(SEED)

    # ① 仔魚: 卵黄嚢期。無色素〜淡いアンバー。背にごく疎な初期メラノフォア点のみ。
    larva = vgrad(G, "#CDB997", "#E0D2BC", "#EFE6D7")
    # ごく疎な微小点(初期メラノフォア)を上部のみ
    dots = rng.random((G, G)) < 0.004
    mask_top = (np.arange(G)[:, None] / G) < 0.45
    dot = dots & mask_top
    larva[dot] = larva[dot] * 0.45 + np.array([60, 55, 48]) * 0.55
    larva += rng.normal(0, 2.5, (G, G, 3))
    Image.fromarray(np.clip(larva, 0, 255).astype(np.uint8)).resize((500, 500), Image.NEAREST).save(os.path.join(_OUT, "swatch-larva.png"))
    print("saved swatch-larva.png")

    # ③ スモルト: 銀化(グアニン/プリン層)。背=暗い鋼青緑→銀→白腹。縦の艶筋。
    smolt = vgrad(G, "#54625C", "#C6CCC8", "#EEF1ED")
    # グアニンの縦筋(極めて弱い)
    streak = 1 + 0.03 * np.sin(np.linspace(0, np.pi * 10, G))[None, :, None]
    smolt = smolt * streak
    smolt += rng.normal(0, 3.0, (G, G, 3))
    Image.fromarray(np.clip(smolt, 0, 255).astype(np.uint8)).resize((500, 500), Image.NEAREST).save(os.path.join(_OUT, "swatch-smolt.png"))
    print("saved swatch-smolt.png")


if __name__ == "__main__":
    main()
