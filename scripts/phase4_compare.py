"""Compare Phase 3 runs: baseline vs intervention arms (same probes, same seeds). Prints tables; judges nothing.

  python scripts/phase4_compare.py                       # baseline vs every phase3/outputs_<tag>.jsonl except 'control'
  python scripts/phase4_compare.py after_n8 after_t08    # only these tags

Automatic columns: loops = outputs that ran to the 200-token cap (matched the author's 13 'repetition loop' labels exactly
on the baseline), parses, mean fraction of repeated lines, generation seconds. If phase3/findings_<tag>.csv exists (your
re-judging of that arm, same columns as findings.csv) it also prints pass/fail, categories and per-probe changes.
"""
import csv, json, sys
from collections import Counter
from pathlib import Path

P3 = Path(__file__).resolve().parents[1] / "phase3"


def load_outputs(tag):
    fn = P3 / ("outputs_control.jsonl" if tag == "baseline" else f"outputs_{tag}.jsonl")  # control == baseline, but has the extra fields
    return {r["id"]: r for r in map(json.loads, open(fn, encoding="utf-8"))}


def load_findings(tag):
    fn = P3 / ("findings.csv" if tag == "baseline" else f"findings_{tag}.csv")
    return {r["probe_id"]: r for r in csv.DictReader(open(fn, encoding="utf-8"))} if fn.exists() else None


def main():
    tags = sys.argv[1:] or sorted(p.stem.removeprefix("outputs_") for p in P3.glob("outputs_*.jsonl")
                                  if p.stem not in ("outputs_control",))
    arms = ["baseline"] + tags
    data = {t: load_outputs(t) for t in arms}
    ids = list(data["baseline"])
    print("| arm | ngram | temp | loops (ran to cap) | parses | mean repeated-line fraction | generation s (26 probes) |\n|---|---|---|---|---|---|---|")
    for t in arms:
        o = data[t]
        s = next(iter(o.values()))["settings"]
        print(f"| {t} | {s.get('no_repeat_ngram', 0)} | {s['temperature']} | {sum(r['ended'] == 'limit' for r in o.values())}/26 | "
              f"{sum(r['parses'] for r in o.values())}/26 | {sum(r['repeat_line_ratio'] for r in o.values()) / len(o):.2f} | {sum(r['gen_seconds'] for r in o.values()):.0f} |")
    for t in tags:
        b, a = data["baseline"], data[t]
        print(f"\n--- {t}: per-probe automatic changes vs baseline ---")
        fixed = [i for i in ids if b[i]["ended"] == "limit" and a[i]["ended"] != "limit"]
        newloop = [i for i in ids if b[i]["ended"] != "limit" and a[i]["ended"] == "limit"]
        gained = [i for i in ids if not b[i]["parses"] and a[i]["parses"]]
        lost = [i for i in ids if b[i]["parses"] and not a[i]["parses"]]
        same = [i for i in ids if b[i]["completion"] == a[i]["completion"]]
        print(f"loop -> no longer hits the cap: {fixed}\nnew cap-runs (regressions): {newloop}\nnow parses: {gained}\nstopped parsing (regressions): {lost}\n"
              f"identical output to baseline: {len(same)}/26")
        fb, fa = load_findings("baseline"), load_findings(t)
        if fa and all(r["outcome"] in ("pass", "fail") for r in fa.values()):
            print(f"\n--- {t}: your re-judging (findings_{t}.csv) ---")
            for name, f in (("baseline", fb), (t, fa)):
                c = Counter(r["category"] if r["outcome"] == "fail" else "PASS" for r in f.values())
                print(f"{name:<12} pass {c.get('PASS', 0)}/26 | " + ", ".join(f"{k} {v}" for k, v in c.most_common() if k != "PASS"))
            moves = Counter((fb[i]["category"] if fb[i]["outcome"] == "fail" else "PASS",
                             fa[i]["category"] if fa[i]["outcome"] == "fail" else "PASS") for i in ids)
            print("category moves (before -> after): " + "; ".join(f"{x}->{y}: {n}" for (x, y), n in sorted(moves.items()) if x != y))
            print("unchanged category:", sum(n for (x, y), n in moves.items() if x == y))
        elif fa is None:
            print(f"\n(no findings_{t}.csv yet: copy phase3/findings.csv's probe ids/groups, clear the judgment columns, and re-judge)")


if __name__ == "__main__":
    main()
