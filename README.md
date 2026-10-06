# CS 5090 Project 1 — small code language model

A GPT-style code model trained from scratch (6 layers / 6 heads / 384 emb, context 512, byte-level BPE with 8,192 tokens, 13.96 M parameters) on ~48 M tokens of permissively licensed Python, then used, probed and improved over four phases. Built on [nanoGPT](https://github.com/karpathy/nanoGPT), vendored at commit `3adf61e` (license in `nanogpt/LICENSE`). Our edits to it are marked `[CS5090 patch]`: a `use_pos_emb` flag for the ablation, a configurable seed, a CSV loss log, and cwd-independent config loading.

## Documentation map
| Doc | What it covers |
|---|---|
| [docs/phase1.md](docs/phase1.md) | Model/data/training choices, concepts, ablation procedure, reading loss curves, limitations |
| [docs/kaggle_guide.md](docs/kaggle_guide.md) | Step-by-step GPU training on Kaggle (baseline and ablation), troubleshooting |
| [docs/phase2.md](docs/phase2.md) | Code-completion task protocol, accept/edit/reject definitions, report checklist |
| [docs/report_outline.md](docs/report_outline.md) | Final report structure, what's done/pending, repo checklist |
| [docs/ai_use_log.md](docs/ai_use_log.md) | AI-use log (add your own entries) |
| [DATASHEET.md](DATASHEET.md) | Corpus sources, filtering/dedup/split/tokenization numbers, licensing |
| [PREDICTION.md](PREDICTION.md) | Ablation prediction (committed before the ablation run) |

## Setup
Python 3.11+ (developed on 3.14). A GPU is needed only for training; everything else runs on CPU.
```bash
pip install -r requirements.txt     # after the Kaggle runs, pin exact versions from results/*_run_metadata.json
```

## Reproduce
```bash
# Phase 1: data (~15 min, ~880 MB download)
python scripts/collect.py            # clone 28 repos at pinned SHAs (data/sources.txt) -> data/raw
python scripts/filter_dedup.py       # filter, dedup, split 90/5/5 by file -> data/processed/*.jsonl
python scripts/train_tokenizer.py    # BPE-8192, TRAIN split only
python scripts/prepare.py            # -> data/code/{train,val,test}.bin + meta.pkl

# Phase 1: training (GPU; see docs/kaggle_guide.md, or notebooks/kaggle_train.ipynb on Kaggle)
python nanogpt/train.py configs/baseline.py
python nanogpt/train.py configs/ablation_nopos.py     # one change: no position embeddings
python scripts/plot_loss.py                           # -> results/loss_curves.png
python scripts/sample.py --ckpt out-baseline/ckpt.pt --prompt "x = a - b" --seed 1

# Phase 2: code completion on 20 held-out functions (see docs/phase2.md)
python scripts/make_phase2_inputs.py                  # -> phase2/inputs.jsonl, blank phase2/judgments.csv
python scripts/run_phase2.py --ckpt out-baseline/ckpt.pt
#   ...judge each output by hand in phase2/judgments.csv...
python scripts/phase2_summary.py
```
Seed 1337 throughout. Run all commands from the repository root.

## Layout
```
configs/            baseline + ablation configs
data/sources.txt    28 repos pinned to commit SHAs (+ license)
docs/               guides and report scaffolding
nanogpt/            vendored model/trainer (patched, see above)
notebooks/          kaggle_train.ipynb
phase2/             inputs, outputs, judgments
results/            loss CSVs, logs, curves, generations, run metadata
scripts/            data pipeline, sampling, plotting, Phase 2 tooling
```
Not in git (rebuilt by the scripts): `data/raw/`, `data/processed/`, `data/code/*.bin`, checkpoints (`out-*/`).

## Status
- [x] Data pipeline run end to end (13,369 files; 47,653,184 train tokens)
- [x] Both configs smoke-tested on CPU; parameter counts verified
- [x] Ablation prediction written and committed
- [x] Phase 2 inputs generated (20 functions from 20 repos); runner and summary dry-run tested
- [ ] Baseline trained on Kaggle  ← **next step**, see [docs/kaggle_guide.md](docs/kaggle_guide.md)
- [ ] Ablation trained and compared (val loss + side-by-side generation)
- [ ] Phase 2: run model, judge 20 outputs by hand
- [ ] Phase 3: probe set, findings CSV (not started)
- [ ] Phase 4: intervention and re-evaluation (not started)
- [ ] Final report, AI-use log, handwritten reflection (due Oct 30)
