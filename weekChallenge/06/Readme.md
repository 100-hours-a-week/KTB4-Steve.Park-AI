# 06 — RAG 아키텍처 미니 프로젝트

Qwen2.5(공개 가중치 모델)를 LLM으로 사용해 문서 로딩부터 응답 생성까지 RAG 파이프라인을 구축하고,
FastAPI로 REST API로 래핑하고, RAGAS로 평가하고, Graph RAG까지 적용해본 과제.

## 과제 요구사항 체크리스트

- [x] Gemini API 또는 공개 가중치 모델(Qwen, Gemma 등)을 LLM으로 RAG 아키텍처 구축
- [x] FastAPI로 REST API 래핑 (스트리밍 포함)
- [x] RAGAS로 파이프라인 평가
- [x] (선택) Graph RAG 적용

## 데이터

`docs/` 아래 박상욱님의 포트폴리오 관련 문서 4종 (형식이 전부 다름):

| 파일 | 형식 | 내용 |
|---|---|---|
| `index.html` | HTML | 포트폴리오 본문 (학력/경력/기술스택/프로젝트 목록) |
| `portfolio_usage.md` | Markdown | 포트폴리오 사용 설명서 |
| `project_info.md` | Markdown | 프로젝트별 공개 정보 정리 |
| `portfolio_review.json` | JSON | 가상 리뷰 데이터 100건 (연습용 샘플) |

## 구조

```
06/
  rag/
    loaders.py      # md/html/json 로딩 (형식별 파서)
    chunking.py      # 형식별 청킹 (마크다운 헤더·HTML 레이블 컨텍스트 보존)
    indexer.py        # 임베딩 + Chroma 인덱스 빌드
    retriever.py      # 벡터 유사도 검색
    generator.py       # Qwen2.5-1.5B-Instruct 응답 생성 (스트리밍 지원)
    graph.py            # index.html에서 회사-프로젝트 관계 그래프 추출 (Graph RAG)
    pipeline.py          # RAGPipeline: 그래프 우선 라우팅 -> 벡터 RAG 폴백
  app.py                 # FastAPI: POST /query, POST /query/stream
  evaluate.py             # RAGAS 평가 (faithfulness/answer_relevancy/context_precision/context_recall)
  requirements.txt
  docs/                    # 원본 데이터
  main.py                   # 초기 탐색 과정을 기록한 개인 노트북 (정식 구조 아님)
```

## 실행 방법

```bash
pip install -r requirements.txt
```

### 1. RAG 파이프라인만 테스트

```bash
python3 repl.py
```

실행하면 모델/인덱스를 로딩한 뒤 `Q>` 프롬프트가 뜨고, 질문을 입력할 때마다 답변과 출처
(`graph`/`vector`)를 바로 출력함. 종료는 `exit`/`quit` 또는 Ctrl+C.

코드로 직접 호출하고 싶다면:

```python
from rag.pipeline import RAGPipeline

pipeline = RAGPipeline()
result = pipeline.answer("어떤 언어를 주로 사용했나요?", k=5)
print(result["answer"])
```

### 2. FastAPI 서버

```bash
uvicorn app:app --reload
```

`POST /query` body: `{"question": "...", "k": 5, "use_graph": true}` → `{"answer", "sources", "source_type"}`
`POST /query/stream` — 같은 입력으로 토큰 스트리밍 응답 (어느 경로로 답했는지는 `X-Source-Type` 헤더로 확인).

`use_graph`(기본값 `true`)로 그래프 라우팅을 켜고 끌 수 있어서, 같은 질문을 그래프 적용/미적용으로
바로 비교해볼 수 있음:

localhost:8000/docs 접속 후 /query에서 
question에는 질문,
use_graph는 True면 그래프검색 설정 / False면 그래프 검색 끄기
로 테스트 가능

