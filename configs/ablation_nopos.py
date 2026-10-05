# Ablation: identical to baseline EXCEPT learned position embeddings are removed. Run from repo root:
#   python nanogpt/train.py configs/ablation_nopos.py
exec(open('configs/baseline.py').read())
out_dir = 'out-ablation-nopos'
log_csv = 'results/ablation_nopos_loss.csv'
use_pos_emb = False         # the ONE change
