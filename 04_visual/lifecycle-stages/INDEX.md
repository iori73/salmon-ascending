# シロザケ生活史 画像インデックス

7ステージモデル（`02_research/life-stage-descriptions.md`）と各画像ファイルの対応表。

> **命名メモ**: 既存ファイルの数字プレフィックス（1〜7）は「卵を1番」とする旧8段階分類に基づく。
> 7ステージモデル（仔魚=1）とは +1 ずれている。新規ファイルは `s{n}` プレフィックスで統一。

---

## Stage 1 — 仔魚（ヨークサック期）
| ファイル | 種別 | ライセンス | 備考 |
|---|---|---|---|
| `2-alevin_eggs-and-alevin_USFWS_PD.jpg` | 写真 | PD | 卵と仔魚・ヨークサック明瞭。**主要画像** |
| `2-alevin_salmon-newborn_OpenCage_CC-BY-SA-2.5.jpg` | 写真 | CC BY-SA 2.5 | 孵化直後の単体 |

## Stage 2 — 稚魚（パーマーク期）
| ファイル | 種別 | ライセンス | 備考 |
|---|---|---|---|
| `3-fry_chum-fingerling-illustration_Chamberlain_PD.jpeg` | イラスト | PD | "Dog Salmon Fingerling" 19c科学図・パーマーク明瞭。**主要画像** |
| `3-fry_chum-fry-transfer_USFWS_PD.png` | 写真 | PD | 孵化場での放流作業シーン（魚体小さく詳細不明） |

## Stage 3 — スモルト（銀化期）
| ファイル | 種別 | ライセンス | 備考 |
|---|---|---|---|
| `4-smolt_chum-silvery-oceanarium_Bukharov_CC-BY-SA-4.0.jpg` | 写真 | CC BY-SA 4.0 | 水族館で群れる銀化スモルト。**主要画像** |
| `s3b-smolt_chum-juvenile-ocean_VonBiela-USGS_PD.jpg` | 写真 | PD | 北極海・定量スケール付き。体長5〜7cmの海洋若魚 |

## Stage 4 — 海洋回遊期（外洋・索餌期）
| ファイル | 種別 | ライセンス | 備考 |
|---|---|---|---|
| `s4-ocean_chum-ocean-illustration_Hornady-NOAAFisheries_PD.png` | イラスト | PD | NOAA Fisheries / Jack Hornady。青緑背×銀白腹の外洋体色。**主要画像** |

## Stage 5 — 沿岸回帰期（銀毛・ギンケ）
| ファイル | 種別 | ライセンス | 備考 |
|---|---|---|---|
| `5-ocean_chum-bright-silver-caught_USFWS_PD.jpg` | 写真 | PD | 釣獲された銀白色成魚（Alaska）。**主要画像** |

## Stage 6 — 河川遡上期（婚姻色・ブナ）
| ファイル | 種別 | ライセンス | 備考 |
|---|---|---|---|
| `6-spawning_chum-male-breeding-color_Vineyard_CC-BY-SA-3.0.jpg` | 写真 | CC BY-SA 3.0 | 雌雄3個体比較・カリコ模様明瞭。**主要画像** |
| `6-spawning_chum-running-river_USForestService_PD.jpg` | 写真 | PD | 河川遡上シーン・群れ |
| `ref-chum-breeding-illustration_Knepp-USFWS_PD.jpg` | イラスト | PD | USFWS Knepp による詳細解剖学的イラスト（参照用） |

## Stage 7 — 産卵後期（ほっちゃれ）
| ファイル | 種別 | ライセンス | 備考 |
|---|---|---|---|
| `7-hocchare_spawned-out-dead-chum_Andshel_CC-BY-SA-3.0.jpg` | 写真 | CC BY-SA 3.0 | 産卵後・腐敗が進んだ姿。**主要画像** |

---

## 参照・補完ファイル（7ステージモデル外）
| ファイル | 内容 | ライセンス |
|---|---|---|
| `1-egg_chum-egg_Assianir_CC-BY-SA-3.0.jpg` | 卵（Stage 0）| CC BY-SA 3.0 |

---

## 鱗構造（全ステージ横断参照資料）
| ファイル | 内容 | ライセンス | 備考 |
|---|---|---|---|
| `scale_chum-kz0503f034-annotated_ADFG_PD.jpg` | 顕微鏡写真（ラベル付き元画像） | ADFG※ | 年齢読み取り標本 Kz0503F034。年齢ゾーン1-3・Focus・Globular reticulation ラベル入り |
| `scale_chum-kz0503f034-ring-lines_ADFG_PD.svg` | ベクター抽出線 v1（ラベルなし） | ADFG※ | sigma=1 Canny。アノテーション位置に白ギャップ・Annulus部が黒塊 |
| `scale_chum-kz0503f034-ring-lines_ADFG_PD.png` | v1 PNGプレビュー | ADFG※ | 白背景・黒線 |
| `scale_chum-kz0503f034-ring-lines-v2_ADFG_PD.svg` | **ベクター抽出線 v2（推奨）** | ADFG※ | sigma=3 Canny + NS inpainting(radius=20)。Annulusが弧線に改善・ギャップ補完済み。1374パス |
| `scale_chum-kz0503f034-ring-lines-v2_ADFG_PD.png` | v2 PNGプレビュー | ADFG※ | 白背景・黒線 |
| `scale_extraction_v2.py` | 抽出スクリプト v2 | — | 再実行・パラメータ調整用 |

※ADFG（Alaska Department of Fish and Game）は州機関のため著作権要確認。教育・研究目的利用想定。
出典: https://www.adfg.alaska.gov/static/fishing/images/research/chinookscaleage/f1_chum_kz0503f034_labelled.jpg

---

## メタデータ（references/images/）
各ファイルの詳細は `references/images/img-*.md` を参照。
- `img-alevin-eggs.md` → Stage 1
- `img-alevin-newborn.md` → Stage 1
- `img-fry-fingerling.md` → Stage 2
- `img-fry-transfer.md` → Stage 2
- `img-smolt-oceanarium.md` → Stage 3
- `img-juvenile-ocean-usgs.md` → Stage 3補完
- `img-ocean-illustration-noaa.md` → Stage 4（新規 2026-06-07）
- `img-ocean-silver.md` → Stage 5
- `img-spawning-breeding-color.md` → Stage 6
- `img-spawning-run.md` → Stage 6
- `img-chum-breeding-illustration.md` → Stage 6参照
- `img-hocchare.md` → Stage 7
