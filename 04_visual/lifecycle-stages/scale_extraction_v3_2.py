#!/usr/bin/env python3
"""
Scale ring extraction v3.2 — targeted gap filling.

Strategy A-seam  (x=482-524, full height):
  Frangi with gamma=5, threshold=25 % of Otsu.
  More sensitive than v3.1 (gamma=15, 40 %) but still selective.
  Fills the inpainted ring texture that was below the original threshold.

Strategy A-label  (tick marks + number labels):
  Frangi with gamma=3, threshold=10 % of Otsu.
  Very sensitive; only applied to small, well-inpainted rectangles.

Strategy B  ("2" label and Globular void):
  Row-by-row bridge, gap-interior-only fill, boundary condition:
  only fills rows where a ring pixel exists at the gap's left OR right edge.
  Prevents the "solid-column" artifact by filling sparsely at ring crossings.
"""

import cv2
import numpy as np
import subprocess, os
from skimage.filters import frangi

DIR       = "/Users/iorikawano/Documents/anthropology-of-japanese-food/04_visual/lifecycle-stages"
SRC_PNG   = f"{DIR}/scale_chum-kz0503f034-ring-lines-v3_1_ADFG_PD.png"
SRC_GRAY  = f"{DIR}/dbg_v3_1/02_inpainted_thin.png"
OUT_BASE  = f"{DIR}/scale_chum-kz0503f034-ring-lines-v3_2_ADFG_PD"
OUT_PBM   = OUT_BASE + ".pbm"
OUT_SVG   = OUT_BASE + ".svg"
OUT_PNG   = OUT_BASE + ".png"
DBG_DIR   = f"{DIR}/dbg_v3_2"
os.makedirs(DBG_DIR, exist_ok=True)

# ── Load v3.1 binary (lines=255 after invert) ────────────────────────────
edges_bw = cv2.imread(SRC_PNG, cv2.IMREAD_GRAYSCALE)
H, W     = edges_bw.shape
lines    = cv2.bitwise_not(edges_bw)

# ── CLAHE on inpainted grayscale ──────────────────────────────────────────
inpainted  = cv2.imread(SRC_GRAY, cv2.IMREAD_GRAYSCALE)
clahe      = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
enhanced   = clahe.apply(inpainted)
enhanced_f = enhanced.astype(np.float64) / 255.0

# ── One Frangi pass at gamma=3 (intermediate sensitivity) ─────────────────
print("Running Frangi (gamma=3)…")
ridges   = frangi(enhanced_f, sigmas=range(1, 5), black_ridges=False, beta=0.5, gamma=3)
ridges_n = (ridges / (ridges.max() + 1e-9) * 255).astype(np.uint8)
cv2.imwrite(f"{DBG_DIR}/01_frangi_g3.png", ridges_n)

