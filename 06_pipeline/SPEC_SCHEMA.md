---
title: subject spec.yaml スキーマ定義
status: v1
scheme: 対象非依存(魚・昆虫・哺乳類・任意の物体のN段階変化シリーズに適用可能)
related:
  - references/SCHEMA.md
  - 02_research/life-stage-descriptions.md
  - 04_visual/lifecycle-stages/color-palette.md
date: 2026-07-29
---

# spec.yaml スキーマ

`06_pipeline/subjects/<subject-id>/spec.yaml` の構造。1ファイル = 1対象(種)、段階配列を持つ。

新規調査ではなく、既存ドキュメント(`life-stage-descriptions.md`, `color-palette.md`, `references/`)からの**転記・構造化**として埋める。フィールド自体は「魚」を前提にしていない — 昆虫なら`appendages.limbs`、哺乳類なら`respiratory_structure`は空欄でよい。

## トップレベル

```yaml
subject: chum-salmon        # kebab-case ID。ディレクトリ名と一致
subject_name: {ja: シロザケ, en: Chum salmon (Oncorhynchus keta)}
stages:
  - <stage entry>
  - ...
```

## stage entry

```yaml
stage_id: 6                          # 通し番号(1始まり)
stage_name: {ja: 河川遡上, en: River run}

body_shape:
  descriptor: "..."                  # 自由記述(体形の特徴。既存の輪郭ジオメトリで表現できない差分のみ)
  confidence: ◎|○|△
  source_ids: [references/sources/src-XX.md, ...]

mouth_jaw:
  kype_present: true|false           # 対象非依存の一般フィールドは "structure_state" のような名前にしてもよいが、
  teeth_developed: true|false        # 鮭固有の観察が既にあるためそのまま採用。将来の種は該当フィールドをfalse/null据え置きでよい
  confidence: ◎|○|△
  source_ids: [...]

eye:
  descriptor: "..."
  confidence: ◎|○|△

respiratory_structure:
  gill_cover_visible: true|false     # 魚以外(昆虫の気門、哺乳類は該当なし)は null で省略可
  confidence: ◎|○|△

appendages:
  fins:                              # 魚用。他対象は limbs/wings 等の同形式リストに置き換え
    - {name: dorsal, present: true}
    - {name: adipose, present: true}
    - {name: anal, present: true}
    - {name: pelvic, present: true}
    - {name: pectoral, present: true}

color_regions:
  - region: flank
    pattern_type: calico_blotchy      # none | parr_bars | calico_blotchy | speckle | uniform | ...
    hex: ["#9CA356", "#8C3A59", "#262F1D"]
    confidence: ◎|○|△
    source_ids: [...]

diagnostic_checklist:                 # ★最重要: ユーザーが実際に指摘した失敗パターンを検証可能な主張に変換したもの
  - claim: "kype(鉤鼻)が吻端に明確に見える"
    expected: true
    severity: required|advisory
    guards_against: no_kype           # 失敗モードの短いラベル。spec_to_prompt.py が否定制約の生成に使う

reference_photos:
  - references/images/img-chum-breeding-illustration.md
  # 対象写真が存在しない場合は文字列 "NONE — 真の対象写真なし" を入れる(critique.py が低信頼フラグを立てる)
```

## 確信度フラグの意味(既存`color-palette.md`と同じ運用)

- `◎` = 文献一次情報 + 実写真からの実測が一致
- `○` = 文献一次情報のみ
- `△` = 類推(直接の裏付けなし)

## `diagnostic_checklist` の設計ルール

1. 各itemは**画像を見て真偽判定できる**主張にする(「美しい婚姻色」のような主観的表現はNG、「側面模様が不規則な紫〜オリーブのまだらである」のような検証可能な表現にする)。
2. `guards_against` は既知の失敗モード名。同じ失敗モードは複数対象・複数段階で使い回してよい(例: `redband_spot_confusion` は鮭以外の魚でも起こりうる)。
3. `severity: required` はQCで1つでもfailなら再生成対象。`advisory` は記録のみで再生成をブロックしない。

## 将来の対象追加時の手順

1. `06_pipeline/subjects/<new-subject>/spec.yaml` を新規作成、上記スキーマに沿って埋める(未調査の一次資料が必要ならresearch用にClaude Codeへ依頼)
2. `06_pipeline/subjects/<new-subject>/geom_adapter.py` を新規作成(`06_pipeline/engine/geom_api.py` の契約を満たす)
3. 参照写真を `references/` に追加
4. `engine/` 配下(`spec_to_prompt.py`, `generate.py`, `critique.py`, `loop.py`)は無改造で流用可能
