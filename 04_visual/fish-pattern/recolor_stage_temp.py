#!/opt/homebrew/bin/python3
"""
recolor_stage_temp.py
scale-stages-combined.svg の各段階(7グループ)を「代表水温の単色」に塗り替える。
- 方針: 真(実水温で塗る/山なり可・同色可)。
- 色: 新色を作らず、既存「水温グラデ」9色からスナップ抽出。
出力: out/stage-scale/scale-stages-combined-temptrue.svg
      out/stage-scale/_temptrue-swatches.png (検証用スウォッチ)
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "out", "stage-scale", "scale-stages-combined.svg")
DST = os.path.join(HERE, "out", "stage-scale", "scale-stages-combined-temptrue.svg")
SWA = os.path.join(HERE, "out", "stage-scale", "_temptrue-swatches.png")

# 既存「水温グラデ」9色（build_lines_grad.py STOPS と同値）暖→寒
PALETTE = ["#F0E8C4", "#DAC988", "#BBBB86", "#86AC93", "#5F9CA0",
           "#56849D", "#566E92", "#45506F", "#313752"]
OFFS = [0.00, 0.10, 0.22, 0.36, 0.50, 0.64, 0.78, 0.90, 1.00]

# 段階: (svg group id, 表示名, 代表水温℃)  ※真=実データ中央値
STAGES = [
    ("stage-1-shigyo",  "仔魚 alevin",    4.0),
    ("stage-2-chigyo",  "稚魚 chigyo",   10.0),
    ("stage-3-smolt",   "降海 smolt",    11.0),
    ("stage-4-ocean",   "海洋 ocean",     8.0),
    ("stage-5-coastal", "沿岸 coastal",  11.0),
    ("stage-6-river",   "遡上 river",     8.0),
    ("stage-7-spawn",   "産卵 spawn",     6.0),
]

TMIN = min(t for *_, t in STAGES)   # 4
TMAX = max(t for *_, t in STAGES)   # 11

def temp_to_color(t):
    """水温→寒さオフセット→9色の最近傍スナップ。"""
    coldness = (TMAX - t) / (TMAX - TMIN)   # 暖=0, 寒=1
    # 最近傍の既存ストップを選ぶ
    idx = min(range(len(OFFS)), key=lambda i: abs(OFFS[i] - coldness))
    return PALETTE[idx], coldness

def main():
    svg = open(SRC).read()
    mapping = []
    for gid, name, t in STAGES:
        col, coldness = temp_to_color(t)
        # <g id="stage-x-..." ... stroke="#XXXXXX" の stroke だけ置換
        pat = re.compile(r'(<g id="' + re.escape(gid) + r'"[^>]*?stroke=")#[0-9A-Fa-f]{6}(")')
        svg, n = pat.subn(lambda m: m.group(1) + col + m.group(2), svg)
        mapping.append((gid, name, t, col, coldness, n))

    open(DST, "w").write(svg)
    print("wrote", DST)
    print(f"{'stage':16}{'temp':>6}{'cold':>7}  color   (replaced)")
    for gid, name, t, col, c, n in mapping:
        print(f"  {name:14}{t:5.0f}°C{c:6.2f}  {col}  x{n}")

    # ---- 検証用スウォッチ ----
    try:
        from PIL import Image, ImageDraw
        W, H, pad = 920, 150, 10
        cw = (W - pad * 2) // len(STAGES)
        im = Image.new("RGB", (W, H), "white")
        dr = ImageDraw.Draw(im)
        for i, (gid, name, t, col, c, n) in enumerate(mapping):
            x0 = pad + i * cw
            rgb = tuple(int(col.lstrip("#")[j:j+2], 16) for j in (0, 2, 4))
            dr.rectangle([x0, 30, x0 + cw - 6, 110], fill=rgb)
            dr.text((x0 + 4, 6), f"{int(t)}C", fill="black")
            dr.text((x0 + 4, 116), col, fill="black")
            dr.text((x0 + 4, 130), name.split()[0], fill="black")
        im.save(SWA)
        print("wrote", SWA)
    except ImportError:
        pass

if __name__ == "__main__":
    main()
