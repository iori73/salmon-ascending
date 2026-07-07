# 水彩サケ — 生成AI用プロンプト & 参照セット（★真上＝背面ビュー版）

**目的**: 計算ベース(点描/反応拡散)とは別の「もう一案」＝手描き水彩の有機的バージョン。
シロザケの生活史7段階を、**同じ筆致**でゆるく描いた透明水彩。

**★最重要の修正**: 図は**真上(背側＝dorsal)から見下ろした角度**でなければならない。
旧プロンプトは "side profile" だったので横向きが出た。**"side profile" は禁止語**。点描の最終図
（鱗＝放射状の波の上を真上から泳ぐ魚）と角度を揃えるため、必ず top-down にする。

**推奨ツール**: Gemini Nano Banana Pro（複数参照＋一貫性が最強）。最終出版アセットのみ Firefly。

---

## ベースプロンプト（英語・1枚＝1段階で回す）

> Loose, wet-on-wet watercolor painting of a single chum salmon (Oncorhynchus keta),
> **STRICT TOP-DOWN DORSAL VIEW — a bird's-eye / map view, looking straight DOWN onto the
> fish from directly overhead, as if looking down into clear shallow water. This is NOT a
> side view, NOT a lateral profile, NOT seen from the side. We see the fish's BACK (dorsal
> surface), never its side.**
> The body is **bilaterally symmetric about the spine, which runs head-to-tail down the
> centre**; both **pectoral fins splay out symmetrically to the left and right**; the
> **dorsal fin and small adipose fin sit on the midline**; the **deeply forked tail spreads
> flat and horizontal** at the end.
> **BODY CENTERLINE / SPINE POSTURE (CRITICAL):** bend the fish's central body axis to follow
> the attached blue curve reference exactly. The spine traces a **single shallow, elongated
> S-curve laid horizontally** — the **head end (left) bends gently DOWNWARD into a trough in
> the front third, then the body sweeps smoothly UPWARD so the tail end (right) lifts above
> the head's level.** One long, lazy, low-amplitude wave — **NOT a one-directional C-curve /
> banana bend, NOT straight.** Head at left, tail at right. Keep the strict top-down view
> while bending. On rough cold-press white watercolor paper. Transparent washes with
> visible granulation, soft bleeding edges, back-runs (cauliflower blooms). Delicate, organic,
> unhurried brushwork — NOT illustration, NOT digital, NOT outlined. The form emerges from
> overlapping translucent washes, not a drawn contour. Pale paper showing through. Subtle
> pencil ghost lines. Negative space around the fish. Botanical-study elegance.
> No background wash, no text, no frame. Single fish centred.

各段階は下の **STAGE BLOCK** をベースの後ろに足す。

### 真上で「見える/見えない」もの（全段階共通の前提）
- 見える＝**暗い背(dorsal surface)**、**背骨に沿う最も濃い正中線(dark dorsal stripe)**、左右に張り出す胸びれ、二叉の尾。
- 見えない＝**銀の腹**（真下なので不可視）。横の鮮やかな色は**上から見ると背に回り込んだ分だけ**見える。
- シロザケは**大きな黒点(spots)が無い**のが種の特徴。斑点は描かない（海洋期の極微細な点のみ可）。

### STAGE BLOCKS（真上ビュー・生物学＋実測色 calibration 準拠）
- **1 仔魚 (alevin/yolk-sac fry)**: "seen from directly above: a tiny, slender, almost
  transparent body, faint olive-grey back with a darker dorsal midline; **the large
  orange-yellow yolk sac bulges out symmetrically on BOTH sides beneath the belly**, visible
  as two soft orange swellings flanking the body; the oversized dark eyes bulge on either
  side of the head." 色: yolk #F2C34E, body 淡 #E7E2D9.
- **2 稚魚 (parr)**: "top-down: olive-green back with a dark dorsal midline; the tops of the
  8–11 oval parr-marks appear as **paired dark saddle blotches descending over both edges of
  the back**; no large spots." 色: back #979181, parr/鞍 #78745B.
- **3 スモルト (smolt)**: "top-down: silvery body, bluish steel sheen, **dark steel-blue
  dorsal stripe**, parr saddles faded to faint smudges; lavender-silver." 色: #A08DAD / #8F859B.