```bash
curl -s localhost:8000/query -H "Content-Type: application/json" -d '{"question": "박상욱님이 스카이워크에서 가장 최근에 참여한 프로젝트는?", "use_graph": true}'
# -> source_type: "graph", answer: "...'코코마인'입니다..."

curl -s localhost:8000/query -H "Content-Type: application/json" -d '{"question": "박상욱님이 스카이워크에서 가장 최근에 참여한 프로젝트는?", "use_graph": false}'
# -> source_type: "vector", answer: "...'놀러와 마이홈'입니다..." (틀린 답)
```

> `-H "Content-Type: application/json"`을 빠뜨리면 curl이 기본값인 `application/x-www-form-urlencoded`로
> 보내서 FastAPI가 body를 파싱하지 못하고 422 에러가 남.

### 3. RAGAS 평가

```bash
python3 evaluate.py
```

OpenAI API 키 없이, judge LLM/임베딩도 로컬 모델(Qwen2.5 + sentence-transformers)을 재사용해서 평가하고
`ragas_eval_result.csv`로 결과를 저장함.

> 로컬 모델은 동시 요청을 처리 못 하므로 `RunConfig(timeout=600, max_workers=1)`로 직렬화함.

## 주요 의사결정 / 트러블슈팅 기록

### 청킹 — 형식별 문제와 수정

- **HTML**: `HTMLParser`로 추출한 텍스트가 공백 하나로 다 이어붙어서 문서 전체가 청크 1개가 되는 문제 →
  블록 태그(`p`, `div`, `h1~h6` 등) 경계에 `\n\n`을 끼워 넣어 단락을 보존.
- **HTML 레이블**: `"백엔드 언어"`(레이블)와 `"Java C# Go ..."`(값)가 서로 다른 청크로 쪼개지면서,
  값 청크엔 "언어"라는 단어가 없어 검색에 안 걸리는 문제 → 짧고 종결부호 없는 문단을 레이블로 인식해서
  바로 다음 문단에 1회성으로 붙임(계속 들고 있으면 무관한 문단까지 잘못 붙는 부작용이 있어서 1회성으로 제한).
- **태그 목록 임베딩 거리**: 실측 결과 `"Java C# Go ..."`처럼 공백으로만 구분된 목록은 임베딩 모델이
  자연어로 인식 못 해서 쿼리와의 거리가 0.88까지 치솟음. 쉼표로 구분(`"Java, C#, Go, ..."`)하면 0.51까지
  떨어짐 → 한글이 전혀 없는 공백 구분 문단을 감지해서 쉼표로 변환.
- **Markdown**: 헤더(`## SKYWALK (2024.01~2026.02)`)와 본문이 별개 청크로 분리되면서, 본문만 검색됐을 때
  "어느 회사 소속 프로젝트인지" 컨텍스트가 사라지는 문제 → 헤더를 컨텍스트로 누적해서 후속 문단에
  `[SKYWALK (2024.01~2026.02)] ### 코코마인 ...` 형태로 prefix.
- **리뷰 JSON 중복**: 리뷰 100건 중 다수가 같은 도입부 문장을 템플릿처럼 반복해서, 검색 시 같은 의견이
  여러 번 뽑혀 다른 사실 정보 청크를 밀어내는 문제 → 도입부 30자가 같으면 중복으로 보고 제거, 최대
  20건만 사용.

### 생성 — 스트리밍 버그

`TextIteratorStreamer`에 `skip_prompt=True`를 안 주면 시스템 프롬프트+컨텍스트+질문까지 전부
스트리밍되어버림(답변 앞에 프롬프트 전체가 출력됨) → `skip_prompt=True` 추가로 해결.

### 알려진 한계

벡터 검색은 "이 중 어느 게 최신/마지막인지" 같은 순서·날짜 비교를 못 함 — 어떤 청크에도 "마지막"이라는
의미가 명시적으로 들어있지 않기 때문. 예: "스카이워크에서 가장 최근에 참여한 프로젝트는?" 질문에
벡터 RAG는 반복적으로 틀린 답(예: "놀러와 마이홈")을 내놓았음. 이걸 해결하기 위해 Graph RAG를 추가함.

