# 執筆ブリーフ — making-of 記事「鱗＝データ記録」

> 制作記事（making-of）の執筆ブリーフ。本文ドラフトはこの後 `article/note-ja.md`（日本語/note）と `article/medium-en.md`（英語/Medium・LinkedIn共有）に展開する。
> 親プロジェクト＝「サーモンは遡上する / Salmon Ascending」（川野いおり, 2026）。本記事はその **Act 3「川に戻る論理」の核グラフィック＝鱗データビジュアライゼーション**を作った過程を、独立した制作エッセイとして書く。
> 作成 2026-06-14。組み立て元＝memory [[salmon-lifestage-variables]] / [[scale-formation-models]] / [[project-salmon-editorial]] / [[references-database]]、repo `editorial-structure.md` / `02_research/research-findings.md` / `references/INDEX.md` / `04_visual/visual-language-concept.md`。

---

## 0. 記事メタ

**主題（角度）**：シロザケの鱗を「読める一枚の図」にするまでの制作記。**美しさを科学的事実に接地させる**過程、そして途中で犯しかけた誤り（チューリング・モデルの誤用）を一次資料で正した「正直な転回」を核にする。

**タイトル候補（JP）**
1. 鱗は、すでにデータだった —— 一匹のシロザケの一生を一枚の図にする
2. 魚の鱗に時間が刻まれている —— 制作の記録
3. 美しさを、事実に接地させる —— シロザケの鱗を描き直した話

**タイトル候補（EN）**
1. The Scale Was Already Data — Drawing a chum salmon's whole life as one diagram
2. A Fish Scale Is a Record of Time — notes from making a data illustration
3. Grounding Beauty in Fact — how I redrew a salmon scale (and corrected myself)

**フック（hook / 1行）**
- JP：「鱗は、装飾ではない。すでにデータの記録媒体だ。」
- EN："A fish scale is not decoration. It is already a data-recording medium."

**媒体別**
| 媒体 | 言語 | 狙い・トーン | 長さ目安 |
|---|---|---|---|
| note | 日本語 | 一人称の制作記。試行錯誤と「正直な転回」を率直に。読み物 | 3,000–4,500字 |
| Medium | 英語 | 国際読者向けに背景（シロザケ／鱗相解析／プロジェクト）を厚めに。図版主導 | 1,500–2,200 words |
| LinkedIn | 英語 | Medium記事へのシェア文。「AIと組んで、視覚を実証科学に接地させた」プロセスの要約 | 投稿3案（下記§9） |

**想定読者**：データビジュアライゼーション/デザイン関心層、エディトリアル/グラフィック、科学コミュニケーション、サケ・自然関心層。専門知識は前提にしない。

---

## 1. 主題と土台の概念（hook を支える事実）

**鱗相解析（sclerochronology）**＝魚の鱗は成長の記録。
- **焦点 focus** ＝ 鱗が出来始めた点（＝個体の若い時期）。
- **隆起線 circuli** ＝ 成長に伴って縁に付加される同心の隆起。間隔が広い＝速い成長、狭い＝遅い成長。
- **年輪 annulus** ＝ 冬の低成長で circuli が密集した帯。半径方向に数えると年齢が読める。
- **半径 ∝ 体長**（body–scale proportionality）。だから鱗は「カレンダー」でなく「成長のグラフ」。
- 時間は**半径方向のみ**（circuli は閉じた同心円＝同一半径＝同一時刻。**角度に時間情報はない**）。

**シロザケ（Oncorhynchus keta）特有**：淡水年輪ゼロ（降海が極早い）／海洋年輪3〜4本／焦点直下に circuli ほぼ無し（後方野＝globular reticulation という粒状組織）。

→ この「鱗＝実在するデータ構造」という再フレームが、プロジェクト全体（[[project-salmon-editorial]] Act3）の核であり、本記事の出発点。

---

## 2. 物語のアーク（8ビート・JP/EN 共通の節構成）

各ビート＝記事の1セクション。図版（§6）を各ビートに割り当て済み。

