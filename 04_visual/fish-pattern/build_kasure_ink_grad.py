#!/usr/bin/env python3
"""scale-ink-kasure.svg のインク色を「中央=明るい / 外周=深い」放射状に強める新規版。
inkgrad の stop を差し替えるだけ(全 fill が url(#inkgrad) 参照なので一括で効く)。"""
import re, pathlib

from _paths import out
HERE = pathlib.Path(__file__).parent
SRC = out("kasure", "scale-ink-kasure.svg")   # build_kasure_ink.py の出力を入力に取る
OUT = out("kasure", "scale-ink-kasure-grad.svg")

# --- 放射状リカラーのノブ ---
# 重要: gradientUnits="userSpaceOnUse" にすることで、全パスが「作品全体の同一座標系」
# の1つのグラデを参照する=線ごとの個別適用ではなく、統一された水温場になる。
# 座標は viewBox(0..1335 x 0..1247)の絶対値。
CX, CY, R = 668, 855, 1010   # 中心=年輪の核。R=外周(濃紺)に届く半径
# 水温: 中央=暖色(金/クリーム) → 外周=寒色(ティール→スレート→濃紺)
STOPS = [
    (0.00, "#F0E8C4"),  # 核: 暖かい淡黄(高水温)
    (0.10, "#DAC988"),  # 金
    (0.22, "#BBBB86"),  # 退色した黄緑
    (0.36, "#86AC93"),  # セージ〜ティール
    (0.50, "#5F9CA0"),  # ティール/シアン
    (0.64, "#56849D"),  # シアン青
    (0.78, "#566E92"),  # スレートブルー
    (0.90, "#45506F"),  # 深いスレート
    (1.00, "#313752"),  # 外周: 濃紺(低水温)
]

stops_xml = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in STOPS)
NEW = (f'<radialGradient id="inkgrad" gradientUnits="userSpaceOnUse" '
       f'cx="{CX}" cy="{CY}" r="{R}">\n    {stops_xml}\n  </radialGradient>')

s = SRC.read_text()
s, n = re.subn(r'<radialGradient id="inkgrad".*?</radialGradient>', NEW, s, count=1, flags=re.DOTALL)
assert n == 1, f"inkgrad not found ({n})"
OUT.write_text(s)
print(f"written {OUT.name}: {len(s)} bytes (inkgrad replaced={n})")
