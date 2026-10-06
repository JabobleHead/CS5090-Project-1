# Training on Kaggle — step by step

You need a trained baseline checkpoint (`out-baseline/ckpt.pt`) for Phase 2, and the ablation checkpoint for Phase 1's comparison. This laptop has no NVIDIA GPU, so both runs happen on Kaggle's free GPU.

## One-time setup
1. Make sure your latest work is pushed: `git status` should be clean (apart from files you intentionally leave out) and `git log origin/master` should show your newest commit. Kaggle clones from GitHub, so anything not pushed won't be there.
2. Create/sign in to a Kaggle account and **verify your phone number** (Settings → Phone verification). Without it, GPUs and internet access are unavailable in notebooks.
3. If the GitHub repo is private, either make it public for the training run or add a GitHub token as a Kaggle secret and use it in `REPO_URL`. Public is simplest; the repo contains only open-source-derived scripts, not the corpus itself.

## Baseline run
1. Kaggle → **Create → New Notebook** → **File → Import Notebook** → upload `notebooks/kaggle_train.ipynb`.
2. Right sidebar → **Session options**: Accelerator = **GPU T4 x1** (or P100); **Internet = On**; Persistence = Files only.
3. In the second cell set `REPO_URL` to `https://github.com/JabobleHead/CS5090-Project-1.git`, keep `RUN = 'baseline'`, and optionally paste the commit SHA you want into `COMMIT` (best for reproducibility; also record it in the report).
4. **Run All**. The notebook will:
   - clone the repo and install `tokenizers` and `datasketch`;
   - rebuild the dataset (clone 28 repos, filter, dedup, tokenize; ~10 min). The numbers must match [DATASHEET.md](../DATASHEET.md) (13,369 files, 47,653,184 train tokens). If they don't, stop and find out why before training;
   - run a **200-iteration smoke test**. Check that loss falls from about **9.0** (that is ln 8192, a model guessing uniformly) to well below it, and note the printed time per iteration;
   - run the full training (8,400 iterations).
5. **Estimate the time from the smoke test:** total ≈ (seconds per iteration) × 8,400. Expect roughly 1–3 hours on a T4. Kaggle sessions last at most 12 hours and the weekly GPU quota is about 30 hours, so one baseline plus one ablation fits comfortably.
6. If the session dies or times out, re-run the training cell with `--init_from=resume` appended. Checkpoints are written every 200 iterations to `out-baseline/`.
7. When finished, the last cell writes `results/baseline_run_metadata.json` and `baseline_outputs.zip`. Download the zip from the **Output** tab.
8. Unzip into the repo so you have `out-baseline/ckpt.pt` and `results/baseline_loss.csv` (+ `baseline_train.log`, metadata). `ckpt.pt` is git-ignored: keep it on disk, do not commit it. Commit the CSV, log and metadata.
9. Run `python scripts/plot_loss.py` to make `results/loss_curves.png`.

## Ablation run
Only after [PREDICTION.md](../PREDICTION.md) is committed and pushed (it is): repeat the steps above with `RUN = 'ablation_nopos'`. Use the **same** commit SHA as the baseline so the only difference between runs is `use_pos_emb`. Then run `python scripts/plot_loss.py` again for the overlay, and generate the side-by-side with the prompts listed in PREDICTION.md:

```bash
python scripts/sample.py --ckpt out-baseline/ckpt.pt        --prompt "x = a - b" --seed 1 > results/gen_baseline.txt
python scripts/sample.py --ckpt out-ablation-nopos/ckpt.pt  --prompt "x = a - b" --seed 1 > results/gen_nopos.txt
```
(CPU generation works; pass `--device cpu` if needed.)

## What to check if something goes wrong
| Symptom | Likely cause |
|---|---|
| `git clone` fails | repo private, or `REPO_URL` wrong |
| collect step fails / no internet | Internet toggle is Off |
| `CUDA out of memory` | add `--batch_size=32 --gradient_accumulation_steps=2` (same tokens per step) |
| Loss stays ≈ 9.0 or becomes `nan` | fp16 overflow: lower `--learning_rate=5e-4`; report the change |
| Loss falls then val loss rises late | expected overfitting (≈5.8 passes over the data): keep the run, report it |
| Session killed | resume with `--init_from=resume` |

Record every deviation (flags changed, restarts, GPU model) in the report's configuration section.
