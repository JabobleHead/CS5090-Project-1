# AI-use log

The assignment asks for a lightweight log of *representative, meaningful* interactions, not every completion: where AI saved time, where it was confidently wrong, what had to be fixed, and how each suggestion was verified. Entries below were recorded from the actual working session with Claude Code (assistant) on this repo. **Add your own entries**, especially for Phases 2–4 and for anything you decided against the assistant's advice. The one-page reflection is separate and must be handwritten without AI.

| # | Date | What I asked / what the AI did | Outcome | How it was verified |
|---|---|---|---|---|
| 1 | 2026-09-30 | Read the assignment PDF, proposed a Phase 1 plan (nanoGPT, Kaggle, BPE-8192, position-embedding ablation) and built the data pipeline | **Saved time** (pipeline, configs, notebook in one session) | Ran every stage locally; checked outputs (counts, tokenizer round-trip, no train/val overlap) |
| 2 | 2026-09-30 | First pipeline run on 6 starter repos produced only 1.05 M train tokens | AI flagged that this was ~250× below the "20 × parameters" budget; I chose to expand to 28 repos (47.7 M tokens) | Measured token counts after each run; documented the remaining ≈5.8-epoch deviation in DATASHEET.md |
| 3 | 2026-09-30 | AI patched nanoGPT's CSV logging with a script that wrote literal newlines into a string | **Confidently wrong:** `SyntaxError` on the first smoke run | Smoke-tested both configs on CPU before any GPU time was spent; fixed to `\n` escapes |
| 4 | 2026-09-30 | AI's first `filter_dedup.py` / `prepare.py` used per-token `MinHash.update` and a Python list of ints | Would have been hours slow and several GB of RAM at 100 M+ tokens; AI rewrote before running at scale (`update_batch`, per-document uint16 arrays) | Full-corpus run: dedup ≈ 2 min, tokenization ≈ 23 s |
| 5 | 2026-09-30 | A very large single shell command with nested quoting for creating many files | Failed with a quoting error and wrote nothing | Switched to writing files individually; checked that nothing was half-written |
| 6 | 2026-10-06 | AI said `PREDICTION.md` was unfinished | **Wrong:** my local copy was stale; the completed prediction was on the remote | I ran `git fetch`; the remote commit "Addded Perdiction" had the full text; fast-forwarded |
| 7 | 2026-10-06 | Wrote `scripts/run_phase2.py`; dry run on a smoke checkpoint | Caught a flaw: signature + docstring alone is valid Python, so an empty completion counted as "parses" | Dry-run printed 20/20 "parses" for gibberish; fixed to require a non-empty completion, re-ran: 0/20 |
| 8 | 2026-10-06 | AI estimated "2–4 GPU hours" for the baseline | Only a rough guess; the real number comes from the Kaggle smoke-test iteration time | Replace with measured time after the run (kaggle_guide.md explains how to estimate) |

## Template for new entries
```
| # | Date | What I asked / what the AI did | Outcome (saved time / wrong / fixed) | How it was verified |
```
Prompts worth logging: anything where the AI produced code you ran, anything it got wrong, anything that changed an experimental decision, and any place you overrode it.

## Honesty notes
- The assistant did not write the prediction or judge Phase 2 outputs. It did give feedback on an early draft of the prediction (pointing at the causal-mask leak and suggesting a code-based example). **Author: add an entry saying how much of the final `PREDICTION.md` text was yours vs AI-assisted, so this log is accurate.** Phase 2 judgments must be entirely yours.
- AI-generated code is verified by running it (smoke tests, dry runs), not by reading it alone.
