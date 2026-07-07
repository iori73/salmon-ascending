#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_lali.py — 反応拡散の「仕組み」を非理系向けに説明する3コマ模式図(SVG)を生成。
局所活性化・長距離抑制(LALI)＝なぜ模様が等間隔に並ぶか。ブランド配色・明朝。
出力: lali-diagram.svg
"""
import math
import os

_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "diagrams")
os.makedirs(_OUT, exist_ok=True)

# ---- ブランド ----
PAPER = "#FAFAF6"; INK = "#2A2A24"; SUB = "#6E6A5E"; LINE = "#E0DDD2"
BLUE = "#2E6E8E"   # 抑制因子 inhibitor
EARTH = "#C4722A"  # 活性化因子 activator
MINCHO = '"Hiragino Mincho ProN","Yu Mincho",serif'
GOTHIC = '"Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif'

W, H = 1060, 470


def gauss(x, mu, sig, amp):
    return amp * math.exp(-((x - mu) ** 2) / (2 * sig * sig))


def curve(pts):
    return "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def panel(ox, title, num):
    s = []
    s.append(f'<text x="{ox}" y="84" font-family=\'{MINCHO}\' font-size="16" fill="{INK}" font-weight="600">'
             f'<tspan fill="{BLUE}">{num}</tspan>  {title}</text>')
    return s


def main():
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family=\'{GOTHIC}\'>')
    out.append(f'<rect width="{W}" height="{H}" fill="{PAPER}"/>')
    # markers
    out.append(f'''<defs>
      <marker id="arE" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto">
        <path d="M0,0 L7,3.2 L0,6.4 Z" fill="{EARTH}"/></marker>
      <marker id="arB" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto">
        <path d="M0,0 L7,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>
      <marker id="arK" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto">
        <path d="M0,0 L7,3.2 L0,6.4 Z" fill="{SUB}"/></marker>
    </defs>''')

    # ---- header ----
    out.append(f'<text x="40" y="44" font-family=\'{MINCHO}\' font-size="23" fill="{INK}" font-weight="600">模様ができる仕組み</text>')
    out.append(f'<text x="40" y="66" font-family=\'{GOTHIC}\' font-size="13" fill="{SUB}">'
               f'局所活性化・長距離抑制（LALI）— なぜ模様は“等間隔”に並ぶのか</text>')
    out.append(f'<rect x="40" y="74" width="60" height="2" fill="{BLUE}"/>')

    base = 300          # 曲線のベースライン
    p1, p2, p3 = 60, 410, 760   # 各パネル左端
    pw = 270

    # ===== パネル1: 二つの物質 =====
    out += panel(p1, "二つの、見えない物質", "①")
    # activator chip + desc
    out.append(f'<circle cx="{p1+14}" cy="150" r="9" fill="{EARTH}"/>')
    out.append(f'<text x="{p1+32}" y="148" font-size="13.5" fill="{INK}" font-weight="600">活性化因子</text>')
    out.append(f'<text x="{p1+32}" y="167" font-size="12" fill="{SUB}">「ここに色をつくれ」</text>')
    out.append(f'<text x="{p1+32}" y="184" font-size="12" fill="{SUB}">自分自身も増やす／<tspan fill="{EARTH}">ゆっくり</tspan>広がる</text>')
    out.append(f'<circle cx="{p1+14}" cy="226" r="9" fill="{BLUE}"/>')
    out.append(f'<text x="{p1+32}" y="224" font-size="13.5" fill="{INK}" font-weight="600">抑制因子</text>')
    out.append(f'<text x="{p1+32}" y="243" font-size="12" fill="{SUB}">「すぐ近くではつくるな」</text>')
    out.append(f'<text x="{p1+32}" y="260" font-size="12" fill="{SUB}">活性化に作られ／<tspan fill="{BLUE}">速く・遠く</tspan>広がる</text>')
    # self-activation loop + inhibition arrow
    out.append(f'<path d="M {p1+150} 300 q 30 -34 60 0" fill="none" stroke="{EARTH}" stroke-width="2" marker-end="url(#arE)"/>')
    out.append(f'<text x="{p1+150}" y="252" font-size="12" fill="{EARTH}">＋ 自己増殖</text>')
    out.append(f'<text x="{p1+8}" y="300" font-size="12" fill="{SUB}">この二つの「速さの差」が、すべてを決めます。</text>')

    # ===== パネル2: せめぎ合い(1つの山) =====
    out += panel(p2, "せめぎ合い（一つの山）", "②")
    ax0, ax1 = p2, p2 + pw
    out.append(f'<line x1="{ax0}" y1="{base}" x2="{ax1}" y2="{base}" stroke="{LINE}" stroke-width="1.5"/>')
    out.append(f'<text x="{ax1-4}" y="{base+18}" font-size="11" fill="{SUB}" text-anchor="end">体の表面（位置）→</text>')
    mu = p2 + pw / 2
    # inhibitor broad dome (under), activator sharp peak (over)
    inh = [(x, base - gauss(x, mu, 64, 70)) for x in range(ax0, ax1 + 1, 4)]
    act = [(x, base - gauss(x, mu, 20, 116)) for x in range(ax0, ax1 + 1, 3)]
    out.append(f'<path d="{curve(inh)}" fill="none" stroke="{BLUE}" stroke-width="2.4"/>')
    out.append(f'<path d="{curve(act)}" fill="none" stroke="{EARTH}" stroke-width="2.4"/>')
    out.append(f'<text x="{mu+6}" y="{base-120}" font-size="12" fill="{EARTH}" font-weight="600">活性化（鋭い山）</text>')
    out.append(f'<text x="{mu+78}" y="{base-44}" font-size="12" fill="{BLUE}" font-weight="600">抑制（広いすそ野）</text>')
    # inhibition reach arrows to both sides
    out.append(f'<line x1="{mu}" y1="{base-150}" x2="{mu}" y2="{base-128}" stroke="{SUB}" stroke-width="1"/>')
    out.append(f'<line x1="{ax0+34}" y1="{base-150}" x2="{mu-30}" y2="{base-150}" stroke="{BLUE}" stroke-width="1.4" marker-start="url(#arB)" stroke-dasharray="4 3"/>')
    out.append(f'<line x1="{ax1-34}" y1="{base-150}" x2="{mu+30}" y2="{base-150}" stroke="{BLUE}" stroke-width="1.4" marker-start="url(#arB)" stroke-dasharray="4 3"/>')
    out.append(f'<text x="{mu}" y="{base-156}" font-size="11" fill="{BLUE}" text-anchor="middle">－ 隣をおさえる（遠くまで）</text>')
    out.append(f'<text x="{ax0}" y="{base+40}" font-size="12" fill="{SUB}">山のまわりは「つくるな」の圏内。だから隣には、</text>')
    out.append(f'<text x="{ax0}" y="{base+58}" font-size="12" fill="{SUB}">少し離れないと次の山ができない。</text>')

    # ===== パネル3: 周期模様 =====
    out += panel(p3, "だから“等間隔”に並ぶ", "③")
    ax0, ax1 = p3, p3 + pw
    out.append(f'<line x1="{ax0}" y1="{base}" x2="{ax1}" y2="{base}" stroke="{LINE}" stroke-width="1.5"/>')
    period = 62
    peaks = [ax0 + 24 + i * period for i in range(4)]
    series = []
    for x in range(ax0, ax1 + 1, 2):
        y = base - sum(gauss(x, m, 15, 96) for m in peaks)
        series.append((x, y))
    out.append(f'<path d="{curve(series)}" fill="none" stroke="{EARTH}" stroke-width="2.4"/>')
    # spacing bracket between first two peaks
    bx0, bx1, by = peaks[0], peaks[1], base - 118
    out.append(f'<line x1="{bx0}" y1="{by}" x2="{bx1}" y2="{by}" stroke="{SUB}" stroke-width="1" marker-start="url(#arK)" marker-end="url(#arK)"/>')
    out.append(f'<text x="{(bx0+bx1)/2}" y="{by-7}" font-size="12" fill="{INK}" text-anchor="middle">間隔 ＝ 波長 λ</text>')
    # map to vertical bars (parr) strip
    sy = base + 18
    out.append(f'<rect x="{ax0}" y="{sy}" width="{pw}" height="40" rx="4" fill="#AEB2A6"/>')
    for m in peaks:
        out.append(f'<rect x="{m-8}" y="{sy}" width="16" height="40" rx="3" fill="#39433C"/>')
    out.append(f'<text x="{ax0}" y="{sy+58}" font-size="12" fill="{SUB}">＝ シロザケ稚魚の縦バー（パーマーク）。</text>')
    out.append(f'<text x="{ax0}" y="{sy+76}" font-size="12" fill="{SUB}">波長が間隔を、拡散の偏りが“縦向き”を決める。</text>')

    # ---- footnote ----
    out.append(f'<text x="40" y="{H-14}" font-family=\'{GOTHIC}\' font-size="11" fill="{SUB}">'
               f'Turing 1952／Gierer &amp; Meinhardt 1972／Kondo &amp; Asai 1995（Nature 376:765）／Kondo &amp; Miura 2010（Science 329:1616）に基づく概念図。'
               f'「サーモンは遡上する」川野いおり 2026。</text>')

    out.append('</svg>')
    p = os.path.join(_OUT, "lali-diagram.svg")
    open(p, "w").write("\n".join(out))
    print("saved", p)


if __name__ == "__main__":
    main()
