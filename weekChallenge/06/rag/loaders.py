import json
from html.parser import HTMLParser

BLOCK_TAGS = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr", "br", "section", "article"}


class HTMLTextExtractor(HTMLParser):
  # 텍스트 조각을 모아둘 리스트 초기화
  def __init__(self):
    super().__init__()
    self.texts = []

  # 블록 태그가 시작되면 단락 구분자(\n\n)를 끼워 넣음
  def handle_starttag(self, tag, attrs):
    if tag in BLOCK_TAGS:
      self.texts.append("\n\n")

  # 블록 태그가 끝나도 동일하게 단락 구분자를 끼워 넣음
  def handle_endtag(self, tag):
    if tag in BLOCK_TAGS:
      self.texts.append("\n\n")

  # 태그 사이의 실제 텍스트 데이터를 수집
  def handle_data(self, data):
    self.texts.append(data.strip())

  # 수집된 조각들을 합치고 중복된 공백/구분자를 정리해 최종 텍스트로 반환
  def get_text(self):
    text = " ".join(t for t in self.texts if t)
    while "\n\n " in text:
      text = text.replace("\n\n ", "\n\n")
    while " \n\n" in text:
      text = text.replace(" \n\n", "\n\n")
    while "\n\n\n\n" in text:
      text = text.replace("\n\n\n\n", "\n\n")
    return text.strip()


# 마크다운 파일을 그대로 읽어 텍스트/메타데이터 형태로 반환
def load_markdown(filepath):
  with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

  return {"text": text, "metadata": {"source": filepath, "format": "markdown"}}


# HTML 파일을 파싱해 단락 구조가 보존된 순수 텍스트로 변환
def load_html(filepath):
  with open(filepath, "r", encoding="utf-8") as f:
    html = f.read()

  parser = HTMLTextExtractor()
  parser.feed(html)
  text = parser.get_text()

  return {"text": text, "metadata": {"source": filepath, "format": "html"}}


DEDUP_PREFIX_LEN = 30
MAX_REVIEWS = 20


# 리뷰들이 같은 도입부 문장을 템플릿처럼 반복하는 경우가 많아서, 검색 시 동일한 의견이
# 여러 번 중복으로 뽑혀 다른 사실 정보 청크를 밀어내는 문제가 있었음.
# content 앞 30자가 같으면 같은 의견으로 보고 처음 등장한 것만 남기고, 그래도 많이 남으면 일부만 샘플링
def _dedup_reviews(reviews):
  seen_prefixes = set()
  deduped = []

  for review in reviews:
    prefix = review.get("content", "")[:DEDUP_PREFIX_LEN]
    if prefix in seen_prefixes:
      continue
    seen_prefixes.add(prefix)
    deduped.append(review)

  return deduped[:MAX_REVIEWS]


# 리뷰 JSON을 읽어 리뷰 1건당 한 줄짜리 텍스트로 변환 (중복 의견은 제거됨)
def load_json_reviews(filepath):
  with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

  reviews = _dedup_reviews(data.get("reviews", []))
  texts = []

  for review in reviews:
    title = review.get("title", "")
    content = review.get("content", "")
    author = review.get("author", "")
    rating = review.get("rating", "")
    texts.append(f"[{author}, {rating}점] {title}: {content}")

  text = "\n".join(texts)

  return {"text": text, "metadata": {"source": filepath, "format": "json"}}


# 확장자를 보고 적절한 로더로 분기
def load_document(filepath):
  if filepath.endswith(".md"):
    return load_markdown(filepath)
  elif filepath.endswith(".html"):
    return load_html(filepath)
  elif filepath.endswith(".json"):
    return load_json_reviews(filepath)
  else:
    raise ValueError(f"지원하지 않는 형식: {filepath}")


# 여러 파일 경로를 한 번에 로딩
def load_documents(filepaths):
  return [load_document(fp) for fp in filepaths]
