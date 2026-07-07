# fish-pattern — ディレクトリ構成

サケの体模様・鱗模様を手続き生成するスクリプト群と生成物。

## レイアウト

```
fish-pattern/
├── *.py                スクリプト(相互importするため全て直下に同居)
├── _paths.py           入出力パス解決ヘルパー(__file__基準・CWD非依存)
├── calibration.json    実画像から抽出した段階別配色(rd/ も親直下を参照するため直下固定)
├── assets/             手描き/取り込みの入力素材
│   ├── scale-lineart.png   scale-brush.svg   scale-ink.svg   _rings_mask.png
├── ref/                参照実写(s1/s3/s5/c4fda/c6male …)— extract_* の入力
├── _grunge_src/        グランジテクスチャ — apply_*_kasure の入力
├── _archive/           旧版アーカイブ
├── rd/                 反応拡散エンジン(別README: rd/RD_MODEL.md)
└── out/                生成物(カテゴリ別)
    ├── kasure/         掠れSVG/PNG (build_kasure* / apply_*_kasure)
    ├── lines/          線画SVG/PNG (build_lines_simple / build_lines_grad)
    ├── scale-bg/       背景パターン+ink (scale_patterns / scale_ink) ← build_matrix の入力
    ├── matrix/         組合せマトリクス (build_matrix)
    ├── stipple/        点描 (stipple_art / fish_stipple / fish_top)
    ├── top/            真上ソフト点描 (fish_top_soft)
    ├── pattern/        実写抽出タイル+montage (extract_pattern / pattern / pattern_form)
    ├── palette/        配色proof (extract_palette)
    ├── provenance/     出典パネル (provenance)
    ├── turing/         チューリングzoo/sweep (turing_zoo / turing_sweep)
    ├── radial/         放射スイムモック (compose_radial)
    ├── stage-vec/      段階ベクター (build_stage_vectors)
    ├── stage-scale/    段階別鱗バンド (build_stage_bands)
    └── bake/           Figma用ベイク書き出し(スクリプト管理外の手動export)
```

## 実行

- **ランタイム**: `/opt/homebrew/bin/python3`(numpy/PIL/scipy 入り。`python3`=3.9 には無い)
- 出力先は全て `_paths.py` が `__file__` 基準で解決するので **どの CWD からでも** `out/<category>/` に書き出される。
- ただし `extract_palette` / `extract_pattern` / `provenance` は `ref/` と `/tmp/` を
  **CWD相対**で読むため、これらはプロジェクトルート(fish-pattern/)から実行すること。

## データフロー(スクリプト間の連鎖)

- `scale_patterns` / `scale_ink` → `out/scale-bg/*` → **`build_matrix`** が入力に取る
- `build_kasure_ink` → `out/kasure/scale-ink-kasure.svg` → **`build_kasure_ink_grad`**
- `build_lines_simple` → `out/lines/scale-lines.svg` → **`build_lines_grad`**
- `extract_palette` → `calibration.json`(直下)→ **`rd/rd_salmon.py`** / `fish_top` / `build_stage_vectors`
