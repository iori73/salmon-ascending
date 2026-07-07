# 反応拡散シミュレーションによるシロザケ7段階体模様の生成 — モデル文書

計算（反応拡散＝Turing 系）で生物の体模様を生成する研究級エンジンと、その
シロザケ（*Oncorhynchus keta*）への適用。AI画像生成と異なり、**模様が数理から創発**し、
**パラメータ変更で他生物にも拡張可能**。各主張は線形安定性解析とFFTで定量検証する。

---

## 1. 数理モデル

### 1.1 反応拡散系（2変数 活性化因子–抑制因子）
活性化因子 `a(x,t)`、抑制因子 `h(x,t)`：

```
∂a/∂t = ∇·(D_a ∇a) + f(a,h)
∂h/∂t = ∇·(D_h ∇h) + g(a,h)
```

主動力学は **Gierer–Meinhardt (1972)**（飽和項付き）:

```
f(a,h) = ρ a² / ( h (1 + κ a²) ) − μ_a a + a0
g(a,h) = ρ_h a² − μ_h h
```

近藤の枠組み（**局所活性化・長距離抑制 LALI**）の標準形。`D_h ≫ D_a` が Turing 不安定の要。
Schnakenberg / Gray–Scott も差替可能（`rd_engine.KINETICS`）。

### 1.2 Turing 不安定と波長（`rd_stability.py`）
同次定常解 `(a*,h*)`（reaction=0）で反応 Jacobian `J` を数値評価。分散関係：

```
σ(k) = max Re eig( J − k² diag(D_a, D_h) )
```

- 同次安定: `tr(J)<0`, `det(J)>0`
- Turing 不安定: ある波数帯 `[k₁,k₂]` で `σ(k)>0`
- **最不安定波数 k\***（σ最大）→ **予測波長 λ_T = 2π/k\***

λ_T は模様の縞間隔・斑点間隔を**理論的に予言**する。検証：シミュレーション結果の
FFT で支配波長を実測し λ_T と照合（§4）。

### 1.3 異方性と縞の向き
拡散を軸ごとに分離（`D_a^x, D_a^y, D_h^x, D_h^y`）。抑制因子の**x方向拡散を大きく**すると
パターンは x 方向に変化＝**縦バー**になる（数値実験で確認）。サケの体軸＝x なので、parr
marks・婚姻色バーの**縦縞**は異方拡散で自然に再現される。

### 1.4 数値解法（研究級の健全性）
- 陽的 Euler、**CFL 安全 dt ≤ margin·dx²/(4·max D)**（dx=1, margin=0.4）。
- **無流束（Neumann）ラプラシアン**：周期境界でなく、**生物シルエット mask 内のみ**で計算し
  mask 境界のフラックスを 0 に（模様を体内に閉じ込め）。
- 成長領域（`rd_engine` に骨子）＝ Gierer–Meinhardt の波長選択で、領域拡大時に縞が
  分裂・挿入（Kondo のエンゼルフィッシュ的）。本サケ図では未使用（§3 の理由）。

---

## 2. 生物学的基盤

- **魚皮膚模様 = 生きた Turing 波**（Kondo & Asai 1995, Nature, エンゼルフィッシュ
  *Pomacanthus*）。後の研究で、化学濃度でなく**色素細胞の遊走・増殖・突起接触**による
  LALI で実現されることが判明（数理的に Turing と等価; Kondo 2009/2010 review,
  zebrafish）。
- **サケの parr marks**：幼魚（*Oncorhynchus*、ピンク除く）の **melanophore 集合**による
  周期的縦バー。縦バー形成＝melanophore 密度・遊走・凝集の動的制御 → Turing/LALI と整合。
  **バー間隔 ↔ Turing 波長**。
- **シロザケ特有**：大きな黒点を持たない（種識別特徴）→ 海洋期は**微細 speckle のみ**。

### 段階遷移の正直なスコープ
**Turing は各段階の空間パターン型**（縦バーの間隔・向き、斑点 vs 縞、一様）を生成する。
**段階間の遷移は発生・ホルモンのスイッチ**としてモデル化（＝段階別パラメータ集合）。理由：
- smoltification の**銀化**（グアニン/プリン層）が色素模様を遮蔽 → スモルトは亜臨界（一様）。
- 成熟で**婚姻色**（erythrophore 系の赤）発現 → 遡上で赤チャネル＋大波長バー。
1本の連続シミュレーションで全7段階を変形させることは**生物学的に不正確**なので行わない。

---

## 3. シロザケ7段階の実装（`rd_salmon.py`）

側面シルエット（`fish_geom`）上で、同一 GM エンジンを段階別パラメータで駆動。
バー数から目標波長 `λ = L_body / バー数` を決め、`λ_T(D_h)` を二分探索で較正。

| 段階 | regime | 模様 | 異方比 | 目標バー数 |
|---|---|---|---|---|
| ①仔魚 | none | 模様未形成（一様） | — | — |
| ②稚魚 | bars | 縦 parr marks | 11 | 10 |
| ③スモルト | none | 一様（銀化＝亜臨界） | — | — |
| ④海洋 | none相当 | **ほぼ無地の銀**＋カウンターシェード（極微細スペックルを amp≈0.05 に抑制） | iso | — |
| ⑤沿岸 | bars | 弱い縦バー再出 | 7 | 10 |
| ⑥遡上 | bars | 太い赤紫 calico バー | 6 | 8 |
| ⑦産卵後 | bars | calico 退色＋摩耗 | 6 | 8 |

色は実測 `calibration.json`（melanophore 暗／flank／dorsal／婚姻色 bar_red）。
カウンターシェーディング（背暗・腹明）と暗い背正中線は別途加算（非 Turing の照明・解剖要素）。

