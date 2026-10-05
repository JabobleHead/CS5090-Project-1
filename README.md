# CS 5090 Project 1 — small code language model

Phase 1 (build & understand) is implemented; Phases 2–4 are not started. Model: GPT-style, 6 layers / 6 heads / 384 emb, context 512, byte-level BPE (8,192), 13.96 M params, trained from scratch with [nanoGPT](https://github.com/karpathy/nanoGPT) (vendored at `3adf61e`, license in `nanogpt/LICENSE`; our edits are marked `[CS5090 patch]`: `use_pos_emb` flag, configurable seed, CSV loss log, cwd-independent config loading).

## Reproduce
```bash
pip install -r requirements.txt              # exact versions used in the real run: results/*_run_metadata.json
python scripts/collect.py                    # clone 28 repos at pinned SHAs (data/sources.txt) -> data/raw   (~880 MB)
python scripts/filter_dedup.py               # filter, dedup, 90/5/5 split by file -> data/processed/*.jsonl
python scripts/train_tokenizer.py            # BPE-8192 on the TRAIN split only
python scripts/prepare.py                    # -> data/code/{train,val,test}.bin + meta.pkl
python nanogpt/train.py configs/baseline.py          # needs a GPU; ~2-4 h on a Kaggle T4 (see notebooks/kaggle_train.ipynb)
python nanogpt/train.py configs/ablation_nopos.py    # AFTER PREDICTION.md is written and committed
python scripts/plot_loss.py                          # results/loss_curves.png
python scripts/sample.py --ckpt out-baseline/ckpt.pt --prompt "def parse_args(" --seed 1
```
Seed 1337 everywhere. Data decisions and numbers: [DATASHEET.md](DATASHEET.md). Ablation: [PREDICTION.md](PREDICTION.md) (`use_pos_emb=False`, everything else identical).

## Layout
`configs/` baseline + ablation · `scripts/` data pipeline, sampling, plotting · `nanogpt/` vendored model/trainer · `notebooks/kaggle_train.ipynb` · `results/` loss CSVs, logs, curves, generations · `data/sources.txt` pinned corpus.

## Status
- [x] Data pipeline run end-to-end (13,369 files, 47.7 M train tokens)
- [x] Both configs smoke-tested on CPU
- [ ] Baseline trained on Kaggle
- [ ] Ablation prediction written + committed
- [ ] Ablation trained, compared (val loss + side-by-side generation)
