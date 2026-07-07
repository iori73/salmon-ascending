# INDEX — 全エントリ索引

> このフォルダを Obsidian で開き Dataview を有効化すると、下記クエリが表として描画される。未導入時は各セクションの静的表で読む（件数は末尾サマリ参照）。

## web出典・データ・論文（sources/）

```dataview
TABLE license, license_use, reliability AS "信頼", coverage AS "網羅", url
FROM "references/sources"
SORT reliability DESC
```

## 画像素材（images/）

```dataview
TABLE license, license_use, dimensions, figma_image_hash
FROM "references/images"
SORT license_use ASC
```

## 着想の参照（reference-only/）

```dataview
TABLE author, url
FROM "references/reference-only"
```

## AI会話（ai-conversations/）

```dataview
TABLE model, verified, access_date
FROM "references/ai-conversations"
WHERE type = "ai-conversation"
SORT access_date DESC
```

## 権利TODO（要確認・share-alike）

```dataview
TABLE type, license, license_use
FROM "references"
WHERE license_use = "要確認" OR contains(license, "SA")
SORT license_use ASC
```

---

## 静的索引（Dataview非導入時）

> 初期移行（2026-06-05）。新規追加時はこの表にも1行足す。

### sources/（web出典・データ・論文）32件

| id | title | license | 転用 | ★信頼 |
|---|---|---|---|---|
| src-01-fra | 水産研究・教育機構 FRA（さけ・ます情報） | 公的統計 | 転用可 | 5★ |
| src-02-hokkaido-akisake | 北海道庁 水産林務部 秋さけ漁獲速報 | 公的統計 | 転用可 | 5★ |
| src-03-hro | 道総研 さけます・内水面水産試験場 | 公的統計 | 参照のみ | 4★ |
| src-04-spf-ocean477 | 笹川平和財団 Ocean Newsletter（第477号） | 不明 | 参照のみ | 3★ |
| src-05-hokudai-arc | 北海道大学 北極域研究センター | 不明 | 参照のみ | 4★ |
| src-06-jfa-furyou | 水産庁 不漁問題に関する検討会 | 公的統計 | 参照のみ | 4★ |
| src-07-estat | e-Stat 海面漁業生産統計調査 | 公的統計 | 転用可 | 5★ |
| src-08-chitose-capture | サケのふるさと千歳水族館 捕獲情報 | 公的統計 | 転用可 | 3★ |
| src-09-cinii | CiNii 北海道区水産研究所研究報告 | 不明 | 参照のみ | 3★ |
| src-10-jstage | J-STAGE（サケの感覚機能と母川回帰 ほか） | 不明 | 参照のみ | 5★ |
| src-11-maff-hokkaido-graph | 北海道農政事務所 グラフでみる北海道の漁業 | 公的統計 | 参照のみ | 4★ |
| src-12-spf-opri | 笹川平和財団 海洋政策研究所 刊行物 | 不明 | 参照のみ | 3★ |
| src-13-hokkaido-isan | 北海道遺産「サケの文化」 | 不明 | 参照のみ | 5★ |
| src-14-ishikari-museum | 石狩市／石狩市博物館 サケ漁の歴史 | 不明 | 参照のみ | 4★ |
| src-15-upopoy | ウポポイ 国立アイヌ民族博物館 | 不明 | 参照のみ | 5★ |
| src-16-chitose-ainu | 千歳水族館 アイヌ文化展示 | 不明 | 参照のみ | 3★ |
| src-17-ishikari-nabe | 農林水産省 うちの郷土料理「石狩鍋」 | 不明 | 参照のみ | 3★ |
| src-18-ruibe | 農林水産省 うちの郷土料理「ルイベ」 | 不明 | 参照のみ | 3★ |
| src-19-hokkaido-np | 北海道新聞（秋サケ不漁報道） | 不明 | 参照のみ | 4★ |
| src-20-ff-ainu | アイヌ民族文化財団 学習資料 | 不明 | 参照のみ | 5★ |
| src-21-marek | 文化遺産オンライン「マレク」 | 不明 | 参照のみ | 3★ |
| src-22-asirichep | 札幌市「アシリチェプノミ」 | 不明 | 参照のみ | 3★ |
| src-23-nikkei | 日本経済新聞「雪が育む“神の魚”」 | 不明 | 参照のみ | 4★ |
| src-24-hm-hokkaido | 北海道博物館「アイヌ文化の世界」 | 不明 | 参照のみ | 5★ |
| src-25-salmon-info6 | 永沢2012「サケ科魚類のプロファイル-10 サケ」SALMON情報 No.6（回遊経路の一次資料・図4＝浦和2000） | 公的統計 | 転用可 | 5★ |
| src-fishbase | FishBase — Oncorhynchus keta | 不明 | 参照のみ | 4★ |
| src-fra-river-data | FRA さけます類の河川別データ（河川別捕獲数） | 公的統計 | 転用可 | 5★ |
| src-gunma-fisheries | 群馬県水産試験場 | 公的統計 | 参照のみ | 3★ |
| src-iwate-fisheries | 岩手県水産技術センター | 公的統計 | 参照のみ | 4★ |
| src-nichibenren-2022 | 日本弁護士連合会 2022年決議（先住民族・アイヌ） | 不明 | 参照のみ | 4★ |
| src-seafood-norway | Seafood Norway 対日輸出統計 | 不明 | 参照のみ | 4★ |
| src-tanaka-swimming | Tanaka et al. 遊泳速度・深度（実測） | 不明 | 参照のみ | 5★ |

