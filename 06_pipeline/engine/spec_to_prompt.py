#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
spec_to_prompt.py — spec.yaml の1段階分から、Gemini画像生成に渡す英語プロンプトを
機械的に組み立てる。手打ちのプロンプト文章を書かないことが目的(対象が変わっても
このファイルは無改造で流用できる)。

肯定記述 = spec本文(body_shape/mouth_jaw/eye/respiratory_structure/appendages/color_regions)
必須事項 = diagnostic_checklist の expected な主張
否定制約 = diagnostic_checklist の guards_against ラベルから自動生成(FAILURE_MODE_NEGATIVESに
           未登録のラベルは、claimをそのまま反転させた汎用文で代替するのでラベル追加を必須にしない)
スタイル = style/<style-name>.md の固定ブロック(対象非依存、常に不変で付加)
"""
import os
import re

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PIPELINE_ROOT = os.path.dirname(HERE)

# 既知の失敗モード -> 具体的な否定プロンプト文。
# ユーザーが実際に指摘した3つの誤り(calico/パーマーク/kype欠落)起点で立てたラベル。
# 新しいguards_againstラベルが出てきたら随時追加していく(必須ではない、フォールバックあり)。
FAILURE_MODE_NEGATIVES = {
    "no_parr_marks": "Do NOT omit parr marks — they must be visible on this juvenile stage.",
    "uniform_parr_mark": (
        "Do NOT render the parr marks as perfectly uniform, evenly-spaced, identical solid ovals. "
        "Real parr marks vary irregularly in spacing and size."
    ),
    "flat_single_color": "Do NOT render the body as one flat uniform color with no countershading.",
    "premature_kype": "Do NOT give this juvenile a hooked jaw (kype) or developed teeth — those appear only in the mature spawning stage.",
    "no_kype": (
        "Do NOT draw a smooth, rounded snout. The male kype (hooked, downward-curving jaw) must be "
        "clearly visible at this spawning stage."
    ),
    "redband_spot_confusion": (
        "Do NOT render the spawning coloration as a neat row of uniform, bright solid-red oval dots "
        "(that is rainbow-trout redband patterning, not chum salmon). The real pattern is an irregular, "
        "blotchy 'calico' mix of purple, olive, and black patches with soft/uneven edges."
    ),
    "missing_posterior_darkening": "Do NOT keep the posterior third of the body light-colored — it should darken toward black near the tail.",
    "retained_silvering": "Do NOT render bright silver/chrome skin at this stage — the spawning-run body has lost all silvering.",
    "no_gill_cover": "Do NOT omit the gill cover outline — it should read as a distinct line/edge behind the eye.",
    "adult_body_shape_on_larva": (
        "Do NOT draw a stout, spindle-shaped adult/juvenile fish body. At this stage the body must be an "
        "elongated, thin, ribbon-like larval form (much lower body-height-to-length ratio than an adult fish), "
        "matching a real newly-hatched alevin, not a miniature adult salmon."
    ),
    "yolk_sac_appears_detached": (
        "Do NOT draw the yolk sac as a separate flat shape merely touching or floating below the body "
        "silhouette. In real alevin the sac is fused to the body: the belly flesh curves over and around "
        "the sac so sac and body read as one continuous organic form with a single unbroken outline, not "
        "two overlapping shapes."
    ),
    "keyline_outline_present": (
        "Do NOT draw any dark outline, keyline, or stroke tracing the body, fins, gill line, or any other "
        "boundary. This is a hard rule of the current style: every edge must be formed only by one flat "
        "color meeting another flat color directly, like abutting cut paper, with zero linework of any kind."
    ),
    "spurious_spots": (
        "Do NOT add small black speckles, dots, or spot patterns scattered across the back or flank. "
        "Ocean-phase chum salmon have a completely unmarked, smooth silver body with no spotting "
        "(unlike Chinook or coho salmon, which do have spots) — keep the body clean and unmarked."
    ),
}


def _load_spec(subject: str) -> dict:
    with open(os.path.join(PIPELINE_ROOT, "subjects", subject, "spec.yaml")) as fp:
        return yaml.safe_load(fp)


def _style_block(style_name: str = "sketch-v1") -> str:
    path = os.path.join(PIPELINE_ROOT, "style", "%s.md" % style_name)
    text = open(path).read()
    m = re.search(r"## プロンプト用記述.*?```\n(.*?)```", text, re.S)
    if not m:
        raise ValueError("could not find prompt block in %s" % path)
    return m.group(1).strip()


def _color_region_lines(stage: dict) -> list:
    lines = []
    for region in stage.get("color_regions", []):
        hexes = ", ".join(region["hex"])
        lines.append(
            "%s: pattern=%s, approximate colors=[%s]"
            % (region["region"], region["pattern_type"], hexes)
        )
    return lines


def _positive_descriptors(stage: dict) -> list:
    lines = []
    if stage.get("body_shape", {}).get("descriptor"):
        lines.append("Body shape: %s" % stage["body_shape"]["descriptor"].strip())
    mj = stage.get("mouth_jaw", {})
    if mj.get("kype_present"):
        lines.append("Mouth/jaw: hooked kype present, teeth developed=%s" % mj.get("teeth_developed"))
    else:
        lines.append("Mouth/jaw: smooth, rounded snout, no kype")
    if stage.get("eye", {}).get("descriptor"):
        lines.append("Eye: %s" % stage["eye"]["descriptor"].strip())
    rs = stage.get("respiratory_structure", {})
    if rs.get("gill_cover_visible"):
        lines.append("Gill cover clearly outlined behind the eye")
    fins = [f["name"] for f in stage.get("appendages", {}).get("fins", []) if f.get("present")]
    if fins:
        lines.append("Fins present: %s" % ", ".join(fins))
    lines.extend(_color_region_lines(stage))
    return lines


def _checklist_lines(stage: dict, severity_filter=None):
    items = stage.get("diagnostic_checklist", [])
    if severity_filter:
        items = [c for c in items if c["severity"] in severity_filter]
    return items


def negatives_for_claims(checklist_items) -> list:
    """guards_against ラベル群 -> 否定プロンプト文のリスト(重複除去・フォールバック付き)。"""
    out = []
    seen = set()
    for c in checklist_items:
        label = c.get("guards_against")
        text = FAILURE_MODE_NEGATIVES.get(
            label, "Do NOT violate: expected %r for the claim %r." % (c["expected"], c["claim"])
        )
        if text not in seen:
            seen.add(text)
            out.append(text)
    return out


def build_prompt(subject: str, stage_id: int, style_name: str = "sketch-v1") -> str:
    spec = _load_spec(subject)
    stage = next(s for s in spec["stages"] if s["stage_id"] == stage_id)
    subj_name = spec["subject_name"]["en"]
    stage_name = stage["stage_name"]["en"]

    required = _checklist_lines(stage, severity_filter=("required",))
    advisory = _checklist_lines(stage, severity_filter=("advisory",))

    parts = []
    parts.append(
        "Scientifically accurate biological illustration of %s, life stage: %s."
        % (subj_name, stage_name)
    )
    parts.append("\nStructural/biological facts to depict:")
    parts.extend("- " + l for l in _positive_descriptors(stage))

    if required:
        parts.append("\nMust show (required, verified against real reference photos):")
        parts.extend("- " + c["claim"] for c in required)

    negatives = negatives_for_claims(required + advisory)
    if negatives:
        parts.append("\nAvoid (known failure modes from prior generation attempts):")
        parts.extend("- " + n for n in negatives)

    parts.append("\n" + _style_block(style_name))

    return "\n".join(parts)


def corrective_prompt(subject: str, stage_id: int, failed_claims: list, style_name: str = "sketch-v1") -> str:
    """critique.py が required 項目のfailを検出した後の再生成用プロンプト。
    failed_claims: critique.py の verdict リストから severity=required かつ fail のものだけ渡す。
    """
    negatives = negatives_for_claims(failed_claims)
    base = build_prompt(subject, stage_id, style_name)
    correction = "\n\nCORRECTIVE INSTRUCTIONS (previous attempt failed these checks):\n" + "\n".join(
        "- " + n for n in negatives
    )
    return base + correction


if __name__ == "__main__":
    import sys

    subject = sys.argv[1] if len(sys.argv) > 1 else "chum-salmon"
    stage_id = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    print(build_prompt(subject, stage_id))
