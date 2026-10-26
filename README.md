# CS 5090 Project 1 — small code language model

A GPT-style code model trained from scratch (6 layers / 6 heads / 384 emb, context 512, byte-level BPE with 8,192 tokens, 13.96 M parameters) on ~48 M tokens of permissively licensed Python, then used, probed and improved over four phases. Built on [nanoGPT](https://github.com/karpathy/nanoGPT), vendored at commit `3adf61e` (license in `nanogpt/LICENSE`). Our edits to it are marked `[CS5090 patch]`: a `use_pos_emb` flag for the ablation, a configurable seed, a CSV loss log, and cwd-independent config loading.

## Documentation map
| Doc | What it covers |
|---|---|
| [docs/phase1.md](docs/phase1.md) | Model/data/training choices, concepts, ablation procedure, reading loss curves, limitations |
| [docs/kaggle_guide.md](docs/kaggle_guide.md) | Step-by-step GPU training on Kaggle (baseline and ablation), troubleshooting |
| [docs/phase4.md](docs/phase4.md) | Phase 4 procedure (decoding intervention) and what to re-judge |
| [PHASE4_HYPOTHESIS.md](PHASE4_HYPOTHESIS.md) | Phase 4 hypothesis and predictions (draft until committed) |
| [docs/phase3.md](docs/phase3.md) | Probe-set design, how to judge and fill the findings CSV |
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
# Phase 3: probes (see docs/phase3.md)
python scripts/make_phase3_probes.py                       # -> phase3/probes.jsonl
python scripts/run_phase3.py --ckpt out-baseline/ckpt.pt   # -> phase3/outputs.jsonl, review.md, findings.csv (created once)
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
- [x] Data pipeline run end to end (13,337 files; 47,778,474 train tokens, Kaggle build)
- [x] Both configs smoke-tested on CPU; parameter counts verified
- [x] Ablation prediction written and committed
- [x] Phase 2 inputs generated (20 functions from 20 repos); runner and summary dry-run tested
- [x] Baseline trained on Kaggle (T4, ~40 min): final val loss **1.7128**, train 1.551; `results/baseline_loss.csv`, `results/loss_curves.png`
- [x] Ablation trained and compared: final val loss 1.7466 vs baseline 1.7128 (+0.034, prediction was +0.03 to +0.15); generations and an indentation probe in `results/` and [docs/phase1.md](docs/phase1.md) section 8. **Still to write:** the lesson, in your own words
- [x] Phase 2: 20 outputs generated and judged by hand: 0 accept / 0 edit / 20 reject (`phase2/judgments.csv`). **Still to do:** choose best / worst / near-miss for the report
- [x] Phase 3: 26 probes judged on the baseline: 26 fail / 0 pass; categories other 13 (repetition loops), wrong-logic 5, context-ignored 4, invented-api 3, insecure 1 (`phase3/findings.csv`, [docs/phase3.md](docs/phase3.md)). **Next:** Phase 4 (see [docs/phase4.md](docs/phase4.md))
- [x] Phase 4: no-repeat 8-gram decoding rule, hypothesis committed first. Loops 13 -> 4 of 26, parses 13 -> 21, **passes 0 -> 0**; loops mostly became wrong-logic ([docs/phase4.md](docs/phase4.md))
- [ ] Final report, AI-use log, handwritten reflection (due Oct 30)
