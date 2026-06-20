from rag.indexer import get_embedding_model


class Retriever:
  # Chroma 컬렉션과 임베딩 모델을 묶어서 들고 있는 래퍼
  def __init__(self, collection):
    self.collection = collection
    self.model = get_embedding_model()

  # 쿼리를 임베딩한 뒤 가장 유사한 청크 k개를 찾아 반환
  def retrieve(self, query, k=3):
    query_embedding = self.model.encode(query).tolist()
    results = self.collection.query(
      query_embeddings=[query_embedding],
      n_results=k,
    )

    hits = []
    for i in range(len(results["documents"][0])):
      hits.append({
        "text": results["documents"][0][i],
        "metadata": results["metadatas"][0][i],
        "distance": results["distances"][0][i],
      })
    return hits
