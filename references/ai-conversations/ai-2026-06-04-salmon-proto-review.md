---
id: ai-2026-06-04-salmon-proto-review
type: ai-conversation
title: プロトタイプ4案の辛口評価 → v2改善版のFigma制作
url: null
author: i_kawano
publisher: null
license: 参照のみ
license_use: 参照のみ
access_date: 2026-06-04
origin:
  - figma:4565:1237
  - figma:4608:1236
  - file:04_visual/prototype-evaluation-prompt.md
model: Claude (Claude Code / Opus)
share_url: null
tags: [dataviz, prototype, review, figma, salmon]
status: active
verified: false
---

**prompt_summary:** シロザケ生活史ビジュアライゼーションのプロトタイプ4案（A回遊マップ/B放射状時計/C横断トラック/D漏斗）を6軸で辛口評価し、その指摘を反映した改善版 v2 を Figma に制作。

**key_takeaways:**
- A は経路線が無く「分布図」止まり → v2 で回遊ルート（方向付き破線ループ）を追加。
- B の英語PDカートゥーンが体系を破壊＋概念と乖離 → v2 で「弧長＝滞在期間」の自作リング（海洋期≈96%）に置換。
- D の漏斗が図として無い → v2 で減衰のテーパー帯＋実比1000:1の正直な注記を実装。
- C（横断トラック）が唯一エンコード実現済みで主図候補。ただし自社作図＝「収集のみ」制約を破る点が方法論の天井。
- **CC BY-SA の share-alike** が合成派生図に波及する権利リスクを脚注化（地図・Sankey）。

**裏取り（必須）:** 数値は [[salmon-lifestage-variables]]（FRA・[[src-tanaka-swimming]]・[[src-fishbase]] ほか）で照合済み。素材ライセンスは各 [[img-pacific-basemap]] 等のエントリ参照。**評価・推奨自体はAI判断**であり、最終決定は人間が行う。

**注意:** AI出力は単独では低信頼。本編採用前に一次ソースで再照合する。
