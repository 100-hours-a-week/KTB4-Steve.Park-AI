from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_relevancy, context_precision, context_recall, faithfulness

from rag.pipeline import RAGPipeline

# RAGAS 평가 대상 질문과 정답(ground truth) 목록
# [주의] "최근/마지막" 질문은 rag/pipeline.py의 그래프 라우팅 대상이라 contexts가 비어서
# RAGAS의 context_precision/recall이 무의미해짐 -> 벡터 RAG를 평가하려는 목적에 맞게 제외
EVAL_SET = [
  {
    "question": "데이터베이스로 무엇을 사용했나요?",
    "ground_truth": "MySQL, Oracle, MSSQL, PostgreSQL, Redis, Google BigQuery 등을 사용했습니다.",
  },
  {
    "question": "백엔드 개발에서 주로 사용한 언어는 무엇인가요?",
    "ground_truth": "C#과 Java를 주로 사용했습니다.",
  },
  {
    "question": "포트폴리오에 RPG 장르 게임이 있나요?",
    "ground_truth": "아니요, RPG 장르 프로젝트는 없습니다. 매치-3 퍼즐, SNS, 드레스업, SNG 장르 프로젝트들이 있습니다.",
  },
]


# EVAL_SET의 각 질문을 파이프라인에 실제로 물어서 RAGAS가 요구하는 형식(question/answer/contexts/ground_truth)으로 변환
def build_eval_dataset(pipeline, k=3):
  questions, answers, contexts_list, ground_truths = [], [], [], []

  for item in EVAL_SET:
    result = pipeline.answer(item["question"], k=k)
    questions.append(item["question"])
    answers.append(result["answer"])
    contexts_list.append([c["text"] for c in result["contexts"]])
    ground_truths.append(item["ground_truth"])

  return Dataset.from_dict({
    "question": questions,
    "answer": answers,
    "contexts": contexts_list,
    "ground_truth": ground_truths,
  })


# OpenAI API 키 없이 평가하기 위해, judge LLM과 judge 임베딩을 모두 로컬 무료 모델(Qwen2.5 + sentence-transformers)로 구성.
# [버그 수정] model=DEFAULT_MODEL_NAME 문자열을 그대로 넘기면 transformers.pipeline()이
# 디바이스를 지정 안 한 채로 같은 모델을 또 "새로" 로드해서 기본값인 CPU에 올라가버림
# (이미 generator가 GPU에 올려둔 모델/토크나이저를 재사용하면 GPU로 돌고, 메모리도 안 낭비됨)
def get_ragas_llm_and_embeddings(generator):
  from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
  from ragas.embeddings import LangchainEmbeddingsWrapper
  from ragas.llms import LangchainLLMWrapper
  from transformers import pipeline as hf_pipeline

  from rag.indexer import EMBEDDING_MODEL_NAME

  text_gen = hf_pipeline(
    "text-generation",
    model=generator.model,
    tokenizer=generator.tokenizer,
    max_new_tokens=512,
    do_sample=False,
    device_map="auto",
  )
  llm = LangchainLLMWrapper(HuggingFacePipeline(pipeline=text_gen))
  embeddings = LangchainEmbeddingsWrapper(HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME))
  return llm, embeddings


# 파이프라인 생성 -> 평가 데이터셋 구축 -> RAGAS 지표 계산 -> 결과 출력/저장
def main():
  from ragas.run_config import RunConfig

  pipeline = RAGPipeline()
  dataset = build_eval_dataset(pipeline)
  llm, embeddings = get_ragas_llm_and_embeddings(pipeline.generator)

  # 로컬 모델은 동시 요청을 처리 못 하는 단일 리소스라 max_workers=1로 직렬화하고 타임아웃을 늘림
  run_config = RunConfig(timeout=600, max_workers=1)

  result = evaluate(
    dataset,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    llm=llm,
    embeddings=embeddings,
    run_config=run_config,
  )

  print(result)
  result.to_pandas().to_csv("ragas_eval_result.csv", index=False)


if __name__ == "__main__":
  main()
