import threading

from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

DEFAULT_MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

SYSTEM_PROMPT = (
  "당신은 주어진 컨텍스트만 근거로 답하는 한국어 어시스턴트입니다. "
  "컨텍스트에 없는 내용은 추측하지 말고 모른다고 답하세요."
)


# 검색된 컨텍스트와 질문을 하나의 사용자 프롬프트 문자열로 합침
def build_prompt(query, contexts):
  context_block = "\n\n".join(f"[{i+1}] {c['text']}" for i, c in enumerate(contexts))
  return (
    f"다음 컨텍스트를 참고하여 질문에 답하세요.\n\n"
    f"컨텍스트:\n{context_block}\n\n"
    f"질문: {query}"
  )


class Generator:
  # Qwen2.5 토크나이저와 모델을 로드(GPU 있으면 자동으로 GPU에 올림)
  def __init__(self, model_name=DEFAULT_MODEL_NAME):
    self.tokenizer = AutoTokenizer.from_pretrained(model_name)
    self.model = AutoModelForCausalLM.from_pretrained(
      model_name,
      torch_dtype="auto",
      device_map="auto",
    )

  # 시스템/유저 메시지를 채팅 템플릿에 맞춰 모델 입력 텐서로 변환
  def _build_inputs(self, query, contexts):
    messages = [
      {"role": "system", "content": SYSTEM_PROMPT},
      {"role": "user", "content": build_prompt(query, contexts)},
    ]
    prompt = self.tokenizer.apply_chat_template(
      messages, tokenize=False, add_generation_prompt=True
    )
    return self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

  # 한 번에 끝까지 생성해서 완성된 답변 문자열을 반환
  def generate(self, query, contexts, max_new_tokens=512):
    inputs = self._build_inputs(query, contexts)
    output_ids = self.model.generate(
      **inputs,
      max_new_tokens=max_new_tokens,
      do_sample=False,
    )
    new_tokens = output_ids[0][inputs["input_ids"].shape[1]:]
    return self.tokenizer.decode(new_tokens, skip_special_tokens=True)

  # 별도 스레드에서 생성을 돌리고 토큰이 만들어지는 대로 하나씩 yield (스트리밍용)
  def generate_stream(self, query, contexts, max_new_tokens=512):
    inputs = self._build_inputs(query, contexts)
    # skip_prompt=True가 없으면 TextIteratorStreamer가 입력 프롬프트(시스템 프롬프트+컨텍스트+질문)까지
    # 그대로 스트리밍해버려서 답변 앞에 프롬프트 전체가 출력되는 문제가 있었음
    streamer = TextIteratorStreamer(self.tokenizer, skip_special_tokens=True, skip_prompt=True)

    generation_kwargs = dict(
      **inputs,
      max_new_tokens=max_new_tokens,
      do_sample=False,
      streamer=streamer,
    )
    thread = threading.Thread(target=self.model.generate, kwargs=generation_kwargs)
    thread.start()

    for token in streamer:
      yield token
