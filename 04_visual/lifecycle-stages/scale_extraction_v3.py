#!/usr/bin/env python3
"""
Scale ring extraction v3:
- Frangi ridge filter (replaces Canny) → single arc per circulus, no double-edge
- Scale body mask (Otsu + morphological closing) → background noise removed
- Two-pass inpainting: large radius for Focus region, small radius for thin annotations
- Small connected-component removal (< 40px²)
"""

import cv2
import numpy as np
import subprocess, os
from skimage.filters import frangi

DIR    = "/Users/iorikawano/Documents/anthropology-of-japanese-food/04_visual/lifecycle-stages"
INPUT  = f"{DIR}/scale_chum-kz0503f034-annotated_ADFG_PD.jpg"
OUT_BASE = f"{DIR}/scale_chum-kz0503f034-ring-lines-v3_ADFG_PD"
OUT_PBM  = OUT_BASE + ".pbm"
OUT_SVG  = OUT_BASE + ".svg"
OUT_PNG  = OUT_BASE + ".png"
DBG_DIR  = f"{DIR}/dbg_v3"
os.makedirs(DBG_DIR, exist_ok=True)

img = cv2.imread(INPUT, cv2.IMREAD_GRAYSCALE)
H, W = img.shape  # 921 × 997

# ── Step 1a: Large-radius inpainting for the Focus/leader region first ─────
# This region (≈180×150px) needs radius=80 to bridge convincingly.
focus_mask = np.zeros((H, W), dtype=np.uint8)
focus_rects_large = [
    (460, 600, 638, 755),   # Focus label + leader line (large gap)
    (258, 548, 368, 635),   # Globular reticulation box
    (295, 630, 562, 820),   # Globular reticulation text + arrow
]
for x1, y1, x2, y2 in focus_rects_large:
    focus_mask[y1:y2, x1:x2] = 255

inpainted_pass1 = cv2.inpaint(img, focus_mask, inpaintRadius=80, flags=cv2.INPAINT_NS)
cv2.imwrite(f"{DBG_DIR}/01_inpaint_pass1_large.png", inpainted_pass1)

# ── Step 1b: Small-radius inpainting for thin annotations ─────────────────
thin_mask = np.zeros((H, W), dtype=np.uint8)
thin_rects = [
    (494, 0,   512, 668),   # vertical zone-boundary line
    (511, 0,   545,  30),   # tick marks
    (511, 75,  543, 108),
    (511, 222, 540, 252),
    (511, 368, 540, 398),
    (511, 560, 538, 595),
    (590,  85, 636, 131),   # "3" label
    (425, 200, 471, 248),   # "2" label
    (545, 370, 616, 430),   # "1" label
    (775, 862, 993, 917),   # scale bar
]
for x1, y1, x2, y2 in thin_rects:
    thin_mask[y1:y2, x1:x2] = 255

inpainted = cv2.inpaint(inpainted_pass1, thin_mask, inpaintRadius=20, flags=cv2.INPAINT_NS)
cv2.imwrite(f"{DBG_DIR}/02_inpaint_pass2_thin.png", inpainted)

# ── Step 2: Build scale-body mask ─────────────────────────────────────────
# Otsu threshold → largest connected component → morphological closing
_, body_bin = cv2.threshold(inpainted, 0, 255, cv2.THRESH_OTSU)
# The scale body is brighter than the black border; invert if needed
# (scale body should be white/gray, border is black)
if body_bin[H//2, W//2] == 0:  # if center is masked, invert
    body_bin = cv2.bitwise_not(body_bin)

k_body = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (40, 40))
body_closed = cv2.morphologyEx(body_bin, cv2.MORPH_CLOSE, k_body, iterations=3)

n_cc, labels_cc, stats_cc, _ = cv2.connectedComponentsWithStats(body_closed)
largest_idx = 1 + np.argmax(stats_cc[1:, cv2.CC_STAT_AREA])
body_mask = (labels_cc == largest_idx).astype(np.uint8) * 255

# Erode slightly so the mask is strictly inside the scale boundary
k_erode = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
body_mask = cv2.erode(body_mask, k_erode, iterations=2)
cv2.imwrite(f"{DBG_DIR}/03_body_mask.png", body_mask)

