# Phase 4 Hypothesis and Prediction

**Status: Draft. I need to review and commit this before running any experiments.**

The git commit timestamp will show that I recorded my predictions before the experiment, just like `PREDICTION.md`. No intervention runs have been completed, and no `phase3/outputs_after*.jsonl` files exist yet.

## Target Failure Pattern

In Phase 3, 13 of the 26 baseline failures were repetition loops. The model repeated a line or block until it reached the 200-token limit, leaving code that did not parse.

Examples included `if n < 0: return False`, `"text": text,`, and `cursor.execute("SELECT ...`.

The same 13 probes reached the token limit and were labeled as repetition loops: p3-01, 02, 03, 04, 05, 08, 12, 13, 19, 21, 22, 24, and 25.

## Hypothesis

I think the repetition loops are mainly caused by decoding. The baseline uses temperature 0.2 and top-k 50, with no rule to discourage repeated text. Once the model writes a line, repeating it may remain the most likely next choice.
The other 13 test cases stopped on their own, which shows that the model can end a completion. This supports my hypothesis, but it does not prove that decoding causes the loops. I expect blocking repeated token sequences to reduce most of them.

## Intervention

I will use a no-repeat n-gram rule with **n = 8** in `scripts/decoding.py`, enabled with `--no_repeat_ngram 8`.

The rule blocks a token if it would complete an eight-token sequence that already appears in the prompt or generated output.

Everything else will match the baseline:

- Checkpoint: `out-baseline/ckpt.pt`
- The same 26 probes
- Temperature: 0.2
- Top-k: 50
- Maximum new tokens: 200
- Seeds: 1337+i
- Device: CPU
- No retraining

I chose n = 8 before running the intervention because the repeated lines appear to be roughly 8–10 tokens long. A smaller value, such as 3 or 4, could block common sequences that valid code needs to repeat.

Before writing this prediction, I checked that disabling the rule reproduces all 26 baseline completions exactly. This supports attributing differences in the main run to the rule.

## Predictions

These predictions will be fixed before the experiment.

| Measure | Baseline | Prediction |
|---|---|---|
| tests reaching the 200-token limit | 13/26 | At most 6/26 |
| Failures labeled `other` because of repetition loops | 13 | At most 6 |
| Outputs that parse | 13/26 | 15–19/26 |
| Outputs judged as passing | 0/26 | 0–3/26 |
| `wrong-logic`, `context-ignored`, and `invented-api` failures | 5 / 4 / 3 | Each count stays the same or increases |
| Phase 2 regression check: outputs that parse | 7/20 | At least 7/20 |

I expect only a small improvement in correct answers because the rule changes decoding without changing the model’s knowledge. 
## Results That Would Challenge My Expectations

- **10 or more probes still reach the token limit:** 

- **Loops disappear, but no outputs pass:** 

- **The parse rate or Phase 2 result gets worse:** 

- **The model repeats slightly different versions of the same line:** 
## Exploratory Runs

I will run three additional settings on the same probes and report all results.

| Run | Change | Purpose |
|---|---|---|
| `after_t08` | Temperature 0.8, no n-gram rule | Check whether increasing temperature reduces loops |
| `after_n4` | n = 4, other baseline settings unchanged | Check sensitivity to a smaller n |
| `after_n16` | n = 16, other baseline settings unchanged | Check sensitivity to a larger n |

These runs are separate from the main n = 8 experiment. I will report any disagreements with the main result and will not select a setting afterward because it performs best.

## Measures and Costs

I will report:

- Number of outputs reaching the token limit
- Number of repetition loops based on my review
- Parse count and pass count
- Failure-category counts
- Per-probe improvements and regressions
- Phase 2 regression results
- Generation time for each set of 26 probes

I will judge all 26 new outputs using the same written rules and findings columns as before.

The baseline took 98 seconds on this CPU. I will compare each run against that time. Validation loss will remain unchanged because the intervention does not change the model’s weights.
