# Phase 1 — Build & Understand

Goal (from the assignment): train a small GPT-style model from scratch, document the data and training choices, run **one ablation** with a prediction written beforehand, and compare by final validation loss plus a side-by-side generation.

## 1. What was built
| Item | Choice | Why |
|---|---|---|
| Framework | nanoGPT (vendored at `3adf61e`, MIT; our edits marked `[CS5090 patch]`) | Recommended by the assignment; small enough to read end to end |
| Architecture | 6 layers / 6 heads / 384 embedding, context 512, no biases, dropout 0.1 | The assignment's example configuration |
| Parameters | 13.96 M (13.77 M without position embeddings) | Matches `get_num_params()` output |
| Tokenizer | Byte-level BPE, vocab 8,192, trained on the **train split only** | Avoids tokenizer leakage from validation/test; byte-level means any text is encodable |
| Corpus | 28 permissively licensed Python repos at pinned commits | Enough tokens to approach the 20×-parameters guideline; details in [DATASHEET.md](../DATASHEET.md) |
| Split | 90/5/5 by hash of file path, after deduplication | A file never appears in two splits; near-duplicates cannot straddle them |
| Optimiser | AdamW, lr 1e-3 → 1e-4 cosine, 200 warm-up steps, weight decay 0.1, β2 0.99 | nanoGPT's small-model defaults |
| Budget | 8,400 iters × 64 seq × 512 tok = ~275 M tokens ≈ 19.7× parameters ≈ 5.8 passes over 47.7 M train tokens | Follows the "≈ 20 × parameter count" guideline |
| Precision | fp16 + GradScaler on Kaggle T4/P100 (no bf16 there); bf16 where supported | `dtype` auto-selected by `train.py`; record what was actually used |
| Seed | 1337 everywhere | Reproducibility |

### Deviations from the example configuration (state these in the report)
- Corpus is multi-epoch (≈5.8 passes) rather than 20× unique tokens. Expect some overfitting and more verbatim memorisation, which is relevant for Phase 3.
- fp16 instead of bf16 if Kaggle's GPU lacks bf16.
- `log_csv`, `seed` and `use_pos_emb` options were added to nanoGPT (see `nanogpt/train.py`, `nanogpt/model.py`).

## 2. How to run
See the [README](../README.md) for commands and [kaggle_guide.md](kaggle_guide.md) for the Kaggle walkthrough.

## 3. Concepts to be able to explain (graded: "clear understanding")
- **Tokenization:** raw source → bytes → BPE merges → ids. A larger vocabulary shortens sequences (3.5 chars/token here) but spreads probability over more symbols; a character tokenizer would be longer sequences, no merges.
- **Embeddings + self-attention:** each token id becomes a vector; attention lets each position take a weighted average of earlier positions' vectors, giving *contextual* representations.
- **Position information:** attention is permutation-blind by itself. The learned position embedding (`wpe`, 512×384) is the model's explicit way of knowing order. The causal mask leaks some order implicitly.
- **Objective:** next-token prediction minimising cross-entropy. A uniform guess scores ln 8192 ≈ 9.01 nats; the first logged loss should be close to that.
- **Pre-training vs inference:** training updates weights on teacher-forced text; inference samples one token at a time with temperature/top-k and never updates weights.
- **Fluent but wrong:** the loss rewards plausible continuations, not correctness. A small model on a small corpus learns surface patterns (syntax, common idioms) faster than semantics.

## 4. Ablation: remove position embeddings
- **Single change:** `use_pos_emb=False` (`configs/ablation_nopos.py`): the `wpe` table is replaced by `nn.Identity()` and token embeddings go straight into the blocks. Parameter count drops by 196,608.
- **Prediction** (written and committed before the run): [PREDICTION.md](../PREDICTION.md): val loss up roughly +0.03 to +0.15 nats; indentation hurt most, operand/argument order next, bracket matching least.
- **Held constant:** data, seed, model size, iterations, LR schedule, batch size, hardware class.
- **Compare:** final validation loss (baseline vs ablation, same step), overlaid curves (`scripts/plot_loss.py`), and side-by-side generations on the prompts in PREDICTION.md with identical seed, temperature (0.8) and top-k (50).
- **Be honest in the write-up:** say whether the prediction was right, by how much, and what the generations showed. A single seed cannot separate a ~0.02 nat difference from noise: say so if the gap is small.

## 5. Reading the loss curves
- Train and val loss falling together = learning general patterns.
- Val flattening while train keeps falling = starting to memorise (expected late, with ≈5.8 epochs).
- Val rising = overfitting; the checkpoint at the end may not be the best one (`always_save_checkpoint=True` keeps the last, so report best-val iteration from the CSV too).
- Spikes or `nan` = learning rate too high / fp16 overflow.

## 6. Limitations and licensing (for the report)
- Library code dominates the corpus: little application/script code, many tests and docstrings; style transfer to "ordinary" code will be weak.
- Validation shares repo-level style with training (split is by file, not repo), so val loss is optimistic about generalisation to new projects.
- Single seed per configuration; differences smaller than run-to-run noise are not conclusions.
- Licences (BSD-3, MIT, Apache-2.0, HPND, PSF-style) permit use with notice. Training a model on them is not the same as redistributing the code, but verbatim reproduction by the model (Phase 3 `memorised` failures) would need attribution. Confirm each LICENSE file by reading it; `collect.py` only checks that one exists.

## 7. Results
| Run | Final train loss | Final val loss | Best val (iter) | GPU / time | dtype |
|---|---|---|---|---|---|
| Baseline | 1.551 | **1.7128** | 1.7120 (8100) | Tesla T4 / ~40 min training (~272 ms/iter) | float16 + GradScaler |
| No position embeddings | 1.646 | **1.7466** | 1.7466 (8400) | Tesla T4 / ~40 min (~268 ms/iter) | float16 + GradScaler |