1. **再フレーム** — 「鱗は装飾でなくデータだ」。一匹のシロザケの一生（孵化→降海→3〜5年の海洋回遊→母川回帰→産卵→死）を、その魚自身の鱗に刻まれた記録として一枚に描けるのではないか。〔図：実鱗 ADFG〕
2. **本物の鱗を読む** — 実物（ADFG/NOAA の顕微画像）を読み解く：焦点・circuli・年輪1/2/3・後方の globular reticulation。シロザケ特有の構造。〔図：ADFG ラベル付き実鱗〕
3. **一生を放射形へ** — 中心=孵化、外へ=時間/体長、7段階（仔魚→稚魚→スモルト→海洋回遊→沿岸回帰→河川遡上→ほっちゃれ）。回遊（オホーツク→北西太平洋→ベーリング→アラスカ湾）と水温の振動も半径に沿って乗る。〔図：放射マスター `6184:216434`〕
4. **視覚の実験** — 墨/魚拓の質感（払い harai・にじみ nijimi・掠れ kasure）、7段階の魚をスパイラル上に成長配置、そして「角度に意味を持たせたい」誘惑と、それが鱗の同心円モデルと矛盾するという気づき（角度=時間ではない）。〔図：魚拓DRY `6188:209376`／7段階魚スパイラル `6241:208590`〕
5. **簡略化の壁** — 密トレースを簡潔にしたい。最初の自作生成＝「焦点からの距離場をノイズで歪ませた等高線」。一見それらしいが**実際の鱗の形でない／生物学的根拠がない**。却下。〔図：却下版 `simple-scale-preview.png`〕
6. **正直な転回（記事の山場）** — 「近藤滋先生のチューリング反応拡散モデルで作れないか？」→ 一次資料を deep-research。判明＝**チューリングRDは体表の色素パターン（縞・斑）専用で、鱗の circuli には使えない**。circuli は**辺縁付加（marginal accretion）＋成長**で形成される、別メカニズム。誤った道具を当てはめかけ、科学で正した。〔図：なし or 概念対比図〕
7. **検証モデルで再構築** — 実証式に基づく辺縁付加ジェネレータ：circuli＝偏心焦点から実輪郭を内側へ（縁に平行）／間隔＝von Bertalanffy 成長×季節変調（夏広・冬密＝年輪）／後方=reticulation。〔図：辺縁付加モデル `scale-accretion-preview.png`〕
8. **人の手の回帰** — 計算で「正しい骨格」を得たうえで、最終的に Adobe Fresco で手描き（紫の circuli）→SVG化。計算的厳密さ × 手仕事の温度。残課題（reticulation の置換・黒/紫ベクターの馴染ませ）。〔図：Fresco手描き最新 `6262:222609`〕

**結び**：データ＝事実、craft＝手。両者を往復し、誤りを正しながら「読めて、かつ美しい一枚」へ。問い「これは何の魚か」＝鱗は「これはどう生きた一匹か」を語る。

---

## 3. 科学（正確な枠組み）＋出典

> 出典詳細は memory [[scale-formation-models]]。**実証パラメータは Atlantic salmon / coho / sockeye 由来＝シロザケ固有値は未確立（アナログ）**という限界を本文でも明記する（プロジェクトの「検証済みのみ」方針 §5）。

- **形成＝辺縁付加**：鱗縁の骨芽細胞がマトリクスを縁に沈着→石灰化。de Vrieze/Pasqualetti 2012 *J Mol Histol*; Iwasaki et al. elasmoid scale review (PMC11015963)。
- **circulus 間隔 ∝ 成長速度**：`CSP = 3.07·SGR + 1.29`（r²0.82, coho）— Fisher & Pearcy 1990 *Fish. Bull.* 88(4):637。
- **沈着ペース**：海洋で約 2.7〜3日/本（Peterson, Sheehan & Zydlewski 2021 *J. Northw. Atl. Fish. Sci.* 52:19）。温度依存 15℃で5.1日→6℃で16.2日/本（Thomas et al. 2019 *J. Fish Biol.*）＝夏広/冬狭=年輪。
- **半径∝体長**：`SR = 0.1018 + 0.005651·TL`（adjR²0.95, Atlantic）— Peterson 2021。back-calc は ΔL∝ΔS（Ricker 1992）＋SPH/BPH（Francis 1990）。von Bertalanffy 成長と連動。
- **越冬年輪の時期**：ベニザケ（近縁）で Nov–Jan、海洋2年目が最密（Barber & Walker 1988 *J. Fish Biol.* 32:237）。
- **チューリング＝色素**：Kondo & Asai 1995 *Nature* 376:765（アケボノチョウチョウウオの縞移動を予測）／Nakamasu & Kondo 2009 *PNAS* 106:8429（色素細胞間相互作用）。**鱗の circuli ではない。**
- **鱗の“配列”（どこに鱗が並ぶか）**：Eda/NF-κB 進行波（Aman et al. 2023 *Development* 150:dev201866）。これも circuli とは別問題。
- **実鱗画像出典**：ADFG（チャム鱗ラベル付き）／NOAA（Ruth Haas-Castro, 大西洋サケ鱗）。

