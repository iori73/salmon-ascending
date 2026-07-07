#!/usr/bin/env python3
"""
clean_scale_svg.py

Clean an Illustrator-traced fish-scale SVG:
  Stage A  release   - split compound paths (multi-subpath) into individual paths
  Stage B  noise     - remove tiny stray specks (もや): micro circle/rect/polygon + tiny path fragments
  Stage C  lines     - remove annotation straight lines (measurement axis / focus pointer)

Design goals:
  - Non-destructive: writes <stem>_clean.svg
  - Conservative: tight thresholds, --dry-run to preview counts/coords
  - Verifiable: --highlight RULE recolors candidates red (keeps everything) for visual check

Handles Adobe Illustrator export: absolute+relative mixed coords, path/circle/rect/polygon, nested <g>.

Usage:
  python3 clean_scale_svg.py SRC.svg --highlight noise   -> SRC_hl-noise.svg
  python3 clean_scale_svg.py SRC.svg --highlight lines    -> SRC_hl-lines.svg
  python3 clean_scale_svg.py SRC.svg --dry-run [--stages A,B,C]
  python3 clean_scale_svg.py SRC.svg --stages A,B,C       -> SRC_clean.svg
"""
import argparse, math, os, re, sys
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
for t in ("path", "circle", "rect", "polygon", "polyline", "line", "g"):
    globals()[f"TAG_{t.upper()}"] = f"{{{SVG_NS}}}{t}"

# ---- Conservative thresholds (viewBox 1703 x 1738 units) ----
NOISE_CIRCLE_R_MAX   = 3.5    # circles with radius below this are dust
NOISE_RECT_AREA_MAX  = 36.0   # tiny rects
NOISE_POLY_DIAG_MAX  = 16.0   # tiny polygon triangles
NOISE_PATH_BBOX_MAX  = 9.0    # isolated path fragments with bbox max-dim below this

LINE_MIN_LENGTH      = 150.0  # annotation line candidate min length
LINE_STRAIGHTNESS    = 0.04   # max_perp_dev / length below this == straight


# ---------- geometry ----------
_TOKEN = re.compile(r'[A-Za-z]|-?\d*\.?\d+(?:[eE]-?\d+)?')

def path_points(d):
    """Return list of on-curve anchor points (x,y) traversed by the path 'd'."""
    toks = _TOKEN.findall(d)
    pts = []
    i = 0; cmd = None; cx = cy = 0.0; sx = sy = 0.0
    def take(n):
        nonlocal i
        v = []
        while len(v) < n and i < len(toks) and not toks[i].isalpha():
            v.append(float(toks[i])); i += 1
        return v
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t; i += 1
            if cmd in 'Zz':
                cx, cy = sx, sy
            continue
        rel = cmd.islower(); c = cmd.upper()
        if c == 'M':
            v = take(2);  cx, cy = (cx+v[0], cy+v[1]) if rel else (v[0], v[1]); sx, sy = cx, cy; pts.append((cx, cy))
            cmd = 'l' if rel else 'L'  # subsequent pairs are implicit lineto
        elif c == 'L':
            v = take(2);  cx, cy = (cx+v[0], cy+v[1]) if rel else (v[0], v[1]); pts.append((cx, cy))
        elif c == 'H':
            v = take(1);  cx = cx+v[0] if rel else v[0]; pts.append((cx, cy))
        elif c == 'V':
            v = take(1);  cy = cy+v[0] if rel else v[0]; pts.append((cx, cy))
        elif c == 'C':
            v = take(6);  cx, cy = (cx+v[4], cy+v[5]) if rel else (v[4], v[5]); pts.append((cx, cy))
        elif c == 'S' or c == 'Q':
            v = take(4);  cx, cy = (cx+v[2], cy+v[3]) if rel else (v[2], v[3]); pts.append((cx, cy))
        elif c == 'T':
            v = take(2);  cx, cy = (cx+v[0], cy+v[1]) if rel else (v[0], v[1]); pts.append((cx, cy))
        elif c == 'A':
            v = take(7);  cx, cy = (cx+v[5], cy+v[6]) if rel else (v[5], v[6]); pts.append((cx, cy))
        else:
            i += 1
    return pts

def bbox_of(pts):
    if not pts: return None
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), max(xs), min(ys), max(ys)

def straightness(pts):
    """Return (max_perp_dev/length, length) using the segment between the two farthest points as the axis."""
    if len(pts) < 2: return (1.0, 0.0)
    # axis = endpoints (first, last); robust enough for stroke-like paths
    (x0, y0), (x1, y1) = pts[0], pts[-1]
    length = math.hypot(x1-x0, y1-y0)
    if length < 1e-6: return (1.0, 0.0)
    nx, ny = (y0-y1)/length, (x1-x0)/length  # unit normal
    maxdev = max(abs((px-x0)*nx + (py-y0)*ny) for px, py in pts)
    return (maxdev/length, length)


# ---------- element classification ----------
def subpath_count(d):
    return len(re.findall(r'[Mm]', d))

def split_subpaths(d):
    return [p.strip() for p in re.split(r'(?=[Mm])', d.strip()) if p.strip()]

def is_noise_circle(el):
    try: return float(el.get('r', 0)) <= NOISE_CIRCLE_R_MAX
    except: return False

