# Phase 4 — Improve & Re-evaluate

**Rules (assignment):** state the hypothesis before the experiment; change one main thing; re-run the same Phase 3 probes under comparable conditions; report improvements **and** regressions; report compute cost and validation loss where relevant; a well-designed negative result is acceptable.

**Chosen intervention:** decoding change, a no-repeat 8-gram rule, aimed at the repetition-loop failures (13 of 26 baseline failures). Hypothesis, predictions and threats are in [PHASE4_HYPOTHESIS.md](../PHASE4_HYPOTHESIS.md). **Do not run the experiment until that file is edited by you and committed.**

## Already verified (before the hypothesis was written)
- `scripts/decoding.py` reproduces nanoGPT's sampler line for line: with the rule off, all **26/26** baseline probe completions are reproduced exactly (`phase3/outputs_control.jsonl`).
- The rule works: on a made-up prompt (not a probe), 119 repeated 8-token windows without it, 0 with it.
- Baseline: the outputs that ran to the 200-token cap are exactly the 13 you labelled as loops, so "ran to the cap" is a valid objective loop measure on the baseline.

## Procedure (after the hypothesis is committed)
```bash
# main arm (the claim)
python scripts/run_phase3.py --ckpt out-baseline/ckpt.pt --no_repeat_ngram 8 --tag after
# regression check on the Phase 2 inputs, written to a separate file (the original phase2/outputs.jsonl is untouched)
python scripts/run_phase2.py --ckpt out-baseline/ckpt.pt --no_repeat_ngram 8 --out phase2/outputs_after.jsonl
# exploratory arms (pre-declared in the hypothesis file, reported in full)
python scripts/run_phase3.py --ckpt out-baseline/ckpt.pt --temperature 0.8 --tag after_t08
python scripts/run_phase3.py --ckpt out-baseline/ckpt.pt --no_repeat_ngram 4  --tag after_n4
python scripts/run_phase3.py --ckpt out-baseline/ckpt.pt --no_repeat_ngram 16 --tag after_n16
python scripts/phase4_compare.py          # automatic table: loops, parses, repeated lines, time, per-probe changes
```
Each Phase 3 run takes about 100 s on this CPU. The runs write `phase3/outputs_<tag>.jsonl` and `review_<tag>.md`; `phase3/findings.csv` and the baseline outputs are never overwritten.

## Your part: re-judge
1. For each arm you want to report (at least `after`), copy `phase3/findings.csv` to `phase3/findings_<tag>.csv`, clear the judgment columns (outcome, category, severity, why_wrong, how_found, unit_tests_would_catch), and re-judge all 26 with the **same rules** you used in Phase 3. Judge the outputs in `review_<tag>.md` before looking at the automatic table (reduces bias).
2. `python scripts/phase4_compare.py` then also prints pass counts, categories and the per-probe category moves (before -> after), so improvements and regressions are both visible.
3. Phase 2 regression check: compare parse rate (and re-judge if the outputs changed much) between `phase2/outputs.jsonl` (7/20 parse) and `phase2/outputs_after.jsonl`.

## What goes in the report (section 4)
Target failure and hypothesis; the intervention and why it follows from the Phase 3 evidence; before/after on the same probes (table of categories, loop counts, parses); regressions; cost (generation time, no retraining, validation loss unchanged); threats to validity; whether it worked **for the reason expected** (the exploratory arms help here) and what you would try next.

## Results (hypothesis committed first: `PHASE4_HYPOTHESIS.md`, commit b934f05; runs 2026-10-18/19; re-judged by the author)
Main arm: `--no_repeat_ngram 8`, everything else identical to the baseline (same checkpoint, 26 probes, temp 0.2, top-k 50, 200 tokens, seeds, CPU). Files: `phase3/outputs_after.jsonl`, `review_after.md`, `findings_after.csv` (your judgments), `phase2/outputs_after.jsonl`.

| Measure | Baseline | Prediction | Actual | Verdict |
|---|---|---|---|---|
| Probes running to the 200-token cap | 13/26 | at most 6 | **4** | met |
| Failures judged `other` (loop) | 13 | at most 6 | **4** | met |
| Outputs that parse | 13/26 | 15-19 | **21** | outside the range (better than predicted) |
| Probes judged passing | 0/26 | 0-3 | **0** | met |
| wrong-logic / context-ignored / invented-api (each stays or rises) | 5 / 4 / 3 | not lower | **12 / 5 / 2** | invented-api fell (3 -> 2), so this prediction failed in part |
| Phase 2 parse rate (regression check) | 7/20 | at least 7 | **10/20** | met |

Category moves (before -> after, 26 probes): 16 unchanged; other -> wrong-logic 7, other -> context-ignored 1, other -> syntax 1, invented-api -> syntax 1. New category: `syntax` (0 -> 2). Author's severity: high 19 -> 14, medium 7 -> 12.
Improvements: 9 of the 13 loops no longer reach the token cap (p3-01, 02, 03, 04, 05, 12, 19, 22, 25). Still looping: p3-08, 13, 21, 24. Regressions: p3-18 stopped parsing (also in the n = 4 arm); on Phase 2, p2-01 stopped parsing (4 started parsing). 12 of 26 outputs are byte-identical to the baseline.
Cost: generation time 98 s -> 105 s per 26 probes on this CPU (+7%); no retraining; validation loss unchanged (weights unchanged).

### Exploratory arms (automatic metrics only; not re-judged; one sample per probe)
| Arm | n-gram | temp | cap-runs | parses | mean repeated-line fraction |
|---|---|---|---|---|---|
| baseline | 0 | 0.2 | 13/26 | 13/26 | 0.42 |
| main (n = 8) | 8 | 0.2 | 4/26 | 21/26 | 0.14 |
| after_t08 | 0 | 0.8 | 3/26 | 20/26 | 0.14 |
| after_n4 | 4 | 0.2 | 5/26 | 18/26 | 0.05 |
| after_n16 | 16 | 0.2 | 5/26 | 22/26 | 0.25 |

### Reading the results (to check against the CSVs before using)
- The intervention did what the hypothesis said and no more: it removed most loops (13 -> 4) and the freed outputs became ordinary wrong code (mostly wrong-logic), so **correct outputs stayed at 0/26**. It removed a symptom, not the capability gap. This is one of the outcomes the hypothesis said would challenge the expectation of "improvement".
- Whether it worked **for the reason expected**: only partly. All four settings cut loops to 3-5 of 26, and raising the temperature to 0.8 with *no* n-gram rule was as effective as the n = 8 rule (3 vs 4). So loops depend on decoding, but the specific rule was not necessary; the temperature half of the hypothesis is at least as supported as the repetition half. Differences of 1-2 probes between arms are within sampling noise (one sample per probe).
- Parsing is not correctness: parses rose 13 -> 21 and passes did not move.
- Not tested: whether a repetition penalty, a larger token limit, or sampling several candidates changes anything; whether a better model (more data, more training) would stop looping on its own.

### Threats to validity (see also PHASE4_HYPOTHESIS.md)
One sample per probe and arm; the diagnosis used the same 26 probes; judging was not blind (the author glanced at outputs before re-judging); the exploratory arms were not re-judged; the 200-token cap and temperature 0.2 are both part of the baseline condition.