---

## 4. 生態の事実と数字（背景・必要分のみ）＋出典

> 本記事は鱗の制作記なので、生態は「なぜ鱗がそれを記録できるか」を支える範囲で使う。**未確証（Project Japan の人名・年・輸出量）は本文に使わない**（`02_research/research-findings.md` で全票否定済み／`05_web/app/about` の編集方針）。

- **シロザケ生活史**：体長 約5cm→海洋成長→約65cm。海洋 3〜5年（**4年魚が最多**＝平均的個体／年輪3本＝海の越冬3回）。回帰 9〜12月。出典＝FRA／永沢2012「サケ科魚類のプロファイル-10」SALMON情報 No.6（`src-25`, 回遊一次資料）／FishBase。
- **回遊**：沿岸→オホーツク海(8–11月)→北西太平洋(越冬12–5月)→ベーリング海(索餌6–11月)→アラスカ湾(越冬)。分布水温 2.7–15.6℃。出典＝永沢2012／Azumaya & Nagasawa 2007。
- **（任意の導入用）現代の文脈**：千歳川捕獲 2022年 587,475尾→2024年 161,276尾（**約72.6%減**）／北海道日本海地区 2024年 119万尾（1990年以降最低）。出典＝千歳水族館公式統計（`src-08`）／水産研究・教育機構2025（`src-01`）。※記事の主筋ではないが「今この魚を見つめ直す」導入に使える。

---

## 5. 編集方針（本記事でも遵守）

- **検証可能な事実のみを断定で書く**。実証モデルのパラメータが他サケ種由来である点、シロザケ固有値が未確立である点は**正直に明記**（これが記事の誠実さ＝魅力でもある）。
- 科学的主張には出典を付す（§3）。
- アイヌ関連には踏み込まない（本記事は鱗の制作記。文化的主題は親プロジェクト本体で扱う）。

---

## 6. 図版インベントリ（各ビートに割り当て）

> ★＝主役候補。Figma は `get_screenshot` で書き出し。**自作の生成図・手描き図は権利フリー（自前）。実鱗の科学画像（ADFG/NOAA）は出典明記＋利用許諾の確認が必要。**

| # | ビート | 画像 | 所在 | 権利/メモ |
|---|---|---|---|---|
| A | 1,2 | 実鱗（ラベル付き・チャム） | ADFG `chinookscaleage/f1_chum_kz0503f034_labelled.jpg`（`/tmp/chum_real.jpg`） | ★読み解きの基準。**ADFG許諾確認** |
| B | 2 | NOAA 鱗（Focus/Circulus/Annulus） | NOAA fisheries（Ruth Haas-Castro） | 出典明記・許諾確認 |
| C | 3 | 放射マスター「merge all」 | Figma `6184:216434` | ★自作。一生を放射形に展開 |
| D | 4 | 魚拓DRY（墨テクスチャ確定） | Figma `6188:209376`（cc merge `6084:242471`）／`04_visual/scale-svg/gyotaku-dry.png` | 自作 |
| E | 4 | 7段階魚スパイラル（採用ハイブリッド） | Figma `6241:208590`（元 `6229:208608`） | 自作。成長＝位置と大きさ |
| F | 5 | 簡略化・却下版（ノイズ等高線） | `04_visual/scale-svg/simple-scale-preview.png` | 自作。「根拠なし」の例として |
| G | 6 | （概念）チューリング＝色素／circuli＝辺縁付加 の対比 | 新規簡易図 or テキスト | 山場。必要なら自作 |
| H | 7 | 辺縁付加モデル（実証ベース生成） | `04_visual/scale-svg/scale-accretion-preview.png`／Figma `6250:208590`「scale 辺縁付加モデル」 | ★自作 |
| I | 8 | Fresco 手描き（紫circuli）最新 | Figma `6262:222609`「手描き20260614」 | ★自作・最新の主役 |
| — | 付録 | 生成スクリプト | `04_visual/scale-svg/{gyotaku.py, simple_scale.py, scale_accretion.py}` | コード抜粋を技術付録に |

