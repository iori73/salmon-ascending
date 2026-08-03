#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
critique.py — 生成画像 + spec.yaml の diagnostic_checklist(+ style/sketch-v1.mdのstyle
checklist)を Claude(画像入力+tool_choice強制JSON)に渡し、項目ごとpass/fail/uncertainの
判定を得る。

自動モード: 環境変数 ANTHROPIC_API_KEY(または 06_pipeline/.env)が設定されていれば
Claude API を直接呼び出す。
手動モード: キー未設定なら、判定リクエストを attempts/<subject>/<stage>/NN.review-request.json
に書き出すだけに留め、Claude Codeセッション(人間が同席する対話)がその画像とチェックリストを
Read/推論で確認して NN.verdict.json を作成する運用に委ねる(2段階マイルストーンではキー1本を
追加取得しなくても検証ループを止めないため)。
"""
import argparse
import json
import os
import re
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate as _generate  # noqa: E402 (再利用: _load_dotenv, PIPELINE_ROOT)

HERE = os.path.dirname(os.path.abspath(__file__))
PIPELINE_ROOT = os.path.dirname(HERE)

CRITIQUE_MODEL = os.environ.get("CRITIQUE_MODEL", "claude-opus-5")

VERDICT_TOOL = {
    "name": "report_checklist_verdicts",
    "description": "画像を見て、渡されたチェックリスト各項目についてpass/fail/uncertainを判定して報告する。",
    "input_schema": {
        "type": "object",
        "properties": {
            "verdicts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "claim": {"type": "string"},
                        "verdict": {"type": "string", "enum": ["pass", "fail", "uncertain"]},
                        "evidence": {"type": "string", "description": "画像のどの部分を根拠にしたか、日本語で簡潔に"},
                    },
                    "required": ["claim", "verdict", "evidence"],
                },
            }
        },
        "required": ["verdicts"],
    },
}


def _load_spec(subject: str) -> dict:
    with open(os.path.join(PIPELINE_ROOT, "subjects", subject, "spec.yaml")) as fp:
        return yaml.safe_load(fp)


def _style_checklist(style_name: str = "sketch-v1") -> list:
    path = os.path.join(PIPELINE_ROOT, "style", "%s.md" % style_name)
    text = open(path).read()
    m = re.search(r"## style checklist.*?\n(.*?)(?:\n##|\Z)", text, re.S)
    if not m:
        return []
    items = []
    for block in re.split(r"\n(?=- claim:)", m.group(1).strip()):
        claim_m = re.search(r'claim:\s*"(.+?)"', block)
        sev_m = re.search(r"severity:\s*(\w+)", block)
        if claim_m:
            items.append({"claim": claim_m.group(1), "severity": sev_m.group(1) if sev_m else "advisory"})
    return items


def _all_checklist_items(subject: str, stage_id: int) -> list:
    spec = _load_spec(subject)
    stage = next(s for s in spec["stages"] if s["stage_id"] == stage_id)
    items = [
        {"claim": c["claim"], "severity": c["severity"], "expected": c["expected"]}
        for c in stage.get("diagnostic_checklist", [])
    ]
    items += _style_checklist()
    return items


def _api_key():
    _generate._load_dotenv()
    return os.environ.get("ANTHROPIC_API_KEY")


def critique_auto(image_path: str, checklist: list) -> list:
    """ANTHROPIC_API_KEY があるときの自動判定。verdictリスト([{claim,verdict,evidence,severity}])を返す。"""
    import base64

    import anthropic

    client = anthropic.Anthropic(api_key=_api_key())
    with open(image_path, "rb") as fp:
        image_b64 = base64.standard_b64encode(fp.read()).decode("utf-8")

    claims_text = "\n".join("- %s" % c["claim"] for c in checklist)
    response = client.messages.create(
        model=CRITIQUE_MODEL,
        max_tokens=4096,
        tools=[VERDICT_TOOL],
        tool_choice={"type": "tool", "name": "report_checklist_verdicts"},
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_b64}},
                    {
                        "type": "text",
                        "text": (
                            "この画像について、以下のチェックリストの各項目をpass/fail/uncertainで判定してください。\n"
                            + claims_text
                        ),
                    },
                ],
            }
        ],
    )
    tool_use = next(b for b in response.content if b.type == "tool_use")
    verdicts = tool_use.input["verdicts"]
    by_claim = {v["claim"]: v for v in verdicts}
    out = []
    for c in checklist:
        v = by_claim.get(c["claim"], {"verdict": "uncertain", "evidence": "(no verdict returned)"})
        out.append({**c, "verdict": v["verdict"], "evidence": v.get("evidence", "")})
    return out


def critique(subject: str, stage_id: int, image_path: str) -> dict:
    checklist = _all_checklist_items(subject, stage_id)
    out_dir = os.path.join(PIPELINE_ROOT, "attempts", subject, str(stage_id))
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(image_path))[0]

    if _api_key():
        verdicts = critique_auto(image_path, checklist)
        required_fail = [v for v in verdicts if v["severity"] == "required" and v["verdict"] != "pass"]
        result = {
            "image": image_path,
            "mode": "auto",
            "verdicts": verdicts,
            "passed": len(required_fail) == 0,
        }
        with open(os.path.join(out_dir, "%s.verdict.json" % base), "w") as fp:
            json.dump(result, fp, ensure_ascii=False, indent=2)
        return result

    # 手動モード: レビュー依頼だけ書き出す
    request_path = os.path.join(out_dir, "%s.review-request.json" % base)
    with open(request_path, "w") as fp:
        json.dump({"image": image_path, "checklist": checklist}, fp, ensure_ascii=False, indent=2)
    print(
        "ANTHROPIC_API_KEY未設定のため手動モード: %s を作成しました。\n"
        "Claude Codeセッションで画像(%s)とチェックリストを確認し、\n"
        "%s に {\"image\":..., \"mode\":\"manual\", \"verdicts\":[...], \"passed\": true|false} を書いてください。"
        % (request_path, image_path, os.path.join(out_dir, "%s.verdict.json" % base)),
        file=sys.stderr,
    )
    return {"image": image_path, "mode": "manual_pending", "review_request": request_path}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("subject")
    ap.add_argument("stage_id", type=int)
    ap.add_argument("image_path")
    args = ap.parse_args()
    result = critique(args.subject, args.stage_id, args.image_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
