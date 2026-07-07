#!/opt/homebrew/bin/python3
"""
build_swim_trace.py — 鮭の生活史を「泳ぎの軌跡（トラック）」として一本の線にする。

コンセプト:
  円弧の弧長 = 各ステージの期間。
  ただし可視線は真円ではなく、ステージごとに性格の変わる「流跡線」。
    - 振幅 amp   : 泳ぎの伸びやかさ / 回遊スケール
    - 周波数 freq: ヒレ打ちの細かさ / 定位のせわしなさ
    - 乱れ jitter: 乱流・抵抗・全力さ（高いほど荒れる）
    - 線幅 width : 遊泳の力強さ（可変幅リボンで描く）

出力:
  out/swim_trace_linear.svg  … 水温ラインの下に展開する横展開版 (B案)
  out/swim_trace_radial.svg  … 鱗の弧をガイドに蛇行させる同心円版 (A案)
  + 同名 .png プレビュー（PIL）
"""
import math, os, struct, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

# ── 生活史ステージ定義 ───────────────────────────────────────────
# dur は相対期間（弧長/横幅に比例）。amp/freq/jitter/width は線の性格。
# color は既存パレット F0E8C4(暖/誕生) → 313752(寒/成熟) のランプから。
STAGES = [
    # name,            dur,  amp,  freq, jitter, width, color
    ("仔魚 alevin",    0.04,  1.0,  0.0,  0.5,   1.5, "#F0E8C4"),
    ("稚魚 fry",       0.12,  5.0, 15.0,  3.5,   2.0, "#DAC988"),
    ("降海 smolt",     0.07,  9.0,  5.0,  1.0,   2.6, "#BBBB86"),
    ("海洋回遊 ocean", 0.52, 28.0,  1.4,  0.4,   3.6, "#5F9CA0"),
    ("回帰 return",    0.08, 15.0,  3.0,  1.2,   3.0, "#56849D"),
    ("遡上 upstream",  0.12,  7.0, 11.0,  7.0,   2.6, "#566E92"),
    ("産卵 spawning",  0.05,  3.0, 17.0,  9.0,   1.8, "#313752"),
]

SAMPLES = 1600  # 軌跡の分解能

