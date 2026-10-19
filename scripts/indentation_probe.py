"""Quantify the prediction "indentation should suffer most": sample many continuations from each model and count how
often the generated code has an indentation error vs another syntax error vs parses.

Each sample = prompt + 120 new tokens, cut back to the last complete line, then ast.parse. The same seed and batch layout
are used for both models. Errors that merely come from truncation ("was never closed", "unexpected EOF") are counted as
`other`; only IndentationError (unexpected indent / expected an indented block / unindent does not match) is `indent`.

  python scripts/indentation_probe.py        -> results/indentation_probe.csv + printed table
"""
import ast, csv, sys, warnings
from pathlib import Path
import torch
from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "nanogpt"))
from model import GPT, GPTConfig  # noqa: E402

warnings.simplefilter("ignore")
PROMPTS = {  # indentation continues on the next line; prompts end with indent-1 spaces (tokenizer-boundary fix)
    "def body": "def process(items, key):\n   ",
    "nested for/if": "for i in range(3):\n    for j in range(3):\n        if i == j:\n           ",
    "class method": "class Handler:\n    def run(self, data):\n       ",
}
N_PER_PROMPT, BATCH, MAX_NEW, TEMP, TOP_K, SEED = 30, 30, 120, 0.8, 50, 1234


def load(path):
    ck = torch.load(path, map_location="cpu")
    m = GPT(GPTConfig(**ck["model_args"]))
    m.load_state_dict({k.removeprefix("_orig_mod."): v for k, v in ck["model"].items()})
    return m.eval()


def classify(src: str) -> str:
    lines = src.rstrip("\n").split("\n")[:-1]  # drop the last (possibly cut-off) line
    code = "\n".join(lines) + "\n"
    try:
        ast.parse(code)
        return "parses"
    except IndentationError:
        return "indent"
    except (SyntaxError, ValueError):
        # a dangling block opener at the very end ("expected an indented block") is truncation, not a model error
        return "other"


def main():
    tok = Tokenizer.from_file(str(ROOT / "data" / "processed" / "tokenizer.json"))
    models = {"baseline": load(ROOT / "out-baseline" / "ckpt.pt"), "no-pos-emb": load(ROOT / "out-ablation-nopos" / "ckpt.pt")}
    rows, tally = [], {n: {p: {"parses": 0, "indent": 0, "other": 0} for p in PROMPTS} for n in models}
    for name, m in models.items():
        for label, prompt in PROMPTS.items():
            torch.manual_seed(SEED)
            ids = torch.tensor([tok.encode(prompt).ids] * BATCH)
            with torch.no_grad():
                g = m.generate(ids, MAX_NEW, temperature=TEMP, top_k=TOP_K)
            for row in g.tolist():
                text = tok.decode(row[:])
                kind = classify(text)
                tally[name][label][kind] += 1
                rows.append({"model": name, "prompt": label, "outcome": kind})
    with open(ROOT / "results" / "indentation_probe.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["model", "prompt", "outcome"])
        w.writeheader()
        w.writerows(rows)
    print(f"{'prompt':<16}{'model':<12}{'parses':>8}{'indent':>8}{'other':>8}   (n={N_PER_PROMPT} each)")
    for label in PROMPTS:
        for name in models:
            t = tally[name][label]
            print(f"{label:<16}{name:<12}{t['parses']:>8}{t['indent']:>8}{t['other']:>8}")
    for name in models:
        tot = {k: sum(tally[name][p][k] for p in PROMPTS) for k in ("parses", "indent", "other")}
        print(f"ALL {name:<12} parses {tot['parses']}  indent {tot['indent']}  other {tot['other']}  of {sum(tot.values())}")


if __name__ == "__main__":
    main()
