# The Scale Was Already Data

### Drawing a chum salmon's whole life as one diagram — and the model I almost misused

> A fish scale is not decoration. It is already a data-recording medium.

You probably know what a salmon fillet looks like. But have you ever *read* a salmon's scale? That small translucent disc holds the record of an entire life.

This is a making-of: notes from turning the scale of a chum salmon (*Oncorhynchus keta*) into a single, readable diagram. It is the core graphic for the third act — "the logic of returning to the river" — of a graphic editorial called *Salmon Ascending*. It is not a story about making something pretty. It is a story about **grounding beauty in fact**, and about a mistake I nearly made along the way: I tried to borrow a beautiful theory, and the primary literature stopped me.

---

## 1. The scale is already data

The first question was this: could I draw a chum salmon's entire life — hatching, migrating to sea, three to five years circling the North Pacific, returning to its natal river, spawning, and dying — as a record inscribed in the fish's own body, all on one page?

It turned out this is not a metaphor. It is literally true. A fish scale *is* a growth record. There is a field for reading it: **sclerochronology**. Under a microscope, a scale reveals the fish's age, how fast it grew, and when it went to sea. The scale was not a blank vessel waiting for me to add meaning. It was **already a data structure**.

That reframing was the starting point for everything that followed.

> *Figure: a real chum salmon scale, labelled. Source — Alaska Department of Fish and Game (Scale Aging). Linked as reference, with attribution.*

---

## 2. Reading a real scale

I began by reading the real thing. The microscope images published by ADFG and NOAA come labelled with the structures:

- **Focus** — the point where the scale first formed; the fish's earliest life.
- **Circuli** — fine ridges added concentrically at the margin as the fish grows.
- **Annulus** — a band where circuli crowd together during the slow growth of winter. Count them along the radius and you read the age.

Chum salmon have their own signature. Because they spend almost no time in fresh water, they have **zero freshwater annuli** and **three to four** ocean annuli — and **almost no circuli directly below the focus** (the posterior field becomes a granular tissue called globular reticulation). An ecological fact — they leave for the sea early — is written directly into the shape of the scale.

One fact here became decisive. **Time on a scale runs only along the radius.** The circuli are closed concentric rings, not a spiral. Every point at the same radius is the same moment. **Angle carries no time information at all.** Later, this fact became the brake that stopped my own temptation.

> *Figure: NOAA scale image with Focus / Circulus / Annulus labels. Source — NOAA Fisheries, Ruth Haas-Castro. Linked as reference.*

---

## 3. Unrolling a life into a radial form

Once the structure was clear, the layout was straightforward. Put hatching (the focus) at the center; let the outward radius be time, which is also body length. I divided the life into seven stages along the radius: alevin, fry, smolt, ocean migration, coastal return, river ascent, and the spent fish after spawning.

I made the radius strictly proportional to body length. Set annuli 1, 2, and 3 to body lengths of 45, 60, and 70 cm, and a single scale of 9.5 px/cm fits all of them. This is just the honest implementation of **body–scale proportionality**: the scale's radius grows in proportion to the fish's length. The migration route (Sea of Okhotsk → northwest Pacific → Bering Sea → Gulf of Alaska) and the water temperature oscillating along it can ride along the same radius.

The center stays nearly empty, because a fry really is tiny. A salmon only becomes a salmon at sea. That honesty felt like the point of the diagram. I refused to pad the center. The smallness is intentional.

> *Figure: the radial life-history master (Figma `6184:216434`, "merge all"). Center = hatching; outer edge = the return and death.*

---

## 4. Visual experiments

