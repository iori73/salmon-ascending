# The Pattern Emerges from an Equation

### Generating the seven life-stages of chum coloration with reaction–diffusion — but I won't say I "derived" it

> I didn't have an AI draw the pattern. I solved equations and printed the pixels. And still I won't say I "derived it by computation."

This is a companion piece. In the earlier essay, *The Scale Was Already Data*, I once tried to apply Turing's reaction–diffusion model to a fish scale, and the primary literature stopped me — the growth rings of a scale form by marginal accretion, not by reaction–diffusion. But the same research pass taught me something else: **where Turing genuinely works is not the scale, but the pigment pattern on the skin.**

So this time I tried it on the right subject. I generated the body patterns across the seven life-stages of a chum salmon (*Oncorhynchus keta*) by numerically integrating reaction–diffusion equations — one more piece in the graphic editorial *Salmon Ascending*.

But the real subject of this essay is not "it worked." It is to draw, honestly and for my own sake, the line between **"made by computation" and "derived by computation."** They are not the same thing.

---

## 1. Why reaction–diffusion

The stripes and spots on a fish's skin can arise spontaneously from nothing but chemical reaction and diffusion — this was Alan Turing's 1952 insight (Turing 1952), demonstrated by Shigeru Kondo and colleagues in the migrating stripes of a marine angelfish (Kondo & Asai 1995). Later work showed that what actually does the work is not chemical concentration but the migration, proliferation, and contact of pigment cells (local activation, long-range inhibition — LALI), which is mathematically equivalent to a Turing system (Nakamasu et al. 2009; Kondo & Miura 2010). Kondo calls it a "live Turing wave" (Kondo 2009).

The vertical bars (parr marks) on a salmon fry form by the periodic aggregation of melanophores. The calico of breeding coloration is likewise a product of the pigment-cell system. **So body color is a legitimate subject for Turing** — unlike the scale.

What separates this from AI image generation is that the pixels of the pattern come not from "plausibility" but from **the numerical integration of equations.** At least in principle, the pattern emerges from mathematics.

---

## 2. How it's made

The implementation is a two-variable Gray–Scott system (Gray & Scott 1984; Pearson 1993). The diffusion and reaction of an activator and an inhibitor are integrated in time, only inside the fish's silhouette. To get vertical bars, I make diffusion axis-dependent (anisotropic): finer along the body axis, smoother along the dorsoventral axis, and the pattern elongates vertically.

The seven stages are not one continuous simulation. **Each stage is a separate parameter set** — and that is not laziness; it is the biologically more honest choice. Smoltification's silvering masks the pigment pattern (subcritical = no pattern), and breeding color appears only at maturity. I represent the developmental and hormonal "switch" as a switch of parameters. I do not hide this.

| Stage | Pattern | Regime |
|---|---|---|
| ① Alevin | none (not yet formed) | uniform |
| ② Fry | vertical parr marks | discrete vertical bars |
| ③ Smolt | none (silvering) | uniform |
| ④ Ocean | near-featureless silver | near-uniform |
| ⑤ Coastal | faint bars re-emerge | discrete vertical bars (faint) |
| ⑥ Ascent | calico (magenta + green-black) | discrete vertical bars (bold) |
| ⑦ Spent | calico, faded | same + fading |

> *Figure: pattern-only swatches (no fish shape, tiled). `04_visual/fish-pattern/rd/rd-swatches.png`.*
> *Figure: the seven stages applied to the fish form. `04_visual/fish-pattern/rd/rd-salmon-montage.png`.*

---

## 3. The honest correction — a maze, and a spot that had to go

The first output was wrong in two places.

**First: both the parr marks and the calico came out as a connected maze.** Real parr marks are discrete vertical bars, but my parameters sat in the connected-stripe (worm/labyrinth) regime, where lines branch and merge. Weak anisotropy doesn't help — a maze stays a maze. The fix is to first enter the regime that produces *spots*, then stretch the spots vertically with strong anisotropy. Only then did I get discrete vertical bars with clear horizontal gaps.

**Second: the ocean stage came out with a clear lattice of spots.** This is critically wrong. **Chum salmon have no large black spots** — that is the very feature distinguishing them from masu or rainbow trout (FishBase and others). Paint spots on that fish and you misidentify the species. The real ocean phase is near-featureless silver. So I cut the pattern amplitude hard and pulled it toward plain silver.

The corrected version is plainly closer to the real animal. But what I want to stress is not that it was fixed — it is that **I had it wrong to begin with.** I only noticed after sweeping parameters and comparing against the real images. Some things you see only once someone looks critically.

---

## 4. Separating what "computed" means

This is the heart of the essay. I can say I "generated" this pattern by computation. But I will not say I "**derived**" it by computation. The difference is decisive.

Honestly decomposed, here is what I actually did:

- **The parameters were hand-tuned to reference images.** The values (F, k, anisotropy ratio) were not *predicted* from biology. I reverse-engineered them so it "looks like a parr mark." That is **fitting and stylization, not prediction.**
- **The wavelength "validation" is circular.** I first *specify* the bar spacing I want, calibrate the diffusion coefficient to hit it, then confirm by FFT that "the spacing I specified came out." That confirms the simulation reproduced a number I set — it is **not proof that the salmon's pattern is biologically correct.** I just got back the number I put in.
- **Gray–Scott is not the real mechanism.** Actual body color forms from pigment-cell behavior (LALI). Gray–Scott is the same *class* of mathematics, but as chemistry it is a toy kinetics.
- **Color, stage transitions, countershading, and fading are all hand-applied** staging, outside the equations.

