# references — 参照ソース＆画像データベース

このプロジェクト（和食人類学・サーモン編）で**参考にしたサイト・画像・データ・AI会話**を一元管理する、単一の真実の源（SSOT）。

- **形式**：1エントリ＝1 Markdownファイル（YAMLフロントマター）。
- **DBとして使う**：このフォルダ `references/` を **Obsidian の vault** として開き、**Dataview** プラグインを入れると、フロントマターを横断クエリして表・フィルタができる（[INDEX.md](INDEX.md) にクエリ同梱）。未導入でも INDEX.md の静的表で読める。
- **git管理**：プレーンテキストなので差分が追える。`.obsidian/` は `.gitignore` 済み。

## フォルダ

| フォルダ | 入れるもの | id接頭辞 |
|---|---|---|
| `sources/` | web出典・公的統計・データセット・論文・書籍 | `src-` |
| `images/` | 採用画像（CC0/PD/CC-BY…）＋ Figma image hash | `img-` |
| `reference-only/` | 着想の参照（転用不可・出典明記のみ） | `ref-` |
| `ai-conversations/` | AI会話の参照（Google AI Mode / ChatGPT / Claude 等） | `ai-` |

フィールド定義は [SCHEMA.md](SCHEMA.md) を参照。

## 更新のしかた（Claudeに依頼）

新しい素材を見つけたら、そのURL/画像/会話をClaudeに渡して：

> 「この〔URL/画像/AI会話〕を references に追加して」

Claudeが type を判定し、SCHEMA準拠のノートを生成 → INDEX.md に追記 → 関連エントリへ `[[link]]` を張ります。判断に迷う項目（ライセンス不明等）は `要確認` フラグで残します。

## 運用ルール

- **重複は1エントリに統合**。同じソースを複数箇所で使ったら、新規ノートを作らず `origin:` に Figma node / file パスを足す。
- **権利TODO**：`license_use: 要確認` と `CC BY-SA`（share-alike 波及注意）は定期的に棚卸し（INDEX.md のクエリで抽出）。
- **AI会話は既定 `verified: false`**。本文に裏取りした一次ソースへの `[[link]]` を必ず張る（AI出力単独は低信頼）。

## Obsidian導入メモ

1. Obsidian で「フォルダを vault として開く」→ この `references/` を選択。
2. 設定 → コミュニティプラグイン → **Dataview** を有効化。
3. INDEX.md を開くと type別の表・権利TODOが描画される。
