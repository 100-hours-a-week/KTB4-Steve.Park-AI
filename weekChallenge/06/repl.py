"""RAG 파이프라인을 코드 없이 터미널에서 바로 테스트하기 위한 REPL.

사용법:
  python3 repl.py
  질문 입력 -> 답변 출력, 반복. 종료는 exit/quit/Ctrl+C.
"""

from rag.pipeline import RAGPipeline


def main():
  print("모델/인덱스 로딩 중...")
  pipeline = RAGPipeline()
  print("준비 완료. 질문을 입력하세요 (종료: exit/quit)\n")

  while True:
    try:
      query = input("Q> ").strip()
    except (EOFError, KeyboardInterrupt):
      print()
      break

    if not query:
      continue
    if query.lower() in ("exit", "quit"):
      break

    result = pipeline.answer(query)
    print(f"A> {result['answer']}")
    print(f"   (source: {result['source']})\n")


if __name__ == "__main__":
  main()
