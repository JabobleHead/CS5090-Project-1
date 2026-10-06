# Baseline: 6 layers / 6 heads / 384 emb, context 512, BPE-8192. Run from the repo root:
#   python nanogpt/train.py configs/baseline.py
out_dir = 'out-baseline'
log_csv = 'results/baseline_loss.csv'
dataset = 'code'            # reads data/code/{train,val}.bin + meta.pkl (vocab_size=8192)

# model
n_layer, n_head, n_embd = 6, 6, 384
block_size = 512
dropout = 0.1               # several epochs over ~48M tokens -> light regularisation
bias = False
use_pos_emb = True

# budget: 64 seq * 512 tok = 32,768 tok/iter; 8,400 iters ~= 275M tokens ~= 20 x 13.8M params (~5.8 epochs)
batch_size = 64
gradient_accumulation_steps = 1
max_iters = 8400
lr_decay_iters = 8400
warmup_iters = 200
learning_rate = 1e-3
min_lr = 1e-4
weight_decay = 0.1
beta2 = 0.99

# eval / checkpointing (always keep the LAST checkpoint so baseline and ablation are compared at the same step)
eval_interval = 300         # divides max_iters, so the final iteration is evaluated; ~29 curve points
eval_iters = 40             # batches per split per eval (an eval of 100 took ~110 s on a T4, i.e. 1.3 h over the run)
log_interval = 50
always_save_checkpoint = True

seed = 1337
dtype = 'float16'           # explicit: a T4 reports bf16 as "supported" but only emulates it (slow); fp16 + GradScaler is native
compile = False             # set True on Kaggle if torch.compile works (faster); does not change the math
