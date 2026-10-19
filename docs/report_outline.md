# Final report outline (6–8 pages, excluding appendices)

Due **Friday, October 30**: (1) this report, (2) the repository. Findings table, AI-use log, configs and the handwritten-reflection scan go in appendices/repo. Graded on understanding, experimental design, evidence, analysis, reproducibility. A well-supported negative result can earn full credit. Judged on rigor, verifiability/transparency and presentation.

This file is an **outline only**: every bullet is a point to make, with the number or file that supports it. Nothing here is written as prose yet. `[you]` marks a point that has to be your own words or your own judgment.

| # | Section | Pages | Status |
|---|---|---|---|
| 1 | Build & Understand | ~2 | Experiments done; **not written** |
| 2 | Use | ~1 | Judged (0/0/20); **not written** |
| 3 | Evaluate & Break | ~1.5 | **In progress** (probe set built, see [phase3.md](phase3.md)) |
| 4 | Improve & Re-evaluate | ~1.5 | Not started |
| 5 | Discussion | ~0.5 | Not started |
| A | Appendices | n/a | Log started; findings CSV, reflection pending |

---

## 1. Build & Understand (~2 pp)  — sources: [phase1.md](phase1.md), [DATASHEET.md](../DATASHEET.md), [PREDICTION.md](../PREDICTION.md)

**1.1 Model and configuration** (a small table is enough)
- nanoGPT (vendored, commit `3adf61e`); 6 layers / 6 heads / 384 embedding / context 512; no biases, dropout 0.1
- 13.96 M parameters (13.77 M without the position table); BPE vocab 8,192 (byte-level)
- AdamW, lr 1e-3 → 1e-4 cosine, 200 warm-up, wd 0.1, batch 64 x 512 tokens, 8,400 iterations (~275 M tokens), seed 1337, float16 + GradScaler on a Tesla T4
- Deviations from the PDF's example: float16 instead of bf16 (T4 only emulates bf16: 1.58 s/iter → 0.27 s/iter); token budget reached by ~5.8 passes over the data, not 20x unique tokens

**1.2 Data (key processing choices)**
- 28 permissive-licence Python repos pinned to commit SHAs (`data/sources.txt`); 15,439 `.py` files found → 13,337 kept
- Filters: size 200 B–200 KB; must parse (`ast.parse`); minified/generated dropped; exact + near-duplicate removal (MinHash, Jaccard ≥ 0.85); dedup **before** the split
- Split by file-path hash 90/5/5 (train 12,012 / val 677 / test 648 files); tokenizer trained on the train split only
- 47.8 M train tokens, 3.43 chars/token
- `[you]` why these choices (leakage, noise, licence) in one or two sentences

**1.3 Training results**
- Figure: `results/loss_curves.png` (two panels)
- Baseline: final val 1.7128, train 1.551, best val 1.7120 (iter 8100); start loss 9.08 ≈ ln 8192
- How to read it: fast early drop, flat after ~7,500; train/val gap 0.16 = mild overfitting from ~5.8 passes; last checkpoint within 0.001 of best
- Cost: ~40 min on a T4

**1.4 Ablation (remove position embeddings)**
- Prediction (written and committed first): val loss +0.03 to +0.15; indentation hurt most; surprise if < 0.02 or > 0.3
- Exact change: `use_pos_emb=False` (drops the 196,608-parameter table); same commit, seed, data, iterations, hardware class
- Result table: baseline 1.7128 vs ablation 1.7466 (**+0.034**); mean last-5-eval gap +0.054; ablation higher at every checkpoint; gap shrinks from +0.33 (iter 900) to +0.03
- Side-by-side generations: `results/gen_comparison.md` (anecdotal, no clear difference)
- Indentation probe: IndentationError 20/90 vs 17/90 → **indentation part of the prediction not supported**; parse rate 36/90 vs 25/90 (p ≈ 0.08, suggestive)
- Caveats to state: one seed per model; eval jitter of the ablation ±0.035; runs also differ in init and batch order (the "same data order" claim in PREDICTION.md is not strictly true)
- `[you]` what you learned: right direction? right size? which part failed and why? what to test next?

