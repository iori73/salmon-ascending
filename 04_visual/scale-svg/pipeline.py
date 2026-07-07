#!/usr/bin/env python3
"""Salmon scale ring SVG extraction pipeline v1
Goal: clean SVG of concentric ring arcs, no annotations
"""
import cv2, numpy as np, subprocess, os, sys
from scipy.ndimage import gaussian_filter
from skimage.filters import frangi
from skimage.morphology import skeletonize, remove_small_objects, disk
from skimage.measure import label as sk_label, regionprops

WORK = "/Users/iorikawano/Documents/anthropology-of-japanese-food/04_visual/scale-svg"

def dbg(name, img):
    if img.dtype == bool:
        arr = (img * 255).astype(np.uint8)
    elif img.dtype != np.uint8:
        arr = np.clip(img, 0, 255).astype(np.uint8)
    else:
        arr = img
    cv2.imwrite(f"{WORK}/dbg_{name}.png", arr)
    print(f"  [dbg] {name}")

# ─── 1. LOAD ──────────────────────────────────────────────────
img_bgr = cv2.imread(f"{WORK}/source.jpg")
if img_bgr is None:
    sys.exit("ERROR: source.jpg not found")
gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
H, W = gray.shape
print(f"Loaded {W}×{H}")
dbg("01_gray", gray)

