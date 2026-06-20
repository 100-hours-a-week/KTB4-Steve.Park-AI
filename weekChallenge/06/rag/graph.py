import re
from datetime import datetime

import networkx as nx

# index.html의 경력/프로젝트 영역은 구조가 일정함:
#   <span class="company">SKYWALK</span> ... <span class="period">...</span>
#   <div class="proj-item">
#     <div class="proj-title">코코마인 <span class="pdate">2024.12 ~ 2026.02</span>...</div>
#     ...<p class="proj-genre">장르: ...</p>
# 회사 span이 나오면 "현재 회사"를 갱신하고, 그 뒤에 나오는 proj-item들을 전부 그 회사 소속으로 묶음
TOKEN_RE = re.compile(
  r'<span class="company">(?P<company>[^<]+)</span>'
  r'|<div class="proj-title">(?P<project>[^<]+?)\s*<span class="pdate">(?P<pdate>[^<]+)</span>'
  r'|<p class="proj-genre">장르:\s*(?P<genre>[^<]+)</p>'
)


# 회사명 -> [회사] -> [프로젝트(시작일/종료일/장르)] 구조의 그래프를 추출
def extract_career_graph(html_path):
  with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

  graph = nx.DiGraph()
  current_company = None
  current_project = None

  for match in TOKEN_RE.finditer(html):
    if match.group("company"):
      current_company = match.group("company").strip()
      graph.add_node(current_company, type="company")

    elif match.group("project"):
      project = match.group("project").strip()
      start, _, end = match.group("pdate").partition("~")
      start = start.strip()
      end = end.strip() or start

      graph.add_node(project, type="project", start=start, end=end, genre=None)
      if current_company:
        graph.add_edge(current_company, project, relation="참여")
      current_project = project

    elif match.group("genre") and current_project:
      graph.nodes[current_project]["genre"] = match.group("genre").strip()

  return graph


def _parse_date(date_str):
  return datetime.strptime(date_str, "%Y.%m")


# 회사 노드에서 뻗어나간 프로젝트들 중 시작일이 가장 늦은(=가장 최근에 참여한) 프로젝트를 찾음
# 벡터 검색은 "이 중 어느 게 최신인지" 비교할 근거가 청크에 없어서 추측에 의존하지만,
# 그래프는 각 프로젝트의 실제 시작일(pdate)을 들고 있어서 날짜 비교로 정확하게 답할 수 있음
def most_recent_project(graph, company):
  if company not in graph:
    return None

  projects = [
    (project, graph.nodes[project])
    for project in graph.successors(company)
  ]
  if not projects:
    return None

  return max(projects, key=lambda p: _parse_date(p[1]["start"]))


# 회사명이 영문(SKYWALK, UXIS)으로만 그래프에 들어있어서, 한글로 묻는 질문("스카이워크", "유시스")도
# 매칭되도록 별칭을 등록해둠
COMPANY_ALIASES = {
  "스카이워크": "SKYWALK",
  "유시스": "UXIS",
}


# 질문에서 회사명 + "최근/마지막" 패턴을 감지해서 그래프로 답할 수 있으면 답하고,
# 아니면 None을 반환해서 호출 쪽이 기존 벡터 RAG로 폴백하게 함
def answer_with_graph(graph, query):
  if not any(keyword in query for keyword in ["최근", "마지막", "최신"]):
    return None

  company = next(
    (c for c in graph.nodes if graph.nodes[c].get("type") == "company" and c in query),
    None,
  )
  if not company:
    alias = next((name for name in COMPANY_ALIASES if name in query), None)
    company = COMPANY_ALIASES.get(alias)
  if not company:
    return None

  result = most_recent_project(graph, company)
  if not result:
    return None

  project, attrs = result
  return (
    f"{company}에서 가장 최근에 참여한 프로젝트는 '{project}'입니다 "
    f"(시작일: {attrs['start']}, 장르: {attrs.get('genre') or '정보 없음'})."
  )
