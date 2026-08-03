---
title: スタイル定義 — sketch-v1 (Giorgia Lupi風ラフ手描き)
status: v1
subject_agnostic: true
date: 2026-07-29
---

# style: sketch-v1

対象(spec.yaml)とは独立したスタイル記述。生成のたびに**不変のまま**プロンプトに付加する。
スタイルを変更したい場合はこのファイルと `anchor.png` だけを差し替え、`spec.yaml` 側は一切変更しない。

## 参照

Giorgia Lupiのデータビジュアライゼーション・スケッチ(Kazimir Malevich/Wassily Kandinsky引用のラフなマーカー+色鉛筆手描き、手書きラベル、幾何形状、点線矢印)。精密な水彩・写実レンダリングではなく、探究過程のメモのような軽さ。

## プロンプト用記述(英語、生成APIにそのまま渡す)

```
Style: loose hand-drawn sketch, as if drawn quickly with a marker and colored pencil during field research —
NOT a polished, photorealistic, or airbrushed illustration. Visible rough linework with some wobble and
inconsistent line weight. Color fills may slightly overshoot the linework, like real marker bleed.
Flat/matte coloring, no gradients, no glossy highlights, no drop shadows. Off-white or cream paper-like
background. If any label text appears, it should look handwritten, not a clean digital font.
Construction lines or a light underlying sketch may be faintly visible. The overall feeling is exploratory
and informal, like a research notebook page — not a finished print/poster illustration.
```

## 禁止事項(ネガティブ制約、スタイル面)

- 写真的レンダリング・厚塗り水彩・グロス感のある光沢
- 均一で機械的なベクター的塗り(境界が完全に滑らかすぎる)
- デジタルフォントのラベル(手書き風でないテキスト)

## style checklist(critique.pyがbiologyチェックリストと独立に判定する項目)

- claim: "線がラフな手描き(マーカー/色鉛筆)に見え、写実的なレンダリングになっていない"
  severity: required
- claim: "色の塗りが完全にフラットな均一ベクター調ではなく、多少のムラ・はみ出しがある"
  severity: advisory

## anchor.png

初回生成で採用されたスタイル出力を `06_pipeline/style/anchor.png` としてロックし、以降の全生成でconditioning画像として使い回す(スタイルの一貫性を担保)。現時点では未生成 — マイルストーン実行時に最初の1枚を採用して配置する。