With the skeleton in place, I went looking for texture: ink and *gyotaku* (fish-rubbing) — *harai* (the brush's release), *nijimi* (bleed), *kasure* (dry-brush scratch). I rasterized the densely traced scale vector and modulated the ink coverage so the scratch intensifies toward the rim, then compared three takes (wet / dry / balanced). I chose the dry one — a single ink tone, floated over the paper ground.

The seven fish are not filled silhouettes but single thick Bézier strokes in color — one stroke of the brush. Orientation comes from rotation, size from length and stroke width, undulation from the curve of the Bézier. Along the spiral path, growth is told through *position and size*.

Then came the temptation. *I want the angle to mean something too.* Start at twelve o'clock, sweep clockwise once around, bring death back up to the top — and the circle of life and death closes. A beautiful composition. But as I had confirmed in section 2, **the scale is concentric; angle carries no time.** Dressing it up as a seasonal clock would contradict the model of the scale itself.

So I gave the angle no temporal meaning. I kept the twelve-o'clock start and the single sweep, but only as **compositional intent** — the distinction is carried entirely by the radius (body length). A free parameter should be fixed deliberately, not pretend to mean something it doesn't.

> *Figure: the dry gyotaku ink texture (Figma `6188:209376`) and the seven-stage fish spiral (Figma `6241:208590`).*

---

## 5. The wall of simplification

A dense trace is accurate, but heavy as a graphic. I wanted something cleaner.

My first generative attempt: take the distance field from the focus, warp it with low-frequency noise, extract contour lines, and call them circuli. Out comes a plausible-looking disc — not perfectly concentric, with a pleasant wobble.

I threw it out. **It is not the actual shape of a scale, and it has no biological basis whatsoever.** It was just noise-warped contours that happened to look scale-ish. "Plausible" is not the same as "true." The spine of this project is *the scale is a real data record* — so the diagram itself has to carry the evidence, or it means nothing.

> *Figure: the rejected simplification (noise contours). `04_visual/scale-svg/simple-scale-preview.png`.*

---

## 6. The honest pivot

This is the turning point of the whole project.

Wanting a *grounded* generative method, I had an idea: *Could I build this with Shigeru Kondo's Turing reaction–diffusion model?* — the famous model for the patterns on a fish's skin. Elegant as theory, biological in origin, and seemingly perfect for a scale.

Working with AI, I ran the primary literature through a deep-research pass — many agents reading the papers, adversarially verifying each claim. And what came back was that my idea was **wrong**.

**Turing's reaction–diffusion model is specifically for skin pigment patterns — stripes and spots.** What Kondo & Asai (1995, *Nature*) predicted was the migration of stripes on an angelfish; what later work (Nakamasu & Kondo, 2009, *PNAS*) addressed was the interaction *between pigment cells*. So it applies, legitimately, to a salmon's body color and breeding coloration. **But the circuli on a scale form by an entirely different mechanism.**

Circuli form by **marginal accretion**. Osteoblasts at the scale's edge deposit matrix at the margin, which then mineralizes, stacking concentrically around the focus. It is not a standing wave painting a pattern; it is material being *added at the growing edge*.

I had been about to apply a beautiful theory to the wrong subject. The primary literature stopped me. **Don't borrow a beautiful theory before checking what it actually models.** That is the single most useful thing this project taught me.

---

## 7. Rebuilding on validated science

Once the mechanism was right, I could rebuild. This time I wrote a marginal-accretion generator grounded in empirical equations.

- **Radius and annulus positions** — a von Bertalanffy growth curve, converted to scale radius via body–scale proportionality. Empirical fit: `SR = 0.1018 + 0.005651·TL` (Atlantic salmon, adjusted R² 0.95, Peterson et al. 2021).
- **Circulus spacing** — proportional to growth rate, modulated by season. `CSP = 3.07·SGR + 1.29` (coho, r² 0.82, Fisher & Pearcy 1990). Deposition runs at roughly one circulus every 2.7–3 days in the ocean (Peterson et al. 2021), but it is temperature-dependent: 5.1 days per circulus at 15°C, stretching to 16.2 days at 6°C (Thomas et al. 2019). **Wide in summer, tight in winter — that is the annulus.**
- **Shape** — from an eccentric focus, scale the real contour inward by similarity. The inner rings are near-circular; the outer ones approach the real scale outline (exactly as marginal accretion adds material parallel to the growing edge).
- **Posterior field** — cut the circuli and place a granular reticulation.

Here I have to be honest about a limit. **These empirical parameters come from Atlantic salmon, coho, and sockeye. Chum-specific constants are not established in the literature I could find.** So my model is an approximation that borrows congeners as analogues. Not hiding that limit is, I think, the minimum requirement for anyone claiming "the scale is data."

> *Figure: the marginal-accretion model output. `04_visual/scale-svg/scale-accretion-preview.png` (Figma `6250:208590`).*

---

## 8. Back to the human hand

The computation gave me a *correct skeleton*. But the final image was hand-drawn in Adobe Fresco. Using the accretion structure as an underlay, I drew the purple circuli one by one and converted it to SVG.

Computational rigor and the warmth of handwork — not one or the other. The data guarantees the facts; the craft hands the viewer a body temperature. I don't think you reach "readable *and* beautiful" except by moving back and forth between the two.

Honestly, it is still in progress. Replacing the granular posterior tissue with a more complex vector, blending the gaps in the black vectors into the width of the purple line — those tasks are still in my notes. This is not a record of a finished thing. It is a record of work underway.

> *Figure: the latest hand-drawn version in Fresco (purple circuli). Figma `6262:222609`.*

---

## Closing

Data carries the facts; craft carries the hand. You move between them, correcting errors as you find them, and inch toward a single page.

Ask "what fish is this?" and a fillet answers with a species. A scale gives a longer answer: **what kind of life was this one fish's?** The focus holds the hatching; the spacing of the circuli holds the summers and winters of growth; three annuli hold three overwinterings. One life, readable along the radius.

A scale is not a calendar. It is a graph of growth. And — radius is time; angle is only composition.

---

## Sources

Basis for the scientific claims (consolidated in the production notes):

- Formation by marginal accretion: de Vrieze / Pasqualetti 2012, *J Mol Histol*; Iwasaki et al., elasmoid scale review (PMC11015963).
- Circulus spacing ∝ growth rate: Fisher & Pearcy 1990, *Fish. Bull.* 88(4):637 (`CSP = 3.07·SGR + 1.29`, r² 0.82, coho).
- Deposition pace and temperature dependence: Peterson, Sheehan & Zydlewski 2021, *J. Northw. Atl. Fish. Sci.* 52:19 (~2.7–3 days/circulus); Thomas et al. 2019, *J. Fish Biol.* (5.1 days at 15°C → 16.2 days at 6°C).
- Radius ∝ body length: Peterson 2021 (`SR = 0.1018 + 0.005651·TL`, adj. R² 0.95, Atlantic salmon); back-calculation per Ricker 1992, Francis 1990.
- Timing of overwintering annuli: Barber & Walker 1988, *J. Fish Biol.* 32:237 (sockeye, Nov–Jan).
- Turing = pigment patterns: Kondo & Asai 1995, *Nature* 376:765; Nakamasu & Kondo 2009, *PNAS* 106:8429. **Not the circuli of a scale.**
- Chum life history and migration: Nagasawa T., "Profiles of Salmonid Fishes-10: Chum Salmon," *SALMON Information* No. 6 (2012, Hokkaido Salmon Research); Azumaya & Nagasawa 2007; FishBase.
- Real scale images: Alaska Department of Fish and Game (labelled chum scale) / NOAA Fisheries (Ruth Haas-Castro, Atlantic salmon scale).

**Stated limit:** the empirical circulus parameters derive from Atlantic salmon, coho, and sockeye; chum-specific values are not established. This diagram is an approximation using congeners as analogues.

---

*From Act 3 of "Salmon Ascending" (Iori Kawano, 2026). Visual language — paper #FAFAF6, cold blue #2E6E8E × warm earth #C4722A, Mincho + EB Garamond.*

---

### For LinkedIn (share copy)

*I tried to generate a salmon scale with Turing's reaction–diffusion model — Kondo's famous fish-pattern work. Then I read the primary literature: that model explains skin pigment stripes, not the growth rings on a scale. Here's how I rebuilt it on the validated science (marginal accretion + growth), finished it by hand, and why "grounding beauty in fact" mattered more than a clever shortcut. A making-of on data, biology, and craft.*