- **4 海洋 (ocean)**: "top-down: broad robust body, **dark metallic steel-blue/green back
  with a darker dorsal midline**, fine tiny speckles (NO large spots), silver edges where the
  flanks roll under; deeply forked tail." 色: back #343A41〜#5A585A, edge 銀 #C1BBB6.
- **5 沿岸 (coastal)**: "top-down: olive-bronze back dulling from silver, dark dorsal
  midline, no bars yet." 色: #78745B / #474D38.
- **6 遡上 (spawning, nuptial calico)**: "top-down: olive-green back with a dark dorsal
  midline, and **bold, irregular, jagged calico saddle-bars (dusky purple-magenta and dark
  olive-green) wrapping up over the back from both flanks (≈8 bars)** — tiger/calico pattern
  seen from above; the hooked jaw (kype) just visible at the snout tip." 色: base olive
  #6B6C4A, 鞍 紫赤 #6E4B52 + 暗 #2C3124.
- **7 産卵後 (post-spawn, hotchare)**: "top-down: spent, emaciated; **darkened faded olive
  back**, patchy worn skin, pale white blotches, ragged fins, weary." 色: #565640 / 退色 #6A4B41.

---

## 渡す参照画像（Nano Banana Pro / GPT-image に同時入力）

1. **スタイル見本** = ユーザー添付の水彩稚魚（にじみ・粒状）= 「この筆致で」
2. **被写体の正確さ** = `ref/c6male.png`(婚姻色calico)・`ref/c4fda.png`(海洋銀)・`ref/s1〜s7.png`(実写7段階)
   — ※これらは**横向き**。**模様だけ採り、向きは必ず真上に翻訳する**こと。
3. **真上の見え方の手本** = 計算した点描の真上図 `stipple-top-color-montage.png` / `radial-swim-mock-color.png`
   を「この角度・このシルエット(左右対称・胸びれ張り出し・二叉尾・S字遊泳)で」の構図リファレンスに使う。
4. **配色** = 上の calibration 16進（プロンプトに文字で埋め込み済み）

指示文（参照付き時）:
> Use image 1 for painting STYLE only (watercolor technique, edge quality, granulation).
> Use the side-view photos for the accurate MARKINGS of this life stage, but **re-project
> them onto a strict top-down dorsal view** — show the dark back and dorsal midline, hide the
> silver belly. Use the stipple top-down image as the COMPOSITION/angle reference (symmetry,
> splayed pectorals, forked tail, swimming S-curve). Keep the loose watercolor style identical
> across all 7 stages so they read as one series by one hand.

---

## 一貫性の出し方（7枚を「ひとつの手」に揃える）
- 1枚目（例: 6 遡上）を真上で満足いくまで作り、その出力を **スタイル＆角度の基準画像**として 2〜7枚目に毎回添付。
- 画面比・余白・紙質・筆幅・**「真上ビュー」の語**を毎回固定。

## 出さない指示（negative）
**side view, side profile, lateral view, profile（=最重要の禁止）**, straight body, banana C-curve,
no outline, no ink lines, no cartoon, no 3D render, no photo, no background scenery, no text,
no watermark, no frame, not glossy.

---

## ★実証済みワークフロー（5沿岸で成功・2026-06 確定）
- **テキストだけ単独で送らない**。posture文だけ送ると真上ビューが消えて横向き＋直線に戻る。必ず
  「TOP-DOWNベース文 ＋ STAGE BLOCK ＋ posture文」を**ひとつのプロンプトに繋げて**送ること。
- **曲率の参照画像（水色のS字ライン）を必ず添付**し、「この曲線に背骨を合わせる」と明記する。
- 冒頭で "NOT a side view / NOT lateral profile" を強めに言うと横向き化を防げる。
- 5沿岸の成功出力を **スタイル＆角度の基準画像**として残り6段階に毎回添付する。
- 曲率の最終的な微調整は無理にガチャらず、7枚揃えてから後工程（パペットワープ等）で一括で
  同じカーブに揃える方が、シリーズの統一感が出て確実。
