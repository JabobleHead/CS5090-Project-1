# Data sheet

## Sources
28 permissively licensed Python repositories, each pinned to an exact commit SHA in [`data/sources.txt`](data/sources.txt) (collected 2026-09-30 by `scripts/collect.py`, shallow clone at the SHA). `collect.py` fails if a repo has no LICENSE/COPYING file at that SHA. Licenses: BSD-3-Clause, MIT, Apache-2.0, Pillow's HPND, matplotlib's PSF-based license (all allow reuse with attribution/notice).
**TODO (licensing section of report):** open each LICENSE file once and confirm the license column; note that training on the code is not the same as redistributing it, and that Phase 3 `memorised` outputs may reproduce licensed code verbatim (attribution concern).

## Processing (`scripts/filter_dedup.py`)
**Canonical numbers are from the Kaggle run** (Python 3.13.15, Linux; `results/data_artifacts/stats.json`, `token_stats.json`, `tokenizer.json`, `test.jsonl`), because that is the corpus and tokenizer the checkpoints were trained with. A rebuild on another machine can differ slightly: the `ast.parse` filter depends on the Python version (3.14 on the author's laptop accepts ~9 more files than 3.13). Line endings are normalised to LF in the pipeline: before that fix, Windows git checkouts (`core.autocrlf`) put CRLF line endings in 11,591 of 12,041 local training files. The tokenizer is only valid with its own checkpoint, so it ships in `results/data_artifacts/`.
| Stage | Files |
|---|---|
| `.py` files found (outside `.git`, docs, build, vendor dirs) | 15,439 |
| rejected: size < 200 B or > 200 KB | 1,917 |
| rejected: not UTF-8 | 0 |
| rejected: fails `ast.parse` | 14 |
| rejected: minified / "auto-generated" header / line > 1000 chars | 29 |
| removed: exact duplicates (whitespace-normalised sha256) | 31 |
| removed: near-duplicates (MinHash LSH, 5-token shingles, Jaccard >= 0.85) | 111 |
| **kept** | **13,337** |

Dedup runs **before** the split so near-duplicates cannot leak between train and validation. Test files are kept in the repo (Phase 2-4 may use them).

## Split
By hash of the file path: 90 / 5 / 5 -> train 12,012 files (164.0 M chars), val 677 files (9.8 M), test 648 files (7.9 M). Split is by file, not by random chunk, so validation measures generalisation to unseen files (though same-repo style overlap remains: a known limitation).

## Tokenization (`scripts/train_tokenizer.py`, `scripts/prepare.py`)
Byte-level BPE, vocab 8,192 (incl. `<|endoftext|>` id 0), trained on the **train split only**. Documents are concatenated with `<|endoftext|>` separators into uint16 `.bin` files. Round-trip decode spot-check on every 50th file; hash-overlap check between splits.

| Split | Tokens | Chars/token |
|---|---|---|
| train | 47,778,474 | 3.43 |
| val | 2,856,401 | 3.43 |
| test | 2,372,921 | 3.35 |

## Token budget vs the "20 x params" guideline
Model = 13.96 M params (13.77 M without position embeddings). 20 x 13.96 M = ~279 M tokens; the corpus has 47.8 M, so the baseline run (8,400 iters x 64 x 512 = 275 M tokens) makes **~5.8 passes** over the training data. Expect val loss to flatten or rise late in training (overfitting) and more verbatim memorisation; both are reported, not hidden.

## Known limitations
- Scientific/web-framework library code dominates; little application or script-style code; tests included.
- Python 3 only; no deduplication against the wider internet (repos also vendor each other's ideas).
- Not filtered for secrets or PII beyond what upstream repos contain.