# ── 決定論的な value noise（乱流用、毎回同じ結果） ──────────────────
def _rng(i, seed):
    x = (i * 374761393 + seed * 668265263) & 0xFFFFFFFF
    x = (x ^ (x >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((x ^ (x >> 16)) & 0xFFFFFFFF) / 0xFFFFFFFF * 2 - 1

def _smooth(a, b, t):
    t = t * t * (3 - 2 * t)
    return a + (b - a) * t

def noise(x, seed=0):
    i = math.floor(x)
    return _smooth(_rng(i, seed), _rng(i + 1, seed), x - i)

def fbm(x, seed=0):
    return 0.6 * noise(x, seed) + 0.3 * noise(x * 2.3, seed + 7) + 0.15 * noise(x * 4.7, seed + 19)

# ── パラメータをtに沿って連続補間（境界をなめらかに繋ぐ） ───────────
def stage_at(t):
    """t∈[0,1] → (補間済みパラメータ, 境界からの混合)。"""
    total = sum(s[1] for s in STAGES)
    acc = 0.0
    bounds = []  # 各ステージの開始t
    for s in STAGES:
        bounds.append(acc / total)
        acc += s[1]
    bounds.append(1.0)
    # 該当ステージ
    for k in range(len(STAGES)):
        if bounds[k] <= t <= bounds[k + 1] or k == len(STAGES) - 1:
            lo, hi = bounds[k], bounds[k + 1]
            local = (t - lo) / max(hi - lo, 1e-9)
            # 隣接ステージとブレンド（境界±15%をクロスフェード）
            amp, freq, jit, wid = STAGES[k][2], STAGES[k][3], STAGES[k][4], STAGES[k][5]
            blend = 0.18
            if local < blend and k > 0:
                f = (blend - local) / blend * 0.5
                p = STAGES[k - 1]
                amp = amp * (1 - f) + p[2] * f
                freq = freq * (1 - f) + p[3] * f
                jit = jit * (1 - f) + p[4] * f
                wid = wid * (1 - f) + p[5] * f
            if local > 1 - blend and k < len(STAGES) - 1:
                f = (local - (1 - blend)) / blend * 0.5
                n = STAGES[k + 1]
                amp = amp * (1 - f) + n[2] * f
                freq = freq * (1 - f) + n[3] * f
                jit = jit * (1 - f) + n[4] * f
                wid = wid * (1 - f) + n[5] * f
            return amp, freq, jit, wid, k
    return STAGES[-1][2], STAGES[-1][3], STAGES[-1][4], STAGES[-1][5], len(STAGES) - 1

# ── 軌跡（中心線・幅・色index）を計算 ─────────────────────────────
def build_track():
    pts = []          # (cx, cy ignored) we return offset+width per sample in param space
    phase = 0.0
    dt = 1.0 / SAMPLES
    prev_freq = 0.0
    rows = []
    for i in range(SAMPLES + 1):
        t = i / SAMPLES
        amp, freq, jit, wid, k = stage_at(t)
        # 位相を積分 → 周波数が変わっても連続
        phase += ((prev_freq + freq) * 0.5) * dt
        prev_freq = freq
        # 法線方向の変位 = 遊泳の波 + 乱流
        swim = math.sin(phase * 2 * math.pi)
        turb = fbm(t * 90.0, seed=3) * jit
        offset = swim * amp + turb
        rows.append((t, offset, wid, k, amp, freq, jit))
    return rows

# ── SVG リボン出力（可変幅 = 中心線を法線に±wid/2でオフセット） ─────
def emit_svg(rows, mode, W, H, fname,
             cx=None, cy=None, R=None, a0=None, a1=None,
             baseline=None, margin=60):
    def guide(t):
        """ガイド上の点と法線(単位)。"""
        if mode == "linear":
            x = margin + t * (W - 2 * margin)
            y = baseline
            nx, ny = 0.0, 1.0  # 法線は縦
            return x, y, nx, ny
        else:  # radial: 弧 a0→a1, 半径R
            a = a0 + (a1 - a0) * t
            x = cx + R * math.cos(a)
            y = cy + R * math.sin(a)
            nx, ny = math.cos(a), math.sin(a)  # 半径方向=外向き法線
            return x, y, nx, ny

    # ステージごとにパスを分け、各ステージ色で塗る
    segs = {}
    for (t, off, wid, k, *_ ) in rows:
        gx, gy, nx, ny = guide(t)
        cxp = gx + nx * off
        cyp = gy + ny * off
        L = (cxp + nx * wid / 2, cyp + ny * wid / 2)
        Rt = (cxp - nx * wid / 2, cyp - ny * wid / 2)
        segs.setdefault(k, {"L": [], "R": []})
        segs[k]["L"].append(L)
        segs[k]["R"].append(Rt)

    parts = []
    for k in sorted(segs):
        Lpts = segs[k]["L"]
        Rpts = segs[k]["R"][::-1]
        d = "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in Lpts)
        d += " L " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in Rpts) + " Z"
        col = STAGES[k][6]
        parts.append(f'<path d="{d}" fill="{col}" opacity="0.95"/>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="{W}" height="{H}" fill="#ffffff"/>
{chr(10).join(parts)}
</svg>'''
    with open(os.path.join(OUT, fname), "w") as f:
        f.write(svg)
    return segs

# ── PILプレビュー（同じ点列を塗る） ──────────────────────────────
def emit_png(segs, W, H, fname):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return
    im = Image.new("RGB", (W, H), "white")
    dr = ImageDraw.Draw(im, "RGBA")
    for k in sorted(segs):
        poly = segs[k]["L"] + segs[k]["R"][::-1]
        col = STAGES[k][6].lstrip("#")
        rgb = tuple(int(col[i:i+2], 16) for i in (0, 2, 4)) + (242,)
        dr.polygon(poly, fill=rgb)
    im.save(os.path.join(OUT, fname))

if __name__ == "__main__":
    rows = build_track()

    # B案: 横展開（水温ラインの下に置く想定）
    W, H = 1400, 360
    segs = emit_svg(rows, "linear", W, H, "swim_trace_linear.svg", baseline=H/2)
    emit_png(segs, W, H, "swim_trace_linear.png")

    # A案: 同心円の弧をガイドに（鱗 focus≈(706,795) を中心に下半周）
    W, H = 1400, 1400
    cx, cy, R = 700, 700, 560
    segs = emit_svg(rows, "radial", W, H, "swim_trace_radial.svg",
                    cx=cx, cy=cy, R=R, a0=math.radians(170), a1=math.radians(370))
    emit_png(segs, W, H, "swim_trace_radial.png")

    print("done ->", OUT)
    for s in STAGES:
        print(f"  {s[0]:14s} dur={s[1]:.2f} amp={s[2]:4.0f} freq={s[3]:4.0f} jit={s[4]:3.0f} w={s[5]}")
