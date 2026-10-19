"""Plot train/val loss for the baseline and (if present) the no-position-embedding ablation -> results/loss_curves.png
Left: full run. Right: zoom on iterations >= 1500 where the curves separate."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = Path(__file__).resolve().parents[1] / "results"
RUNS = (("baseline_loss.csv", "baseline", "C0"), ("ablation_nopos_loss.csv", "no pos-emb", "C3"))


def load(name):
    p = R / name
    if not p.exists():
        return None
    with open(p) as f:
        rows = list(csv.DictReader(f))
    return [int(r["iter"]) for r in rows], [float(r["train_loss"]) for r in rows], [float(r["val_loss"]) for r in rows]


fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
for ax, zoom in zip(axes, (False, True)):
    for name, label, color in RUNS:
        d = load(name)
        if not d:
            continue
        it, tr, va = d
        keep = [i for i, x in enumerate(it) if (x >= 1500 if zoom else True)]
        ax.plot([it[i] for i in keep], [tr[i] for i in keep], "--", color=color, alpha=0.6, label=f"{label} train")
        ax.plot([it[i] for i in keep], [va[i] for i in keep], "-", color=color, label=f"{label} val (final {va[-1]:.3f})")
    ax.set_xlabel("iteration (32,768 tokens each)")
    ax.set_ylabel("cross-entropy (nats/token)")
    ax.set_title("Phase 1 loss curves" + (" (zoom, iter >= 1500)" if zoom else ""))
    ax.grid(alpha=0.3)
    if zoom:
        ax.set_ylim(1.5, 2.4)
    ax.legend()
fig.tight_layout()
fig.savefig(R / "loss_curves.png", dpi=150)
print("wrote", R / "loss_curves.png")
