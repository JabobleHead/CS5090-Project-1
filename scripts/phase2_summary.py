"""Summarise Phase 2: accept / edit / reject counts from phase2/judgments.csv plus parse rate from outputs.jsonl.
Decisions are filled in BY HAND (accept | edit | reject); this script never judges anything."""
import csv, json, sys
from collections import Counter
from pathlib import Path

P2 = Path(__file__).resolve().parents[1] / "phase2"
LABELS = {"accept": "Accept as-is", "edit": "Accept after editing", "reject": "Reject"}


def main():
    rows = list(csv.DictReader(open(sys.argv[1] if len(sys.argv) > 1 else P2 / "judgments.csv", encoding="utf-8")))
    decided = [r for r in rows if r["decision"].strip()]
    bad = [r["id"] for r in decided if r["decision"].strip().lower() not in LABELS]
    if bad:
        sys.exit(f"invalid decision (use accept | edit | reject) for: {bad}")
    counts = Counter(r["decision"].strip().lower() for r in decided)
    print(f"judged {len(decided)}/{len(rows)}\n\n| Outcome | Count |\n|---|---|")
    for k, label in LABELS.items():
        print(f"| {label} | {counts.get(k, 0)} |")
    out = P2 / "outputs.jsonl"
    if out.exists():
        outs = [json.loads(l) for l in open(out, encoding="utf-8")]
        print(f"\nparse rate (prompt+completion is valid Python): {sum(o['parses'] for o in outs)}/{len(outs)}")
    mins = [float(r["minutes_to_check"]) for r in decided if r["minutes_to_check"].strip()]
    if mins:
        print(f"mean minutes spent checking/editing: {sum(mins) / len(mins):.1f}")
    print("\nPick for the report (your call): best =", [r["id"] for r in decided if r["decision"] == "accept"][:5],
          "| worst/near-miss candidates =", [r["id"] for r in decided if r["decision"] == "reject"][:5])


if __name__ == "__main__":
    main()
