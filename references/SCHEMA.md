# SCHEMA — フロントマター定義

各エントリは下記フロントマター＋本文で構成する。`*` は必須。

```yaml
---
id: src-01-fra                 # * 一意。接頭辞 src-/img-/ref-/ai-
type: web-source               # * enum 下記
title: 水産研究・教育機構 FRA    # *
url: https://salmon.fra.affrc.go.jp/   # 一次URL（画像は元ファイルURL）
author: 水産研究・教育機構（FRA）
publisher: FRA
license: 公的統計               # * enum 下記
license_use: 参照のみ           # * 転用可 | 参照のみ | 要確認
reliability: 5                 # ★1–5（リサーチ二軸評価を継承。任意）
coverage: 4                    # ★1–5（任意）
access_date: 2026-06-05        # 取得/確認日
origin:                        # * プロジェクト内で使った場所（複数可）
  - figma:4393:1221
  - file:02_research/life-stage-variables.md
local_path: null               # 画像のみ：リポ内パス（揮発tmpは記載しない）
figma_image_hash: null         # 画像のみ：Figma再利用hash
dimensions: null               # 画像のみ：例 760x520
credit: null                   # 画像のみ：©表記の原文
model: null                    # ai-conversationのみ：Google AI Mode / ChatGPT / Claude…
share_url: null                # ai-conversationのみ：共有リンク（あれば）
tags: [salmon, ecology]        # 自由タグ
status: active                 # active | archived | superseded
verified: true                 # 事実照合済みか（ai-conversationは既定 false）
---

要約 / 代表事実（1–3行）。
**転用条件:** CC/PD/参照のみ・改変表明（recolored/cropped）の要否。
関連: [[src-03-hro]] [[img-keta-vector]]
```

## enum

**type**
| 値 | 意味 |
|---|---|
| `web-source` | 公式サイト・記事・解説ページ |
| `dataset` | 統計・データファイル（e-Stat, FRA xlsx 等） |
| `paper` | 論文・学術記事（J-STAGE, CiNii, PubMed） |
| `book` | 書籍 |
| `image` | 採用画像・図版素材 |
| `reference-only` | 着想の参照（転用不可） |
| `ai-conversation` | AIとの会話（要検証） |

**license**：`CC0` / `PD`（Public Domain）/ `CC BY 2.0` / `CC BY 4.0` / `CC BY-SA 2.1 jp` / `CC BY-SA 3.0` / `CC BY-SA 4.0` / `SIL OFL`（フォント）/ `公的統計` / `参照のみ` / `不明`

**license_use**
| 値 | 意味 |
|---|---|
| `転用可` | 出典明記で図版に転用できる（CC0/PD/CC-BY/CC-BY-SA） |
| `参照のみ` | 著作権物。着想の参照に留め、図版に転用しない |
| `要確認` | ライセンス未確定。使用前に要調査 |

## 記入規約

- **CC BY-SA**（share-alike）は本文に必ず注意を書く：「再着色・合成した派生図は同一 CC BY-SA で提供する義務を負い得る。SA素材は隔離 or 全体SA表記 or 差替で対応」。
- **改変**した素材（再着色・トリミング・単色化）は `credit` か本文に `recolored` / `cropped` を明示（CC BY/BY-SA の要件）。
- **重複統合**：同一ソースは1ノート。複数箇所で使用したら `origin:` を増やす。
- **id命名**：`src-NN-keyword`（番号付き）／ `img-keyword` ／ `ref-keyword` ／ `ai-YYYY-MM-DD-topic`。
