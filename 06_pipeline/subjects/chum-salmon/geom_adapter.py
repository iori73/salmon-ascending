#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
geom_adapter.py (chum-salmon) — 06_pipeline/engine/geom_api.py の契約を、
既存の 04_visual/fish-pattern/build_stage_vectors.py にそのまま委譲して満たす薄いアダプタ。

build_stage_vectors.py は既に calibration.json(実写真からの抽出色)を基準に、
kype(鉤鼻, 段階6/7)・gill_path(鰓)・parr_bars(段階2)・calico alternating bars(段階6)を
幾何学的に生成済みなので、新規のジオメトリコードは書かず再利用する。

stage_spec(dict, spec.yamlの1段階分)は現時点では未使用(build_stage_vectors.py側の
calibration.json駆動ロジックが同じ生物学的事実を既に正しく反映しているため)。将来
spec.yaml側の値を優先させたい場合は、ここで stage_spec の color_regions/diagnostic_checklist
を build_stage_vectors.stage_palette() の上書きに使うよう拡張する。
"""
import os
import sys

_FISH_PATTERN_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..",
    "04_visual", "fish-pattern",
)
sys.path.insert(0, os.path.abspath(_FISH_PATTERN_DIR))

import build_stage_vectors as _bsv  # noqa: E402


def render_stage_svg(stage_id: int, stage_spec: dict) -> str:
    if stage_id not in _bsv.SLUG:
        raise ValueError(
            "build_stage_vectors.py has no geometry for stage %d yet "
            "(only %s implemented)" % (stage_id, sorted(_bsv.SLUG))
        )
    return _bsv.render_stage_svg(stage_id, standalone=True)


def canvas_size():
    return (_bsv.W, _bsv.H)
