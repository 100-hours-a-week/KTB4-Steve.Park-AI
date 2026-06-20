import chromadb
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

_embedding_model = None


# 임베딩 모델을 한 번만 로드해서 재사용하기 위한 싱글톤 getter
def get_embedding_model():
  global _embedding_model
  if _embedding_model is None:
    _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
  return _embedding_model


# 청크들을 임베딩해서 새 Chroma 컬렉션에 적재
def build_index(chunks, collection_name="docload_demo", client=None):
  model = get_embedding_model()
  client = client or chromadb.Client()

  try:
    client.delete_collection(collection_name)
  except Exception:
    pass

  collection = client.create_collection(
    name=collection_name,
    metadata={"hnsw:space": "cosine"},
  )

  texts = [c["text"] for c in chunks]
  metadatas = [c["metadata"] for c in chunks]
  embeddings = model.encode(texts).tolist()

  collection.add(
    ids=[f"chunk_{i}" for i in range(len(texts))],
    documents=texts,
    embeddings=embeddings,
    metadatas=metadatas,
  )

  return collection