## Graph RAG (선택 항목)

`index.html`의 `proj-title`/`pdate`(시작일~종료일)/`proj-genre` 구조를 정규식으로 파싱해서
회사 → 프로젝트 관계 그래프(`networkx.DiGraph`)를 만들고, 질문에 "최근/마지막/최신" + 회사명이
들어있으면 그래프에서 프로젝트들의 **실제 시작일을 비교**해서 정확한 답을 낸 뒤, 안 되면 기존
벡터 RAG로 폴백하는 하이브리드 구조(`rag/pipeline.py`의 `RAGPipeline.answer()`).
`answer(..., use_graph=False)`로 그래프를 끄고 순수 벡터 RAG만 쓸 수도 있음 — FastAPI 쪽에도
`use_graph` 파라미터로 그대로 노출되어 있어서 두 방식을 나란히 비교해볼 수 있음(위 FastAPI 섹션 참고).

```
SKYWALK
  코코마인: 2024.12 ~ 2026.02            <- 가장 최근에 시작 (정답)
  코코마인 산리오 캐릭터즈: 2024.07 ~ 2026.02
  걸글로브: 2024.04 ~ 2026.02
  유미의 세포들: 2024.04 ~ 2026.02
  놀러와, 마이홈: 2024.01 ~ 2026.02        <- 벡터 RAG는 이걸 틀리게 답했음
```

벡터 RAG는 청크들에 날짜 비교 근거가 없어 추측했지만, 그래프는 `pdate`를 직접 비교해서
"코코마인"이라고 정확히 답함 — Graph RAG가 관계형 질문에서 벡터 검색보다 우월함을 보여주는 예시.

## 회고

<details>
<summary><b>기획 단계</b></summary>

