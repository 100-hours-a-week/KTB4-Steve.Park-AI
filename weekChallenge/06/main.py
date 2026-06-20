# https://colab.research.google.com/drive/1-Xq6pKrbkttZJnQhDYjISSZEP7NsRbo2?usp=drive_link
# 1. (미니 프로젝트) Gemini API 또는 공개 가중치 모델(Qwen, Gemma 등)을 LLM으로 삼아 문서 로딩부터 응답 생성까지 RAG 아키텍처를 구축하세요.
#   1. 구축한 RAG 파이프라인을 FastAPI로 래핑하여 REST API로 배포해 보세요. (선택: 스트리밍)
#   2. 구축한 RAG 파이프라인을 평가해 보세요. (RAGAS 등 활용) 
#   3. (선택) Graph RAG을 알아보고 적용해보세요.

# !pip install -q sentence-transformers chromadb numpy

import json
from html.parser import HTMLParser

class HTMLTextExtractor(HTMLParser):
  def __init__(self):
    super().__init__()
    self.texts = []
  
  def handle_data(self, data):
    self.texts.append(data.strip())

  def get_text(self):
    return " ".join(t for t in self.texts if t)

# ===== Markdown 로딩 =====
def load_markdown(filepath):
  with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

  return {"text": text, "metadata": {"source":filepath, "format":"markdown"}}

# ===== HTML 로딩 =====
def load_html(filepath):
  with open(filepath, "r", encoding="utf-8") as f:
    html = f.read()

  parser = HTMLTextExtractor()
  parser.feed(html)
  text = parser.get_text()

  return {"text": text, "metadata": {"source":filepath, "format":"html"}}

# ===== JSON 로딩 =====
def load_json_reviews(filepath):
  with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

  reviews = data.get("reviews", [])

  texts = []

  for review in reviews:
      title = review.get("title", "")
      content = review.get("content", "")
      author = review.get("author", "")
      rating = review.get("rating", "")

      texts.append(f"[{author}, {rating}점] {title}: {content}")

  text = "\n".join(texts)

  return {"text": text, "metadata": {"source": filepath, "format": "json"}}

def load_document(filepath):
  if filepath.endswith(".md"):
    return load_markdown(filepath)

  elif filepath.endswith(".html"):
    return load_html(filepath)

  elif filepath.endswith(".json"):
    return load_json_reviews(filepath)

  else:
    raise ValueError(f"지원하지 않는 형식: {filepath}")

files = ["portfolio_usage.md", "project_info.md", "index.html", "portfolio_review.json"]

documents = []

for filepath in files:
  filepath = f"Portfolio/{filepath}"
  doc = load_document(filepath)
  documents.append(doc)
  print(f"[{doc['metadata']['format'].upper()}] {doc['metadata']['source']}")
  print(f"  텍스트 길이: {len(doc['text'])}자")
  print(f"  미리보기: {doc['text'][:80]}...")
  print()

# ===== 로딩된 문서를 청크 단위로 저장 =====
import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

client = chromadb.Client()

collection = client.create_collection(
  name="docload_demo",
  metadata={"hnsw:space": "cosine"}
)

all_chunks = []
all_metadatas = []

for doc in documents:
  fmt = doc["metadata"]["format"]
  if fmt == "json":
    chunks = [line.strip() for line in doc["text"].split("\n") if line.strip()]
  else:
    chunks = [p.strip() for p in doc["text"].split("\n\n") if p.strip()]

  for chunk in chunks:
    all_chunks.append(chunk)
    all_metadatas.append(doc["metadata"])

print(f"총 청크 수: {len(all_chunks)}")

embeddings = model.encode(all_chunks).tolist()

collection.add(
  ids=[f"chunk_{i}" for i in range(len(all_chunks))],
  documents=all_chunks,
  embeddings=embeddings,
  metadatas=all_metadatas
)

# 검색 후 출력
def search_and_print(collection, model, query, n_results=2):
  query_embedding = model.encode(query).tolist()
  results = collection.query(
    query_embeddings=[query_embedding],
    n_results=n_results
  )

  print(f"Query: {query}\n")

  for i in range(len(results["documents"][0])):
    print(f"[{i+1}위] {results['documents'][0][i][:80]}...")
    print(f"     출처: {results['metadatas'][0][i]['source']}")
    print(f"     형식: {results['metadatas'][0][i]['format']}")
    print(f"     거리: {results['distances'][0][i]:.4f}")
    print()

  print("=" * 80)
  print()

search_and_print(collection, model, "포트폴리오의 마지막 프로젝트는 무엇인가요?")
search_and_print(collection, model, "어떤 언어를 주로 사용했나요?")
search_and_print(collection, model, "RPG장르가 있나요?")