# ── Step 3: CLAHE contrast enhancement ────────────────────────────────────
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
enhanced = clahe.apply(inpainted)
cv2.imwrite(f"{DBG_DIR}/04_clahe.png", enhanced)

# ── Step 4: Frangi ridge filter ───────────────────────────────────────────
# Frangi detects bright curvilinear ridges → single arc per circulus.
# black_ridges=False → light circuli on darker background
# sigmas: tune to ring width (1–4px range covers fine circuli and annuli)
enhanced_f = enhanced.astype(np.float64) / 255.0
ridges = frangi(
    enhanced_f,
    sigmas=range(1, 5),      # 1,2,3,4 pixel width support
    black_ridges=False,
    beta=0.5,                # shape sensitivity (0.5 = standard)
    gamma=15,                # background suppression (lower = more sensitive)
)

# Normalize and threshold
ridges_norm = (ridges / (ridges.max() + 1e-9) * 255).astype(np.uint8)
cv2.imwrite(f"{DBG_DIR}/05_frangi_raw.png", ridges_norm)

# Adaptive threshold to binarize ridge response
# Use Otsu on the non-zero ridge pixels to find a natural cutoff
nonzero = ridges_norm[ridges_norm > 0]
if len(nonzero) > 0:
    otsu_val, _ = cv2.threshold(nonzero.reshape(-1, 1), 0, 255,
                                cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    ridge_thresh = max(int(otsu_val * 0.4), 8)  # use 40% of Otsu for sensitivity
else:
    ridge_thresh = 20
ridge_bin = (ridges_norm >= ridge_thresh).astype(np.uint8) * 255
cv2.imwrite(f"{DBG_DIR}/06_frangi_bin.png", ridge_bin)

# ── Step 5: Apply body mask ────────────────────────────────────────────────
ridge_masked = cv2.bitwise_and(ridge_bin, body_mask)

# ── Step 6: Remove small connected components (noise dots / short dashes) ──
min_area = 40  # px²
n_cc2, labels_cc2, stats_cc2, _ = cv2.connectedComponentsWithStats(ridge_masked)
clean = np.zeros_like(ridge_masked)
for i in range(1, n_cc2):
    if stats_cc2[i, cv2.CC_STAT_AREA] >= min_area:
        clean[labels_cc2 == i] = 255
ridge_clean = clean
cv2.imwrite(f"{DBG_DIR}/07_cleaned.png", ridge_clean)

# ── Step 7: Light morphological thinning to single-pixel-ish arcs ─────────
k_thin = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
ridge_clean = cv2.morphologyEx(ridge_clean, cv2.MORPH_OPEN, k_thin)

# ── Save white-background preview PNG ─────────────────────────────────────
preview = np.full((H, W), 255, dtype=np.uint8)
preview[ridge_clean > 128] = 0
cv2.imwrite(OUT_PNG, preview)
print(f"Preview PNG: {OUT_PNG}")

# ── Step 8: PBM → potrace → SVG ───────────────────────────────────────────
inverted = cv2.bitwise_not(ridge_clean)
rows, cols = inverted.shape
with open(OUT_PBM, 'wb') as f:
    f.write(f"P4\n{cols} {rows}\n".encode())
    pad_cols = (cols + 7) // 8 * 8
    padded = np.zeros((rows, pad_cols), dtype=np.uint8)
    padded[:, :cols] = (inverted < 128).astype(np.uint8)
    for row in padded:
        f.write(np.packbits(row).tobytes())

result = subprocess.run([
    "potrace", OUT_PBM, "-s", "-o", OUT_SVG,
    "-t", "5",      # suppress blobs < 5px²
    "-a", "1.0",
    "-O", "0.2",
    "-C", "#000000",
    "-W", f"{W}pt", "-H", f"{H}pt",
], capture_output=True, text=True)

if result.returncode != 0:
    print("potrace error:", result.stderr)
else:
    size_kb = os.path.getsize(OUT_SVG) / 1024
    path_count = open(OUT_SVG).read().count('<path')
    print(f"SVG: {OUT_SVG}  ({size_kb:.0f} KB, {path_count} paths)")
    print(f"Debug frames: {DBG_DIR}/")
