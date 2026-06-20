# KTB Weekly Challenge

> 카카오 테크 부트캠프 4기 — 주차별 챌린지 과제 모음

---

## 목록

| 주차 | 주제 | 링크 |
|------|------|------|
| Week 06 | RAG 아키텍처 (벡터+Graph RAG) & FastAPI & RAGAS 평가 | [바로가기](06/README.md) |
| Week 05 | CNN 전이학습(ResNet/VGG) & 한국어 Mini-GPT 챗봇 | [바로가기](05/Readme.md) |
| Week 04 | ML 알고리즘 & 딥러닝 모델 탐구 | [바로가기](04/Readme.md) |
| Week 03 | NumPy / Pandas / 데이터 시각화 미니퀘스트 | [바로가기](03/Readme.md) |
| Week 02 | FastAPI 커뮤니티 게시판 + AI 요약 | [바로가기](02/Readme.md) |
| Week 01 | CLI 기반 RPG 로그인 시스템 | [바로가기](01/Week01/Readme.md) |

---

## 주차별 요약

### Week 06 — RAG 아키텍처 미니 프로젝트

공개 가중치 모델(Qwen2.5)을 LLM으로 문서 로딩부터 응답 생성까지 RAG 파이프라인을 구축하고,
FastAPI로 래핑하고, RAGAS로 평가하고, Graph RAG까지 적용

- md/html/json 형식별 청킹 (헤더·레이블 컨텍스트 보존, 임베딩 거리 실측 기반 튜닝)
- FastAPI `POST /query`, `/query/stream` (스트리밍, `use_graph` 토글)
- RAGAS 평가 (로컬 모델을 judge로 재사용, OpenAI API 키 불필요)
- `index.html`에서 회사-프로젝트 관계 그래프 추출 → 날짜 비교가 필요한 질문은 그래프로,
  나머지는 벡터 RAG로 답하는 하이브리드 라우팅

---

### Week 05 — CNN 전이학습 & 한국어 Mini-GPT 챗봇

ResNet50/VGG16 전이학습 비교 실험과, BPE 토크나이저부터 직접 구현한 한국어 SOP_GPT 챗봇

- `weights='imagenet'` + `trainable=False` 조합이 가장 효과적 (RandomSearch: Test Accuracy 0.33 → 0.90)
- BPE 토크나이저 직접 구현(NFD 자모 분해 + UNK 버킷팅) + nanoGPT 스타일 SOP_GPT 아키텍처
- Stage 1(이어쓰기) → Stage 2(Q&A fine-tuning) 2단계 학습, FastAPI로 채팅형 UI 서빙

---

### Week 04 — ML 알고리즘 & 딥러닝

PUBG 스탯 데이터로 머신러닝 알고리즘을 비교하고, CNN 이미지 분류까지 실습

- K-NN / Perceptron / SVM / Random Forest / Naive Bayes
- SMOTE 데이터 증강 (0.8889 → 0.9625)
- 활성화 함수 비교 / MLP / CNN (고양이 vs 강아지)

---

### Week 03 — 데이터 분석 미니퀘스트

NumPy, Pandas, Matplotlib, Seaborn, SciPy 핵심 개념 실습

- NumPy 6개 퀘스트 (차원, Shape, dtype, 인덱싱, 연산, ufunc)
- Pandas 9개 퀘스트 (Series, DataFrame, 필터링, 그룹화, 병합 등)
- 시각화 / 시계열 / 통계 검정 / 양자회로(Qiskit)

---

### Week 02 — Community Board API

FastAPI 기반 커뮤니티 게시판 백엔드 구현

- 회원가입 / 로그인 / 게시글·댓글 CRUD / 좋아요 / 조회수
- SQLite + SQLAlchemy 비동기 ORM
- Ollama(gemma4:e2b) 연동 AI 게시글·댓글 요약

---

### Week 01 — Sloppy RPG

CLI에서 동작하는 RPG 게임 인증 시스템 구현

- 계정 생성 / 로그인 / 삭제
- AES-CBC 암호화 기반 비밀번호 보안
- JSON 파일 기반 유저 데이터 영속성