### images/（採用画像）29件

| id | title | license | 転用 |
|---|---|---|---|
| img-keta-photo | シロザケ（Oncorhynchus keta） | CC0 | 転用可 |
| img-egg | シロザケの卵（受精卵）①卵 | **CC BY-SA 3.0** | 転用可※ |
| img-alevin-eggs | サケの卵と仔魚（ヨークサック期）②仔魚 | PD | 転用可 |
| img-alevin-newborn | 砂利上の仔魚（ヨークサック期）②仔魚 | **CC BY-SA 2.5** | 転用可※ |
| img-fry-fingerling | シロザケ稚魚（パーマーク）学術図 ③稚魚 | PD | 転用可 |
| img-smolt-oceanarium | 銀白色のシロザケ（銀化）④スモルト | **CC BY-SA 4.0** | 転用可※ |
| img-ocean-silver | 海洋期のシロザケ（銀白色）⑤海洋 | PD | 転用可 |
| img-spawning-breeding-color | シロザケの婚姻色（カリコ模様）⑥遡上 | **CC BY-SA 3.0** | 転用可※ |
| img-spawning-run | シロザケの遡上（群れ）⑥遡上 | PD | 転用可 |
| img-hocchare | ホッチャレ（産卵後・白化）⑦死 | **CC BY-SA 3.0** | 転用可※ |
| img-chum-breeding-illustration | シロザケ（婚姻色）標準学術図 | PD | 転用可 |
| img-thermometer | 温度計アイコン（未使用・archived） | CC0 | 転用可 |
| img-spawn-migration | シロザケの遡上・産卵回遊 | PD | 転用可 |
| img-fry-transfer | サケ稚魚の移送（ふ化放流） | PD | 転用可 |
| img-hokkaido-map | 北海道 市町村図 | PD | 転用可 |
| img-ainu-formal | 正装のアイヌの人々（19世紀） | PD | 転用可 |
| img-lifecycle-pacific-pd | Lifecycle of Pacific salmon（円環図） | PD | 転用可 |
| img-minard-1869 | Minard 1869：進軍と減耗 | PD | 転用可 |
| img-predator-silhouettes | 捕食者シルエット4種 | PD | 転用可 |
| img-chum-vector-dbcls | サケ図 — DBCLS | CC BY 4.0 | 転用可 |
| img-ishikari-nabe | 石狩鍋 | CC BY 2.0 | 転用可 |
| img-isotype-gastev | Isotype 反復ピクト作例 | CC BY 2.0 | 転用可 |
| img-sujiko-sor | 筋子（サケの卵） | CC BY 2.0 | 転用可 |
| img-waterwheel | インディアン水車（千歳川） | **CC BY-SA 3.0** | 転用可※ |
| img-pacific-basemap | 北太平洋 LAEA地図 | **CC BY-SA 3.0** | 転用可※ |
| img-sankey-cmglee | Sankey ダイアグラム作例 | **CC BY-SA 3.0** | 転用可※ |
| img-ikura-gunkan | イクラ軍艦巻き | **CC BY-SA 4.0** | 転用可※ |
| img-ruibe | ルイベ | **CC BY-SA 4.0** | 転用可※ |
| img-sacchep | サッチェプ（干し鮭） | **CC BY-SA 2.1 jp** | 転用可※ |