> **海洋期の注意（種特徴）**：シロザケは大きな黒点を持たない（種識別点）。よって海洋期に
> 斑点格子を出すと種を誤認させる。明瞭な speckle は禁で、銀地に寄せた準・無地とする。

> **レジーム指針（離散縦バー）**：parr marks／婚姻色 calico は連続ストライプ（worm/迷路域）
> ではなく**離散した縦バー**。連続ストライプ域で弱い異方を掛けると分岐・合流した迷路になる。
> 離散バーは ①spot 域（高め k・低め F）で離散斑を作り ②強い縦異方（Dy_h ≪ Dx_h、ay≫ax）で
> 縦に伸ばして得る。バーの本数は λ で、太さは特徴サイズ（D／領域スケール）で制御。

> **エンジンの別（重要）**：魚形版 `rd_salmon.py` は **Gierer–Meinhardt**（抑制因子のみ異方
> `Dx_h≠Dy_h`）。タイル状スウォッチ `rd_swatch.py` は **Gray–Scott**（spot 域＋全場異方）。
> 下の §4.1/§4.2 の λ_T 検証は **GM（魚形版）** の値であり、GS スウォッチには直接適用されない。

---

## 4. 定量検証（学者が確認できる証拠）

### 4.1 エンジン検証（`rd_validate.py`）
等方 GM（D_a=1, D_h=20, κ=0）: **予測 λ_T = 10.81px / FFT実測 = 10.17px**（誤差 ~6%）。
λ_T は D_h とともに単調増加（D_h=20/40/80 → λ_T=10.8/12.4/14.4px）＝ Turing 理論どおり。
異方拡散で縦バー化を確認。

### 4.2 段階別検証（`rd_salmon.py` 出力）
| 段階 | 予測 λ_T | FFT実測 | 一致 |
|---|---|---|---|
| ②稚魚 parr | 9.80px | 9.89px | ✓ |
| ⑤沿岸 | 9.80px | 9.89px | ✓ |
| ⑥遡上 calico | 11.10px | 11.13px | ✓ |
| ⑦産卵後 | 11.10px | 11.13px | ✓ |
| ④海洋 speckle | (短波長) | 5.56px | ✓(微細) |

parr（密・短波長）と婚姻色（疎・長波長）の**間隔差**も理論どおり。

---

## 5. 拡張性（汎用エンジン）
`rd_engine` は kinetics・パラメータ・異方性・マスク領域を入力に取る汎用 Turing
シミュレータ。(F,k)/D比/異方性を変えれば、zebrafish 縞・ヒョウのロゼット・キリンの網目・
フグの迷路など**他生物の模様も同一原理で再現可能**（本タスクはサケに集中、zoo 実証は後）。

---

## 6. 参考文献
- Turing, A.M. (1952) "The chemical basis of morphogenesis." *Phil. Trans. R. Soc. B*.
- Gierer, A. & Meinhardt, H. (1972) "A theory of biological pattern formation." *Kybernetik*.
- Kondo, S. & Asai, R. (1995) "A reaction–diffusion wave on the skin of the marine angelfish *Pomacanthus*." *Nature* 376.
- Kondo, S. & Miura, T. (2010) "Reaction–diffusion model as a framework for understanding biological pattern formation." *Science* 329.
- Kondo, S. (2009) "How animals get their skin patterns: fish pigment pattern as a live Turing wave." *Int. J. Dev. Biol.*
- Murray, J.D. *Mathematical Biology II* (Turing 解析・波長選択).
- salmonid parr marks / vertical bar 形成（melanophore 凝集）に関する魚類色素研究。

---

## 7. ファイル構成

スクリプト（`.py`）は相互 import と `calibration.json`（親 `fish-pattern/`）・`fish_geom`（親）への依存があるため、すべて `rd/` 直下に同居させる。生成物は `out/` 配下にカテゴリ別、ビューア（HTML）は `viewers/` に分離した。各スクリプトの出力先は `__file__` 基準で解決するため、どの CWD から実行しても `out/<category>/` に書き出される。

```
rd/
├── RD_MODEL.md
├── rd_engine.py        汎用 GM 反応拡散（無流束マスク異方拡散・CFL安全・kinetics 差替）
├── rd_stability.py     線形安定性解析（Jacobian→分散関係→λ_T）＋ FFT 波長計測  → out/validation/dispersion-gm.png
├── rd_validate.py      エンジン検証（予測 vs 実測波長・異方性向き）              → out/validation/
├── rd_salmon.py        シロザケ7段階生成＋段階別 λ 検証                          → out/salmon/rd-salmon-montage.png
├── rd_stipple.py       点描（stipple）段階画像・montage・遡上 hero               → out/stipple/
├── rd_swatch.py        段階別 Turing 模様 swatch ＋ montage                      → out/swatches/
├── rd_swatch_uniform.py 無模様段階（仔魚・スモルト）の swatch                    → out/swatches/
├── rd_gallery.py       創発シーケンス／Turing zoo                               → out/gallery/
├── make_lali.py        LALI 仕組み説明の3コマ模式図                             → out/diagrams/lali-diagram.svg
├── viewers/            ブラウザ確認用 HTML（自己完結）
│   ├── rd-explainer.html
│   ├── rd_simulator.html
│   ├── rd_salmon_sim.html
│   └── rd_salmon_sim_v1.html
└── out/                生成物
    ├── stipple/        段階点描・montage・hero（png/svg）
    ├── swatches/       段階別 swatch ＋ rd-swatches.png
    ├── validation/     val-iso / val-aniso-vbar / rd-verify-compare / dispersion-gm
    ├── gallery/        rd-emergence / rd-zoo
    ├── salmon/         rd-salmon-montage
    └── diagrams/       lali-diagram.svg
```
