# 引き継ぎプロンプト — シロザケ反応拡散ビジュアル（トップビュー・ライブ化）

> 別セッションにこの本文をそのまま貼って続行する。メモリ（`MEMORY.md` 経由で自動読込、特に
> `rd_turing_salmon.md`）も併せて参照すること。

## このプロジェクトは何か
グラフィックエディトリアル「サーモンは遡上する / Salmon Ascending」（川野いおり, 2026）の一部。
シロザケ *Oncorhynchus keta* 7段階（①仔魚→②稚魚parr→③スモルト→④海洋→⑤沿岸→⑥遡上calico→⑦産卵後）の
体表模様を、**AI画像生成でなく反応拡散（Turing/近藤滋の枠組み）の数値計算**で生成・可視化する。
作業ディレクトリ: `04_visual/fish-pattern/`（スクリプトは `rd/` 同居、生成物は `out/<category>/`）。

## 絶対に守る原則（最重要）
1. **正直さ**：「計算で**生成**した」とは言うが「計算で**導出/予測**した」とは言わない。パラメータは
   実物参照画像へのfitting。λ_T検証は「指定波長の再現確認」で生物学的正しさの証明ではない。過剰主張禁止。
2. **cosine ≠ RD の区別**：模様が cosine 擬似縞（`0.5+0.5cos(2π·n·t)`）のものは「反応拡散で計算」と
   言ってはいけない。**本物RD**は GM/Gray–Scott を解いたもの＝ `rd/rd_salmon.py`・`rd/rd_swatch.py`・
   `rd/rd_stipple.py`・`fish_top_rd.py`・トップビューsimの真上パネル。
3. **作業前に実物を見る**：`04_visual/lifecycle-stages/` の本物写真を必ず確認してから配色/形を決める
   （過去に確認せず進めて何度も是正した）。仔魚は**ベージュでなく半透明銀＋オレンジ卵黄嚢**、
   ④海洋は**黒点なし**（種特徴）、⑥calicoは**黄緑地＋マゼンタ＋緑黒の高コントラスト虎縞**。
4. **段階で体型/姿勢が違う**：仔魚=直線(フラット)、幼魚=細い、海洋=太い紡錘、遡上=深い+カイプ、産卵後=痩せ+ボロひれ。

## 現在の到達点（完了済み）
- 側面RD：`rd/rd_salmon.py`(GM,λ_T較正,高解像)→`out/salmon/rd-salmon-montage.png`。`rd/rd_swatch.py`(GS swatch)。配色は `calibration.json`（実物基準に是正済、仔魚に `yolk` 追加）。
- 記事2本：`article/note-ja-rd-pattern.md` / `article/medium-en-rd-pattern.md`（鱗記事 `note-ja.md`等の姉妹編。正直さ・出典・限界明記済）。
- 非理系向け解説：`rd/rd-explainer.html`（ブランド化インタラクティブ）＋ `rd/make_lali.py`→`out/diagrams/lali-diagram.svg`（LALI模式図）。
- **トップビュー(背側)7段階・2スタイル**（`out/top/` 整理済）:
  - `cosine/soft/` `cosine/stipple/` … cosine擬似縞（**非RD**）
  - `rd/soft/` `rd/stipple/` … **本物RD**（`fish_top_rd.py`が`rd_salmon.simulate_stage`のGM活性場を体軸プロファイルに集約）
  - 各 `{1-alevin..7-postspawn}.png/.svg` + `montage`。生成: `fish_top_soft.py`(soft raster)/`make_top_svg.py`(soft vector svg)/`make_top_stipple.py`(点描)/`fish_top_rd.py`(本物RD両スタイル)。幾何=`fish_top.py`(真上,`build(...,wscale=)`)。
- **ライブ・トップビューsim**：`rd/viewers/rd_salmon_sim_topview.html`（現23KB自己完結。確認用ローカルサーバ: `python3 -m http.server 8731` → `http://localhost:8731/rd/viewers/rd_salmon_sim_topview.html`）。
  横向きライブRDシミュレータ `rd/viewers/rd_salmon_sim.html`（公開Artifact「ハイブリッド3層」の実体）に、
  **同じRD場Vから毎フレーム体軸プロファイルを作り真上softrdを描く**パネルを注入。模様の生成過程が真上でも
  立ち上がり、段階/速度/模様の強さ(amp)/異方性(aniso)/リセットに連動。動作確認済み。