# ─── 2. DETECT VERTICAL SEAM ─────────────────────────────────
# Seam = near-black vertical stripe near x=500
# Use middle half of image rows (avoids dark background edges)
mid = gray[H//4 : 3*H//4, 460:540]
col_p10 = np.percentile(mid, 10, axis=0)
seam_local = np.where(col_p10 < 30)[0]
if len(seam_local) >= 4:
    SEAM_L = int(seam_local.min()) + 460 - 3
    SEAM_R = int(seam_local.max()) + 460 + 4
else:
    SEAM_L, SEAM_R = 489, 515
print(f"Seam: x={SEAM_L}–{SEAM_R}  (width={SEAM_R-SEAM_L}px)")

# ─── 3. ANNOTATION MASK ──────────────────────────────────────
ann = np.zeros((H, W), dtype=np.uint8)

# 3a. Vertical seam
ann[:, SEAM_L:SEAM_R] = 255

# 3b. Tick marks (thin dark horizontal lines flanking seam, ≤20px long)
for x0, x1 in [(max(0, SEAM_L-65), SEAM_L), (SEAM_R, min(W, SEAM_R+65))]:
    stripe = gray[:, x0:x1]
    for r in range(H):
        ndark = int((stripe[r] < 40).sum())
        if 2 <= ndark <= 20:
            ann[r, x0:x1] = 255

# 3c. Number label "2" (explicit from problem description)
ann[188:255, 413:486] = 255

# 3d. Detect number labels "1" and "3" as small bright rectangles
roi_top = gray[140:325, :]
_, bright_top = cv2.threshold(roi_top, 215, 255, cv2.THRESH_BINARY)
cnts, _ = cv2.findContours(bright_top, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
label_boxes = []
for cnt in cnts:
    x, y, w, h = cv2.boundingRect(cnt)
    area = w * h
    if 600 < area < 14000 and 0.3 < w/max(h,1) < 3.5:
        abs_y = y + 140
        # Skip if overlaps "2" label
        if not (x < 486 and x+w > 413 and abs_y < 255 and abs_y+h > 188):
            ann[abs_y:abs_y+h, x:x+w] = 255
            label_boxes.append((x, abs_y, x+w, abs_y+h))
            print(f"  Label box: x={x}–{x+w}, y={abs_y}–{abs_y+h}")

# 3e. Focus label (bottom-center, ~180×150px)
ann[710:880, 382:578] = 255

# 3f. Scale bar (bottom-right)
ann[838:921, 838:997] = 255

# 3g. Try to detect "Globular reticulation" label (left/lower half)
roi_l = gray[350:710, 25:350]
_, bright_l = cv2.threshold(roi_l, 215, 255, cv2.THRESH_BINARY)
cnts_l, _ = cv2.findContours(bright_l, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
for cnt in cnts_l:
    x, y, w, h = cv2.boundingRect(cnt)
    if w * h > 4000 and w > 55 and h > 40:
        abs_y = y + 350
        ann[abs_y:abs_y+h, x:x+w] = 255
        print(f"  Globular area: x={x}–{x+w}, y={abs_y}–{abs_y+h}")

ann_d = cv2.dilate(ann, np.ones((5, 5), np.uint8), iterations=1)
dbg("02_ann_mask", ann_d)

# ─── 4. THREE-PASS INPAINTING ────────────────────────────────
# Pass 1: large opaque blobs (Focus, Globular, scale bar) — NS r=80
large = np.zeros((H, W), dtype=np.uint8)
large[710:880, 382:578] = 255
large[838:921, 838:997] = 255
for cnt in cnts_l:
    x, y, w, h = cv2.boundingRect(cnt)
    if w * h > 4000 and w > 55 and h > 40:
        abs_y = y + 350
        large[abs_y:abs_y+h, x:x+w] = 255

ip1 = cv2.inpaint(gray, large, 80, cv2.INPAINT_NS)
dbg("03_ip1_large", ip1)

# Pass 2: thin annotations (seam, ticks, small labels) — TELEA r=25
thin = ann_d.copy()
thin[large > 0] = 0
thin[188:255, 413:486] = 0  # "2" label handled separately
ip2 = cv2.inpaint(ip1, thin, 25, cv2.INPAINT_TELEA)
dbg("04_ip2_thin", ip2)

# Pass 3: "2" label gap (~70px wide) — NS r=50, more propagation
label2 = np.zeros((H, W), dtype=np.uint8)
label2[188:255, 413:486] = 255
ip3 = cv2.inpaint(ip2, label2, 50, cv2.INPAINT_NS)
dbg("05_ip3_label2", ip3)

# ─── 5. CLAHE ────────────────────────────────────────────────
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
enh = clahe.apply(ip3)
dbg("06_clahe", enh)

# ─── 6. BODY MASK ────────────────────────────────────────────
# Try both Otsu variants; keep whichever gives the largest centred region
def make_body_mask(g, invert=False):
    flag = cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU if invert else cv2.THRESH_BINARY + cv2.THRESH_OTSU
    _, bt = cv2.threshold(g, 0, 255, flag)
    lbl = sk_label(bt)
    props = regionprops(lbl)
    if not props:
        return None
    main = max(props, key=lambda p: p.area)
    bm = (lbl == main.label).astype(np.uint8)
    bm = cv2.morphologyEx(bm, cv2.MORPH_CLOSE, disk(10).astype(np.uint8))
    bm = cv2.erode(bm, disk(12).astype(np.uint8))
    return bm

bm = make_body_mask(gray, invert=False)
bm_inv = make_body_mask(gray, invert=True)
# Pick the one that covers more of the image centre
def centre_coverage(bm):
    if bm is None:
        return 0
    cy, cx = H//2, W//2
    return int(bm[cy-50:cy+50, cx-50:cx+50].sum())

bm = bm if centre_coverage(bm) >= centre_coverage(bm_inv) else bm_inv
if bm is None or bm.sum() < H * W * 0.03:
    bm = np.zeros((H, W), dtype=np.uint8)
    bm[30:H-30, 30:W-30] = 1
    print("WARNING: using fallback rectangular body mask")
dbg("07_body_mask", bm * 255)

# ─── 7. FRANGI RIDGE FILTER ──────────────────────────────────
ef = enh.astype(np.float64) / 255.0
ridge = frangi(ef, sigmas=range(1, 5), black_ridges=False, gamma=15)
rmax = ridge.max()
rn = ridge / rmax if rmax > 0 else ridge
r8 = (rn * 255).astype(np.uint8)
otsu_v, _ = cv2.threshold(r8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
thr = max(otsu_v * 0.35, 4) / 255.0
rb = (rn > thr) & bm.astype(bool)
dbg("08_frangi_raw", r8)
dbg("09_frangi_bin", rb)

# ─── 8. CLEAN + SKELETONIZE ──────────────────────────────────
rbc = remove_small_objects(rb, min_size=40)
skel = skeletonize(rbc)
dbg("10_skel", skel)

# ─── 9. SEAM BRIDGING (orientation-field streamlines) ────────
# Compute structure tensor tangent angles from the enhanced image
ef_f = enh.astype(np.float64)
Ix = gaussian_filter(ef_f, 4, order=[0, 1])
Iy = gaussian_filter(ef_f, 4, order=[1, 0])
Ixx = gaussian_filter(Ix * Ix, 4)
Iyy = gaussian_filter(Iy * Iy, 4)
Ixy = gaussian_filter(Ix * Iy, 4)
theta = 0.5 * np.arctan2(2 * Ixy, Ixx - Iyy)

bridge = np.zeros((H, W), dtype=bool)
GAP = SEAM_R - SEAM_L
SEARCH = 10

n_bridge_rows = 0
for row in range(H):
    has_left  = skel[row, max(0, SEAM_L - SEARCH):SEAM_L].any()
    has_right = skel[row, SEAM_R:min(W, SEAM_R + SEARCH)].any()
    if not (has_left and has_right):
        continue
    n_bridge_rows += 1
    a0 = float(theta[row, max(0, SEAM_L - 2)])
    a1 = float(theta[row, min(W - 1, SEAM_R + 2)])
    for step in range(GAP + 1):
        col = SEAM_L + step
        t = step / max(GAP, 1)
        angle = (1 - t) * a0 + t * a1
        dr = int(round(step * np.tan(angle)))
        tr = row + dr
        if 0 <= tr < H:
            bridge[tr, col] = True

print(f"Bridge: {n_bridge_rows} rows connected, {bridge.sum()} pixels")
dbg("11_bridge", bridge)

# ─── 10. ELLIPSE SYNTHESIS FOR "2" VOID ─────────────────────
VX0, VY0, VX1, VY1 = 413, 188, 486, 255
M = 130  # context margin for ellipse fitting

sk_for_fit = (skel | bridge).copy()
sk_for_fit[VY0:VY1, VX0:VX1] = False

ry0, ry1 = max(0, VY0 - M), min(H, VY1 + M)
rx0, rx1 = max(0, VX0 - M), min(W, VX1 + M)
ctx = sk_for_fit[ry0:ry1, rx0:rx1]
ctx_lbl = sk_label(ctx)

void_rgn = np.zeros((H, W), dtype=bool)
void_rgn[VY0:VY1, VX0:VX1] = True
synth = np.zeros((H, W), dtype=bool)
n_ellipses = 0

for cid in range(1, int(ctx_lbl.max()) + 1):
    ys_l, xs_l = np.where(ctx_lbl == cid)
    if len(xs_l) < 20:
        continue
    xs_g = xs_l + rx0
    ys_g = ys_l + ry0
    pts = np.column_stack([xs_g, ys_g]).astype(np.float32)
    try:
        ellipse = cv2.fitEllipse(pts)
    except Exception:
        continue
    cx_e, cy_e = ellipse[0]
    ax_a = ellipse[1][0] / 2
    ax_b = ellipse[1][1] / 2
    if ax_a < 5 or ax_b < 5 or ax_a > W * 0.9 or ax_b > H * 0.9:
        continue
    tmp = np.zeros((H, W), dtype=np.uint8)
    try:
        cv2.ellipse(tmp,
                    (int(round(cx_e)), int(round(cy_e))),
                    (max(1, int(round(ax_a))), max(1, int(round(ax_b)))),
                    ellipse[2], 0, 360, 255, 1)
    except Exception:
        continue
    contrib = (tmp > 0) & void_rgn
    if contrib.any():
        synth |= contrib
        n_ellipses += 1

print(f"Void synthesis: {n_ellipses} ellipses, {synth.sum()} pixels")
dbg("12_synth_void", synth)

# ─── 11. MERGE + FINAL CLEAN ─────────────────────────────────
final = (skel | bridge | synth) & bm.astype(bool)
final = remove_small_objects(final, min_size=20)
dbg("13_final_skel", final)

# Dilate to 3px width so potrace produces visible paths
kern = disk(1).astype(np.uint8)
final_d = cv2.dilate(final.astype(np.uint8), kern) > 0
dbg("14_final_dilated", final_d)

# ─── 12. POTRACE → SVG ───────────────────────────────────────
# potrace: dark pixels = foreground (rings); white = background
bmp_arr = np.where(final_d, 0, 255).astype(np.uint8)
bmp_path = f"{WORK}/final.bmp"
cv2.imwrite(bmp_path, bmp_arr)

svg_path = f"{WORK}/scale_rings.svg"
result = subprocess.run([
    "potrace", "--svg",
    "-o", svg_path,
    "--turdsize", "8",
    "--opttolerance", "0.15",
    "--alphamax", "0.8",
    bmp_path
], capture_output=True, text=True)

if result.returncode == 0:
    sz = os.path.getsize(svg_path)
    print(f"✓ SVG: {svg_path}  ({sz // 1024} KB)")
else:
    print(f"✗ potrace error: {result.stderr}")

print("\nAll debug images saved in:", WORK)
print("Pipeline complete.")
