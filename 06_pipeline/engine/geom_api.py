#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
geom_api.py — 各 subject の geom_adapter.py が満たすべき契約。

build_scaffold.py はこの契約の関数だけを呼ぶ。中身(パラメトリック幾何・鰭/kype/鰓の
生成方法)は subject ごとに自由に実装してよい — chum-salmon の場合は既存の
04_visual/fish-pattern/fish_geom.py + build_stage_vectors.py をそのまま再利用する薄い
アダプタで足りている(geom_adapter.py 参照)。

必須関数:

    render_stage_svg(stage_id: int, stage_spec: dict) -> str
        spec.yaml の1段階分のdict(body_shape/mouth_jaw/appendages/color_regionsなど)を
        受け取り、その段階の構造スキャフォールドSVG(完全なXML文字列)を返す。
        アキュラシー担保のため、この出力だけで以下が幾何学的に保証されていなければならない:
          - body_shape に応じた輪郭
          - mouth_jaw.kype_present == True の場合、鉤鼻の形状が輪郭に含まれる
          - appendages.fins の各 present:true な鰭が正しい位置に存在する
          - respiratory_structure.gill_cover_visible == True の場合、鰓蓋の線が含まれる
          - color_regions の pattern_type(parr_bars/calico_blotchy/uniformなど)に応じた
            塗り分け(細かい実際の色味はAI生成側で仕上げてよいが、模様の"種類"は幾何側で確定する)

任意関数(あれば build_scaffold.py が利用、なくても動く):

    canvas_size() -> (width: float, height: float)
        デフォルトは (360.0, 140.0) — fish_geom.py の値を踏襲。

契約を満たす新規 subject を追加する手順は SPEC_SCHEMA.md 参照。
"""

from typing import Protocol


class GeomAdapter(Protocol):
    def render_stage_svg(self, stage_id: int, stage_spec: dict) -> str:
        ...