def is_noise_rect(el):
    try: return float(el.get('width', 0)) * float(el.get('height', 0)) <= NOISE_RECT_AREA_MAX
    except: return False

def is_noise_polygon(el):
    nums = [float(x) for x in re.findall(r'-?\d*\.?\d+', el.get('points', ''))]
    if len(nums) < 4: return True
    xs = nums[0::2]; ys = nums[1::2]
    return max(max(xs)-min(xs), max(ys)-min(ys)) <= NOISE_POLY_DIAG_MAX

def is_noise_path(el):
    bb = bbox_of(path_points(el.get('d', '')))
    if not bb: return True
    return max(bb[1]-bb[0], bb[3]-bb[2]) <= NOISE_PATH_BBOX_MAX

def is_line_path(el):
    pts = path_points(el.get('d', ''))
    s, length = straightness(pts)
    return (length >= LINE_MIN_LENGTH and s <= LINE_STRAIGHTNESS), s, length


# ---------- main passes ----------
def iter_with_parent(root):
    parent = {c: p for p in root.iter() for c in p}
    for el in list(root.iter()):
        if el in parent:
            yield el, parent[el]

def do_release(root):
    n_comp = n_new = 0
    parent = {c: p for p in root.iter() for c in p}
    for path in list(root.iter(TAG_PATH)):
        d = path.get('d', '')
        if subpath_count(d) <= 1: continue
        subs = split_subpaths(d)
        if len(subs) <= 1: continue
        n_comp += 1; n_new += len(subs)
        par = parent[path]; idx = list(par).index(path); par.remove(path)
        for k, sub in enumerate(subs):
            np = ET.Element(TAG_PATH)
            for a, val in path.attrib.items(): np.set(a, val)
            np.set('d', sub)
            par.insert(idx+k, np)
    return n_comp, n_new

def collect_candidates(root, rule):
    """Return list of (element, parent, label) candidates for the given rule."""
    parent = {c: p for p in root.iter() for c in p}
    out = []
    if rule == 'noise':
        for el in root.iter(TAG_CIRCLE):
            if is_noise_circle(el): out.append((el, parent[el], 'circle'))
        for el in root.iter(TAG_RECT):
            if is_noise_rect(el): out.append((el, parent[el], 'rect'))
        for el in root.iter(TAG_POLYGON):
            if is_noise_polygon(el): out.append((el, parent[el], 'poly'))
        for el in root.iter(TAG_PATH):
            if is_noise_path(el): out.append((el, parent[el], 'path'))
    elif rule == 'lines':
        for el in root.iter(TAG_PATH):
            ok, s, length = is_line_path(el)
            if ok: out.append((el, parent[el], f'line s={s:.3f} L={length:.0f}'))
    return out


# ---------- highlight (verification, non-destructive) ----------
def highlight(svg_path, rule):
    ET.register_namespace('', SVG_NS)
    tree = ET.parse(svg_path); root = tree.getroot()
    if rule in ('lines',):
        do_release(root)  # release first so candidate lines are isolated
    cands = collect_candidates(root, rule)
    for el, _, _ in cands:
        el.set('fill', '#ff0000'); el.set('stroke', '#ff0000'); el.set('stroke-width', '6')
        if 'class' in el.attrib: del el.attrib['class']
    stem, ext = os.path.splitext(svg_path)
    out = f"{stem}_hl-{rule}{ext}"
    tree.write(out, xml_declaration=True, encoding='unicode')
    print(f"  highlighted {len(cands)} '{rule}' candidates -> {out}")
    return out


# ---------- clean ----------
def clean(svg_path, stages, dry_run=False):
    ET.register_namespace('', SVG_NS)
    tree = ET.parse(svg_path); root = tree.getroot()

    if 'A' in stages:
        nc, nn = do_release(root)
        print(f"  [A] released {nc} compound paths -> {nn} individual paths")

    removed = {'noise': 0, 'lines': 0}
    if 'B' in stages:
        cands = collect_candidates(root, 'noise')
        removed['noise'] = len(cands)
        from collections import Counter
        by = Counter(l.split()[0] for _, _, l in cands)
        print(f"  [B] noise candidates: {len(cands)}  {dict(by)}")
        if not dry_run:
            for el, par, _ in cands:
                par.remove(el)
    if 'C' in stages:
        cands = collect_candidates(root, 'lines')
        removed['lines'] = len(cands)
        print(f"  [C] annotation-line candidates: {len(cands)}")
        for _, _, l in cands: print(f"        {l}")
        if not dry_run:
            for el, par, _ in cands:
                par.remove(el)

    if dry_run:
        print("  [dry-run] no file written")
        return
    stem, ext = os.path.splitext(svg_path)
    out = f"{stem}_clean{ext}"
    tree.write(out, xml_declaration=True, encoding='unicode')
    total = len(root.findall(f".//{TAG_PATH}"))
    print(f"  -> {out}  ({total} paths remaining)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--highlight', choices=['noise', 'lines'])
    ap.add_argument('--stages', default='A,B,C', help='comma list of A,B,C')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    if not os.path.exists(args.src):
        print(f"ERROR: not found: {args.src}", file=sys.stderr); sys.exit(1)
    print(os.path.basename(args.src))
    if args.highlight:
        highlight(args.src, args.highlight)
    else:
        stages = {s.strip().upper() for s in args.stages.split(',')}
        clean(args.src, stages, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
