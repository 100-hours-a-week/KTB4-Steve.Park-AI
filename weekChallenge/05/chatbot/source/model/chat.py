import torch

from model import device
from bpe import tokenize, decode

def chat(model, stoi, itos, merges, base_set):
    model.load_state_dict(torch.load("SOP_GPT.pt", map_location=device))
    model.eval()
    # "." / "?" / "!"로 끝나는 토큰(예: "요.", "습니다.", "다.")이 생성되면 한 문장이 끝난 것으로 보고 멈춘다.
    stop_tokens = {i for t, i in stoi.items() if t and t[-1] in ".?!"}
    print("Type a prompt and the model will continue it (empty line or Ctrl-D to quit).")
    while True:
        try:
            prompt = input("> ")
        except EOFError:
            break
        if not prompt:
            break
        ids = [stoi[t] for t in tokenize(prompt, merges, base_set) if t in stoi]
        if not ids:
            print("(no tokens from the prompt are in the vocabulary)")
            continue
        idx = torch.tensor([ids], dtype=torch.long, device=device)
        out = model.generate(idx, 200, stop_tokens=stop_tokens, temperature=0.8, top_k=40, repetition_penalty=1.3)[0].tolist()
        print(decode(out[len(ids):], itos))  # print only the continuation


def chat_qa(model, stoi, itos, merges, base_set):
    """Stage 2: "질문: ...\\n답변: " 포맷으로 fine-tuning된 모델과의 Q&A REPL."""
    model.load_state_dict(torch.load("SOP_GPT_qa.pt", map_location=device))
    model.eval()
    # 줄바꿈으로 끝나는 토큰이 나오면 "답변: ..." 한 줄이 끝난 것으로 보고 멈춘다.
    stop_tokens = {i for t, i in stoi.items() if t.endswith("\n")}
    print("Ask something (empty line or Ctrl-D to quit).")
    while True:
        try:
            question = input("질문: ")
        except EOFError:
            break
        if not question:
            break
        prompt = f"질문: {question}\n답변: "
        ids = [stoi[t] for t in tokenize(prompt, merges, base_set) if t in stoi]
        idx = torch.tensor([ids], dtype=torch.long, device=device)
        out = model.generate(idx, 60, stop_tokens=stop_tokens, temperature=0.8, top_k=40, repetition_penalty=1.3)[0].tolist()
        print("답변:", decode(out[len(ids):], itos).strip())
