#!/usr/bin/env python3
"""
remove_annotation_paths.py

Remove annotation/measurement line artifacts from potrace-generated
fish scale SVG files. Identifies them by geometry: extremely tall and
narrow (nearly vertical line segments from the original photo's ruler annotation).

Detection: endpoint-only x_range < 20 AND (y_range / x_range) > 10

Outputs <original_stem>_clean.svg (non-destructive).

Usage:
    python3 remove_annotation_paths.py              # process default files
    python3 remove_annotation_paths.py --dry-run    # report only, no output
    python3 remove_annotation_paths.py file.svg     # specific file
"""

import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
TAG_PATH = f"{{{SVG_NS}}}path"
TAG_G = f"{{{SVG_NS}}}g"

DEFAULT_FILES = [
    os.path.join(os.path.dirname(__file__), "scale_chum-kz0503f034-ring-lines-v3_1_ADFG_PD.svg"),
    os.path.join(os.path.dirname(__file__), "scale_chum-kz0503f034-ring-lines-v3_2_ADFG_PD.svg"),
]

ASPECT_THRESHOLD = 12.0
X_RANGE_THRESHOLD = 15.0

# SVG coordinate constraints (transform: translate(0,921) scale(0.1,-0.1))
# Only remove paths within this region — excludes outer edge and globular bottom
SVG_X_MAX = 650.0   # right boundary: outer edge is beyond this
SVG_Y_MAX = 750.0   # lower boundary: globular area is below this


def endpoint_bbox(d):
    """
    Bounding box using endpoint-only traversal (not Bezier control points).
    Bezier control points inflate x_range and cause false negatives on annotation paths.
    Returns (xmin, xmax, ymin, ymax) or None.
    """
    m = re.match(r"M\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)", d)
    if not m:
        return None

    cx, cy = float(m.group(1)), float(m.group(2))
    xs = [cx]
    ys = [cy]

    tokens = re.findall(r"[A-Za-z]|[-+]?\d+(?:\.\d+)?", d[m.end():])
    i = 0
    cmd = None
    while i < len(tokens):
        tok = tokens[i]
        if tok.isalpha():
            cmd = tok
            i += 1
            continue

        if cmd == "c":  # relative cubic bezier: dx1 dy1 dx2 dy2 dx dy
            if i + 5 < len(tokens):
                try:
                    cx += float(tokens[i + 4])
                    cy += float(tokens[i + 5])
                except ValueError:
                    break
                xs.append(cx)
                ys.append(cy)
                i += 6
            else:
                break
        elif cmd == "l":  # relative line-to: dx dy
            if i + 1 < len(tokens):
                try:
                    cx += float(tokens[i])
                    cy += float(tokens[i + 1])
                except ValueError:
                    break
                xs.append(cx)
                ys.append(cy)
                i += 2
            else:
                break
        else:
            i += 1

    return min(xs), max(xs), min(ys), max(ys)


def is_annotation(d):
    """Returns (flagged: bool, metrics: dict)."""
    bbox = endpoint_bbox(d)
    if bbox is None:
        return False, {}

    xmin, xmax, ymin, ymax = bbox
    x_range = xmax - xmin
    y_range = ymax - ymin

    # Convert potrace coords to SVG coords for positional filtering
    # transform: translate(0, 921) scale(0.1, -0.1)
    svg_x = xmin * 0.1
    svg_y = 921 - ymin * 0.1  # ymin in potrace = topmost in SVG (highest y value)

    if x_range <= 0:
        metrics = {"x_range": 0, "y_range": y_range, "aspect": float("inf"), "xmin": xmin, "ymin": ymin, "svg_x": svg_x, "svg_y": svg_y}
        in_region = svg_x < SVG_X_MAX and svg_y < SVG_Y_MAX
        return in_region, metrics

    aspect = y_range / x_range
    metrics = {"x_range": round(x_range, 1), "y_range": round(y_range, 1), "aspect": round(aspect, 1), "xmin": xmin, "ymin": ymin, "svg_x": svg_x, "svg_y": svg_y}

    # Positional guard: skip outer right edge and globular bottom area
    in_region = svg_x < SVG_X_MAX and svg_y < SVG_Y_MAX
    return (aspect > ASPECT_THRESHOLD and x_range < X_RANGE_THRESHOLD and in_region), metrics


def process_file(svg_path, dry_run=False):
    ET.register_namespace("", SVG_NS)
    tree = ET.parse(svg_path)
    root = tree.getroot()

    g = root.find(f".//{TAG_G}")
    if g is None:
        print(f"  WARNING: no <g> element in {os.path.basename(svg_path)}")
        return 0

    paths = g.findall(TAG_PATH)
    total = len(paths)
    to_remove = []

    for path in paths:
        flagged, metrics = is_annotation(path.get("d", ""))
        if flagged:
            to_remove.append((path, metrics))

    if not to_remove:
        print(f"  No annotation paths found ({total} paths total)")
        return 0

    print(f"  {len(to_remove)} annotation path(s) to remove (of {total} total):")
    for _, m in to_remove:
        # Convert potrace coords → approximate SVG viewBox coords for readability
        svg_x = m["xmin"] * 0.1
        svg_y = round(921 - m["ymin"] * 0.1, 1)
        print(f"    SVG≈({svg_x:.1f}, {svg_y:.1f})  x_range={m['x_range']}  y_range={m['y_range']}  aspect={m['aspect']}")

    if dry_run:
        print("  [dry-run] No file written.")
        return len(to_remove)

    for path, _ in to_remove:
        g.remove(path)

    stem, ext = os.path.splitext(svg_path)
    out_path = stem + "_clean" + ext
    tree.write(out_path, xml_declaration=True, encoding="unicode")

    remaining = len(tree.getroot().findall(f".//{TAG_PATH}"))
    print(f"  -> {out_path}  ({remaining} paths remaining)")

    return len(to_remove)


def main():
    parser = argparse.ArgumentParser(description="Remove annotation paths from potrace fish scale SVGs.")
    parser.add_argument("files", nargs="*", default=DEFAULT_FILES)
    parser.add_argument("--dry-run", action="store_true", help="Report without writing output")
    args = parser.parse_args()

    total = 0
    for path in args.files:
        if not os.path.exists(path):
            print(f"ERROR: not found: {path}", file=sys.stderr)
            continue
        print(f"\n{os.path.basename(path)}")
        total += process_file(path, dry_run=args.dry_run)

    print(f"\nTotal removed: {total}")


if __name__ == "__main__":
    main()
