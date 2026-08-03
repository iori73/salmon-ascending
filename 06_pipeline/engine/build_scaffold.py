#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_scaffold.py — subject の spec.yaml + geom_adapter.py から、各段階の
「構造スキャフォールド」ラスタ画像(PNG)を生成する。

このPNGは完成イラストではなく、generate.py がGeminiに渡す構造条件画像(img2img的な下敷き)。
体形・鰭配置・kype有無・鰓・模様の"種類"がここでピクセルレベルに確定しているため、
AIが解剖学を発明する余地をなくす。

使い方:
    python3 build_scaffold.py <subject-id> [stage_id ...]
    例: python3 build_scaffold.py chum-salmon 2 6
"""
import importlib.util
import os
import sys

import cairosvg
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PIPELINE_ROOT = os.path.dirname(HERE)


def _load_adapter(subject: str):
    adapter_path = os.path.join(PIPELINE_ROOT, "subjects", subject, "geom_adapter.py")
    if not os.path.exists(adapter_path):
        raise FileNotFoundError("no geom_adapter.py for subject '%s' at %s" % (subject, adapter_path))
    spec = importlib.util.spec_from_file_location("geom_adapter_%s" % subject, adapter_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_spec(subject: str) -> dict:
    spec_path = os.path.join(PIPELINE_ROOT, "subjects", subject, "spec.yaml")
    with open(spec_path) as fp:
        return yaml.safe_load(fp)


def build_scaffold(subject: str, stage_id: int, scale: float = 4.0) -> str:
    """1段階分のSVGを生成しPNGにラスタライズ。保存先パスを返す。"""
    adapter = _load_adapter(subject)
    spec = _load_spec(subject)
    stage_entries = {s["stage_id"]: s for s in spec["stages"]}
    if stage_id not in stage_entries:
        raise ValueError("stage %d not found in %s/spec.yaml" % (stage_id, subject))

    svg = adapter.render_stage_svg(stage_id, stage_entries[stage_id])

    out_dir = os.path.join(PIPELINE_ROOT, "subjects", subject, "scaffold")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "stage-%d.png" % stage_id)
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=out_path, scale=scale)
    return out_path


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    subject = sys.argv[1]
    stage_ids = [int(a) for a in sys.argv[2:]] if len(sys.argv) > 2 else None
    if stage_ids is None:
        spec = _load_spec(subject)
        stage_ids = [s["stage_id"] for s in spec["stages"]]
    for sid in stage_ids:
        path = build_scaffold(subject, sid)
        print("saved", path)


if __name__ == "__main__":
    main()
