import os

from rag.chunking import chunk_documents
from rag.generator import Generator
from rag.graph import answer_with_graph, extract_career_graph
from rag.indexer import build_index
from rag.loaders import load_documents
from rag.retriever import Retriever

DEFAULT_FILES = ["portfolio_usage.md", "project_info.md", "index.html", "portfolio_review.json"]


class RAGPipeline:
  # 문서 로딩~인덱싱(retriever)과 LLM(generator)을 한 번에 준비
  def __init__(self, docs_dir="docs", files=None, model_name=None):
    self.docs_dir = docs_dir
    self.files = files or DEFAULT_FILES
    self.generator = Generator(model_name) if model_name else Generator()
    self.retriever = self._build_retriever()
    self.graph = self._build_graph()

  # docs_dir의 파일들을 로딩 -> 청킹 -> 인덱싱해서 Retriever를 만듦
  def _build_retriever(self):
    filepaths = [os.path.join(self.docs_dir, f) for f in self.files]
    documents = load_documents(filepaths)
    chunks = chunk_documents(documents)
    collection = build_index(chunks)
    return Retriever(collection)

  # index.html에서 회사-프로젝트 관계 그래프를 뽑아둠 (없으면 그래프 기능 없이 동작)
  def _build_graph(self):
    html_path = os.path.join(self.docs_dir, "index.html")
    if not os.path.exists(html_path):
      return None
    return extract_career_graph(html_path)

  # use_graph=True(기본값)면 "최근/마지막" 같은 관계형 질문을 그래프로 먼저 답을 시도하고
  # (날짜 비교라 정확함), 그래프가 못 답하면(회사명이 없거나 관계형 질문이 아니면) 벡터 RAG로 폴백.
  # use_graph=False면 그래프를 아예 거치지 않고 항상 벡터 RAG로만 답함 (둘을 비교해볼 때 사용)
  def answer(self, query, k=5, max_new_tokens=512, use_graph=True):
    if use_graph and self.graph is not None:
      graph_answer = answer_with_graph(self.graph, query)
      if graph_answer:
        return {"answer": graph_answer, "contexts": [], "source": "graph"}

    contexts = self.retriever.retrieve(query, k=k)
    answer = self.generator.generate(query, contexts, max_new_tokens=max_new_tokens)
    return {"answer": answer, "contexts": contexts, "source": "vector"}

  # 검색 후 답변을 토큰 스트림으로 받고 싶을 때 사용 (use_graph 의미는 answer()와 동일)
  def answer_stream(self, query, k=5, max_new_tokens=512, use_graph=True):
    if use_graph and self.graph is not None:
      graph_answer = answer_with_graph(self.graph, query)
      if graph_answer:
        return [], iter([graph_answer]), "graph"

    contexts = self.retriever.retrieve(query, k=k)
    token_stream = self.generator.generate_stream(query, contexts, max_new_tokens=max_new_tokens)
    return contexts, token_stream, "vector"
