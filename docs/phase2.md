# Phase 2 — Use the model on a real SE task

**Task: code completion.** Given a Python function's signature (and docstring, if it has one), the baseline model writes the function body. You judge 20 outputs.

## Protocol
1. **Inputs (already generated):** `python scripts/make_phase2_inputs.py` → `phase2/inputs.jsonl` (20 inputs) and a blank `phase2/judgments.csv`.
   - Source: the held-out **test split** (`data/processed/test.jsonl`), which the tokenizer and model never saw.
   - One function per file, round-robin across repos (current set: 20 functions from 20 different repos), bodies of 6–30 lines, prompts ≤ 300 tokens, seeded (1337), and any function whose body appears verbatim in the training split is skipped (0 skipped in the current set).
   - The original body is stored as `reference_body` so you can compare. **Do not show the reference to the model.**
2. **Generate (needs the baseline checkpoint):**
   ```bash
   python scripts/run_phase2.py --ckpt out-baseline/ckpt.pt        # -> phase2/outputs.jsonl
   ```
   Fixed settings: temperature 0.2, top-k 50, up to 200 new tokens, per-input seed 1337+i, completion cut at `<|endoftext|>` or at the first line that returns to column 0. The settings are stored in each output record. `parses` is true only if the completion is non-empty and `prompt + completion` is valid Python.
3. **Judge by hand.** For each input, read the prompt, the model's completion and the reference, then fill one row of `phase2/judgments.csv`:
   - `decision`: `accept`, `edit`, or `reject`
   - `edit_needed`: what you had to change (for `edit`)
   - `minutes_to_check`: how long it took you to decide/fix
   - `notes`: anything worth remembering
4. **Summarise:** `python scripts/phase2_summary.py` prints the outcome table (Accept as-is / Accept after editing / Reject), parse rate and mean minutes.
5. **Pick three examples** for the report: the **best** result, the **worst**, and one **near-miss** (looked correct at first glance but was not; explain what exposed it, e.g. reading carefully, running it, comparing to the reference).

## What the decisions mean (use these consistently and say so in the report)
- **Accept as-is:** valid Python, does what the signature/docstring asks, you would keep it unchanged.
- **Accept after editing:** the idea is right and the fixes are small (wrong name, off-by-one, missing line). If fixing takes longer than writing it yourself, it is a **reject**.
- **Reject:** doesn't parse, wrong behaviour, irrelevant, repeats the prompt, or checking costs more than writing the code.
- Judge the *behaviour*, not similarity to the reference: a different but correct implementation is an accept.

## Be honest about
- A 14 M-parameter model trained on ~48 M tokens will mostly produce plausible-looking but wrong code. A high reject rate is an expected, reportable result, and the grade is for honest judgments, not good ones.
- Don't "fix" prompts or re-sample until the output looks good. If you try a second setting, report it as a separate run.
- Near-misses are the most valuable examples: write down *why* it looked right.

## Threats to validity (for the report)
- Test files come from the same 28 repos as training, so style overlap makes the task easier than truly unseen projects.
- 20 inputs is a small sample; report counts, not percentages with false precision.
- The functions are library code (numpy, django, ...) with long docstrings, not the everyday application code a developer might ask a model about.
- You are the only judge (no second reviewer).

## Report checklist
- [ ] SE task, input source, definition of "accept"
- [ ] Accept / edit / reject counts (table from `phase2_summary.py`)
- [ ] Best, worst, near-miss: prompt, output, short analysis
- [ ] When the model was useful vs when checking cost more than doing the work yourself
- [ ] Settings and checkpoint used (commit SHA, run metadata)

## Results (fill in after judging)
| Outcome | Count |
|---|---|
| Accept as-is | TODO |
| Accept after editing | TODO |
| Reject | TODO |