"""
나는 왜 교재와 다르게 매우 다른 답변이 나오는걸까. chunking부분이 잘못되었나?
그렇다면 한번 claude에게 물어보자.
클로드의 답변은

원인: 
HTMLTextExtractor.get_text()가 모든 텍스트 노드를 " ".join()으로 공백 하나로 이어붙이기 때문입니다. 
<p>, <div>, <h2> 같은 블록 태그 경계에서 줄바꿈이 전혀 보존되지 않아서, 
이후 text.split("\n\n") 로직이 아무 효과가 없습니다.

영향: 
"RPG 장르가 있나요?", "어떤 언어를 주로 사용했나요?" 같은 질문에 대해 
학력/경력/어학/프로젝트 정보가 전부 뭉쳐진 거대한 청크 하나만 검색되므로, 
정확도가 떨어지고 교재와 다른(엉뚱한) 검색 결과가 나올 수밖에 없습니다. 
md/json은 청크가 15~18개씩 잘 쪼개지는데 html만 1개라서 격차가 큽니다.

음 그럼 html청킹을 수정해보자.
"""

# ===== HTML 로딩 =====
BLOCK_TAGS = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr", "br", "section", "article"}

class HTMLTextExtractorV2(HTMLParser):
  def __init__(self):
    super().__init__()
    self.texts = []

  def handle_starttag(self, tag, attrs):
    if tag in BLOCK_TAGS:
      self.texts.append("\n\n")

  def handle_endtag(self, tag):
    if tag in BLOCK_TAGS:
      self.texts.append("\n\n")

  def handle_data(self, data):
    self.texts.append(data.strip())

  def get_text(self):
    text = " ".join(t for t in self.texts if t)
    while "\n\n " in text:
      text = text.replace("\n\n ", "\n\n")
    while " \n\n" in text:
      text = text.replace(" \n\n", "\n\n")
    while "\n\n\n\n" in text:
      text = text.replace("\n\n\n\n", "\n\n")
    return text.strip()

def load_html_v2(filepath):
  with open(filepath, "r", encoding="utf-8") as f:
    html = f.read()

  parser = HTMLTextExtractorV2()
  parser.feed(html)
  text = parser.get_text()

  return {"text": text, "metadata": {"source":filepath, "format":"html"}}
  

def load_document_v2(filepath):
  if filepath.endswith(".md"):
    return load_markdown(filepath)

  elif filepath.endswith(".html"):
    return load_html_v2(filepath)

  elif filepath.endswith(".json"):
    return load_json_reviews(filepath)

  else:
    raise ValueError(f"지원하지 않는 형식: {filepath}")

files = ["portfolio_usage.md", "project_info.md", "index.html", "portfolio_review.json"]

documents = []

for filepath in files:
  filepath = f"Portfolio/{filepath}"
  doc = load_document_v2(filepath)
  documents.append(doc)
  print(f"[{doc['metadata']['format'].upper()}] {doc['metadata']['source']}")
  print(f"  텍스트 길이: {len(doc['text'])}자")
  print(f"  미리보기: {doc['text'][:80]}...")
  print()

# ===== 로딩된 문서를 청크 단위로 저장 =====
import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

client = chromadb.Client()

collection = client.create_collection(
  name="docload_demo_v2",
  metadata={"hnsw:space": "cosine"},
)

all_chunks = []
all_metadatas = []

for doc in documents:
  fmt = doc["metadata"]["format"]
  if fmt == "json":
    chunks = [line.strip() for line in doc["text"].split("\n") if line.strip()]
  else:
    chunks = [p.strip() for p in doc["text"].split("\n\n") if p.strip()]

  for chunk in chunks:
    all_chunks.append(chunk)
    all_metadatas.append(doc["metadata"])

print(f"총 청크 수: {len(all_chunks)}")

embeddings = model.encode(all_chunks).tolist()

collection.add(
  ids=[f"chunk_{i}" for i in range(len(all_chunks))],
  documents=all_chunks,
  embeddings=embeddings,
  metadatas=all_metadatas
)

# 검색 후 출력
def search_and_print(collection, model, query, n_results=2):
  query_embedding = model.encode(query).tolist()
  results = collection.query(
    query_embeddings=[query_embedding],
    n_results=n_results
  )

  print(f"Query: {query}\n")

  for i in range(len(results["documents"][0])):
    print(f"[{i+1}위] {results['documents'][0][i][:80]}...")
    print(f"     출처: {results['metadatas'][0][i]['source']}")
    print(f"     형식: {results['metadatas'][0][i]['format']}")
    print(f"     거리: {results['distances'][0][i]:.4f}")
    print()

  print("=" * 80)
  print()

search_and_print(collection, model, "포트폴리오의 마지막 프로젝트는 무엇인가요?")
search_and_print(collection, model, "어떤 언어를 주로 사용했나요?")
search_and_print(collection, model, "RPG장르가 있나요?")

"""
확실히 개선 된 것이 보인다.
index.html에는 나의 포트폴리오 정보가 다 들어있기 때문에 웬만하면 모든 질문은 여기 html에서 찾아볼 수 있다.
하지만 질문에 대한 정확한 대답과는 다르게 우선 큰 청크부터 보여주는걸 알 수가 있다.
"""