import re

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)")
HR_RE = re.compile(r"^-{3,}$")


# 마크다운 문단들을 순회하며, 단독 헤더 문단은 컨텍스트로만 누적하고
# 실제 내용 문단에는 상위 헤더(예: "## SKYWALK (2024.01~2026.02)")를 prefix로 붙여서
# "어느 회사/기간 소속 프로젝트인지"가 청크 텍스트 자체에 남도록 함
def chunk_markdown(text):
  heading_stack = {}
  chunks = []

  for paragraph in text.split("\n\n"):
    paragraph = paragraph.strip()
    if not paragraph or HR_RE.match(paragraph):
      continue

    lines = paragraph.split("\n")
    match = HEADING_RE.match(lines[0])

    if match and len(lines) == 1:
      level = len(match.group(1))
      heading_stack[level] = match.group(2)
      for deeper in [l for l in heading_stack if l > level]:
        del heading_stack[deeper]
      continue

    own_level = None
    if match:
      own_level = len(match.group(1))
      heading_stack[own_level] = match.group(2)
      for deeper in [l for l in heading_stack if l > own_level]:
        del heading_stack[deeper]

    context_levels = sorted(l for l in heading_stack if own_level is None or l < own_level)
    prefix = " > ".join(heading_stack[l] for l in context_levels)
    chunks.append(f"[{prefix}] {paragraph}" if prefix else paragraph)

  return chunks


LABEL_MAX_LEN = 20
HANGUL_RE = re.compile(r"[가-힣]")


# 짧고 문장 종결부호가 없는 한 줄짜리 문단은 "백엔드 언어", "데이터베이스"처럼
# 원본 HTML의 제목/레이블이었을 가능성이 높음 (마크다운의 "#" 같은 표식이 없으므로 길이로 추정)
def _is_label(paragraph):
  return (
    "\n" not in paragraph
    and len(paragraph) <= LABEL_MAX_LEN
    and not paragraph.endswith((".", "!", "?", ")"))
  )


# 한글이 전혀 없고 공백으로만 구분된 문단("Java C# Go ... C++")은 기술 태그 목록일 가능성이 높음.
# [실측] 임베딩 모델이 공백 구분 목록은 자연어로 못 읽어서 쿼리와의 거리가 0.88까지 치솟지만,
# 쉼표로 구분하면 0.51까지 떨어짐 ("어떤 언어를 사용했나요?" 같은 질문에 실제로 검색되려면 필요)
def _looks_like_tag_list(paragraph):
  tokens = paragraph.split()
  return not HANGUL_RE.search(paragraph) and len(tokens) >= 2


# HTML에서 추출한 문단들을 순회하며, 레이블성 문단을 바로 다음 문단 하나에만 prefix로 붙임
# (계속 들고 있으면 그 뒤로 등장하는 무관한 문단까지 같은 레이블이 잘못 붙기 때문에 1회성으로 소비)
def chunk_html(text):
  current_label = None
  chunks = []

  for paragraph in text.split("\n\n"):
    paragraph = paragraph.strip()
    if not paragraph:
      continue

    if _is_label(paragraph):
      # [되돌림] 한때 연속 레이블을 다 이어붙여봤지만, 레이블이 3~4개씩 연속될 때
      # (날짜/자격증명/섹션명 등 무관한 레이블까지) 진짜 중요한 마지막 레이블("백엔드 언어")이
      # 노이즈에 묻혀버리는 더 나쁜 문제가 생겼음. 가장 가까운(=가장 구체적인) 레이블만 유지
      current_label = paragraph
      continue

    if current_label:
      if _looks_like_tag_list(paragraph):
        tag_list = ", ".join(paragraph.split())
        chunks.append(f"{current_label}: {tag_list}")
      else:
        chunks.append(f"[{current_label}] {paragraph}")
      # [버그 수정] 이 줄을 지우면 current_label이 다음 레이블이 나오기 전까지 계속 유지되어,
      # "Go C# MySQL Redis" 같은 레이블이 그 뒤 한참 떨어진 무관한 문단들에까지 잘못 붙는 문제가 재발함
      current_label = None
    else:
      chunks.append(paragraph)

  return chunks


# 문서 하나를 포맷에 맞는 기준으로 청크 리스트로 쪼갬
# json: 줄 단위 / markdown·html: 레이블·헤더 컨텍스트를 붙인 문단 단위
def chunk_document(doc):
  fmt = doc["metadata"]["format"]

  if fmt == "json":
    pieces = [line.strip() for line in doc["text"].split("\n") if line.strip()]
  elif fmt == "markdown":
    pieces = chunk_markdown(doc["text"])
  elif fmt == "html":
    pieces = chunk_html(doc["text"])
  else:
    pieces = [p.strip() for p in doc["text"].split("\n\n") if p.strip()]

  return [{"text": piece, "metadata": doc["metadata"]} for piece in pieces]


# 문서 목록 전체를 청크 목록 하나로 합침
def chunk_documents(documents):
  chunks = []
  for doc in documents:
    chunks.extend(chunk_document(doc))
  return chunks
