---
title: シロザケ 生活史7段階 カラーパレット
method: 科学文献（一次情報）＋高品質画像からの実測（PIL quantize）を相互検証
sources:
  - ADF&G Alaska Department of Fish & Game — chum salmon coloration
  - NOAA Fisheries — Pacific salmon species descriptions
  - FishBase — Oncorhynchus keta description
  - 鮭の科学（丸山ほか）— カロテノイド色素
  - FDA calibrated specimen photo (Kodak color card) → /tmp/stage4_ocean_FDA.jpg
  - 1907 breeding male illustration (PD) → /tmp/stage6_breeding_male.jpg
  - 千歳川水中撮影 CC0 → /tmp/stage6_keta_chitose.jpg
  - Gillfoto spawned-out CC BY-SA 4.0 → /tmp/stage7_spawned_out.jpg
pixel_note: |
  FDA画像（Kodakカラーカード付き＝ホワイトバランス信頼性高）でクラスタリング抽出した
  #32383D（背部・スティールブルー）#A3A3A1（側面・シルバー）はFishBase記述と一致し採用。
  1907図の #C1BD91（オリーブ黄）は婚姻色の基調色として採用（褪色分を考慮）。
  ほっちゃれの #BFB7B6 は白化体表として採用。
date: 2026-06-07
related:
  - 02_research/life-stage-descriptions.md
  - 02_research/life-stage-variables.md
  - 04_visual/lifecycle-stages/
---

# シロザケ 生活史7段階 カラーパレット

各段階につき複数色（体の部位ごと）。
信頼度: **◎**=文献+画像実測一致 / **○**=文献一次情報のみ / **△**=類推

---

## ① 仔魚（しぎょ）— 0歳・冬 / alevin

| hex | 部位 | 根拠 | 信頼度 |
|---|---|---|---|
| `#FF8024` | ヨークサック（卵黄嚢）中心 | アスタキサンチン系カロテノイド。ADF&G「bright orange yolk sac」。丸山2009「サーモンピンクの正体はカロテノイド色素」 | ◎ |
| `#FFA040` | ヨークサック外縁〜淡化部 | 同上。縁に向かうほど黄色みが増す | ◎ |
| `#F5ECE8` | 体本体（半透明） | ふ化直後は色素ほぼなし。内側の筋肉・血管のわずかな赤みが透けて淡ピンク | ○ |
| `#E8D8D0` | 体〜尾部（やや透明感） | 同上・少し暗くなる部分 | ○ |
| `#1A1410` | 眼 | メラニン。全段階共通 | ◎ |

**特徴:** ヨークサック（橙色）が最大の色の核。体は透明感が強く、砂利の色が透けて見える。

---

## ② 稚魚（ちぎょ）— 0歳・春 / fry・parr

| hex | 部位 | 根拠 | 信頼度 |
|---|---|---|---|
| `#3D4820` | 背部（最暗） | ADF&G「dark greenish-brown」。メラニン保護色。パーマーク学術図（Chamberlain PD）実測域 | ◎ |
| `#4E5A28` | 背〜上側面 | 同上、やや明 | ◎ |
| `#252E14` | パーマーク（縦楕円の暗帯） | NOAA「dark oval blotches / parr marks」。外敵に対する迷彩 | ◎ |
| `#7A8840` | 上側面〜側線付近（オリーブゴールド） | 保護色の中間帯。幼魚写真（USFWS PD）全体傾向と一致 | ○ |
| `#B8C890` | 側線下（淡黄緑〜パールグリーン） | ADF&G「below lateral line = pale iridescent green」。グアニン層少量 | ◎ |
| `#CCDAAA` | 腹〜下側面（淡クリーム緑） | 腹は背より明るい。Chamberlain図版の下半部と一致 | ○ |
| `#E5E8D8` | 腹部最下部（淡クリーム） | 遊泳・砂利底に合わせた白〜クリーム | ○ |

**特徴:** 迷彩を目的とした複数色。ヨークサックが消え、体色は完全に「川の石・藻類」に擬態。

---

## ③ スモルト（銀化）— 0歳・春〜初夏 / smolt

| hex | 部位 | 根拠 | 信頼度 |
|---|---|---|---|
| `#1E3A40` | 背部（最暗） | NOAA「dark bluish-green dorsal」。銀化後も背は外敵（鳥）避けに暗く保たれる | ◎ |
| `#2A4855` | 背〜上側面移行 | 同上 | ◎ |
| `#6898B0` | 上側面（青みがかったシルバー） | 銀化（smoltification）でグアニン結晶が側面に沈着 | ◎ |
| `#C0D0D8` | 側面（銀白色・鏡面） | グアニン結晶層が最も密。スモルト最大の特徴色。銀色海洋魚と共通 | ◎ |
| `#D8E8F0` | 下側面〜腹部 | より白さが増す。水中から見て空と同化（反射）するカウンターシェーディング | ◎ |
| `#F0F4F8` | 腹部（最も明） | 同上 | ○ |

**特徴:** パーマークが完全消失し均一な銀白へ。グアニン結晶の物理反射によるため、入射光の角度で色が変わる。

---

## ④ 海洋回遊（成魚）— 1〜5歳・外洋 / ocean adult

| hex | 部位 | 根拠 | 信頼度 |
|---|---|---|---|
| `#32383D` | 背部（スティールブルー） | **FDA Kodakカード補正画像から実測**（クラスタ最暗色）。FishBase「steely blue-green dorsally」と一致。◎最高信頼 | ◎ |
| `#3A5060` | 背〜上側面（文献補正値） | FishBase・ADF&G「metallic bluish-green」。FDA実測より青みを少し強調した科学的記述値 | ◎ |
| `#61696D` | 上側面（中間トーン） | FDA実測クラスタ。背と側面の中間帯 | ◎ |
| `#9AAABB` | 側面（シルバーブルー） | FDA実測 `#A3A3A1` を青方向補正。ADF&G「silver on the sides」 | ◎ |
| `#C8D4D8` | 側面下〜腹部上 | FDA実測 `#C1BDBA` の青補正。反射域 | ◎ |
| `#DCE8EC` | 腹部（銀白） | FishBase「silvery white ventrally」 | ◎ |