> ※ **CC BY-SA（share-alike）**：合成・改変した派生図は同一ライセンスでの提供義務を負い得る。各エントリの注記参照。

### reference-only/（着想の参照・転用不可）10件

| id | title |
|---|---|
| ref-nwf-migration | Salmon Migration — A journey that connects us all（NWF） |
| ref-noaa-westcoast | West Coast Salmon & Steelhead Management Map（NOAA） |
| ref-nasco-atlas | Wild Atlantic Salmon Atlas（NASCO） |
| ref-storytelling-with-data | Recapping "Radials"（Storytelling with Data） |
| ref-american-scientist | Circular Visualizations |
| ref-make-it-make-sense | Radial Timeline Template |
| ref-juice-analytics | Better Know a Visualization: Small Multiples |
| ref-the-pudding | The Pudding（視覚エッセイ実例集） |
| ref-tufte-flowingdata | Small Multiples 概念（Tufte / FlowingData） |
| ref-isotype-neurath | Isotype（O. Neurath の手法） |

### ai-conversations/ 2件

| id | title | model | verified |
|---|---|---|---|
| ai-2026-06-04-salmon-proto-review | プロトタイプ4案の辛口評価 → v2改善版のFigma制作 | Claude (Claude Code / Opus) | false |
| ai-2026-06-05-isotope-migration | アイソトープ（同位体）によるサケ回遊ルート推定の理解 | Google Gemini | false |

---

## 権利TODO（要対応）

- **✅ プロトタイプ画像URL確定（2026-06-05、Commons API照合）**：pacific-basemap / chum-vector-dbcls / lifecycle-pacific-pd / sujiko-sor / minard-1869 / isotype-gastev / sankey-cmglee の7点に実URL・著作者を投入済み。
- **⚠️ クレジット誤記の修正**：img-pacific-basemap は Figma 表記「© Tentotwo」が誤りで、正しくは **Uwe Dedering（CC BY-SA 3.0）**。Figma v1/v2 のクレジットも要修正。
- **URL残（4件・いずれもテキスト出典の公式URL）**：src-iwate-fisheries / src-gunma-fisheries / src-seafood-norway / src-nichibenren-2022。
- **img-thermometer は実体なしと判明**：Figmaに画像ノードが無く、脚注クレジットに「温度計 CC0」と記載されただけ（水温行は色帯で表現）。`status: archived` に変更。Figma脚注から当該クレジットを削除するのが筋。
- **img-predator-silhouettes 解決**：合成のため4部品URLを credit に記録（NIH BioArt #184/#164/#428＋Crow CC0）。
- **要最終確認**：img-sankey-cmglee は著作者・ライセンス一致だが Cmglee の複数 Sankey のうち採用ファイルの特定は余地あり。img-sujiko-sor は `Sujiko by sor.jpg`（別カット `Sujiko 2 by sor.jpg` も同 sor/CC BY 2.0）。
- **CC BY-SA share-alike（11画像）**：img-waterwheel / img-pacific-basemap / img-sankey-cmglee / img-ikura-gunkan / img-ruibe / img-sacchep / img-alevin-newborn / img-smolt-oceanarium / img-hocchare / **img-egg / img-spawning-breeding-color**。公開図に合成する場合は隔離 / 全体SA表記 / 差替のいずれかを決定。
- **生活史7ステージ画像（2026-06-06追加・計10点）**：`04_visual/lifecycle-stages/` に①卵→②仔魚→③稚魚→④スモルト→⑤海洋→⑥遡上/婚姻色→⑦ホッチャレ をDL（接頭辞1〜7＝段階順、ref-はKnepp参考図）。シロザケ特定写真が稀少な③稚魚パーマーク（学術図で代用）・④スモルト銀化（海洋期成魚で色のみ代用）・⑤海洋（釣獲個体・要トリミング）は要注意。Figma取込時は figma_image_hash を各ノートに追記。
- **画像hashは先頭8桁のみ**のものがある（プロトタイプ素材）。Figma fill から full hash を取得して `figma_image_hash:` を更新すると再利用が確実。

## サマリ（件数）

- sources: **32** ／ images: **29** ／ reference-only: **10** ／ ai-conversations: **2** ／ 合計 **73**（生活史7ステージ画像10点 追加 2026-06-06）

### 未登録の一次ソースTODO

- **サケ回遊 isoscape 原著論文**（[[ai-2026-06-05-isotope-migration]] の Fig.2–4 の出典／Koch et al. 1992 を基礎）を特定して `src-` 化する。