So here is what I am **allowed to say honestly:**

> "Building on the established framework that fish skin patterns can be explained by reaction–diffusion (Kondo & Asai 1995), I **reconstructed and visualized** the pattern of each chum life-stage with a reaction–diffusion simulation. The parameters for each stage were **tuned** to reference images."

And here is what I **must not say:**

> "I *derived / predicted* the chum's pattern by computation" / "this is a *scientifically accurate reproduction*" — that would be passing off fitting as discovery.

A scholar reading with a reviewer's eye would spot the lack of rigor immediately. But I am not writing a paper. I am releasing this as a personal art piece. **In that context, the one thing not permitted is to wear a stronger face than the truth — to claim I "derived" it.** As long as I state the framework honestly, this is a work I can publish with a clear conscience.

---

## 5. Limits that remain

While I'm being honest, the current limits:

- The calico is finer-striped than the real animal; real breeding bars are bolder and fewer.
- A single-scalar-field Gray–Scott fundamentally cannot produce the true calico, where green-black bars and magenta-red bars alternate as independent bands. What I have is an approximation (magenta bars with dark cores). Doing it properly would require coupling two pigment fields — melanophores and erythrophores.
- The parameters were not fitted to measured chum data. The bar counts, too, were target values I supplied.

Carrying these limits, calling the result an "accurate reproduction" would be doubly indefensible. So I don't.

---

## Closing

The lesson of the earlier essay was: *don't apply a beautiful theory before checking what it models.* This time the subject was right — a theory I was allowed to apply. And still the lesson continues: **even when the theory is right, the gap between "computed" and "derived by computation" has to be written down honestly.**

Equations do raise the pattern up. That much is true. But what you fed in, what you decided by hand, and what you did *not* validate — only by disclosing those does computation become an honest tool.

The pattern emerges from an equation. But the hand that decided that pattern *is* a chum salmon was mine, comparing it against reference photographs. Not lying about that is, I think, the whole spine of this as a work.

---

## Sources

**Reaction–diffusion & pigment patterns (academic)**
- Turing, A. M. (1952) "The Chemical Basis of Morphogenesis." *Philosophical Transactions of the Royal Society B* 237(641):37–72.
- Gierer, A. & Meinhardt, H. (1972) "A theory of biological pattern formation." *Kybernetik* 12:30–39.
- Gray, P. & Scott, S. K. (1984) "Autocatalytic reactions in the isothermal, continuous stirred tank reactor." *Chemical Engineering Science* 39(6):1087–1097.
- Pearson, J. E. (1993) "Complex Patterns in a Simple System." *Science* 261(5118):189–192. (Gray–Scott phase diagram)
- Kondo, S. & Asai, R. (1995) "A reaction–diffusion wave on the skin of the marine angelfish *Pomacanthus*." *Nature* 376:765–768.
- Nakamasu, A., Takahashi, G., Kanbe, A. & Kondo, S. (2009) "Interactions between zebrafish pigment cells responsible for the generation of Turing patterns." *PNAS* 106(21):8429–8434.
- Kondo, S. & Miura, T. (2010) "Reaction–Diffusion Model as a Framework for Understanding Biological Pattern Formation." *Science* 329(5999):1616–1620.
- Kondo, S. (2009) "How animals get their skin patterns: fish pigment pattern as a live Turing wave." *International Journal of Developmental Biology* 53:851–856.

**Ecology & identification**
- Nagasawa, T. (2012) "Profiles of Salmonid Fishes-10: Chum Salmon," *SALMON Information* No. 6, Hokkaido Salmon Research, Fisheries Research Agency.
- FishBase, *Oncorhynchus keta* species account (diagnostic: lacks distinct black spots on the body).

**Reference images (the real animal at each stage, used for visual comparison)**
- Fry (parr marks): illustration "Dog Salmon Fingerling" (A. F. Chamberlain, 19th-c. scientific plate, Public Domain).
- Ocean phase: illustration, NOAA Fisheries / Jack Hornady (Public Domain).
- Coastal phase (silver adult): photograph, U.S. Fish and Wildlife Service (Public Domain).
- Ascent (breeding calico): photograph by *Vineyard* (CC BY-SA 3.0).
- Spent fish (*hocchare*): photograph by *Andshel* (CC BY-SA 3.0).

(CC BY-SA images must be displayed with attribution and under share-alike terms.)

**Stated limit:** The parameters in this work are a fitting/stylization to reference images; they were not validated against measured chum quantitative data. The wavelength self-check only confirms reproduction of values I specified — it is not proof of biological accuracy. The swatches use Gray–Scott while the fish-form version uses Gierer–Meinhardt; the two are different engines. This work is a **visualization/stylization** using the reaction–diffusion framework, not a biological prediction or derivation.

---

*From the *Salmon Ascending* series (Iori Kawano, 2026). Visual language — paper #FAFAF6, cold blue #2E6E8E × warm earth #C4722A, Mincho + EB Garamond. Companion to *The Scale Was Already Data*.*

---

### For LinkedIn (share copy)

*The earlier piece was about a model I almost misused. This one is the opposite case: a model I was actually allowed to use — Turing reaction–diffusion for fish skin color — applied to the seven life-stages of a chum salmon. I generated the patterns by solving equations, not by AI. But the real point is a line I drew for myself: "made by computation" is not "derived by computation." The parameters were hand-tuned to reference photos; the wavelength "validation" is circular; the species' no-black-spots rule had to be enforced by hand. A making-of on honesty, transparency, and why I refuse to claim more than the math actually did.*
