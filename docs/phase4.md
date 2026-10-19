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
