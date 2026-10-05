"""Generate from a trained checkpoint with the repo's BPE tokenizer (same settings for baseline and ablation).
  python scripts/sample.py --ckpt out-baseline/ckpt.pt --prompt_file prompts/p1.py --seed 1 > results/gen_baseline.txt
"""
import argparse, sys
from pathlib import Path
import torch
from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "nanogpt"))
from model import GPT, GPTConfig  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--prompt", default="")
    ap.add_argument("--prompt_file")
    ap.add_argument("--max_new_tokens", type=int, default=300)
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--top_k", type=int, default=50)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    a = ap.parse_args()

    torch.manual_seed(a.seed)
    ck = torch.load(a.ckpt, map_location=a.device)
    model = GPT(GPTConfig(**ck["model_args"]))
    sd = {k.removeprefix("_orig_mod."): v for k, v in ck["model"].items()}
    model.load_state_dict(sd)
    model.eval().to(a.device)
    tok = Tokenizer.from_file(str(ROOT / "data" / "processed" / "tokenizer.json"))
    prompt = Path(a.prompt_file).read_text() if a.prompt_file else a.prompt
    ids = torch.tensor([tok.encode(prompt).ids], dtype=torch.long, device=a.device)
    with torch.no_grad():
        out = model.generate(ids, a.max_new_tokens, temperature=a.temperature, top_k=a.top_k)
    print(tok.decode(out[0].tolist()))


if __name__ == "__main__":
    main()
