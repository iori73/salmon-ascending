---
id: ai-2026-06-05-isotope-migration
type: ai-conversation
title: アイソトープ（同位体）によるサケ回遊ルート推定の理解
url: null
author: i_kawano
publisher: Google
license: 参照のみ
license_use: 参照のみ
access_date: 2026-06-05
origin:
  - file:references/ai-conversations/アイソトープ（同位体）とは何か - Google Gemini 20260605.html
model: Google Gemini
share_url: null
local_path: "references/ai-conversations/アイソトープ（同位体）とは何か - Google Gemini 20260605.html"
tags: [salmon, migration, isotope, nitrogen, isoscape, methodology]
status: active
verified: false
---

**prompt_summary:** アイソトープ（同位体）とは何かをGeminiに解説させ、さらに原著論文の図キャプション（Fig.2 椎骨の回顧的同位体比／Fig.3 北太平洋のδ¹⁵N Isoscape／Fig.4 状態空間モデルによる個体回遊推定）を貼って、サケ回遊ルート解明の手法を理解した。

**key_takeaways:**
- **アイソトープ＝同位体**（中性子数が違う＝重さが違う仲間）。構成比の違いが「動かぬ手がかり」になる。
- **椎骨は成長の年輪**：中心＝幼魚期、縁＝成熟期のδ¹⁵Nが記録される（断面を内→外へ分析＝回顧的分析。基礎手法は Koch et al. 1992）。
- **Isoscape**：海域ごとにδ¹⁵N比のパターンがある。北太平洋でカイアシ類のアミノ酸の化合物別同位体分析からδ¹⁵N地図を作成。
- **ベーリング海陸棚がδ¹⁵N最高**：高生産域で食物連鎖が長く複雑なため、栄養段階を上がるごとにδ¹⁵Nが段階的に濃縮（→「地図上のランドマーク」になる）。
- **手法3段階**：①Isoscape作成 → ②帰国した成熟シロザケ（日本の3河川）椎骨の回顧的δ¹⁵N分析 → ③状態空間モデルで照合し個体ごとの回遊ルートを推定。発信機なしで体内の自然データから数千kmの旅路を再現。

**プロジェクトへの含意:**
- Board A 回遊ジャーニーマップの**ルート（ベーリング海など）の科学的裏付け**になる。[[img-pacific-basemap]] のベーリング海・北太平洋ラベルと整合。
- δ¹⁵Nの栄養段階濃縮は、生活史データの**「栄養段階3.7」**（[[salmon-lifestage-variables]]）の根拠と整合。

**裏取り（必須・TODO）:** 本会話の元になった**原著論文（Fig.2–4 の出典、Koch et al. 1992 を基礎とする近年のサケ回遊 isoscape 研究／日本の3河川の成熟シロザケ・状態空間モデル）を特定して `src-` エントリ化**すること。現状は一次ソース未登録のため `verified: false`。Gemini の説明は概念整理にとどめ、数値・固有名詞は原著で照合する。

**アーカイブ:** 保存HTML（同階層）。`_files` フォルダには Google の gtm.js／cookie 等のトラッキング資産が含まれるため、整理時に本文に不要なものは削除可。
