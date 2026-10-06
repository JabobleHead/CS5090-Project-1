# Ablation prediction: remove position embeddings

## Prediction

I think removing position embeddings will hurt the model's ability to
distinguish statements like `x = a - b` and `x = b - a`. Token wise they
contain the same tokens, and without position embeddings the model has no
way of understanding the order of the tokens it has already seen. Because of
the causal mask, each token can only attend to its preivious tokens. That means the model
can still know *which* tokens came before, but not directly *where* they were.

The damage should be partial rather than total. The causal mask leaks some
positional information: the first token can only attend to itself, and the
averaging in attention dilutes any single token's contribution as the prior context
grows, so the model gets a rough sense of "how far in" it is. Deeper layers can
also partly rebuild order, since each earlier position's representation already
depends on its own prefix.

- **Final validation loss vs baseline:** up by roughly +0.03 to +0.15 nats.
  There is a real chance it lands near zero, since the mask may supply most of
  the positional signal at this scale.
- **Why:** The causal mask makes position partly recoverable from the tokens weve seen size.
  What gets lost is precise order and exact offsets (e.g. "the token 3 back"),
  not the identity of earlier tokens.
- **Expected qualitative change in generated code:** Indentation should suffer
  most, because Python indentation depends on tracking line starts and columns.
  Next I expect operand order in non-commutative expressions (the `a - b` case),
  statement ordering, and argument ordering in calls. Bracket matching should
  degrade least, since it is mostly counting, which averaging handles
  reasonably well.
- **What result would surprise me:** Validation loss within noise of baseline
  (< 0.02), meaning the causal mask provides nearly all the positional signal.
  Or a jump of more than 0.3 with bag-of-tokens-looking output, meaning the
  mask leak is much weaker than I expected.

## Concrete check

Prompts to run on both models for the side-by-side comparison:

- `x = a - b` vs `x = b - a`
- Nested indentation blocks (`for` / `if` / `else` three levels deep)
- A function call with several positional arguments

## Controls

Same seed, same data order, same number of iterations for baseline and ablated
runs, so any difference in loss is attributable to the ablation alone.