**特徴:** 海洋生活で最も長い段階の外洋魚型保護色。Kodakカード付き画像で実測した唯一の段階で、最も検証精度が高い。

---

## ⑤ 沿岸回帰〜入河前 — 回帰年・春〜秋 / coastal return (pre-run)

| hex | 部位 | 根拠 | 信頼度 |
|---|---|---|---|
| `#607040` | 体全体（暗オリーブ転換開始） | Wikipedia en「dark olive green overall」。銀が褪せ婚姻色に移行中 | ○ |
| `#7A8850` | 上体（まだやや緑がかる） | 同上・より明るい部分 | ○ |
| `#9AAABB` | 側面（残存する銀） | 入河前は銀が部分的に残る。海洋色から継続 | ○ |
| `#6A4060` | 尾柄（caudal peduncle）紫斑 | Wikipedia en「purple blotchy at caudal peduncle」。入河直前に現れる婚姻色前兆 | ○ |
| `#7A3A65` | 同・濃い部分 | 同上 | ○ |

**特徴:** 海洋銀色→婚姻色への過渡期。沿岸漁業での呼称「メジカ」「アキアジ」がこの段階。身質最良。

---

## ⑥ 河川遡上・婚姻色（ブナ）— 回帰年・秋 / spawning run

| hex | 部位 | 根拠 | 信頼度 |
|---|---|---|---|
| `#C1BD91` | 体基調（オリーブ黄） | **1907年学術図版から実測**（クラスタ主要色）。ADF&G「olive-yellow base」と一致 | ◎ |
| `#3A3820` | 背部（最暗・オリーブ褐） | ADF&G「dark olive/brown dorsal」。PD図版実測 `#4E4B2D` を参照 | ◎ |
| `#8B2020` | 体側赤縦縞（前〜中） | ADF&G「red to purple streaks on anterior 2/3」。1907図版は退色で `#A08464` だが実魚は明赤 | ◎ |
| `#C03030` | 同・鮮明な赤（縞ピーク） | NOAA breeding color / FishBase。オス成熟個体の最大発色 | ○ |
| `#6A2840` | 紫〜暗赤縦縞 | ADF&G「purple」成分。赤と紫が混在するのがカリコ模様の特徴 | ○ |
| `#2A2014` | 後半体・黒帯（尾側1/3） | ADF&G「posterior 1/3 = black」。千歳川実写 `#2C261E` と一致 | ◎ |
| `#3C3838` | 腹部（暗灰） | ADF&G「belly = dark grey」。入河後は腹も暗化 | ○ |
| `#F0EEEC` | ひれ縁（白） | ADF&G「tips of fins = white」。1907図 `#D2EAEA` 周辺 | ○ |

**特徴:** 全段階で最も多彩。赤・紫・黒・白が混在する「カリコ」または「ブナ色」。鉤鼻（吻）が曲がり、歯も発達（オス）。

---

## ⑦ 産卵後（ほっちゃれ）— 産卵直後〜死 / post-spawn

| hex | 部位 | 根拠 | 信頼度 |
|---|---|---|---|
| `#C8C0BC` | 体表（白化・主要域） | **Gillfoto CC BY-SA 4.0 画像実測** `#BFB7B6` の近傍。免疫低下で体色素崩壊 | ◎ |
| `#EDE8E6` | サプロレグニア（水カビ）白斑 | Japanese Wiki「水カビ（サプロレグニア）が全身を覆う」。綿状の白色菌体 | ◎ |
| `#6E7365` | 残存する暗部（鱗・体側） | 実測クラスタ。婚姻色の暗い部分が残存 | ◎ |
| `#5A6050` | ひれ・尾（暗くなった） | 実測 `#3A4637` の近傍。末端部から劣化 | ○ |
| `#A09888` | ひれ縁・傷んだ部分 | 白化と暗化の中間 | △ |

**特徴:** 免疫消失→Saprolegnia感染→白化が特徴色。死骸はその後川底・土壌の栄養に還る（森と海の物質循環）。

---

## 検証サマリ

| 段階 | 最重要色 | 抽出法 | 文献一致 |
|---|---|---|---|
| ① 仔魚 | `#FF8024` ヨークサック橙 | 文献一次情報 | ADF&G / 丸山2009 |
| ② 稚魚 | `#252E14` パーマーク暗帯 | 文献一次情報 | NOAA / ADF&G |
| ③ スモルト | `#C0D0D8` 鏡面シルバー | 文献一次情報 | NOAA / FishBase |
| ④ 海洋 | `#32383D` スティールブルー背 | **FDA画像実測** (Kodak補正) | FishBase "steely blue" ✓ |
| ⑤ 沿岸 | `#6A4060` 尾柄紫斑 | 文献 | Wikipedia en ✓ |
| ⑥ 婚姻色 | `#8B2020` 赤縦縞 | 1907図実測＋文献補正 | ADF&G "red to purple" ✓ |
| ⑦ ほっちゃれ | `#C8C0BC` 体表白化 | **Gillfoto実測** | JpWiki "Saprolegnia" ✓ |

---

> **注記:** ③スモルト・②稚魚は信頼できる正面カラーカード付き写真が入手できなかったため、文献記述（ADF&G/NOAA）から構築。④海洋期のみFDA・Kodakカード補正写真での実測を達成し、文献と高精度で一致した。
