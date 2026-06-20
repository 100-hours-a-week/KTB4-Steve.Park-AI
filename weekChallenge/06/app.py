from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from rag.pipeline import RAGPipeline

pipeline: RAGPipeline | None = None


# 서버 기동 시 한 번만 RAGPipeline(모델 로딩 포함)을 만들어 전역으로 재사용
@asynccontextmanager
async def lifespan(app: FastAPI):
  global pipeline
  pipeline = RAGPipeline()
  yield


app = FastAPI(lifespan=lifespan)


class QueryRequest(BaseModel):
  question: str
  k: int = 5
  max_new_tokens: int = 512
  use_graph: bool = True  # False로 보내면 그래프 없이 항상 벡터 RAG로만 답함 (둘을 비교해볼 때 사용)


class Source(BaseModel):
  text: str
  source: str
  format: str
  distance: float


class QueryResponse(BaseModel):
  answer: str
  sources: list[Source]
  source_type: str  # "graph" 면 회사-프로젝트 관계 그래프로 답한 것, "vector" 면 벡터 검색+LLM 생성


# 내부 컨텍스트 dict 목록을 응답 모델(Source)로 변환
def _to_sources(contexts):
  return [
    Source(
      text=c["text"],
      source=c["metadata"]["source"],
      format=c["metadata"]["format"],
      distance=c["distance"],
    )
    for c in contexts
  ]


# 질문을 받아 검색+생성을 수행하고 답변과 근거 출처를 한 번에 반환
@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
  result = pipeline.answer(
    req.question, k=req.k, max_new_tokens=req.max_new_tokens, use_graph=req.use_graph
  )
  return QueryResponse(
    answer=result["answer"],
    sources=_to_sources(result["contexts"]),
    source_type=result["source"],
  )


# 답변을 토큰 단위로 스트리밍해서 내려주는 버전 (그래프로 답한 경우는 토큰 1개로 한 번에 내려감)
@app.post("/query/stream")
def query_stream(req: QueryRequest):
  contexts, token_stream, source_type = pipeline.answer_stream(
    req.question, k=req.k, max_new_tokens=req.max_new_tokens, use_graph=req.use_graph
  )
  return StreamingResponse(
    token_stream, media_type="text/plain", headers={"X-Source-Type": source_type}
  )