---

## 7. 「正直な転回」を山場に（トーンの核）

記事の魅力＝**「AIと組んで近藤先生のチューリングモデルで作ろうとしたが、一次資料に当たったら“それは色素パターンのモデルで鱗には使えない”と判明し、正しい形成モデル（辺縁付加＋成長）に作り直した」**という誠実な軌道修正。
- 教訓：かっこいい理論を安易に当てはめない／実証された一次資料で接地する／誤りを認めて直すことが質を上げる。
- これは note でもMedium/LinkedInでも刺さる普遍テーマ（「美しさ × 事実」「AI協働での検証の重要性」）。

---

## 8. 未決・TODO・権利

- **Fresco 残TODO（node `6262:222609` に記載）**：①globular reticulation を複雑shapeの vector に置換／②黒ベクターの途切れを紫ベクター幅に自然に馴染ませる。→ 記事は「完成途上の記録」として正直に書ける。
- **科学の限界**：circulus の実証パラメータは Atlantic/coho/sockeye 由来、**シロザケ固有値は未確立**。本文で明記。
- **画像権利**：ADFG・NOAA の実鱗画像を載せるなら出典明記＋許諾確認。代替＝主役を自作（生成図＋Fresco手描き）に寄せれば権利クリア。
- **角度の扱い**：採用版で「12時スタート→一周→死が頂点に回帰」という構図を入れたが、これは**作図上の意匠（角度に時間的意味はない）**であることを誤解させない記述にする。
- **次工程**：このブリーフ確定後 → `note-ja.md` / `medium-en.md` 本文ドラフト。

---

## 9. リード/引用候補・LinkedIn 文案

**リード候補（JP）**
- 「サケの切り身は知っていても、サケの鱗を読んだことはあるだろうか。あの小さな円盤には、一匹の一生が刻まれている。」

**Pull quotes（JP）**
- 「鱗は、カレンダーではない。成長のグラフだ。」
- 「美しい理論を、安易に当てはめてはいけない。」
- 「半径は時間。角度は、ただの意匠だ。」

**Pull quotes（EN）**
- "A scale is not a calendar. It is a graph of growth."
- "Don't borrow a beautiful theory before checking what it actually models."
- "Radius is time. Angle is only composition."

**LinkedIn 共有文案（EN, 3案）**
1. *I tried to generate a salmon scale with Turing's reaction-diffusion model (Kondo's famous fish-pattern work). Then I read the primary literature: that model explains skin pigment stripes — not the growth rings on a scale. Here's how I rebuilt it on the validated science (marginal accretion + growth), and why "grounding beauty in fact" mattered more than a clever shortcut.*
2. *A fish scale is already a data record — focus = birth, circuli = growth, annuli = years. I spent weeks turning a chum salmon's whole life into one diagram, made a wrong modeling assumption, corrected it against peer-reviewed sources, and finished it by hand. A making-of on data, biology, and craft.*
3. *Making-of: a data illustration where the dataset is a fish's own body. What I learned about combining AI research, validated biological models, and hand-drawing — including the model I almost misused.*

---

## 10. 参考：親プロジェクトの位置づけ（文脈）

「サーモンは遡上する / Salmon Ascending」5幕（Act1 消費の現在／Act2 渡来の物語／Act3 川に戻る論理／Act4 神の魚／Act5 帰着）。本記事の鱗可視化＝**Act3 の核グラフィック制作の舞台裏**。視覚言語＝紙地#FAFAF6・冷青#2E6E8E×温土#C4722A・明朝＋EB Garamond（`04_visual/visual-language-concept.md`）。記事のトーンもこの「知的厳密 × 静かな美」を踏襲する。
