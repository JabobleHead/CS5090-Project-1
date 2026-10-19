"""Turn an outputs .jsonl file into a plain-text file with real line breaks (jsonl stores code as one escaped line).

  python scripts/pretty_outputs.py phase3/outputs.jsonl              -> phase3/outputs_readable.txt
  python scripts/pretty_outputs.py phase2/outputs.jsonl out.txt      (optional explicit output path)
"""
import json, sys
from pathlib import Path


def main():
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_name(src.stem + "_readable.txt")
    bar = "=" * 78
    parts = []
    for line in open(src, encoding="utf-8"):
        r = json.loads(line)
        head = f"{r['id']}"
        if r.get("group"):
            head += f"   [{r['group']}]" + (f"   pair {r['pair']}" if r.get("pair") else "")
        hints = [f"parses: {r.get('parses')}"]
        if "security_flags" in r:
            hints.append(f"security flags: {', '.join(r['security_flags']) or 'none'}")
        if "verbatim_lines" in r:
            hints.append(f"lines found verbatim in training: {r['verbatim_lines']}")
        if "ref_similarity" in r:
            hints.append(f"similarity to training original: {r['ref_similarity']}")
        parts.append(f"{bar}\n{head}\n{' | '.join(hints)}\n{bar}\n"
                     f"--- PROMPT ---\n{r['prompt'].rstrip()}\n\n"
                     f"--- MODEL OUTPUT ---\n{r['completion'].rstrip() or '(empty)'}\n")
    dst.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {dst} ({len(parts)} items)")


if __name__ == "__main__":
    main()
