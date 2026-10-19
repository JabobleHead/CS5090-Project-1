"""Decoding with an optional no-repeat n-gram rule (Phase 4 intervention).

`generate` is nanoGPT's GPT.generate loop (nanogpt/model.py) line for line, so with no_repeat_ngram=0 it consumes the
random stream identically and reproduces the baseline outputs exactly for the same seed. The only addition: when
no_repeat_ngram = n > 0, a token is forbidden if it would complete an n-token window that already occurs anywhere in
the sequence so far (prompt + generated text). The ban is applied to the logits before top-k, so sampling is
otherwise unchanged. Batch size 1 only.
"""
import torch
import torch.nn.functional as F


@torch.no_grad()
def generate(model, idx, max_new_tokens, temperature=1.0, top_k=None, no_repeat_ngram=0):
    assert idx.size(0) == 1, "batch size 1 only"
    n = no_repeat_ngram
    seq = idx[0].tolist()
    seen = {}  # (n-1)-token prefix -> set of tokens that followed it somewhere in the sequence
    if n > 0:
        for i in range(len(seq) - n + 1):
            seen.setdefault(tuple(seq[i:i + n - 1]), set()).add(seq[i + n - 1])
    for _ in range(max_new_tokens):
        idx_cond = idx if idx.size(1) <= model.config.block_size else idx[:, -model.config.block_size:]
        logits, _ = model(idx_cond)
        logits = logits[:, -1, :] / temperature
        if n > 0 and len(seq) >= n - 1:
            banned = seen.get(tuple(seq[len(seq) - (n - 1):]) if n > 1 else (), ())
            if banned:
                logits[0, list(banned)] = -float("Inf")
        if top_k is not None:
            v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
            logits[logits < v[:, [-1]]] = -float("Inf")
        probs = F.softmax(logits, dim=-1)
        idx_next = torch.multinomial(probs, num_samples=1)
        idx = torch.cat((idx, idx_next), dim=1)
        tok = idx_next.item()
        if n > 0:
            if len(seq) >= n - 1:
                seen.setdefault(tuple(seq[len(seq) - (n - 1):]) if n > 1 else (), set()).add(tok)
        seq.append(tok)
    return idx
