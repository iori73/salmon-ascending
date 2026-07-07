#!/usr/bin/env python3
"""
Scale ring extraction v3.1:
- Body mask from ORIGINAL image (not inpainted) → fixes lower-left rectangle hole
- Large annotation areas: explicitly blanked AFTER Frangi (not inpainted)
  → no false-flat regions fed into Frangi
- Thin annotations (vertical line, ticks, labels): inpaint before Frangi
- Wider vertical-line mask (x=490-516) to suppress seam artifact
"""

import cv2
import numpy as np
import subprocess, os
from skimage.filters import frangi

DIR      = "/Users/iorikawano/Documents/anthropology-of-japanese-food/04_visual/lifecycle-stages"
INPUT    = f"{DIR}/scale_chum-kz0503f034-annotated_ADFG_PD.jpg"
OUT_BASE = f"{DIR}/scale_chum-kz0503f034-ring-lines-v3_1_ADFG_PD"
OUT_PBM  = OUT_BASE + ".pbm"
OUT_SVG  = OUT_BASE + ".svg"
OUT_PNG  = OUT_BASE + ".png"
DBG_DIR  = f"{DIR}/dbg_v3_1"
os.makedirs(DBG_DIR, exist_ok=True)

img = cv2.imread(INPUT, cv2.IMREAD_GRAYSCALE)
H, W = img.shape  # 921 × 997

# ── Step 1: Build body mask from ORIGINAL (unmodified) image ──────────────
# Using original avoids flat-inpaint patches being excluded.
_, body_bin = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU)
if body_bin[H//2, W//2] == 0:
    body_bin = cv2.bitwise_not(body_bin)

k_body = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (40, 40))
body_closed = cv2.morphologyEx(body_bin, cv2.MORPH_CLOSE, k_body, iterations=3)

n_cc, labels_cc, stats_cc, _ = cv2.connectedComponentsWithStats(body_closed)
largest_idx = 1 + np.argmax(stats_cc[1:, cv2.CC_STAT_AREA])
body_mask = (labels_cc == largest_idx).astype(np.uint8) * 255

# Erode inward so mask is strictly inside the scale boundary
k_erode = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
body_mask = cv2.erode(body_mask, k_erode, iterations=2)
cv2.imwrite(f"{DBG_DIR}/01_body_mask.png", body_mask)

# ── Step 2: Inpaint THIN annotations only ────────────────────────────────
# Large regions (Focus, Globular reticulation) are NOT inpainted here;
# they will be explicitly blanked after Frangi.
thin_mask = np.zeros((H, W), dtype=np.uint8)
thin_rects = [
    # Vertical zone-boundary line (widened ±4px vs v3 to suppress seam)
    (490, 0,   516, 668),
    # Tick marks
    (515, 0,   548,  30),
    (515, 75,  546, 108),
    (515, 222, 544, 252),
    (515, 368, 543, 398),
    (515, 560, 541, 595),
    # Number labels "3", "2", "1" (slightly wider boxes)
    (586,  82, 640, 134),
    (421, 197, 475, 251),
    (541, 367, 620, 433),
    # Scale bar
    (775, 862, 997, 921),
    # Hard left dark strip
    (0, 0, 58, 921),
]
for x1, y1, x2, y2 in thin_rects:
    thin_mask[y1:y2, x1:x2] = 255

inpainted = cv2.inpaint(img, thin_mask, inpaintRadius=22, flags=cv2.INPAINT_NS)
cv2.imwrite(f"{DBG_DIR}/02_inpainted_thin.png", inpainted)

# ── Step 3: CLAHE contrast enhancement ────────────────────────────────────
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
enhanced = clahe.apply(inpainted)
cv2.imwrite(f"{DBG_DIR}/03_clahe.png", enhanced)

# ── Step 4: Frangi ridge filter ───────────────────────────────────────────
enhanced_f = enhanced.astype(np.float64) / 255.0
ridges = frangi(
    enhanced_f,
    sigmas=range(1, 5),
    black_ridges=False,
    beta=0.5,
    gamma=15,
)

ridges_norm = (ridges / (ridges.max() + 1e-9) * 255).astype(np.uint8)
cv2.imwrite(f"{DBG_DIR}/04_frangi_raw.png", ridges_norm)

# Adaptive threshold: 40% of Otsu threshold on non-zero pixels
nonzero = ridges_norm[ridges_norm > 0]
ridge_thresh = max(int(cv2.threshold(
    nonzero.reshape(-1, 1), 0, 255,
    cv2.THRESH_BINARY + cv2.THRESH_OTSU)[0] * 0.4), 8)
ridge_bin = (ridges_norm >= ridge_thresh).astype(np.uint8) * 255
cv2.imwrite(f"{DBG_DIR}/05_frangi_bin.png", ridge_bin)

# ── Step 5: Apply body mask ───────────────────────────────────────────────
ridge_masked = cv2.bitwise_and(ridge_bin, body_mask)

# ── Step 6: Blank large annotation areas AFTER Frangi ────────────────────
# These regions can't be reconstructed; show as intentional white space.
blank_rects = [
    (460, 595, 642, 758),   # Focus label + leader
    (252, 543, 372, 638),   # Globular reticulation box
    (290, 628, 566, 824),   # Globular reticulation text + arrow
]
for x1, y1, x2, y2 in blank_rects:
    ridge_masked[y1:y2, x1:x2] = 0

# ── Step 7: Remove small connected components ─────────────────────────────
n_cc2, labels_cc2, stats_cc2, _ = cv2.connectedComponentsWithStats(ridge_masked)
clean = np.zeros_like(ridge_masked)
for i in range(1, n_cc2):
    if stats_cc2[i, cv2.CC_STAT_AREA] >= 40:
        clean[labels_cc2 == i] = 255
ridge_clean = clean

# Light morphological opening to thin any merged blobs
k_thin = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
ridge_clean = cv2.morphologyEx(ridge_clean, cv2.MORPH_OPEN, k_thin)
cv2.imwrite(f"{DBG_DIR}/06_final_edges.png", ridge_clean)

# ── Save preview PNG (white background) ───────────────────────────────────
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
    "-t", "5",
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
    print(f"Debug: {DBG_DIR}/")
