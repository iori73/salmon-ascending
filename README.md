# サーモンは遡上する / Salmon Ascending

一尾の魚——「サーモン」——をめぐる、三層の関係史を描くグラフィックエディトリアル。
消費・生態・文化を横断して、日本とサーモンの関係を辿る個人制作プロジェクト。

**🌐 公開サイト**: https://salmon-ascending.vercel.app/

A graphic editorial tracing the relationship between Japan and salmon across three
layers — consumption, ecology, and culture. A personal editorial/data-journalism project.

---

## 構成 / Structure

このリポジトリはプロジェクト全体のモノレポです。

| ディレクトリ | 内容 |
|---|---|
| `01_narrative/` | 物語構成・エディトリアル設計 |
| `02_research/` | リサーチノート（生活史・変数・固有名など。※論文PDF/スキャンは非収録） |
| `04_visual/` | 図版のソース（SVG・生成スクリプト。※重い生成ラスターは非収録） |
| `05_web/` | 公開サイト本体（Next.js 14 / App Router） |
| `article/` | note・Medium 用の記事下書き |
| `references/` | 参照ソースの一元DB（Markdown メモ） |
| `sns/` | SNS 投稿キャプション・書き出し画像 |

## サイトの開発・デプロイ / Web

サイトは `05_web/` にあります。

```bash
cd 05_web
npm install
npm run dev      # http://localhost:3000
```

- **Vercel デプロイ時は Root Directory = `05_web`**（モノレポのためリポジトリ直下ではない）
- フォントはセルフホスト（源ノ明朝 / EB Garamond）。詳細は [`05_web/README.md`](05_web/README.md) と [`05_web/FONTS.md`](05_web/FONTS.md)

## 注記 / Notes

- 本作は**個人の学習・作品制作**であり、査読論文ではありません。数値・図解は一次資料に基づく代表値です。
- 第三者著作物（論文PDF・スキャン・素材テクスチャ等）、巨大な生成画像、作業用ディレクトリは `.gitignore` で除外しています。

編集・図版：川野いおり / 2026