처음엔 그냥 "교재랑 다르게 왜 이상한 답이 나오지?"라는 질문 하나로 시작했다. md/html/json 세 가지 형식을 로딩해서 Chroma에 넣고 검색하는 기본 골격은 비슷하게 따라갔는데, 검색 결과가 교재 예시와 너무 다르게 나왔다. 처음엔 "내가 뭘 잘못 베꼈나" 싶었지만, 한 단계씩 파고들면서 결국 형식별 청킹 방식 자체가 문제라는 걸 깨달았고, 거기서부터 RAG 파이프라인을 거의 처음부터 다시 설계하게 됐다.

  <details>
  <summary><b>1. HTML이 통째로 청크 1개가 되어 있었다</b></summary>

  `HTMLTextExtractor.get_text()`가 모든 텍스트 노드를 `" ".join()`으로 공백 하나로 이어붙이고 있었다. `<p>`, `<div>`, `<h2>` 같은 블록 태그 경계에서 줄바꿈이 전혀 보존되지 않으니, 이후 `text.split("\n\n")`로 청킹해도 분리될 지점이 없어서 6700자짜리 `index.html` 전체가 청크 1개로 들어가 있었다. md/json은 15~18개씩 잘 쪼개지는데 html만 1개인 걸 보고서야 격차를 체감했다. 블록 태그가 열리고 닫힐 때마다 `\n\n`을 끼워 넣는 것으로 해결했는데, 이렇게 간단한 수정 하나로 청크 수가 1개에서 100개 이상으로 뛰는 걸 보고 "청킹이 이렇게까지 결과를 좌우하는구나"를 처음 체감했다.

  </details>

  <details>
  <summary><b>2. 레이블과 값이 분리되면서, 고쳤다가 다시 망가뜨린 이야기</b></summary>

  `"백엔드 언어"`라는 레이블과 그 값인 `"Java C# Go ..."`가 서로 다른 청크로 쪼개지면서, "어떤 언어를 사용했나요?"라는 질문에 정작 값 청크에는 "언어"라는 단어 자체가 없어 검색에 안 걸리는 문제가 있었다. 레이블을 다음 문단에 붙이는 방식으로 고쳤는데, 처음엔 "레이블을 계속 들고 있다가 다음 레이블이 나오면 교체"하는 방식으로 짰다. 그랬더니 `"Go C# MySQL Redis"` 같은 짧은 기술스택 한 줄이 레이블로 오인되어, 그 뒤로 한참 떨어진 무관한 문단들에까지 잘못 붙어버리는 새로운 버그가 생겼다. "레이블이 사라지는 것보다 잘못 붙는 게 더 나쁘다"는 판단으로, 레이블은 바로 다음 문단 1개에만 붙고 즉시 소비(reset)되도록 되돌렸다. 한 번의 수정이 다른 문제를 만들고, 그걸 또 되돌리는 과정에서 "그나마 덜 나쁜 실패를 고르는 것"도 설계의 일부라는 걸 느꼈다.

  </details>

  <details>
  <summary><b>3. 임베딩 모델은 쉼표 하나로 거리가 0.88 → 0.51</b></summary>

  레이블을 붙였는데도 `"[백엔드 언어] Java C# Go ..."` 청크가 검색 결과에 계속 안 나타나서, 직접 `sentence-transformers`로 코사인 거리를 찍어봤다. 같은 내용인데 `"Java C# Go Node.js ..."`(공백 구분)는 쿼리와 거리가 0.88까지 치솟았고, `"Java, C#, Go, Node.js, ..."`(쉼표 구분)는 0.51로 떨어졌다. multilingual MiniLM 같은 평균 풀링 임베딩 모델이 공백으로만 나열된 고유명사 목록을 자연어로 못 읽는다는 걸 숫자로 직접 확인한 셈이다. 한글이 전혀 없는 공백 구분 문단을 감지해서 쉼표로 바꿔주는 것만으로 검색 1위 청크가 바뀌었다 — "왜 안 되지"를 추측만 하지 않고 직접 거리값을 찍어보는 게 훨씬 빨랐다.

  </details>

  <details>
  <summary><b>4. 리뷰 100개가 거의 다 같은 말이었다</b></summary>

  "마지막 프로젝트가 뭐냐"는 질문에 자꾸 리뷰 데이터에서 "오늘의 라면" 같은 엉뚱한 답이 끼어들어서 리뷰 JSON을 들여다봤더니, 100개 리뷰 중 다수가 "기술 스택 섹션이 백엔드 언어부터 인프라까지 폭넓게 정리되어 있어..." 같은 도입부를 템플릿처럼 반복하고 있었다. 전체 청크의 약 44%를 리뷰가 차지하면서, 자연스러운 문장 형태라 오히려 사실 정보 청크보다 임베딩 유사도가 더 높게 나오는 역설적인 상황이었다. 도입부 30자가 같으면 같은 의견으로 보고 제거하니 100개에서 20개로 줄었고, 사실 질문에 리뷰가 끼어드는 빈도가 눈에 띄게 줄었다. (AI가 데이터를 잘 만들어준다해도 100% 확신하고 믿지는 말자....)

  </details>

  <details>
  <summary><b>5. 스트리밍에 프롬프트가 통째로 새고 있었다</b></summary>

  FastAPI 스트리밍 엔드포인트를 테스트해보니 답변 앞에 시스템 프롬프트, 컨텍스트, 질문까지 전부 토큰으로 흘러나오고 있었다. `TextIteratorStreamer`가 기본적으로 입력 프롬프트까지 같이 스트리밍한다는 걸 몰랐던 게 원인이었다 — `skip_prompt=True`를 안 주면 모델이 "읽은 것"까지 다 보여준다. 일반 `generate()`에서는 `output_ids[0][input_length:]`로 입력을 잘라내는 처리를 이미 해뒀으면서, 스트리밍 쪽엔 똑같은 처리를 빼먹었던 것 — 같은 패턴을 두 군데 구현할 때는 한쪽만 고치고 다른 쪽을 잊어버리기 쉽다는 걸 새삼 느꼈다.

  </details>

  <details>
  <summary><b>6. RAGAS 설치만 세 번을 실패했다</b></summary>

  RAGAS를 로컬 무료 모델로 돌리려고 했는데, `ragas`가 내부적으로 `langchain_community.chat_models.vertexai`를 무조건 import하다가 최신 `langchain_community`엔 그 모듈이 없어서 죽었다. `langchain_community<0.3`으로 고정하니 이번엔 너무 오래된 버전이라 최신 `pydantic`과 메타클래스 충돌이 났다. 적당한 중간 버전(`0.3.7`)으로 다시 고정했더니 이번엔 `langchain_openai`가 요구하는 `ContextOverflowError`가 `langchain_core`에 없다며 또 죽었다. 알고 보니 진짜 원인은 `pip install`을 세 줄로 나눠서 따로 실행한 것이었다 — 각 줄이 그 시점 기준으로만 의존성을 풀다 보니 매번 어딘가 어긋났다. 한 번의 `pip install`로 전부 같이 요청하니 그제서야 pip 리졸버가 전체적으로 호환되는 조합을 골라줬다. "버전을 하나씩 맞춰나가는" 접근 자체가 틀렸다는 걸 세 번 실패하고서야 깨달았다.

  </details>

  <details>
  <summary><b>7. judge 모델을 또 CPU에 새로 로드하고 있었다</b></summary>

  RAGAS 평가가 자꾸 타임아웃 났는데, 처음엔 `max_workers`를 늘린 게 문제인 줄 알았다. 알고 보니 judge LLM을 만들 때 `transformers.pipeline(model=DEFAULT_MODEL_NAME)`처럼 모델 이름 문자열을 그대로 넘기고 있어서, 이미 GPU에 올려둔 generator의 모델과는 별개로 **같은 모델을 또 새로 CPU에 로드**하고 있었다. 메모리도 두 배로 먹고, CPU 추론이라 한 호출이 한참 걸리니 타임아웃이 날 수밖에 없었다. `generator.model`/`generator.tokenizer`를 그대로 재사용하도록 고치고서야 해결됐다 — 증상(타임아웃)만 보고 동시성 문제로 단정하기 전에, 모델이 실제로 어디에 올라가 있는지부터 확인했어야 했다.

  </details>

  <details>
  <summary><b>8. Graph RAG가 보여준 것 — 벡터 RAG는 계속 틀린 답을 정답처럼 말하고 있었다</b></summary>

  "스카이워크에서 가장 최근에 참여한 프로젝트는?"이라는 질문에 벡터 RAG는 거의 매번 "놀러와 마이홈"이라고 답했고, 너무 자주 같은 답이 나오니 한동안 RAGAS 평가의 ground truth에도 그대로 적어뒀다. Graph RAG를 데모 수준으로 붙여보려고 `index.html`의 `proj-title`/`pdate`를 파싱해서 회사-프로젝트 그래프를 만들고 실제 시작일을 비교해보니, 정답은 "코코마인"(2024.12 시작)이었다 — "놀러와, 마이홈"은 오히려 SKYWALK 소속 5개 프로젝트 중 가장 먼저 시작한 프로젝트였다. 벡터 RAG가 그럴듯한 문장으로 자신 있게 틀린 답을 반복하니, 사람이 보기에도 "맞나보다"하고 ground truth까지 잘못 적게 만들 수 있다는 게 가장 섬뜩했던 부분이다. 날짜·순서처럼 명확한 관계가 있는 질문은 애초에 벡터 유사도로 풀 문제가 아니라, 구조화된 데이터(그래프)로 풀어야 하는 문제였다.

  </details>


</details>