nonzero  = ridges_n[ridges_n > 0].reshape(-1, 1)
otsu_val = float(cv2.threshold(nonzero, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[0])

# Two threshold levels
thresh_seam  = max(int(otsu_val * 0.25), 8)   # seam: more selective
thresh_label = max(int(otsu_val * 0.10), 5)   # labels/ticks: more sensitive
print(f"Otsu={otsu_val:.0f}  thresh_seam={thresh_seam}  thresh_label={thresh_label}")

seam_bin  = (ridges_n >= thresh_seam ).astype(np.uint8) * 255
label_bin = (ridges_n >= thresh_label).astype(np.uint8) * 255

# Remove tiny specks from label_bin
n_cc, lab, stats, _ = cv2.connectedComponentsWithStats(label_bin)
label_bin_clean = np.zeros_like(label_bin)
for i in range(1, n_cc):
    if stats[i, cv2.CC_STAT_AREA] >= 20:
        label_bin_clean[lab == i] = 255
cv2.imwrite(f"{DBG_DIR}/02_label_bin_clean.png", label_bin_clean)

# ── Helper: build rect mask ────────────────────────────────────────────────
def rect_mask(rects, h, w):
    m = np.zeros((h, w), dtype=np.uint8)
    for x1, y1, x2, y2 in rects:
        m[y1:y2, x1:x2] = 255
    return m

# ── Strategy A-seam: Frangi @ 25 % threshold in seam strip ───────────────
seam_rects = [
    (482, 0, 524, 668),   # vertical annotation seam
]
mask_seam = rect_mask(seam_rects, H, W)
fill_seam = cv2.bitwise_and(seam_bin, mask_seam)

# ── Strategy A-label: Frangi @ 10 % threshold in tick/label rects ─────────
label_rects = [
    (508,   0, 555,  40),   # tick top
    (508,  67, 552, 118),   # tick 2
    (508, 214, 550, 262),   # tick 3
    (508, 360, 550, 410),   # tick 4
    (508, 552, 548, 608),   # tick 5
    (578,  74, 648, 142),   # "3" label
    (413, 189, 483, 259),   # "2" label (also in Strategy A now)
    (541, 367, 621, 434),   # "1" label (exclude Focus leader below)
]
mask_label = rect_mask(label_rects, H, W)
fill_label = cv2.bitwise_and(label_bin_clean, mask_label)

# Merge Strategy A into result
result = lines.copy()
result = cv2.bitwise_or(result, fill_seam)
result = cv2.bitwise_or(result, fill_label)
cv2.imwrite(f"{DBG_DIR}/03_after_stratA.png", cv2.bitwise_not(result))

# ── Strategy B: boundary-condition row bridge ──────────────────────────────
# Fills only the gap interior (x1:x2) and only for rows where a ring pixel
# exists at the gap's left edge (x1-1) AND/OR right edge (x2), with a small
# vertical tolerance (±v_tol rows) to handle slightly angled rings.

def bridge_interior(img, rects, v_tol=2):
    out = img.copy()
    for (x1, y1, x2, y2) in rects:
        for y in range(max(0, y1), min(img.shape[0], y2)):
            # Check left boundary: any ring within ±v_tol rows at x1-1
            has_left = False
            if x1 > 0:
                for dy in range(-v_tol, v_tol + 1):
                    yy = y + dy
                    if 0 <= yy < img.shape[0] and out[yy, x1 - 1] > 0:
                        has_left = True
                        break
            # Check right boundary: any ring within ±v_tol rows at x2
            has_right = False
            if x2 < img.shape[1]:
                for dy in range(-v_tol, v_tol + 1):
                    yy = y + dy
                    if 0 <= yy < img.shape[0] and out[yy, x2] > 0:
                        has_right = True
                        break
            if has_left and has_right:
                out[y, x1:x2] = 255
    return out

bridge_rects_B = [
    (413, 189, 483, 230),   # "2" label upper half (Frangi missed this band)
    (244, 535, 380, 648),   # Globular reticulation void
]
result = bridge_interior(result, bridge_rects_B, v_tol=0)

# ── Final: erase known residual text artifacts (Focus/leader area) ────────
# These ghost glyph fragments come from NS inpainting leaving faint text traces
# that gamma=3 Frangi picks up. Known bad rectangles:
artifact_erase = [
    (462, 590, 645, 760),   # Focus label + leader full zone
    (287, 625, 568, 825),   # "Globular reticulation" text zone
]
for x1, y1, x2, y2 in artifact_erase:
    result[y1:y2, x1:x2] = 0
cv2.imwrite(f"{DBG_DIR}/04_after_stratB.png", cv2.bitwise_not(result))

# ── Final cleanup: remove tiny isolated components ────────────────────────
n_cc2, lab2, stats2, _ = cv2.connectedComponentsWithStats(result)
final = np.zeros_like(result)
for i in range(1, n_cc2):
    if stats2[i, cv2.CC_STAT_AREA] >= 30:
        final[lab2 == i] = 255

# ── Save preview ──────────────────────────────────────────────────────────
preview = cv2.bitwise_not(final)
cv2.imwrite(OUT_PNG, preview)
print(f"Preview PNG: {OUT_PNG}")

# ── PBM → potrace → SVG ──────────────────────────────────────────────────
inverted = cv2.bitwise_not(final)
rows, cols = inverted.shape
with open(OUT_PBM, 'wb') as f:
    f.write(f"P4\n{cols} {rows}\n".encode())
    pad_cols = (cols + 7) // 8 * 8
    padded = np.zeros((rows, pad_cols), dtype=np.uint8)
    padded[:, :cols] = (inverted < 128).astype(np.uint8)
    for row in padded:
        f.write(np.packbits(row).tobytes())

proc = subprocess.run([
    "potrace", OUT_PBM, "-s", "-o", OUT_SVG,
    "-t", "5", "-a", "1.0", "-O", "0.2",
    "-C", "#000000",
    "-W", f"{W}pt", "-H", f"{H}pt",
], capture_output=True, text=True)

if proc.returncode != 0:
    print("potrace error:", proc.stderr)
else:
    size_kb    = os.path.getsize(OUT_SVG) / 1024
    path_count = open(OUT_SVG).read().count('<path')
    print(f"SVG: {OUT_SVG}  ({size_kb:.0f} KB, {path_count} paths)")
    print(f"Debug: {DBG_DIR}/")
