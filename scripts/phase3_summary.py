"""Validate phase3/findings.csv against the assignment's rules, print the failure distribution, and write the full table
(input + relevant output + your columns) to phase3/findings_full.csv. Never judges anything.

  python scripts/phase3_summary.py [findings.csv] [outputs.jsonl]
"""
import csv, json, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P3 = ROOT / "phase3"
CATEGORIES = {"syntax", "invented-api", "wrong-logic", "insecure", "memorised", "prompt-sensitive", "context-ignored", "other"}
MAX_OUT_LINES = 12  # lines of the model output kept in the full table (the full text stays in outputs.jsonl)


def main():
    fpath = Path(sys.argv[1]) if len(sys.argv) > 1 else P3 / "findings.csv"
    opath = Path(sys.argv[2]) if len(sys.argv) > 2 else P3 / "outputs.jsonl"
    rows = list(csv.DictReader(open(fpath, encoding="utf-8")))
    outs = {r["id"]: r for r in map(json.loads, open(opath, encoding="utf-8"))}
    probes = {r["id"]: r for r in map(json.loads, open(P3 / "probes.jsonl", encoding="utf-8"))}

    problems = []
    for r in rows:
        if r["outcome"] not in ("pass", "fail"):
            problems.append(f"{r['probe_id']}: outcome must be pass or fail (got {r['outcome']!r})")
        if r["outcome"] == "fail":
            if r["category"] not in CATEGORIES:
                problems.append(f"{r['probe_id']}: category {r['category']!r} is not one of the 8 names")
            for col in ("severity", "why_wrong", "how_found", "unit_tests_would_catch"):
                if not r[col].strip():
                    problems.append(f"{r['probe_id']}: empty {col}")
            if r["category"] == "other" and not r["why_wrong"].strip():
                problems.append(f"{r['probe_id']}: 'other' needs an explanation")
    fails = [r for r in rows if r["outcome"] == "fail"]
    cats = Counter(r["category"] for r in fails)
    print(f"probes judged: {len(rows)} | pass {sum(r['outcome'] == 'pass' for r in rows)} | fail {len(fails)}")
    print(f"assignment checks: >=10 failures: {'OK' if len(fails) >= 10 else 'NO'} | >=4 categories: {'OK' if len(cats) >= 4 else 'NO'} ({len(cats)})")
    print(f"validation problems: {problems or 'none'}\n")
    print("| category | count |\n|---|---|")
    for c, n in cats.most_common():
        print(f"| {c} | {n} |")
    print("\nby probe group (fail / total):")
    for g in dict.fromkeys(r["group"] for r in rows):
        gr = [r for r in rows if r["group"] == g]
        print(f"  {g:<18}{sum(r['outcome'] == 'fail' for r in gr)}/{len(gr)}   categories: {dict(Counter(r['category'] for r in gr if r['outcome'] == 'fail'))}")
    print("\nseverity:", dict(Counter(r["severity"] for r in fails)))
    t = Counter(r["unit_tests_would_catch"].strip().lower().split(",")[0].split(" ")[0] for r in fails)
    print("unit tests would catch (first word of your answer):", dict(t))

    with open(P3 / "findings_full.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["probe_id", "group", "input", "relevant_output", "outcome", "category", "severity", "why_wrong", "how_found", "unit_tests_would_catch"])
        for r in rows:
            o = outs[r["probe_id"]]
            lines = o["completion"].rstrip().splitlines()
            shown = "\n".join(lines[:MAX_OUT_LINES]) + (f"\n... ({len(lines) - MAX_OUT_LINES} more lines in outputs.jsonl)" if len(lines) > MAX_OUT_LINES else "")
            w.writerow([r["probe_id"], r["group"], probes[r["probe_id"]]["prompt"].rstrip(), shown, r["outcome"], r["category"],
                        r["severity"], r["why_wrong"], r["how_found"], r["unit_tests_would_catch"]])
    print("\nwrote phase3/findings_full.csv")


if __name__ == "__main__":
    main()
