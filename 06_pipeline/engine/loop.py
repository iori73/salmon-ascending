#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
loop.py — generate.py → critique.py を繋ぎ、required項目のfailがあれば
spec_to_prompt.corrective_prompt() で修正プロンプトを組み立てて再生成する
(最大 MAX_RETRIES 回)。全試行を attempts/<subject>/<stage>/ に記録する。

ANTHROPIC_API_KEYが無い場合、critique.pyは手動モードで動く(review-request.jsonを
書き出すだけ)。その場合このループは1回生成した時点で止まり、人間 or Claude Codeの
レビューを待つよう案内する。
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import critique as _critique  # noqa: E402
import generate as _generate  # noqa: E402
import spec_to_prompt  # noqa: E402

MAX_RETRIES = 4


def run(subject: str, stage_id: int):
    prompt = spec_to_prompt.build_prompt(subject, stage_id)

    for attempt in range(1, MAX_RETRIES + 1):
        print("--- attempt %d/%d ---" % (attempt, MAX_RETRIES), file=sys.stderr)
        image_path = _generate.generate(subject, stage_id, prompt_text=prompt)
        print("generated", image_path, file=sys.stderr)

        result = _critique.critique(subject, stage_id, image_path)

        if result.get("mode") == "manual_pending":
            print(
                "手動レビュー待ち。%s のレビューを完了したら再度 loop.py を実行してください。"
                % result["review_request"],
                file=sys.stderr,
            )
            return result

        if result["passed"]:
            print("PASS on attempt %d" % attempt, file=sys.stderr)
            return result

        failed_required = [v for v in result["verdicts"] if v["severity"] == "required" and v["verdict"] != "pass"]
        print(
            "FAIL (%d required item(s) failed): %s"
            % (len(failed_required), ", ".join(v["claim"] for v in failed_required)),
            file=sys.stderr,
        )
        if attempt < MAX_RETRIES:
            prompt = spec_to_prompt.corrective_prompt(subject, stage_id, failed_required)

    print("EXHAUSTED retries without passing all required checks — flagging for human review.", file=sys.stderr)
    result["needs_human_review"] = True
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("subject")
    ap.add_argument("stage_id", type=int)
    args = ap.parse_args()
    result = run(args.subject, args.stage_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
