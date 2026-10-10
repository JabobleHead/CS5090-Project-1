"""Build phase2/review.md: each input's prompt, the model's completion and the original body, side by side, for judging by hand.
  python scripts/make_review_sheet.py
Judgments themselves go in phase2/judgments.csv (this script never judges anything)."""
import json
from pathlib import Path

P2 = Path(__file__).resolve().parents[1] / "phase2"


def main():
    inputs = {r["id"]: r for r in map(json.loads, open(P2 / "inputs.jsonl", encoding="utf-8"))}
    outs = [json.loads(l) for l in open(P2 / "outputs.jsonl", encoding="utf-8")]
    parts = ["# Phase 2 review sheet\n",
             "For each item: read the PROMPT, then the MODEL OUTPUT, then (last) the ORIGINAL. Decide `accept`, `edit` or `reject` "
             "and write it in `judgments.csv` (see docs/phase2.md). Judge whether the model's code is correct and usable for the "
             "signature/docstring, not whether it matches the original. `parses` only means it is valid Python.\n"]
    for o in outs:
        i = inputs[o["id"]]
        parts.append(f"\n---\n\n## {o['id']}  ({i['path']})   parses: {o['parses']}\n")
        parts.append("**PROMPT (what the model saw)**\n```python\n" + i["prompt"].rstrip() + "\n```\n")
        parts.append("**MODEL OUTPUT (the body it wrote)**\n```python\n" + (o["completion"].rstrip() or "(empty)") + "\n```\n")
        parts.append("**ORIGINAL BODY (for comparison only)**\n```python\n" + i["reference_body"].rstrip() + "\n```\n")
    (P2 / "review.md").write_text("\n".join(parts), encoding="utf-8")
    print("wrote", P2 / "review.md", f"({len(outs)} items)")


if __name__ == "__main__":
    main()
