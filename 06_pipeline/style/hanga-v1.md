---
title: スタイル定義 — hanga-v1 (版画/リノカット風フラットイラスト)
status: v1
subject_agnostic: true
date: 2026-07-29
---

# style: hanga-v1

対象(spec.yaml)とは独立したスタイル記述。`sketch-v1`と並ぶ第2スタイル。生成のたびに**不変のまま**プロンプトに付加する。
スタイルを変更したい場合はこのファイルと`anchor-hanga-v1.png`だけを差し替え、`spec.yaml`側は一切変更しない。

## 参照

ユーザー提供のPinterest参考画像(鯖のイラスト、"Modern fish illustration")。リノカット/版画(hanga)・色分解(color-separation)印刷の質感。**黒い輪郭線(キーライン)は一切無く**、色面同士が直接隣り合う紙切り絵(paper cut-out)のような構成。鱗や模様を有機的な質感ではなく幾何学的な反復パターン(ダイヤ形・シェブロン)として様式化する。Charley Harperの野生動物イラストに近い、大胆で装飾的なミニマリズム。

## プロンプト用記述(英語、生成APIにそのまま渡す)

```
Style: bold flat-color print/poster illustration in the style of a color-separation print or paper
cut-out — NOT a sketchy hand-drawn look, NOT photorealistic, NOT soft or painterly. CRITICAL: there is
NO outline, NO keyline, NO stroke of any kind around any shape — every form is built purely from flat
colored shapes abutting each other directly, the way separate layers of colored paper would be cut and
overlaid, or the way a color-separation print registers one flat color plate against another. Edges are
defined only by where one flat color meets another, never by a drawn line. Flat, saturated, limited
color fills only — absolutely no gradients, no shading, no highlights, no texture noise. Scale patterns,
stripes, and body markings should be stylized into clean repeating geometric shapes (diamonds, chevrons,
dot rows) as separate flat color shapes, rather than organic/naturalistic texture — think mid-century
modern wildlife illustration (e.g. Charley Harper) crossed with a Japanese woodblock print. High contrast
between a small number of flat colors (3-5 max) plus a cream or muted off-white background.

ABSOLUTE HARD RULE, repeated because prior generations keep violating it: do not draw a dark outline,
keyline, or stroke around the body, fins, gill line, mouth, or any internal color boundary anywhere in the
image. Every single edge in the entire image — body-to-background, body-to-fin, color-region-to-color-region
— must be formed ONLY by two flat colors meeting directly, exactly like two pieces of cut paper placed
edge-to-edge with no line drawn between them. If you find yourself about to render a thin dark line tracing
any shape's boundary, stop and remove it — that line is the single most common failure mode for this style.
```

## 禁止事項(ネガティブ制約、スタイル面)

- **黒い輪郭線・キーライン・ストローク(最重要禁止事項— 色面のみで形を作ること)**
- ラフな手描き線・鉛筆やマーカーのムラ(これは`sketch-v1`の特徴であり、hanga-v1では禁止)
- グラデーション・光沢・写実的な陰影
- 有機的でランダムな質感(点描・にじみ・水彩ムラ)

## style checklist(critique.pyがbiologyチェックリストと独立に判定する項目)

- claim: "黒い輪郭線(キーライン)が一切なく、色面同士が直接接する紙切り絵/色分解印刷のような構成になっている"
  severity: required
- claim: "グラデーションのないフラットな限定色塗りで構成されている"
  severity: required
- claim: "鱗や模様が有機的な質感ではなく、幾何学的な反復パターンとして様式化されている"
  severity: advisory

## anchor-hanga-v1.png

初回生成で採用されたスタイル出力を`06_pipeline/style/anchor-hanga-v1.png`としてロックし、以降このスタイルでの全生成でconditioning画像として使い回す。現時点では未生成。
