# Final report outline (6–8 pages, excluding appendices)

Submit on **Friday, October 30**: (1) this report, (2) the code repository. Everything else (findings table, AI-use log, configs, handwritten reflection scan) goes in appendices or the repo. Graded on understanding, experimental design, evidence, analysis and reproducibility; a well-supported negative result can earn full credit. Judged on rigor, verifiability/transparency, and presentation.

| # | Section | Contents | Source material | Status |
|---|---|---|---|---|
| 1 | Build & Understand (~2 pp) | Architecture and config, training setup, data processing, loss curve, ablation (prediction, exact change, result, lesson), limitations, data/licensing | [phase1.md](phase1.md), [DATASHEET.md](../DATASHEET.md), [PREDICTION.md](../PREDICTION.md), `results/loss_curves.png` | Code done; **needs Kaggle runs** |
| 2 | Use (~1 p) | Task, source of 20 inputs, definition of accept, counts table, best/worst/near-miss, when it was useful vs not | [phase2.md](phase2.md), `phase2/judgments.csv` | Inputs generated; **needs baseline + judging** |
| 3 | Evaluate & Break (~1.5 pp) | Probe-set design (20–30 probes), failure distribution, key examples, root causes, what unit tests would/wouldn't catch | Phase 3 (not started) | Not started |
| 4 | Improve & Re-evaluate (~1.5 pp) | Target failure, hypothesis (stated *before* running), one intervention, before/after on the same probes, regressions, cost, threats | Phase 4 (not started) | Not started |
| 5 | Discussion (~0.5 p) | What was learned, threats to validity, what to try next | all | Not started |
| A | Appendices | Full findings table (CSV in repo), AI-use log, handwritten reflection scan, configs, extra plots | [ai_use_log.md](ai_use_log.md) | Log started |

## Phase 3 category names (use exactly)
`syntax`, `invented-api`, `wrong-logic`, `insecure`, `memorised`, `prompt-sensitive`, `context-ignored`, `other` (explain). Per failure record: input, relevant output, category, severity, one-line why-wrong, how found, would a normal unit-test suite catch it.

## Phase 4 rules to remember
State hypothesis before the run · change one main thing · re-run the same Phase 3 probes under comparable conditions · report improvements **and** regressions · report compute cost / val loss where relevant · a negative result is acceptable.

## Repository checklist (from the assignment)
- [x] README with setup/reproduction instructions
- [x] Environment/dependency spec and code version (`requirements.txt`; pin exact versions from `results/*_run_metadata.json` after the Kaggle runs)
- [x] Data preparation / rebuild instructions
- [ ] Baseline and ablation configs (written; results pending)
- [ ] Phase 2 input/result records (inputs done; results pending)
- [ ] Phase 3 probe set and findings CSV
- [ ] Phase 4 intervention code/config and before/after results
- [ ] AI-use log (started, [ai_use_log.md](ai_use_log.md))

## Not forgotten
- One-page **handwritten** reflection, written without AI, scanned/photographed into an appendix. Questions: what can you explain now that you couldn't before; did building your own model change how you judge Copilot/ChatGPT; which phase taught you the most; what about language models still confuses you.
- Budget: ≲ 15 GPU-hours across the project.
- Intermediate dates are recommended milestones, not deadlines (Phase 1 was suggested by Sep 25, Phase 2 by Oct 9, Phase 3 by Oct 16, Phase 4 by Oct 23).
