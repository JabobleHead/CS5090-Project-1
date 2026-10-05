"""Tokenise each split into uint16 .bin files (nanoGPT memmap format) + meta.pkl.
Documents are separated by <|endoftext|>. Also runs round-trip and leakage checks."""
import json, pickle
from pathlib import Path
import numpy as np
from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parents[1]
PROC, OUT = ROOT / "data" / "processed", ROOT / "data" / "code"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tok = Tokenizer.from_file(str(PROC / "tokenizer.json"))
    eot = tok.token_to_id("<|endoftext|>")
    assert tok.get_vocab_size() <= 65535
    info, hashes = {}, {}
    for split in ("train", "val", "test"):
        parts, chars, hs = [], 0, set()  # per-doc uint16 arrays: a Python list of ints would need GBs at 100M+ tokens
        texts = [json.loads(l)["text"] for l in open(PROC / f"{split}.jsonl", encoding="utf-8")]
        for i in range(0, len(texts), 256):
            batch = texts[i:i + 256]
            for text, enc in zip(batch, tok.encode_batch(batch)):
                if (i + len(parts)) % 50 == 0:  # round-trip spot check on every 50th doc
                    assert tok.decode(enc.ids) == text, "tokenizer round-trip failed"
                parts.append(np.array(enc.ids + [eot], dtype=np.uint16))
                chars += len(text)
                hs.add(hash(text))
        arr = np.concatenate(parts)
        arr.tofile(OUT / f"{split}.bin")
        hashes[split] = hs
        info[split] = {"tokens": int(arr.size), "chars": chars, "chars_per_token": round(chars / arr.size, 3)}
    assert not (hashes["train"] & hashes["val"]), "train/val leakage"
    assert not (hashes["train"] & hashes["test"]), "train/test leakage"
    with open(OUT / "meta.pkl", "wb") as f:
        pickle.dump({"vocab_size": tok.get_vocab_size()}, f)
    (PROC / "token_stats.json").write_text(json.dumps(info, indent=2))
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
