"""Plot train/val loss for the baseline and (if present) the no-position-embedding ablation -> results/loss_curves.png"""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = Path(__file__).resolve().parents[1] / "results"


def load(name):
    p = R / name
    if not p.exists():
        return None
    with open(p) as f:
        rows = list(csv.DictReader(f))
    return [int(r["iter"]) for r in rows], [float(r["train_loss"]) for r in rows], [float(r["val_loss"]) for r in rows]


fig, ax = plt.subplots(figsize=(7, 4.5))
for name, label, color in (("baseline_loss.csv", "baseline", "C0"), ("ablation_nopos_loss.csv", "no pos-emb", "C3")):
    d = load(name)
    if d:
        it, tr, va = d
        ax.plot(it, tr, "--", color=color, alpha=0.6, label=f"{label} train")
        ax.plot(it, va, "-", color=color, label=f"{label} val (final {va[-1]:.3f})")
ax.set_xlabel("iteration (32,768 tokens each)")
ax.set_ylabel("cross-entropy (nats/token)")
ax.set_title("Phase 1 loss curves")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(R / "loss_curves.png", dpi=150)
print("wrote", R / "loss_curves.png")
