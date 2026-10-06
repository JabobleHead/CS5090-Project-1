"""Select the 20 Phase 2 inputs (code completion) from the held-out TEST split.

Each input = a function's signature (+ docstring if present) as the prompt; the original body is kept as the
reference for the human judge. Selection is seeded and spread across repos (round-robin, one function per file),
and any function whose body appears verbatim in the TRAIN split is skipped.

  python scripts/make_phase2_inputs.py            -> phase2/inputs.jsonl, phase2/judgments.csv (blank template)
"""
import ast, csv, json, random, re, textwrap
from collections import defaultdict
from pathlib import Path
from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parents[1]
PROC, OUT = ROOT / "data" / "processed", ROOT / "phase2"
SEED, N_INPUTS = 1337, 20
MIN_BODY, MAX_BODY, MAX_PROMPT_TOKENS = 6, 30, 300


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def candidates(path: str, text: str):
    """Yield (prompt, reference) for functions with a body of MIN_BODY..MAX_BODY lines."""
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return
    lines = text.splitlines(keepends=True)
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = node.body
        has_doc = isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
            and isinstance(body[0].value.value, str)
        real = body[1:] if has_doc else body
        if not real:
            continue
        start = real[0].lineno  # first real statement (1-indexed)
        end = node.end_lineno
        if not MIN_BODY <= end - start + 1 <= MAX_BODY:
            continue
        first = node.decorator_list[0].lineno if node.decorator_list else node.lineno
        col = node.col_offset
        cut = lambda chunk: "".join(l[col:] if l[:col].strip() == "" else l.lstrip() for l in chunk)
        prompt, ref = cut(lines[first - 1:start - 1]), cut(lines[start - 1:end])
        if prompt.strip() and ref.strip():
            yield prompt, ref


def main():
    OUT.mkdir(exist_ok=True)
    tok = Tokenizer.from_file(str(PROC / "tokenizer.json"))
    rng = random.Random(SEED)
    by_repo = defaultdict(list)  # repo -> list of (path, prompt, reference), one pick per file
    for line in open(PROC / "test.jsonl", encoding="utf-8"):
        row = json.loads(line)
        cands = [c for c in candidates(row["path"], row["text"]) if len(tok.encode(c[0]).ids) <= MAX_PROMPT_TOKENS]
        if cands:
            prompt, ref = rng.choice(cands)
            by_repo[row["path"].split("/")[0]].append((row["path"], prompt, ref))
    print("repos with candidates:", len(by_repo), "| files:", sum(map(len, by_repo.values())))

    train_norm = norm("\n".join(json.loads(l)["text"] for l in open(PROC / "train.jsonl", encoding="utf-8")))
    for v in by_repo.values():
        rng.shuffle(v)
    repos = sorted(by_repo)
    rng.shuffle(repos)
    chosen, skipped_memorised = [], 0
    while len(chosen) < N_INPUTS and any(by_repo.values()):
        for r in repos:
            if len(chosen) >= N_INPUTS:
                break
            while by_repo[r]:
                path, prompt, ref = by_repo[r].pop()
                if norm(ref) in train_norm:
                    skipped_memorised += 1
                    continue
                chosen.append({"repo": r, "path": path, "prompt": prompt, "reference_body": ref})
                break
    for i, c in enumerate(chosen, 1):
        c["id"] = f"p2-{i:02d}"
    with open(OUT / "inputs.jsonl", "w", encoding="utf-8") as f:
        for c in chosen:
            f.write(json.dumps({"id": c["id"], **{k: v for k, v in c.items() if k != "id"}}) + "\n")
    with open(OUT / "judgments.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "decision", "edit_needed", "minutes_to_check", "notes"])  # decision: accept | edit | reject
        for c in chosen:
            w.writerow([c["id"], "", "", "", ""])
    print(f"wrote {len(chosen)} inputs from {len({c['repo'] for c in chosen})} repos; skipped {skipped_memorised} verbatim-in-train")


if __name__ == "__main__":
    main()