- **calico 2色素連立（2026-06-22/23 完了）**：旧来calico/産卵後は単一GS場Vを位置(cs<0.75)で赤/緑黒に塗り分けるだけ＝2色素が独立していなかった。是正＝第2のGS場 Ub,Vb(erythrophore赤紫)を連立し活性化子の**相互消滅項 −χ·V·Vb**(χ=0.85)でV(melanophore緑黒)と空間排他→**緑黒バーと赤紫バーが位相をずらして交互の縦縞に創発**。`twoPig`フラグ(calico/産卵後のみ)で分岐、他段階は単一場のまま不変。垂直化に異方を 0.46:1.54→**0.26:1.74**へ強化。side/topview両方を2場独立着色、#eq数式も2場連立(−χ項)へ切替。バックアップ `rd_salmon_sim_topview.bak_pre2pig.html`。詳細はメモリ `rd_turing_salmon.md`。
- **段階別カラースウォッチ（2026-06-23）**：最新sim配色(2色素含む)を出典に7段階のカラーパレットを生成 → `out/swatches/salmon-stage-swatches.{png,svg}`(SVGは編集可・各色=rect)。⑥calicoは赤紫#8A3D56と緑黒#272C1Dを別色素として明示。**Figma未配置**(下記ブロッカー)。
- **⚠️Figma配置ブロッカー**：配置先 section「近藤先生のシミュレーション方式」(node `6574:245092`) はページ「anthropology-of-japanese-food」(`4216:13473`)上。**このページが巨大で use_figma の `setCurrentPageAsync`/`getNodeByIdAsync` がロード完了前にtransport切断**(scoped read=get_metadata(node)/get_screenshotは可、ページ単位write不可)。回避案: ①ユーザがデスクトップで当該ページを開いてから再試行 ②軽いページにネイティブ生成→手動移動 ③書き出しSVG/PNGを手動ドラッグ。

## 次にやる候補（未完・続きの起点）
1. **2色素タイルスウォッチの生成（未着手・依頼想定）**：「模様が四角の中」のタイルスウォッチ(`rd_swatch.py`→`rd/out/swatches/rd-swatches.png`＋`swatch-*.png`、Figma「RD模様スウォッチ」symbol `6643:244053`の元)は**全て2026-06-20生成＝2色素化より前**。calicoは旧単一場カラーマップのまま(交互虎縞でない)。ライブsimの2色素連立(−χ·V·Vb)を `rd_swatch.py` のcalico/産卵後に移植して2色素版タイルを再生成する必要あり。
2. **カラースウォッチのFigma配置**：上記ブロッカーの回避案で `salmon-stage-swatches` を section `6574:245092` へ。
3. **公開Artifactへの反映**：`rd_salmon_sim_topview.html` をユーザが再パブリッシュ（or 依頼あればArtifactツールで新リンク発行=公開操作なので要確認）。元artifact URL断片: claude.ai/code/artifact/415dd4e0-d322-4b14-824a-80792655…
4. **真上の正直度↑（任意）**：真上の縞は「側面RD場の体軸プロファイルを背側へ写したもの」＝位置/間隔は本物RDだが幅方向適用は様式化。必要なら**背側ジオメトリ上で2次元RDを直接解く**版に拡張。
5. **段階別シルエットの追い込み**：カイプ(真上では控えめ)、産卵後のひれ侵食、海洋の体幅 など。
6. 後片付け：リポジトリ直下に確認用スクショ（`topview-*.png` 等）が残存。`rm`が権限拒否されるので `mv` か手動削除。

## 環境・運用の注意（ハマりどころ）
- シェルはzsh：**`for x in $VAR` は単語分割されない**。ループはリテラル列（`for s in 1-alevin 2-parr …`）で書く。
- **`rm` は権限で拒否される**ことが多い。削除は `mv` で退避するかユーザに依頼。
- 出力規約：`_paths.py` の `out(category, name)`（`out/<category>/` 自動作成）。SVG検証は `python3 -c "import xml.dom.minidom..."`、SVG→PNGプレビューは `qlmanage -t -s <px> -o <dir> file.svg`（正方形クロップに注意）。ブラウザ確認は `python3 -m http.server` + playwright（file://は不可）。
- ブランド視覚言語：紙地 `#FAFAF6`／冷青 `#2E6E8E`(=抑制因子)／温土 `#C4722A`(=活性化因子)／明朝+EB Garamond。テンプレ型インフォグラフィックツール(Canva等)はブランド毀損で不可＝自作。
- 専門ロール：辛口・忖度なしの魚類色素/反応拡散レビュアーとして振る舞うことが期待されている。

## 最初の一手（推奨）
このファイルとメモリ `rd_turing_salmon.md` を読み、`rd/viewers/rd_salmon_sim_topview.html` をブラウザで起動して
現状を目視確認 → ユーザに「①公開反映 ②背側2次元RD ③calico2色 ④形の追い込み」のどれを進めるか確認してから着手する。
