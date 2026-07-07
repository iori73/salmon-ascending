#!/opt/homebrew/bin/python3
"""
handdraw_stage_lines.py
scale-stages-combined-temptrue.svg の各同心円ラインを「手描きペン線」化する。
（共有された Fresco の魚イラストの外枠線の質感を狙う）

変換:
  1) 手ブレ  : 各線に低周波の揺らぎ（真円/コンパス感を消す。線ごとに独立シード）
  2) 可変幅  : 端をすぼめるテーパー + 筆圧ムラ → 塗りリボン化
  3) 縁の粗さ: 高周波の微ノイズで輪郭をわずかにざらつかせる
  4) 色      : 段階の代表水温色をそのまま継承

出力: out/stage-scale/scale-stages-combined-handdrawn.svg
      out/stage-scale/_handdrawn-preview.png
"""
import os, re, math

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "out", "stage-scale", "scale-stages-combined-temptrue.svg")
DST = os.path.join(HERE, "out", "stage-scale", "scale-stages-combined-handdrawn.svg")
PNG = os.path.join(HERE, "out", "stage-scale", "_handdrawn-preview.png")

# ── 手描き感のノブ ───────────────────────────────
WOBBLE_AMP   = 1.6   # 手ブレの振幅(px)
WOBBLE_WAVE  = 46.0  # 手ブレの波長(px) 大きいほどゆったり
WIDTH_SCALE  = 1.25  # 基準線幅の倍率
WIDTH_JITTER = 0.45  # 筆圧ムラ(0=均一,0.5=±50%)
EDGE_ROUGH   = 0.22  # 縁のざらつき(px相当の比率)
TAPER_LEN    = 7.0   # 端をすぼめる距離(px)
MIN_PTS      = 2

# ── 決定論ノイズ ─────────────────────────────────
def _rng(i, seed):
    x = (i * 374761393 + seed * 668265263) & 0xFFFFFFFF
    x = (x ^ (x >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((x ^ (x >> 16)) & 0xFFFFFFFF) / 0xFFFFFFFF * 2 - 1

def _sm(a, b, t):
    t = t * t * (3 - 2 * t); return a + (b - a) * t

def noise(x, seed):
    i = math.floor(x); return _sm(_rng(i, seed), _rng(i + 1, seed), x - i)

def fbm(x, seed):
    return 0.6*noise(x,seed)+0.3*noise(x*2.2,seed+7)+0.1*noise(x*4.6,seed+19)

# ── SVGパース ────────────────────────────────────
FLOAT = re.compile(r'-?\d+\.?\d*')

def parse_paths(svg):
    """[(stage_color, [(x,y),...]), ...]"""
    out = []
    for gm in re.finditer(r'<g id="(stage-\d-[a-z]+)"[^>]*?stroke="(#[0-9A-Fa-f]{6})"[^>]*?>(.*?)</g>', svg, re.S):
        color = gm.group(2)
        body = gm.group(3)
        for pm in re.finditer(r'<path d="([^"]+)"', body):
            nums = [float(x) for x in FLOAT.findall(pm.group(1))]
            pts = list(zip(nums[0::2], nums[1::2]))
            if len(pts) >= MIN_PTS:
                out.append((color, pts))
    return out

# ── 1本を手描きリボンに ──────────────────────────
def handdraw(pts, base_w, seed):
    # 弧長
    s = [0.0]
    for i in range(1, len(pts)):
        dx = pts[i][0]-pts[i-1][0]; dy = pts[i][1]-pts[i-1][1]
        s.append(s[-1] + math.hypot(dx, dy))
    total = s[-1]
    if total < 1e-3:
        return None
    L, R = [], []
    for i, (x, y) in enumerate(pts):
        # 接線→法線
        a = max(0, i-1); b = min(len(pts)-1, i+1)
        tx = pts[b][0]-pts[a][0]; ty = pts[b][1]-pts[a][1]
        tl = math.hypot(tx, ty) or 1.0
        nx, ny = -ty/tl, tx/tl
        # 手ブレ（低周波）
        wob = fbm(s[i]/WOBBLE_WAVE, seed) * WOBBLE_AMP
        cx = x + nx*wob; cy = y + ny*wob
        # 幅: テーパー(両端) × 筆圧ムラ × 縁ざらつき
        taper = min(1.0, s[i]/TAPER_LEN) * min(1.0, (total-s[i])/TAPER_LEN)
        taper = taper**0.7
        press = 1.0 + WIDTH_JITTER * fbm(s[i]/22.0, seed+5)
        w = base_w * WIDTH_SCALE * taper * max(0.15, press)
        eL = EDGE_ROUGH * base_w * fbm(s[i]/6.0, seed+11)
        eR = EDGE_ROUGH * base_w * fbm(s[i]/6.0, seed+23)
        L.append((cx + nx*(w/2+eL), cy + ny*(w/2+eL)))
        R.append((cx - nx*(w/2+eR), cy - ny*(w/2+eR)))
    return L + R[::-1]

def main():
    svg = open(SRC).read()
    m = re.search(r'<svg[^>]*width="(\d+)"[^>]*height="(\d+)"', svg)
    W, H = int(m.group(1)), int(m.group(2))
    lines = parse_paths(svg)
    print(f"parsed {len(lines)} lines, canvas {W}x{H}")

    # base width を段階順に（太→細）。stroke-width が拾えないので順序近似:
    # ここでは色ごとに固定幅テーブルを使う
    BW = {"#313752":1.0, "#566E92":1.4, "#86AC93":1.9, "#5F9CA0":1.9,
          "#DAC988":2.6, "#F0E8C4":3.0}
    DEFAULT_BW = 2.0

    polys = []
    for idx, (color, pts) in enumerate(lines):
        ribbon = handdraw(pts, BW.get(color, DEFAULT_BW), seed=idx*131+7)
        if ribbon:
            polys.append((color, ribbon))

    # ---- SVG出力 ----
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
             f'<rect width="{W}" height="{H}" fill="#ffffff"/>']
    for color, rib in polys:
        d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in rib) + " Z"
        parts.append(f'<path d="{d}" fill="{color}" opacity="0.96"/>')
    parts.append("</svg>")
    open(DST, "w").write("\n".join(parts))
    print("wrote", DST)

    # ---- PILプレビュー ----
    try:
        from PIL import Image, ImageDraw
        SS = 2  # supersample
        im = Image.new("RGB", (W*SS, H*SS), "white")
        dr = ImageDraw.Draw(im, "RGBA")
        for color, rib in polys:
            rgb = tuple(int(color.lstrip("#")[j:j+2],16) for j in (0,2,4)) + (245,)
            dr.polygon([(x*SS, y*SS) for x, y in rib], fill=rgb)
        im = im.resize((W, H), Image.LANCZOS)
        im.save(PNG)
        print("wrote", PNG)
    except ImportError:
        pass

if __name__ == "__main__":
    main()
