#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rd_validate.py — エンジン検証: 予測 λ_T vs シミュレーション実測波長 + 異方性で縞の向き確認。"""
import os
import numpy as np
from PIL import Image
import rd_engine as E
import rd_stability as S

_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "validation")
os.makedirs(_OUT, exist_ok=True)
p = dict(rho=1.0, mu_a=1.0, rho_h=1.0, mu_h=2.0, kappa=0.0, a0=0.0)


def rect_mask(H, W, pad=4):
    m = np.zeros((H, W), bool); m[pad:H - pad, pad:W - pad] = True; return m


def save(field, mask, path):
    img = (E.normalize(field, mask) * 255).astype(np.uint8)
    Image.fromarray(img).save(path)


def run(label, Da, Dh, D, steps, kmax=2.0, axis="x"):
    r = S.turing_analysis("gm", p, Da, Dh, kmax=kmax)
    H = W = 130
    mask = rect_mask(H, W)
    dt = E.cfl_dt(D["Dx_a"], D["Dy_a"], D["Dx_h"], D["Dy_h"], margin=0.4)
    a, h, _ = E.simulate(mask, "gm", p, D, steps=steps, dt=dt, seed=1, noise=0.02)
    fld = E.normalize(a, mask)
    lam = S.measure_wavelength(fld, mask, axis=axis)
    print(f"[{label}] predicted λ_T={r['lambda_T']:.2f}px  measured λ({axis})={lam:.2f}px  Turing={r['turing']}")
    return fld, mask, r


if __name__ == "__main__":
    # isotropic: spots/labyrinth; predicted vs measured wavelength
    f1, m1, r1 = run("iso Dh=20", 1.0, 20.0, dict(Dx_a=1, Dy_a=1, Dx_h=20, Dy_h=20), steps=45000)
    save(f1, m1, os.path.join(_OUT, "val-iso.png"))
    # anisotropic: high inhibitor diffusion along x -> pattern varies in x -> VERTICAL bars
    f2, m2, r2 = run("aniso vbar", 1.0, 20.0, dict(Dx_a=1, Dy_a=1, Dx_h=60, Dy_h=8), steps=45000, axis="x")
    save(f2, m2, os.path.join(_OUT, "val-aniso-vbar.png"))
    print("saved", _OUT, "(val-iso.png, val-aniso-vbar.png)")
