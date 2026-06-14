import os
import sys
import torch

from chat import chat, chat_qa
from model import device, steps, lr, SOP_GPT
from tokenizer import load_korean_chatbot_data, load_kowikitext_data, load_chatbot_qa_data
from bpe import train_bpe, build_vocab, base_alphabet, encode, decode, save_bpe, load_bpe
from train_utils import make_batcher, train_loop

BPE_VOCAB_SIZE = 8000
BPE_PATH = "bpe_vocab.json"
KOWIKI_TRAIN_CHARS = 80_000_000  # kowikitext train split은 ~1.6GB라 앞부분만 사용

GEN_CKPT = "SOP_GPT.pt"      # Stage 1(이어쓰기) 가중치
QA_CKPT = "SOP_GPT_qa.pt"    # Stage 2(Q&A) 가중치

EARLY_STOP_PATIENCE = 10     # 연속 10번 평가(=200 step) 동안 개선이 없으면 중단
EARLY_STOP_MIN_DELTA = 1e-3  # 이보다 작은 감소는 "개선 없음"으로 취급

FT_STEPS = 3000
FT_LR = 3e-4                 # Stage 1보다 낮은 lr로 미세조정 (급격한 망각 방지)

if os.path.exists(BPE_PATH):
    vocab, merges = load_bpe(BPE_PATH)
else:
    text = load_kowikitext_data(train_chars=KOWIKI_TRAIN_CHARS) + "\n" + load_korean_chatbot_data()
    vocab, merges = train_bpe(text, BPE_VOCAB_SIZE)
    save_bpe(BPE_PATH, vocab, merges)

stoi, itos = build_vocab(vocab)
vocab_size = len(vocab)
base_set = base_alphabet(vocab)


def train_stage1(model):
    text = load_kowikitext_data(train_chars=KOWIKI_TRAIN_CHARS) + "\n" + load_korean_chatbot_data()
    data = torch.tensor(encode(text, merges, stoi, base_set), dtype=torch.long)
    print(f"text length: {len(text):,} chars, {len(data):,} tokens, vocab_size: {vocab_size}, device: {device}")

    n_train = int(0.9 * len(data))
    get_batch = make_batcher(data[:n_train], data[n_train:])

    print(f"{sum(p.numel() for p in model.parameters()):,} parameters, device={device}")
    train_loop(model, get_batch, steps, lr, GEN_CKPT, EARLY_STOP_PATIENCE, EARLY_STOP_MIN_DELTA)

    model.eval()
    prompt = torch.zeros((1, 1), dtype=torch.long, device=device)  # start token
    # chat()과 동일한 생성 옵션을 줘야 "이상한 토큰 반복"이 아닌 의미 있는 샘플이 나온다.
    stop_tokens = {i for t, i in stoi.items() if t and t[-1] in ".?!"}
    print("\n--- sample ---")
    print(decode(model.generate(prompt, 200, stop_tokens=stop_tokens, temperature=0.8, top_k=40, repetition_penalty=1.3)[0].tolist(), itos))


def train_stage2(model):
    text = load_chatbot_qa_data()
    data = torch.tensor(encode(text, merges, stoi, base_set), dtype=torch.long)
    print(f"qa text length: {len(text):,} chars, {len(data):,} tokens, vocab_size: {vocab_size}, device: {device}")

    n_train = int(0.9 * len(data))
    get_batch = make_batcher(data[:n_train], data[n_train:])

    model.load_state_dict(torch.load(GEN_CKPT, map_location=device))
    print(f"loaded {GEN_CKPT}, fine-tuning on {len(data):,} QA tokens, device={device}")
    train_loop(model, get_batch, FT_STEPS, FT_LR, QA_CKPT, EARLY_STOP_PATIENCE, EARLY_STOP_MIN_DELTA)


MODES = {
    "train": train_stage1,
    "train_qa": train_stage2,
    "chat": lambda model: chat(model, stoi, itos, merges, base_set),
    "chat_qa": lambda model: chat_qa(model, stoi, itos, merges, base_set),
}

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "chat"
    if mode not in MODES:
        sys.exit(f"unknown mode: {mode} (use one of {', '.join(MODES)})")

    model = SOP_GPT(vocab_size).to(device)
    MODES[mode](model)
