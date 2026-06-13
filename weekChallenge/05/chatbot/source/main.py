import sys

import torch
import torch.nn as nn
import torch.nn.functional as F


# --- hyperparameters ---
block_size = 128     # max context length
n_embd = 256         # embedding dimension
n_head = 4           # attention heads
n_layer = 6          # transformer blocks
batch_size = 64
steps = 20000
lr = 1e-3
dropout = 0.2
device = (
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)
torch.manual_seed(1337)

# --- data: character-level tokenizer over a tiny corpus ---
text = open("input.txt").read()
chars = sorted(set(text))
vocab_size = len(chars)
stoi = {c: i for i, c in enumerate(chars)}
itos = {i: c for c, i in stoi.items()}
encode = lambda s: [stoi[c] for c in s]
decode = lambda ids: "".join(itos[i] for i in ids)
data = torch.tensor(encode(text), dtype=torch.long)
n_train = int(0.9 * len(data))  # hold out the last 10% to measure overfitting
train_data, val_data = data[:n_train], data[n_train:]