#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rd_engine.py — 汎用 反応拡散(Turing)エンジン (研究級)

近藤滋の枠組み(魚皮膚模様 = 局所活性化・長距離抑制 LALI = Turing 系)を、
活性化因子-抑制因子 (activator a, inhibitor h) の2変数反応拡散で実装する。
主動力学は Gierer–Meinhardt(1972, 飽和項付き)。kinetics は差替可能。

特徴(研究級):
  - 無流束(Neumann)境界 + 任意マスク領域(生物シルエット内のみで計算・体内に模様を閉込め)
  - 異方性拡散(Dx, Dy を独立指定 → 縞の向きを制御)
  - CFL 安全な陽的 Euler(dt を拡散から自動上限)
  - kinetics はプラガブル(gierer_meinhardt / schnakenberg / gray_scott)
数式・引用は RD_MODEL.md。

参考: Turing 1952; Gierer & Meinhardt 1972; Kondo & Asai 1995 (Nature);
      Kondo 2009/2010 "live Turing wave" reviews.
"""
import numpy as np

# ============================================================
# kinetics (reaction terms)  f = (da/dt, dh/dt) without diffusion
# 各 kinetics は params dict を受け、(fa, fh) と steady-state 推定を提供
# ============================================================

def gierer_meinhardt(a, h, p):
    """飽和 Gierer–Meinhardt:
      da/dt = rho * a^2 / (h (1 + kappa a^2)) - mu_a a + a0
      dh/dt = rho_h a^2 - mu_h h
    """
    rho = p["rho"]; kappa = p.get("kappa", 0.0); mu_a = p["mu_a"]
    a0 = p.get("a0", 0.0); rho_h = p.get("rho_h", rho); mu_h = p["mu_h"]
    hc = np.maximum(h, 1e-9)
    fa = rho * a * a / (hc * (1.0 + kappa * a * a)) - mu_a * a + a0
    fh = rho_h * a * a - mu_h * h
    return fa, fh


def schnakenberg(a, h, p):
    """Schnakenberg: da/dt = c1 - c2 a + c3 a^2 h ; dh/dt = c4 - c3 a^2 h"""
    c1, c2, c3, c4 = p["c1"], p["c2"], p["c3"], p["c4"]
    aah = c3 * a * a * h
    return (c1 - c2 * a + aah, c4 - aah)


def gray_scott(a, h, p):
    """Gray-Scott(参考・既存互換): u=a, v=h
      da/dt = -a h^2 + F(1-a) ; dh/dt = a h^2 - (F+k) h"""
    F, k = p["F"], p["k"]
    ahh = a * h * h
    return (-ahh + F * (1 - a), ahh - (F + k) * h)


KINETICS = {"gm": gierer_meinhardt, "schnakenberg": schnakenberg, "gray_scott": gray_scott}


# ============================================================
# homogeneous steady state (numeric root find of reaction = 0)
# ============================================================

def steady_state(kin, p, guess=None):
    """同次(非自明)定常解 (a*, h*)。
    GM は解析解を初期値にし、反応のみの relaxation で安定SSへ収束(正値保存・自明解(0,0)回避)。"""
    f = KINETICS[kin]
    if guess is None:
        if kin == "gm":
            rho = p["rho"]; mu_a = p["mu_a"]; rho_h = p.get("rho_h", rho); mu_h = p["mu_h"]
            a = rho * mu_h / (mu_a * rho_h)            # 解析解(kappa=0,a0=0)
            h = rho_h * a * a / mu_h
            guess = (max(a, 1e-3), max(h, 1e-3))
        elif kin == "gray_scott":
            guess = (0.5, 0.25)
        else:
            guess = (1.0, 1.0)
    a = np.array([float(guess[0])]); h = np.array([float(guess[1])])
    dt = 0.01
    for _ in range(200000):
        fa, fh = f(a, h, p)
        if abs(float(fa[0])) + abs(float(fh[0])) < 1e-11:
            break
        a = np.maximum(a + dt * fa, 1e-9); h = np.maximum(h + dt * fh, 1e-9)
    return float(a[0]), float(h[0])


def jacobian(kin, p, a_s, h_s):
    """同次定常解での反応 Jacobian(数値)。"""
    f = KINETICS[kin]; e = 1e-6
    fa0, fh0 = f(np.array([a_s]), np.array([h_s]), p)
    fa0, fh0 = float(fa0[0]), float(fh0[0])
    fa_a = (f(np.array([a_s + e]), np.array([h_s]), p)[0][0] - fa0) / e
    fa_h = (f(np.array([a_s]), np.array([h_s + e]), p)[0][0] - fa0) / e
    fh_a = (f(np.array([a_s + e]), np.array([h_s]), p)[1][0] - fh0) / e
    fh_h = (f(np.array([a_s]), np.array([h_s + e]), p)[1][0] - fh0) / e
    return np.array([[fa_a, fa_h], [fh_a, fh_h]])


# ============================================================
# masked, anisotropic, no-flux Laplacian
# ============================================================

def _masked_aniso_lap(Z, mask, Dx, Dy):
    """マスク内のみ・無流束(Neumann)・異方(Dx,Dy)ラプラシアン。
    マスク外の隣接はフラックス0(=体内に閉込め)。grid端はマスクFalseで安全。"""
    up = np.roll(Z, -1, 0); dn = np.roll(Z, 1, 0)
    lf = np.roll(Z, -1, 1); rt = np.roll(Z, 1, 1)
    mu = np.roll(mask, -1, 0); md = np.roll(mask, 1, 0)
    ml = np.roll(mask, -1, 1); mr = np.roll(mask, 1, 1)
    cu = np.where(mu, up - Z, 0.0); cd = np.where(md, dn - Z, 0.0)
    cl = np.where(ml, lf - Z, 0.0); cr = np.where(mr, rt - Z, 0.0)
    lap = Dy * (cu + cd) + Dx * (cl + cr)
    lap[~mask] = 0.0
    return lap


def cfl_dt(Dx_a, Dy_a, Dx_h, Dy_h, margin=0.25):
    """陽的 Euler の CFL 安全 dt(dx=1)。"""
    Dmax = max(Dx_a, Dy_a, Dx_h, Dy_h)
    return margin / (4.0 * Dmax)


# ============================================================
# simulate
# ============================================================

def simulate(mask, kin, p, D, steps=20000, dt=None, seed=0,
             noise=0.01, record_every=0):
    """
    mask: (H,W) bool — 計算領域(生物シルエット)。境界 False を確保しておくこと。
    kin : "gm"/"schnakenberg"/"gray_scott"
    p   : kinetics パラメータ dict
    D   : dict(Dx_a,Dy_a,Dx_h,Dy_h) 異方拡散係数
    戻り: a(活性化因子場, パターン), h, frames(record_every>0時)
    """
    H, W = mask.shape
    rng = np.random.default_rng(20260618 + seed)
    Dx_a, Dy_a = D["Dx_a"], D["Dy_a"]; Dx_h, Dy_h = D["Dx_h"], D["Dy_h"]
    if dt is None:
        dt = cfl_dt(Dx_a, Dy_a, Dx_h, Dy_h)
    a_s, h_s = steady_state(kin, p)
    a = np.full((H, W), a_s, float); h = np.full((H, W), h_s, float)
    a[mask] += noise * a_s * rng.standard_normal(int(mask.sum()))
    a[~mask] = a_s; h[~mask] = h_s
    f = KINETICS[kin]
    frames = []
    for it in range(steps):
        la = _masked_aniso_lap(a, mask, Dx_a, Dy_a)
        lh = _masked_aniso_lap(h, mask, Dx_h, Dy_h)
        fa, fh = f(a, h, p)
        a = a + dt * (la + np.where(mask, fa, 0.0))
        h = h + dt * (lh + np.where(mask, fh, 0.0))
        h = np.maximum(h, 1e-9); a = np.maximum(a, 0.0)
        a[~mask] = a_s; h[~mask] = h_s
        if record_every and it % record_every == 0:
            frames.append(a.copy())
    return a, h, frames


def normalize(a, mask):
    """マスク内で 0..1 正規化(パターンの濃淡)。"""
    v = a[mask]
    lo, hi = np.percentile(v, 1), np.percentile(v, 99)
    out = np.clip((a - lo) / (hi - lo + 1e-9), 0, 1)
    out[~mask] = 0
    return out