**1.5 Limitations and licensing**
- Library-heavy corpus (numpy, django, sympy…), little application code; split by file, not repo, so val is optimistic
- Licences (BSD-3, MIT, Apache-2.0, HPND, matplotlib/PSF-style) allow use with notice; verbatim reproduction by the model (Phase 3 `memorised`) would need attribution; `[you]` confirm each LICENSE file by reading it
- Windows CRLF and Python-version effects on rebuilds (Kaggle's corpus/tokenizer are canonical)

**Concepts to be able to explain in the text** (the PDF's "what you should understand" list): tokenization and why the BPE choice matters (the Phase 2 bare-newline bug is a concrete example); embeddings + self-attention; next-token prediction and cross-entropy; pre-training vs inference; reading loss curves; why a small model writes fluent but wrong code.

---

## 2. Use (~1 p) — sources: [phase2.md](phase2.md), `phase2/judgments.csv`, `phase2/review.md`
- Task: code completion; input = signature + docstring (+ decorators); model writes the body
- Inputs: 20 functions from the held-out test split, 20 different repos, 6–30 line bodies, none verbatim in training; seeds fixed; settings temp 0.2, top-k 50, 200 tokens
- Definition of accept / accept-after-edit / reject (copy from phase2.md)
- Counts table: **0 / 0 / 20**; 7/20 parse; 4.0 min per input (~80 min total)
- Method note: first attempt gave 20 empty outputs because prompts ended at a bare newline (a token the model only saw before column-0 lines); fixed by ending prompts with the training-style indentation token; both attempts kept
- Best, worst, near-miss: `[you]` choose from `phase2/review.md`; use your own notes from the judgments sheet (themes: unterminated/truncated syntax, invented names, ignoring the docstring)
- `[you]` when was it useful vs when did checking cost more than writing it (with 0 accepts: say so plainly)
- Threats: same repos as training; only 20 inputs; hard library code; one judge

## 3. Evaluate & Break (~1.5 pp) — sources: [phase3.md](phase3.md), `phase3/findings.csv`
- Probe design: 26 probes in 6 groups (ordinary, misleading comment/name, long-context, security, prompt variations, similar-to-training), why each group
- Failure distribution: table of categories (syntax, invented-api, wrong-logic, insecure, memorised, prompt-sensitive, context-ignored, other)
- Most important examples (3–4) with the input, the output, and the one-line why-wrong
- `[you]` likely root causes (data, scale, objective, context window, tokenizer)
- Testability: what fraction of failures a normal unit-test suite would catch vs not (from the CSV column)

## 4. Improve & Re-evaluate (~1.5 pp)
- Target failure pattern (from Phase 3), **hypothesis stated before the run**
- One intervention (decoding/prompting, data, fine-tuning, or software-system layer such as a syntax/static check or retry loop); why it follows from the Phase 3 evidence
- Before/after on the **same probes**, same conditions; improvements **and** regressions; compute cost; threats to validity; did it work for the expected reason; what next
- Negative results are acceptable if the experiment is well designed

## 5. Discussion (~0.5 p)
- `[you]` what was learned across phases; threats to validity (single seed, small samples, one judge); what to try next

## Appendices
- A. Full findings table (`phase3/findings.csv`)
- B. AI-use log ([ai_use_log.md](ai_use_log.md); add your own entries; include where AI was wrong and how you verified)
- C. Handwritten one-page reflection (scan/photo; **no AI**): what can you explain now; did building a model change how you judge Copilot/ChatGPT; which phase taught most; what still confuses you
- D. Configs, extra plots (`results/gen_comparison.md`, `results/indentation_probe.csv`)

---

## Phase 3 category names (use exactly)
`syntax`, `invented-api`, `wrong-logic`, `insecure`, `memorised`, `prompt-sensitive`, `context-ignored`, `other` (explain). Per failure: input, relevant output, category, severity, one-line why-wrong, how found, would a normal unit-test suite catch it. At least 10 failure instances, ideally 4+ categories.

## Phase 4 rules
State hypothesis before the run · change one main thing · re-run the same Phase 3 probes · report improvements and regressions · report cost / val loss where relevant · negative results are fine.

## Repository checklist
- [x] README with setup and reproduction instructions
- [x] Environment/dependency spec and code version (pin exact versions from `results/*_run_metadata.json`)
- [x] Data preparation / rebuild instructions
- [x] Baseline and ablation configs and results
- [x] Phase 2 input/result records
- [ ] Phase 3 probe set and findings CSV (probe set done; findings pending)
- [ ] Phase 4 intervention code/config and before/after results
- [ ] AI-use log (started)

## Timeline (recommended milestones, not deadlines)
Phase 1 Sep 25 · Phase 2 Oct 9 · Phase 3 Oct 16 · Phase 4 Oct 23 · final **Oct 30**. Budget ≲ 15 GPU-hours (used so far: about 1.5 h on Kaggle).
