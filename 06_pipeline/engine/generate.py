#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate.py — Gemini(gemini-2.5-flash-image, 通称 Nano Banana)のネイティブ多画像入力を使い、
構造スキャフォールド(build_scaffold.pyの出力)+実写真(references/)+スタイルアンカーを
条件画像として渡し、spec_to_prompt.pyで組み立てたプロンプトで1枚生成する。

img2img的に「構造を保ったまま指定スタイルで再描画」させるのが狙いで、ControlNet等の
追加インフラは不要(Geminiのネイティブ画像編集能力を利用)。

APIキーは 06_pipeline/.env (gitignore済み、KEY=VALUE形式) に
GOOGLE_API_KEY=... と書くか、環境変数 GOOGLE_API_KEY / GEMINI_API_KEY を直接設定する。

使い方:
    python3 generate.py <subject-id> <stage_id> [--prompt-override TEXT] [--out PATH]
"""
import argparse
import os
import re
import sys

import yaml
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec_to_prompt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PIPELINE_ROOT = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(PIPELINE_ROOT)

MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")


def _load_dotenv():
    """06_pipeline/.env (gitignore済み) から KEY=VALUE を読み、未設定の環境変数だけ埋める。
    APIキーを会話やコマンド引数に一切出さずに済ませるため。"""
    env_path = os.path.join(PIPELINE_ROOT, ".env")
    if not os.path.exists(env_path):
        return
    for line in open(env_path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def _api_key():
    _load_dotenv()
    return os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")


def _load_spec(subject: str) -> dict:
    with open(os.path.join(PIPELINE_ROOT, "subjects", subject, "spec.yaml")) as fp:
        return yaml.safe_load(fp)


def _resolve_reference_photo(ref_entry: str):
    """references/images/img-xxx.md -> 実画像ファイルの絶対パス。'NONE...'の場合はNoneを返す。"""
    if ref_entry.upper().startswith("NONE"):
        return None
    md_path = os.path.join(REPO_ROOT, ref_entry)
    if not os.path.exists(md_path):
        print("warning: reference file not found: %s" % md_path, file=sys.stderr)
        return None
    text = open(md_path).read()
    m = re.search(r"^local_path:\s*(.+)$", text, re.M)
    if not m:
        print("warning: no local_path in %s" % md_path, file=sys.stderr)
        return None
    local_path = m.group(1).strip()
    full_path = os.path.join(REPO_ROOT, local_path)
    if not os.path.exists(full_path):
        print("warning: local_path does not exist: %s" % full_path, file=sys.stderr)
        return None
    return full_path


def _next_attempt_path(subject: str, stage_id: int, style_name: str):
    out_dir = os.path.join(PIPELINE_ROOT, "attempts", subject, str(stage_id))
    os.makedirs(out_dir, exist_ok=True)
    pattern = re.compile(r"(\d+)-%s\.png$" % re.escape(style_name))
    existing = [pattern.match(f) for f in os.listdir(out_dir)]
    n = max([int(m.group(1)) for m in existing if m], default=0) + 1
    return os.path.join(out_dir, "%02d-%s.png" % (n, style_name)), n


def generate(subject: str, stage_id: int, prompt_text: str = None, out_path: str = None, style_name: str = "sketch-v1", use_references: bool = True):
    api_key = _api_key()
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY (or GEMINI_API_KEY) environment variable is not set. "
            "Get a key from Google AI Studio and export it before running generate.py."
        )
    import google.genai as genai
    from google.genai import types

    spec = _load_spec(subject)
    stage = next(s for s in spec["stages"] if s["stage_id"] == stage_id)

    if prompt_text is None:
        prompt_text = spec_to_prompt.build_prompt(subject, stage_id, style_name=style_name)

    contents = [prompt_text]

    scaffold_path = os.path.join(PIPELINE_ROOT, "subjects", subject, "scaffold", "stage-%d.png" % stage_id)
    if os.path.exists(scaffold_path):
        contents.append(Image.open(scaffold_path))
    else:
        print("warning: no structural scaffold at %s (run build_scaffold.py first)" % scaffold_path, file=sys.stderr)

    if use_references:
        for ref in stage.get("reference_photos", []):
            img_path = _resolve_reference_photo(ref)
            if img_path:
                contents.append(Image.open(img_path))
    else:
        print("skipping reference_photos conditioning (--no-references)", file=sys.stderr)

    anchor_path = os.path.join(PIPELINE_ROOT, "style", "anchor-%s.png" % style_name)
    if os.path.exists(anchor_path):
        contents.append(Image.open(anchor_path))

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"]),
    )

    image_bytes = None
    for part in response.candidates[0].content.parts:
        if getattr(part, "inline_data", None) is not None:
            image_bytes = part.inline_data.data
            break
    if image_bytes is None:
        raise RuntimeError("Gemini response contained no image part. Response: %r" % response)

    if out_path is None:
        out_path, _n = _next_attempt_path(subject, stage_id, style_name)
    with open(out_path, "wb") as fp:
        fp.write(image_bytes)
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("subject")
    ap.add_argument("stage_id", type=int)
    ap.add_argument("--prompt-override", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--style", default="sketch-v1", dest="style_name")
    ap.add_argument("--no-references", action="store_false", dest="use_references",
                     help="skip stage reference_photos conditioning (useful when a reference's own rendering "
                          "style, e.g. a painterly/photoreal illustration, conflicts with a flat-style target)")
    args = ap.parse_args()
    path = generate(args.subject, args.stage_id, prompt_text=args.prompt_override, out_path=args.out,
                     style_name=args.style_name, use_references=args.use_references)
    print("saved", path)


if __name__ == "__main__":
    main()
