"""Side-by-side generations from the baseline and the no-position-embedding ablation (same prompts, same seeds,
same sampling settings). Prompts come from PREDICTION.md's "Concrete check". Prompts that continue onto an indented
line end with indent[:-1] spaces, as in Phase 2 (tokenizer-boundary fix).

  python scripts/compare_generations.py            -> results/gen_comparison.md (+ results/gen_baseline.txt, gen_nopos.txt)
"""
import ast, sys
from pathlib import Path
import torch
from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "nanogpt"))
from model import GPT, GPTConfig  # noqa: E402

PROMPTS = {
    "a - b": "x = a - b",
    "b - a": "x = b - a",
    "nested indentation": "for i in range(3):\n    for j in range(3):\n        if i == j:\n           ",  # 11 spaces = 12 - 1
    "call with several positional args": "result = compute(",
}
SEEDS, MAX_NEW, TEMP, TOP_K = (1, 2, 3), 80, 0.8, 50


def load(path, device="cpu"):
    ck = torch.load(path, map_location=device)
    m = GPT(GPTConfig(**ck["model_args"]))
    m.load_state_dict({k.removeprefix("_orig_mod."): v for k, v in ck["model"].items()})
    return m.eval().to(device)


def main():
    tok = Tokenizer.from_file(str(ROOT / "data" / "processed" / "tokenizer.json"))
    models = {"baseline": load(ROOT / "out-baseline" / "ckpt.pt"), "no-pos-emb": load(ROOT / "out-ablation-nopos" / "ckpt.pt")}
    outs = {n: {} for n in models}
    for name, m in models.items():
        for label, prompt in PROMPTS.items():
            for s in SEEDS:
                torch.manual_seed(s)
                ids = torch.tensor([tok.encode(prompt).ids])
                with torch.no_grad():
                    g = m.generate(ids, MAX_NEW, temperature=TEMP, top_k=TOP_K)[0].tolist()
                outs[name][(label, s)] = prompt + tok.decode(g[ids.size(1):])
    for fn, name in (("gen_baseline.txt", "baseline"), ("gen_nopos.txt", "no-pos-emb")):
        (ROOT / "results" / fn).write_text("\n\n".join(f"### {l} (seed {s})\n{t}" for (l, s), t in outs[name].items()), encoding="utf-8")
    md = ["# Baseline vs no position embeddings: generations\n",
          f"Same prompts, seeds {list(SEEDS)}, temperature {TEMP}, top-k {TOP_K}, {MAX_NEW} new tokens, CPU. "
          "Checkpoints: out-baseline/ckpt.pt and out-ablation-nopos/ckpt.pt (iteration 8400 each).\n"]
    for label in PROMPTS:
        md.append(f"\n## {label}\n")
        for s in SEEDS:
            md.append(f"\n### seed {s}\n")
            for name in models:
                md.append(f"**{name}**\n```python\n{outs[name][(label, s)]}\n```\n")
    (ROOT / "results" / "gen_comparison.md").write_text("\n".join(md), encoding="utf-8")
    print("wrote results/gen_comparison.md, gen_baseline.txt, gen_nopos.txt")


if __name__ == "__main__":
    main()
