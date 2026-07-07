#!/usr/bin/env python3
"""
Improved scale line extraction v2:
- Inpainting (radius=20) to fill annotation gaps with reconstructed ring texture
- Gaussian blur sigma=3 to represent annuli as clean arc lines (not black blobs)
- Narrow annotation masks (precise coordinates) for better ring preservation
"""

import cv2
import numpy as np
import subprocess, os

INPUT   = "/Users/iorikawano/Downloads/f1_chum_kz0503f034_labelled.jpg"
OUT_PBM = "/Users/iorikawano/Downloads/scale_lines_v2.pbm"
OUT_SVG = "/Users/iorikawano/Downloads/scale_lines_v2.svg"

img = cv2.imread(INPUT, cv2.IMREAD_GRAYSCALE)
H, W = img.shape  # 921 × 997

# ── Step 1: Inpainting mask — precise annotation positions only ────────────
# Narrower than before to preserve maximum ring data near annotation edges
inpaint_rects = [
    # Vertical zone-boundary line (x=498-508, confirmed)
    (494, 0,    512, 668),
    # Tick mark right-extensions at zone boundaries
    (511, 0,    545, 30),
    (511, 75,   543, 108),
    (511, 222,  540, 252),
    (511, 368,  540, 398),
    (511, 560,  538, 595),
    # Zone "3" label box (594,89→632,127)
    (590, 85,   636, 131),
    # Zone "2" label box (429,205→467,244)
    (425, 200,  471, 248),
    # Zone "1" label box
    (545, 370,  616, 430),
    # "Focus" label + leader line
    (460, 600,  638, 750),
    # Globular reticulation rectangle
    (258, 548,  368, 630),
    # Arrow + "Globular reticulation" text
    (295, 625,  562, 820),
    # Scale bar
    (775, 862,  993, 917),
]

inpaint_mask = np.zeros((H, W), dtype=np.uint8)
for x1, y1, x2, y2 in inpaint_rects:
    inpaint_mask[y1:y2, x1:x2] = 255

# Large-radius inpainting reconstructs ring texture across gaps
# NS (Navier-Stokes) often gives smoother texture reconstruction than TELEA
inpainted = cv2.inpaint(img, inpaint_mask, inpaintRadius=20, flags=cv2.INPAINT_NS)
cv2.imwrite("/Users/iorikawano/Downloads/dbg_v2_inpainted.png", inpainted)

# ── Step 2: Edge detection with sigma=3 (annulus-safe) ────────────────────
clahe    = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
enhanced = clahe.apply(inpainted)
blurred  = cv2.GaussianBlur(enhanced, (0, 0), 3.0)  # sigma=3: annuli → clean arcs
edges    = cv2.Canny(blurred, 20, 60)

# ── Step 3: Erase only non-inpainted artifacts ─────────────────────────────
# The inpainted areas now have valid reconstructed ring edges — DO NOT erase them.
# Only erase: (a) a narrow boundary halo around inpaint edges (artifacts),
#             (b) areas not covered by inpainting (left strip, corners).

# Narrow boundary halo: erode inpaint mask to get interior, subtract → only boundary ring
k_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
inpaint_interior = cv2.erode(inpaint_mask, k_small)
inpaint_boundary = cv2.subtract(inpaint_mask, inpaint_interior)
# Expand boundary outward by 5px to catch artifacts
k_boundary = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
boundary_erase = cv2.dilate(inpaint_boundary, k_boundary)

# Non-inpainted artifacts to fully erase
hard_erase_rects = [
    (0,   0,   55,  921),   # left dark strip
    (0,   892, 220, 921),   # bottom-left corner
    (780, 886, 997, 921),   # bottom-right corner
]
hard_erase_mask = np.zeros((H, W), dtype=np.uint8)
for x1, y1, x2, y2 in hard_erase_rects:
    hard_erase_mask[y1:y2, x1:x2] = 255

full_erase = cv2.bitwise_or(boundary_erase, hard_erase_mask)
edges = cv2.bitwise_and(edges, cv2.bitwise_not(full_erase))

# Light morphological cleanup
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
edges = cv2.dilate(edges, k, iterations=1)
edges = cv2.erode(edges,  k, iterations=1)

# ── Save previews ──────────────────────────────────────────────────────────
preview = np.full((H, W), 255, dtype=np.uint8)
preview[edges > 128] = 0
cv2.imwrite("/Users/iorikawano/Downloads/scale_preview_v2.png", preview)

# ── Step 4: PBM → potrace → SVG ───────────────────────────────────────────
inverted = cv2.bitwise_not(edges)
rows, cols = inverted.shape
with open(OUT_PBM, 'wb') as f:
    f.write(f"P4\n{cols} {rows}\n".encode())
    pad_cols = (cols + 7) // 8 * 8
    padded   = np.zeros((rows, pad_cols), dtype=np.uint8)
    padded[:, :cols] = (inverted < 128).astype(np.uint8)
    for row in padded:
        f.write(np.packbits(row).tobytes())

result = subprocess.run([
    "potrace", OUT_PBM, "-s", "-o", OUT_SVG,
    "-t", "3",       # suppress tiny blobs < 3px²
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
    print(f"✓ {OUT_SVG}  ({size_kb:.0f} KB, {path_count} paths)")
    print(f"  Preview:   /Users/iorikawano/Downloads/scale_preview_v2.png")
    print(f"  Inpainted: /Users/iorikawano/Downloads/dbg_v2_inpainted.png")
