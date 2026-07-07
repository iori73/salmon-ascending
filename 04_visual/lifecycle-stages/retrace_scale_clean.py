#!/usr/bin/env python3
"""
retrace_scale_clean.py

Re-trace the ADFG chum-salmon scale photo into a CLEAN line-free vector.

Why re-trace instead of editing the existing SVG:
  The central measurement line / focus pointer / labels were fused into one giant
  4093-point path together with the left-half scale ridges in the Illustrator trace,
  so they could not be deleted as elements. Removing the annotation from the *raster*
  (inpaint) and re-tracing produces a clean result in one pass — and potrace's
  turdsize also removes the もや (speckle) at the same time.

Pipeline:
  1. Build annotation mask from the labelled photo:
       - dark ink (<35) connected components that are large/elongated  (line, arrows, box outlines, text)
       - white label boxes / text backgrounds (1/2/3, Focus, Globular reticulation)
       - explicit "1 mm" scale-bar region (bottom-right)
  2. Inpaint those regions on the grayscale (Navier-Stokes, r=5) → ridges reconstructed across the line
  3. Threshold 128 (matches the original Illustrator "Threshold 128" aesthetic)
  4. Isolate the scale body via local-variance (texture) region, whiten the flat dark
     photo corner/edges, smooth the boundary
  5. potrace (-t 16 despeckle, -a 1.2, --tight) → clean SVG

Input : f1_chum_kz0503f034_labelled.jpg (ADFG)
Output: scale_chum_kz0503f034_clean-retrace.svg

Deps: opencv-python, numpy, potrace, ImageMagick
"""
import os, subprocess, sys
import cv2, numpy as np

SRC = sys.argv[1] if len(sys.argv) > 1 else "/tmp/chum_labelled_original.jpg"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/tmp/scale_clean_retrace.svg"
TMP = "/tmp/_retrace_bw.png"


def build_mask(img):
    H, W = img.shape
    mask = np.zeros((H, W), "uint8")
    # dark ink annotation components
    dark = (img < 35).astype("uint8")
    n, lbl, stats, _ = cv2.connectedComponentsWithStats(dark, 8)
    for i in range(1, n):
        x, y, w, h, a = stats[i]
        if x == 0:           # exclude top-left black photo corner (touches border)
            continue
        if a >= 180 or (h / max(w, 1) >= 3 and h >= 25) or (w / max(h, 1) >= 3 and w >= 25):
            mask[lbl == i] = 255
    # white label boxes / text backgrounds
    white = (img > 235).astype("uint8")
    nw, lw, sw, _ = cv2.connectedComponentsWithStats(white, 8)
    for i in range(1, nw):
        x, y, w, h, a = sw[i]
        if w * h == 0:
            continue
        fill = a / (w * h); ar = w / h
        if x >= 915 and h > 120:     # skip bright scale-edge reflection
            continue
        is_textbg = fill >= 0.7 and 60 <= w <= 260 and 25 <= h <= 60
        is_numbox = fill >= 0.45 and 28 <= w <= 70 and 28 <= h <= 70 and 0.5 <= ar <= 1.8
        if is_textbg or is_numbox:
            mask[y:y+h, x:x+w] = 255
    mask[855:921, 770:995] = 255      # explicit "1 mm" scale bar
    return cv2.dilate(mask, np.ones((5, 5), "uint8"), 1)


def scale_region(inp, T=18):
    """Texture-based scale-body region; flat dark corner/edges excluded."""
    f = inp.astype(np.float32); win = 15
    mean = cv2.boxFilter(f, -1, (win, win))
    std = cv2.sqrt(np.maximum(cv2.boxFilter(f*f, -1, (win, win)) - mean*mean, 0))
    tex = cv2.morphologyEx((std > T).astype("uint8"), cv2.MORPH_CLOSE, np.ones((9, 9), "uint8"))
    n, lbl, stats, _ = cv2.connectedComponentsWithStats(tex, 8)
    big = max(range(1, n), key=lambda i: stats[i, 4])
    region = (lbl == big).astype("uint8")
    region = cv2.morphologyEx(region, cv2.MORPH_CLOSE, np.ones((35, 35), "uint8"))
    ff = region.copy(); h, w = region.shape
    cv2.floodFill(ff, np.zeros((h+2, w+2), "uint8"), (0, 0), 1)
    region[ff == 0] = 1                                  # fill internal holes
    region = (cv2.GaussianBlur(region.astype(np.float32)*255, (31, 31), 0) > 128).astype("uint8")
    return region


def main():
    img = cv2.imread(SRC, cv2.IMREAD_GRAYSCALE)
    if img is None:
        sys.exit(f"cannot read {SRC}")
    mask = build_mask(img)
    inp = cv2.inpaint(img, (mask > 0).astype("uint8"), 5, cv2.INPAINT_NS)
    _, bw = cv2.threshold(inp, 128, 255, cv2.THRESH_BINARY)
    region = scale_region(inp)
    bw[region == 0] = 255                                # whiten background
    cv2.imwrite(TMP, bw)
    subprocess.run(["magick", TMP, "-threshold", "50%", "/tmp/_retrace.pbm"], check=True)
    subprocess.run(["potrace", "-s", "-t", "16", "-a", "1.2", "--tight",
                    "/tmp/_retrace.pbm", "-o", OUT], check=True)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
