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

## 7. Results (fill in after the runs)
| Run | Final train loss | Final val loss | Best val (iter) | GPU / time | dtype |
|---|---|---|---|---|---|
| Baseline | TODO | TODO | TODO | TODO | TODO |
| No position embeddings | TODO | TODO | TODO | TODO | TODO |

Figures: `results/loss_curves.png`. Side-by-side generations: `results/gen_baseline.txt`, `results/gen_nopos.txt`.
