"""Train a byte-level BPE tokenizer (vocab 8192) on the TRAIN split only."""
import json
from pathlib import Path
from tokenizers import Tokenizer, models, pre_tokenizers, decoders, trainers

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
VOCAB = 8192
EOT = "<|endoftext|>"


def texts(split):
    with open(PROC / f"{split}.jsonl", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)["text"]


def main():
    tok = Tokenizer(models.BPE())
    tok.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tok.decoder = decoders.ByteLevel()
    trainer = trainers.BpeTrainer(vocab_size=VOCAB, special_tokens=[EOT],
                                  initial_alphabet=pre_tokenizers.ByteLevel.alphabet(), show_progress=True)
    tok.train_from_iterator(texts("train"), trainer)  # train split ONLY
    tok.save(str(PROC / "tokenizer.json"))
    print("vocab size:", tok.get_vocab_size(), "| EOT id:", tok.token_to_id(EOT))


if __name__ == "__main__":
    main()
