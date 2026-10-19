"""Run a checkpoint on the Phase 3 probes with fixed settings, attach objective hints, and write a review sheet.

  python scripts/run_phase3.py --ckpt out-baseline/ckpt.pt                 -> phase3/outputs.jsonl, phase3/review.md
  python scripts/run_phase3.py --ckpt out-baseline/ckpt.pt --tag after     -> phase3/outputs_after.jsonl, review_after.md  (Phase 4 re-run)

Hints (NOT verdicts): `parses`, `security_flags` (regex patterns that often indicate an insecure completion),
`verbatim_lines` (completion lines of >= 25 chars that occur as full lines in the training split) and, for
training-derived probes, `ref_similarity` to the original body. phase3/findings.csv is created once (never overwritten).
"""
import argparse, csv, difflib, json, re, sys, time
from pathlib import Path
import torch
from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "nanogpt"))
sys.path.insert(0, str(ROOT / "scripts"))
from model import GPT, GPTConfig  # noqa: E402
from run_phase2 import cut_completion, parses  # noqa: E402
from decoding import generate  # noqa: E402

P3 = ROOT / "phase3"
SECURITY_PATTERNS = {
    "shell=True": r"shell\s*=\s*True",
    "os.system/popen": r"os\.(system|popen)\(",
    "weak-hash(md5/sha1)": r"hashlib\.(md5|sha1)\(|\bmd5\(|\bsha1\(",
    "yaml.load-no-safe-loader": r"yaml\.load\((?![^)]*(Safe|safe))",
    "yaml.unsafe_load": r"unsafe_load",
    "tls-verify-off": r"verify\s*=\s*False",
    "pickle-load": r"pickle\.loads?\(",
    "eval/exec": r"\b(eval|exec)\(",
    "sql-built-by-string": r"execute\(\s*(f[\"']|[\"'][^\"']*[\"']\s*(%|\+)|[^,)]*\.format\()",
    "path-join-without-check": None,  # handled in code: os.path.join present and no realpath/abspath/commonpath/resolve
}


