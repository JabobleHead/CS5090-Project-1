"""Run the model on the Phase 2 inputs (code completion) with fixed, recorded settings.

  python scripts/run_phase2.py --ckpt out-baseline/ckpt.pt          -> phase2/outputs.jsonl
Same seed per input every run, so results are reproducible. The completion is cut at <|endoftext|> or at the first
line that returns to column 0 (i.e. the function ended and unrelated code began).
"""
import argparse, ast, json, sys
from pathlib import Path
import torch
from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "nanogpt"))
from model import GPT, GPTConfig  # noqa: E402


def cut_completion(text: str) -> str:
    out = []
    for i, line in enumerate(text.splitlines(keepends=True)):
        if line.strip() and not line[0].isspace():  # dedent to column 0 -> function is over
            break
        out.append(line)
    return "".join(out).rstrip() + "\n"


def parses(src: str) -> bool:
    try:
        ast.parse(src)
        return True
    except (SyntaxError, ValueError):
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--inputs", default=str(ROOT / "phase2" / "inputs.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "phase2" / "outputs.jsonl"))
    ap.add_argument("--max_new_tokens", type=int, default=200)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--top_k", type=int, default=50)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--no_indent_fix", dest="indent_fix", action="store_false", help="end prompt at a bare newline (first, flawed attempt)")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    a = ap.parse_args()

    ck = torch.load(a.ckpt, map_location=a.device)
    model = GPT(GPTConfig(**ck["model_args"]))
    model.load_state_dict({k.removeprefix("_orig_mod."): v for k, v in ck["model"].items()})
    model.eval().to(a.device)
    tok = Tokenizer.from_file(str(ROOT / "data" / "processed" / "tokenizer.json"))
    eot = tok.token_to_id("<|endoftext|>")

    rows = [json.loads(l) for l in open(a.inputs, encoding="utf-8")]
    with open(a.out, "w", encoding="utf-8") as f:
        for i, r in enumerate(rows):
            torch.manual_seed(a.seed + i)
            # Tokenizer-boundary fix: in training text "\n" + indentation + word is tokenised as one merged whitespace
            # token ("\n" + all-but-one indent chars) followed by " word"; a bare "\n" token almost always precedes a
            # column-0 line. So end the prompt with indent[:-1], exactly as the training data would. Only whitespace
            # from the reference's first line is used, never any of its code.
            first = next(l for l in r["reference_body"].splitlines() if l.strip())
            indent = first[:len(first) - len(first.lstrip())]
            lead = indent[:-1] if a.indent_fix else ""
            ids = torch.tensor([tok.encode(r["prompt"] + lead).ids], dtype=torch.long, device=a.device)
            with torch.no_grad():
                gen = model.generate(ids, a.max_new_tokens, temperature=a.temperature, top_k=a.top_k)[0].tolist()
            new = gen[ids.size(1):]
            if eot in new:
                new = new[:new.index(eot)]
            completion = cut_completion(lead + tok.decode(new))
            rec = {"id": r["id"], "prompt": r["prompt"], "completion": completion,
                   # an empty completion must not count: a signature+docstring alone is already valid Python
                   "parses": bool(completion.strip()) and parses(r["prompt"] + completion),
                   "settings": {"temperature": a.temperature, "top_k": a.top_k, "max_new_tokens": a.max_new_tokens,
                                "seed": a.seed + i, "ckpt": a.ckpt, "indent_fix": a.indent_fix}}
            f.write(json.dumps(rec) + "\n")
            print(f"{r['id']}: parses={rec['parses']} ({len(completion.splitlines())} lines)")


if __name__ == "__main__":
    main()
