"""Filter, deduplicate and split the raw corpus.

Stages (counts are printed and written to data/processed/stats.json for DATASHEET.md):
  1. keep *.py outside skip-dirs, 200 B <= size <= 200 KB
  2. drop files that are not valid UTF-8 or fail ast.parse (Python 3 syntax)
  3. drop minified/generated-looking files (any line > 1000 chars or 'auto-generated' header)
  4. exact dedup (sha256 of whitespace-normalised text)
  5. near-dup removal (MinHash LSH, 5-token shingles, Jaccard >= 0.85)
  6. split BY FILE PATH HASH: 90% train / 5% val / 5% test. Dedup runs BEFORE the split so
     near-duplicates cannot straddle train/val.
"""
import ast, hashlib, json, platform, re, warnings
from pathlib import Path
from datasketch import MinHash, MinHashLSH

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "data" / "raw", ROOT / "data" / "processed"
SKIP_DIRS = {".git", "docs", "docs_src", "build", "dist", "node_modules", "venv", ".venv", "__pycache__", "vendor", "_vendor"}
MIN_B, MAX_B, MAX_LINE, JACCARD = 200, 200_000, 1000, 0.85
warnings.simplefilter("ignore", SyntaxWarning)  # ast.parse warns on legacy escape sequences; not errors


def split_of(key: str) -> str:
    h = int(hashlib.sha256(key.encode()).hexdigest(), 16) % 100
    return "train" if h < 90 else "val" if h < 95 else "test"


def minhash(text: str) -> MinHash:
    toks = re.findall(r"\w+|[^\w\s]", text)
    m = MinHash(num_perm=128)
    m.update_batch([" ".join(toks[i:i + 5]).encode() for i in range(len(toks) - 4)])  # vectorised: ~100x faster than update()
    return m


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    stats = {"found": 0, "size_rejected": 0, "not_utf8": 0, "syntax_error": 0,
             "generated_or_minified": 0, "exact_dup": 0, "near_dup": 0}
    seen, lsh, kept = set(), MinHashLSH(threshold=JACCARD, num_perm=128), []
    for p in sorted(RAW.rglob("*.py")):
        rel = p.relative_to(RAW)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        stats["found"] += 1
        raw = p.read_bytes()
        try:
            # normalise line endings: Windows git (core.autocrlf) checks files out as CRLF, Linux as LF; without this
            # the same commit would yield different corpora/tokenizers on different machines
            text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
        except UnicodeDecodeError:
            stats["not_utf8"] += 1
            continue
        if not MIN_B <= len(text.encode("utf-8")) <= MAX_B:  # size rule applied on the normalised text
            stats["size_rejected"] += 1
            continue
        try:
            ast.parse(text)
        except (SyntaxError, ValueError, RecursionError):
            stats["syntax_error"] += 1
            continue
        if max(len(l) for l in text.splitlines()) > MAX_LINE or "auto-generated" in text[:500].lower():
            stats["generated_or_minified"] += 1
            continue
        digest = hashlib.sha256(re.sub(r"\s+", " ", text).encode()).hexdigest()
        if digest in seen:
            stats["exact_dup"] += 1
            continue
        seen.add(digest)
        mh = minhash(text)
        if lsh.query(mh):
            stats["near_dup"] += 1
            continue
        lsh.insert(rel.as_posix(), mh)
        kept.append((rel.as_posix(), text))
    files = {"train": [], "val": [], "test": []}
    for rel, text in kept:
        files[split_of(rel)].append({"path": rel, "text": text})
    stats["kept"] = len(kept)
    stats["python_version"] = platform.python_version()  # ast.parse accepts different syntax per version (affects syntax_error)
    for s, rows in files.items():
        with open(OUT / f"{s}.jsonl", "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        stats[f"{s}_files"] = len(rows)
        stats[f"{s}_chars"] = sum(len(r["text"]) for r in rows)
    (OUT / "stats.json").write_text(json.dumps(stats, indent=2))
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
