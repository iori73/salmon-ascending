# 05_web — サーモンは遡上する / Salmon Ascending（Webサイト）

グラフィックエディトリアル「サーモンは遡上する」の公開サイト。
Next.js 14（App Router）＋ TypeScript ＋ Tailwind CSS。

**🌐 公開**: https://salmon-ascending.vercel.app/

## 開発 / Getting Started

```bash
npm install
npm run dev      # http://localhost:3000
```

- `npm run build` … 本番ビルド
- `npm run fonts` … フォントのサブセット再生成（下記）

## ページ構成

- `/` … トップ（5幕の目次）
- `/act/1`〜`/act/5` … 本編（第1〜5幕）
- `/about` … プロジェクトについて
- `/fieldwork` … フィールドワーク記録

図版は `components/` の自作 SVG コンポーネント群（河川断面・回遊マップ・遡上グラフ 等）。

## フォント（セルフホスト）

**源ノ明朝（Noto Serif JP, SIL OFL）＋ EB Garamond** をセルフホストし、Google Fonts への
外部依存はありません。`npm run fonts`（`scripts/generate-fonts.mjs`）が本文の使用文字だけを
集めて woff2 サブセットを生成し、`public/fonts/` と `app/fonts.css` を書き出します。
⚠️ 本文に新しい漢字を足したら `npm run fonts` を再実行（詳細は [`FONTS.md`](FONTS.md)）。

## デプロイ（Vercel）

このサイトはモノレポの `05_web/` 配下にあります。Vercel でインポートする際は
**Root Directory を `05_web` に設定**してください（リポジトリ直下ではビルドできません）。
Framework は Next.js が自動検出されます。