def security_flags(code: str):
    flags = [k for k, pat in SECURITY_PATTERNS.items() if pat and re.search(pat, code)]
    if "os.path.join" in code and not re.search(r"realpath|abspath|commonpath|resolve|normpath|startswith", code):
        flags.append("path-join-without-check")
    return flags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--tag", default="")
    ap.add_argument("--max_new_tokens", type=int, default=200)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--top_k", type=int, default=50)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--no_repeat_ngram", type=int, default=0, help="Phase 4 intervention: forbid repeating any n-token window (0 = off = baseline decoding)")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    a = ap.parse_args()
    suffix = f"_{a.tag}" if a.tag else ""

    probes = [json.loads(l) for l in open(P3 / "probes.jsonl", encoding="utf-8")]
    ck = torch.load(a.ckpt, map_location=a.device)
    model = GPT(GPTConfig(**ck["model_args"]))
    model.load_state_dict({k.removeprefix("_orig_mod."): v for k, v in ck["model"].items()})
    model.eval().to(a.device)
    tok = Tokenizer.from_file(str(ROOT / "data" / "processed" / "tokenizer.json"))
    eot = tok.token_to_id("<|endoftext|>")

    outs = []
    for i, p in enumerate(probes):
        torch.manual_seed(a.seed + i)
        lead = p["indent"][:-1]  # tokenizer-boundary fix (see docs/phase2.md)
        ids = torch.tensor([tok.encode(p["prompt"] + lead).ids], dtype=torch.long, device=a.device)
        t0 = time.time()
        gen = generate(model, ids, a.max_new_tokens, temperature=a.temperature, top_k=a.top_k, no_repeat_ngram=a.no_repeat_ngram)[0].tolist()
        secs = time.time() - t0
        new = gen[ids.size(1):]
        hit_eot = eot in new
        if hit_eot:
            new = new[:new.index(eot)]
        raw = lead + tok.decode(new)
        completion = cut_completion(raw)
        ended = "eot" if hit_eot else ("dedent" if completion.rstrip() != raw.rstrip() else "limit")  # limit = ran to the token cap
        lines = [l.strip() for l in completion.splitlines() if l.strip()]
        repeat_ratio = round(1 - len(set(lines)) / len(lines), 3) if lines else 0.0
        rec = {"id": p["id"], "group": p["group"], "pair": p["pair"], "prompt": p["prompt"], "completion": completion,
               "parses": bool(completion.strip()) and parses(p["prompt"] + completion),
               "security_flags": security_flags(completion),
               "ended": ended, "repeat_line_ratio": repeat_ratio, "gen_seconds": round(secs, 2),
               "settings": {"temperature": a.temperature, "top_k": a.top_k, "max_new_tokens": a.max_new_tokens,
                            "seed": a.seed + i, "ckpt": a.ckpt, "no_repeat_ngram": a.no_repeat_ngram}}
        if p.get("reference_body"):
            rec["ref_similarity"] = round(difflib.SequenceMatcher(None, p["reference_body"], completion).ratio(), 3)
        outs.append(rec)
        print(f"{p['id']} [{p['group']}] parses={rec['parses']} ended={ended} repeat={repeat_ratio} flags={rec['security_flags']} {len(completion.splitlines())} lines")

    # verbatim-in-training check: one streaming pass over the train split
    cand = {}
    for r in outs:
        for line in r["completion"].splitlines():
            s = line.strip()
            if len(s) >= 25:
                cand.setdefault(s, set()).add(r["id"])
    found = {}
    for row in open(ROOT / "data" / "processed" / "train.jsonl", encoding="utf-8"):
        for line in json.loads(row)["text"].splitlines():
            s = line.strip()
            if s in cand:
                for pid in cand[s]:
                    found.setdefault(pid, set()).add(s)
    for r in outs:
        total = len({l.strip() for l in r["completion"].splitlines() if len(l.strip()) >= 25})
        r["verbatim_lines"] = f"{len(found.get(r['id'], ()))}/{total}"

    with open(P3 / f"outputs{suffix}.jsonl", "w", encoding="utf-8") as f:
        for r in outs:
            f.write(json.dumps(r) + "\n")

    by_id = {p["id"]: p for p in probes}
    md = [f"# Phase 3 review sheet{' (' + a.tag + ')' if a.tag else ''}\n",
          "For each probe: read the PROMPT and 'a correct answer would', then the MODEL OUTPUT. If it is a failure, add a row to "
          "`phase3/findings.csv` with one category from: syntax, invented-api, wrong-logic, insecure, memorised, prompt-sensitive, "
          "context-ignored, other (explain). The hints are automatic and can be wrong: **you decide**.\n"]
    for r in outs:
        p = by_id[r["id"]]
        md.append(f"\n---\n\n## {r['id']}  [{p['group']}] {p['targets']}" + (f"   (pair {p['pair']})" if p["pair"] else "") + "\n")
        md.append(f"**A correct answer would:** {p['expect']}\n")
        hint = f"parses: {r['parses']} | ended: {r['ended']} | security-pattern flags: {r['security_flags'] or 'none'} | lines found verbatim in training: {r['verbatim_lines']}"
        if "ref_similarity" in r:
            hint += f" | similarity to the original training body: {r['ref_similarity']}"
        md.append(f"*Hints (automatic, not verdicts):* {hint}\n")
        md.append("**PROMPT**\n```python\n" + r["prompt"].rstrip() + "\n```\n")
        md.append("**MODEL OUTPUT**\n```python\n" + (r["completion"].rstrip() or "(empty)") + "\n```\n")
        if p.get("reference_body"):
            md.append("**ORIGINAL BODY (from training data)**\n```python\n" + p["reference_body"].rstrip() + "\n```\n")
    (P3 / f"review{suffix}.md").write_text("\n".join(md), encoding="utf-8")

    fcsv = P3 / "findings.csv"
    if not fcsv.exists():
        with open(fcsv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["probe_id", "group", "outcome", "category", "severity", "why_wrong", "how_found", "unit_tests_would_catch"])
            for p in probes:  # outcome: pass | fail ; the other columns only for failures (one row per failure; duplicate a row for a 2nd failure)
                w.writerow([p["id"], p["group"], "", "", "", "", "", ""])
        print("created", fcsv)
    n_ok = sum(r["parses"] for r in outs)
    print(f"\nwrote phase3/outputs{suffix}.jsonl and review{suffix}.md | {n_ok}/{len(outs)} parse")


if __name__ == "__main__":
    main()
