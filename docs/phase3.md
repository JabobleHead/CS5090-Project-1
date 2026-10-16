# Phase 3 — Evaluate & Break

**Goal (assignment):** build a probe set of about 20–30 inputs designed to expose weaknesses, document **at least 10 failure instances** across **multiple failure categories (4+ where the model allows)** rather than many variations of one mistake, and record for each failure: the input, the relevant output, category, severity, a specific one-line reason, how you found it, and whether a normal unit-test suite would likely catch it. Keep the full findings table as a CSV in the repo.

## What is already built
| Item | File |
|---|---|
| 26 probes in 6 groups, each with a "correct answer would…" note | `phase3/probes.jsonl`, summary in `phase3/probes_design.md` (built by `scripts/make_phase3_probes.py`) |
| Baseline outputs, fixed settings (temp 0.2, top-k 50, 200 tokens, seed 1337+i) | `phase3/outputs.jsonl` (`scripts/run_phase3.py`) |
| Readable review sheet with automatic hints | `phase3/review.md` |
| Empty findings table, one row per probe | `phase3/findings.csv` |

Prompts end the way the training data tokenises an indented line (the Phase 2 tokenizer-boundary fix, handled by the runner).

## The probe design (what each group tests and why)
| Group (n) | What it targets | Failure categories it can reveal |
|---|---|---|
| ordinary (4) | easy, common tasks: a sanity baseline | wrong-logic, syntax, invented-api |
| misleading (4) | docstring/comment/name contradicting each other; the docstring is the spec | context-ignored, wrong-logic |
| long-context (3) | a constant or helper defined ~200+ tokens earlier that must be used | context-ignored, invented-api |
| security (6) | command injection, SQL injection, weak hashing, unsafe YAML, disabled TLS verification, path traversal | insecure |
| variation (6 = 3 pairs) | the same task worded two ways (docstring vs comment, different name/types) | prompt-sensitive |
| training-similar (3) | real functions from the training split (one per repo, seeded) | memorised |

Why these: they map one-to-one to the assignment's list (ordinary inputs, misleading comments or names, long-context inputs, security-related prompts, prompt variations, prompts similar to the training data) and to the category names. Phase 4 will re-run **these same probes**, so none may be added or edited after the first judging.

## What you do (judging is yours)
1. Open [phase3/review.md](../phase3/review.md). For each of the 26 probes read the prompt, the "correct answer would…" line and the model output. The hints are automatic and can be wrong or incomplete (for example the security regexes do not know that `hashlib.sha256(password)` is also a weak, unsalted choice).
2. In `phase3/findings.csv`, set `outcome` to `pass` or `fail` for every probe. For each **failure** also fill:
   - `category`: exactly one of `syntax`, `invented-api`, `wrong-logic`, `insecure`, `memorised`, `prompt-sensitive`, `context-ignored`, `other` (explain why in `why_wrong` if `other`)
   - `severity`: e.g. low / medium / high (define your scale in the report; suggested: high = silently wrong or exploitable, medium = wrong but obviously so, low = cosmetic or harmless)
   - `why_wrong`: one specific sentence (not "it is bad")
   - `how_found`: e.g. "read the output", "ran `ast.parse`", "compared with the paired probe", "grep in training data"
   - `unit_tests_would_catch`: `yes` / `no` / `maybe`, plus a few words (does an ordinary functional test fail, or would you need a security test or a static analyser?)
   - If one output has two distinct failures, add a second row with the same `probe_id`.
3. For the `variation` pairs, judge each member normally and additionally ask: did the rewording change the behaviour substantially? If so, record `prompt-sensitive` on the pair (one row is enough, say which probes).
4. For `training-similar`, check the hint (verbatim lines / similarity) but decide yourself whether the output is **memorised** (near-verbatim reproduction) or just generic.
5. Aim for at least 10 failures spread over 4+ categories. If the model fails everything in one way (see below), say so honestly and cover the other categories with the probes that do separate them.

## Things the first run already shows (to check, not to copy)
- Several outputs are **degenerate repetition** (the same `if` block, dict entry or call repeated until the token limit). Decide how to categorise this consistently (`other` with an explanation, or `wrong-logic`), and use the same choice everywhere. It is likely to dominate the findings, which is why the report should also cover the categories that the other probes separate out.
- The short, valid-looking one-liners (`return np.max(values)` for "return the smallest element", `return len(rows)`, `return hashlib.sha256(password)`) are the interesting ones: they parse, so only reading or a test reveals the problem. These are the "would a unit test catch it?" cases.
- Names that do not exist in the prompt context (`np`, `url.encode(...)`, `upload_dir.read(...)`) are candidates for `invented-api`.

## Checks to keep Phase 4 honest
- Same probes, same settings, same seeds: `python scripts/run_phase3.py --ckpt <new checkpoint> --tag after` writes `outputs_after.jsonl` and `review_after.md` without touching the baseline files; `findings.csv` is never overwritten by the runner.
- Per-probe pass/fail counts before and after are what the Phase 4 results table will be built from.

## Threats to validity (for the report)
- 26 probes and one sampled completion each at temperature 0.2: one-off sampling noise can flip a single probe's outcome.
- Probes are written by the author, so they reflect what the author thought of; no external benchmark.
- One judge; the categorisation of repetition loops is a judgment call.
- The model only completes code; "prompt variation" is limited to docstring/comment/name/type-hint rewordings.

## Report checklist (section 3)
- [ ] How the probe set was designed and what each group targets
- [ ] Failure distribution table (counts per category) and the most important 3–4 examples
- [ ] Interpretation of likely root causes (data, scale, objective, context, tokenizer)
- [ ] Fraction and types of failures that ordinary unit tests would and would not catch
