#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rd_stability.py — 反応拡散系の線形安定性解析(Turing 解析)＋ 波長検証

Turing 不安定の判定と、最不安定波数 k* / 予測波長 λ_T = 2π/k* を、
同次定常解での反応 Jacobian J と拡散行列 D=diag(Da,Dh) から数値的に求める。
分散関係 σ(k²) = max Re eig(J − k² D)。σ>0 の帯が Turing 不安定帯。

検証: シミュレーション結果の FFT から実測波長を測り、予測 λ_T と照合する
(= 学者が確認できる定量的検証)。

参考: Turing 1952; Murray "Mathematical Biology"; Gierer–Meinhardt 1972。
"""
import os
import numpy as np
import rd_engine as E

_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "validation")
os.makedirs(_OUT, exist_ok=True)


def dispersion(J, Da, Dh, kmax=3.0, n=600):
    """分散関係 σ(k) = max Re eig(J − k² diag(Da,Dh))。kは空間周波数(rad/px)。"""
    ks = np.linspace(1e-4, kmax, n)
    sig = np.empty(n)
    for i, k in enumerate(ks):
        M = J - (k * k) * np.diag([Da, Dh])
        sig[i] = np.max(np.real(np.linalg.eigvals(M)))
    return ks, sig


def turing_analysis(kin, p, Da, Dh, kmax=3.0):
    """Turing 解析。戻り: dict(steady, J, trace, det, turing(bool), k_star, lambda_T, band)。"""
    a_s, h_s = E.steady_state(kin, p)
    J = E.jacobian(kin, p, a_s, h_s)
    tr = J[0, 0] + J[1, 1]; det = J[0, 0] * J[1, 1] - J[0, 1] * J[1, 0]
    ks, sig = dispersion(J, Da, Dh, kmax)
    pos = sig > 0
    turing = bool(pos.any()) and (tr < 0) and (det > 0)
    k_star = float(ks[np.argmax(sig)]) if sig.max() > 0 else float("nan")
    lam = (2 * np.pi / k_star) if k_star == k_star and k_star > 0 else float("nan")
    band = (float(ks[pos].min()), float(ks[pos].max())) if pos.any() else None
    return dict(steady=(a_s, h_s), J=J, trace=tr, det=det, turing=turing,
                k_star=k_star, lambda_T=lam, band=band, ks=ks, sig=sig,
                homo_stable=(tr < 0 and det > 0))


def measure_wavelength(field, mask, axis="x"):
    """パターンの実測支配波長(px)を FFT で。axis='x'=横方向(縦バーの法線)。
    マスク内の最大内接帯で1D信号を作り、detrend→FFTのピーク周波数→波長。"""
    ys, xs = np.where(mask)
    y0, y1 = ys.min(), ys.max(); x0, x1 = xs.min(), xs.max()
    sub = field[y0:y1 + 1, x0:x1 + 1]
    msub = mask[y0:y1 + 1, x0:x1 + 1]
    sub = np.where(msub, sub, np.nan)
    if axis == "x":
        sig = np.nanmean(sub, axis=0)            # 列平均(xに沿う1D)
    else:
        sig = np.nanmean(sub, axis=1)
    sig = sig[~np.isnan(sig)]
    if len(sig) < 8:
        return float("nan")
    sig = sig - sig.mean()
    win = np.hanning(len(sig))
    sp = np.abs(np.fft.rfft(sig * win))
    freqs = np.fft.rfftfreq(len(sig), d=1.0)     # cycles/px
    sp[0] = 0
    kpk = freqs[np.argmax(sp)]
    return (1.0 / kpk) if kpk > 0 else float("nan")


def report(kin, p, Da, Dh, label=""):
    r = turing_analysis(kin, p, Da, Dh)
    print(f"[{label}] kin={kin} steady a*={r['steady'][0]:.4f} h*={r['steady'][1]:.4f}")
    print(f"   trace={r['trace']:.4f} det={r['det']:.4f} homo_stable={r['homo_stable']}")
    print(f"   Turing-unstable={r['turing']}  k*={r['k_star']:.4f}  λ_T={r['lambda_T']:.2f}px  band={r['band']}")
    return r


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # 代表 GM パラメータ(spots/stripes 域) — λ_T が拡散比で決まることを示す
    p = dict(rho=1.0, mu_a=1.0, rho_h=1.0, mu_h=2.0, kappa=0.0, a0=0.0)
    cases = [("GM Da=1 Dh=20", 1.0, 20.0), ("GM Da=1 Dh=40", 1.0, 40.0), ("GM Da=1 Dh=80", 1.0, 80.0)]
    fig, ax = plt.subplots(figsize=(7, 4))
    for lab, Da, Dh in cases:
        r = report(lab, ) if False else turing_analysis("gm", p, Da, Dh, kmax=2.0)
        ax.plot(r["ks"], r["sig"], label=f"{lab}: λ_T={r['lambda_T']:.1f}px")
        report("gm", p, Da, Dh, lab)
    ax.axhline(0, color="k", lw=0.6)
    ax.set_xlabel("wavenumber k (rad/px)"); ax.set_ylabel("growth rate σ(k)")
    ax.set_title("Gierer–Meinhardt dispersion relation (Turing band where σ>0)")
    ax.legend(fontsize=8)
    p = os.path.join(_OUT, "dispersion-gm.png")
    fig.tight_layout(); fig.savefig(p, dpi=120)
    print("saved", p)
