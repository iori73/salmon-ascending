# フォント運用メモ

本サイトは **源ノ明朝（Source Han Serif JP ＝ Noto Serif JP, SIL OFL）** と **EB Garamond** を
セルフホストしている。Google Fonts への外部依存はない。

## 仕組み

`npm run fonts`（= `node scripts/generate-fonts.mjs`）が、

1. `app/**` と `components/**` に登場する文字を収集（＋全かな・約物・ASCII の安全セット）
2. その文字集合だけを含む woff2 を Google Fonts の `text=` サブセット API から取得
3. `public/fonts/*.woff2` に保存（各ウェイト数十KB）
4. `app/fonts.css`（@font-face、自動生成）を書き出す

`app/fonts.css` は `app/layout.tsx` で読み込まれる。**手で編集しない。**

## ⚠️ 重要

**本文（page.tsx 等）を編集して新しい漢字を増やしたら、必ず `npm run fonts` を再実行する。**
サブセットに無い字は豆腐（□）になる。かな・約物・ASCII は安全セットに含むため、
通常は新出漢字を追加したときだけ再生成すればよい。

ウェイトは Light(300) / Regular(400) / SemiBold(600) の3種。