Baseline run facts (`results/baseline_loss.csv`, `baseline_run_metadata.json`): repo commit `77b99ed`, Python 3.13.15, torch 2.11.0+cu128, seed 1337, 8,400 iterations (~275 M tokens, ~5.8 passes over 47.8 M train tokens), start loss 9.08 (= ln 8192, as expected).
How to read it: val loss falls fast (9.08 -> 2.46 by iter 900), then slowly; it flattens after ~iter 7,500 (1.714 at 7,500 vs 1.713 at 8,400) as the learning rate decays, and the train/val gap is 0.16 nats. That is mild overfitting from repeated passes, not divergence; the last checkpoint is within 0.001 of the best, so final-vs-best makes no practical difference here.
Caveats: single seed; each logged loss is an average over only 40 batches (~1.3 M tokens), so differences below roughly 0.01-0.02 nats are not interpretable.

Figures: `results/loss_curves.png`. Side-by-side generations: `results/gen_baseline.txt`, `results/gen_nopos.txt` (after the ablation).

### Deviations actually made (for the report)
- `dtype=float16` fixed in the config. The first attempt used nanoGPT's default, which picked bfloat16 on the T4 (reported as supported, but emulated): 1.58 s/iter vs 0.27 s/iter with float16.
- Eval every 300 iterations with 40 batches (was 200 / 100) to cut eval time; this does not change training.
- A smoke-test cell crashed once (warmup equal to lr-decay iterations in the 200-iteration override: division by zero); fixed in the notebook, the full run was unaffected.


## 8. Ablation result: remove position embeddings (`use_pos_emb=False`)
Setup actually run: identical to the baseline (commit `77b99ed`, seed 1337, 8,400 iters, float16, same Kaggle-built data/tokenizer; `results/data_artifacts/*` are byte-identical between the two runs). Only the learned position table (196,608 params) is removed. Files: `results/ablation_nopos_loss.csv`, `ablation_nopos_train.log`, `ablation_nopos_run_metadata.json`, `results/loss_curves.png`, `results/gen_comparison.md`, `results/indentation_probe.csv`.

### Validation loss (the required comparison)
| | Baseline | No position embeddings | Difference |
|---|---|---|---|
| Final val loss (iter 8400) | 1.7128 | 1.7466 | **+0.034** |
| Mean val-loss gap over the last 5 evals | | | +0.054 (range +0.034 to +0.080) |
| Final train loss | 1.551 | 1.646 | +0.095 |
| Val gap at iter 300 / 900 / 3000 | | | +0.20 / +0.33 / +0.10 |

- The ablated model's val loss is higher than the baseline's at **every** evaluation after iteration 0, and the gap shrinks steadily: the model without position embeddings learns more slowly and catches up most, but not all, of the way.
- The prediction (`PREDICTION.md`, committed before the run) was "up by roughly +0.03 to +0.15 nats". The final value (+0.034) is inside that range at its low end; it is also above the "< 0.02 within noise" surprise threshold. The late-run curve is noisier for the ablation: its eval-to-eval changes reach about +/-0.035, versus about +/-0.01 for the baseline, so the single final number (+0.034) is of the same size as that jitter. The mean of the last five gaps (+0.054) and the sign at every earlier eval are stronger evidence than the final value alone.
- Each eval averages 40 batches, there is one seed per model, and the two runs differ in initial weights and batch order beyond the removed table (a missing `wpe` draw changes the random stream). `PREDICTION.md` says "same data order", which is not strictly true; say so in the report.
- Training loss is also higher (+0.095) and the train/val gap is smaller (0.10 vs 0.16). The ablation fits the training set less well; it does not generalise better in absolute terms.

### Generations (`results/gen_comparison.md`, 4 prompts x 3 seeds per model, same seeds/settings)
At temperature 0.8 both models produce fluent-looking but meaningless code for `x = a - b`, `x = b - a`, a nested `for`/`if` block and `compute(`. Anecdotal observations (12 samples each, no statistics): the ablation continued more often into doctest-style text (`>>> ...`); both models repeat themselves; the ablation produced one visibly odd indentation jump (nested prompt, seed 2) and one degenerate repeat (`_update_for_update...`), but the baseline also produces broken structure. Neither model showed a clear, consistent difference on operand order for `a - b` vs `b - a`.

### Quantitative check of "indentation suffers most" (`scripts/indentation_probe.py`, 90 samples per model)
| | parses | IndentationError | other syntax error |
|---|---|---|---|
| Baseline | 36 | 20 | 34 |
| No position embeddings | 25 | 17 | 48 |

- **Indentation errors did not increase** in the ablation (20/90 vs 17/90; difference not significant), so this specific part of the prediction is **not supported** by this probe.
- Overall syntactic validity is lower in the ablation (36/90 = 40% vs 25/90 = 28%; rough two-proportion test p ~ 0.08, so suggestive, not conclusive). The extra failures are mostly "other" syntax errors (brackets, truncated statements), not indentation.
- Caveats: samples are cut to the last complete line before parsing, so some "other" errors are truncation artefacts; three short prompts; one seed; the 90 samples are not independent evidence about a whole corpus.

### What to write yourself in the report ("what I learned")
Do this in your own words: was the direction right, was the size right, which part of the prediction failed (indentation) and why you think so (hypothesis only: the causal mask leaks enough order for local structure such as indentation, but long-range ordering/bracket structure degrades), and what you would test next (e.g. several seeds, or a larger eval set, to tell a 0.03 nat gap from noise).
