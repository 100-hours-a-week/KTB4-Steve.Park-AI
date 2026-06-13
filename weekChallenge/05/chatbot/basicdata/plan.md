# 한국어 Mini-GPT 프로젝트 계획

## 목표
- 1차: `mini_gpt.py`처럼 글을 자연스럽게 "이어쓰는" 한국어 모델
- 2차: 입력(질문/프롬프트)에 대해 완전한 문장으로 "응답"하는 모델로 확장
- 토크나이저는 직접 구현하는 BPE/subword 사용
- 최종적으로 FastAPI로 서빙

## Phase 0 — 환경 & 프로젝트 구조
- 가상환경 세팅 후 PyTorch CUDA 버전 설치 (NVIDIA GPU + CUDA 13.1 확인됨)
- 모듈 분리: `tokenizer.py` / `model.py` / `train.py` / `chat.py` / `app.py(FastAPI)`
- 1차 목표: 작은 토이 데이터로 데이터 → 배치 → forward/backward → 체크포인트 저장까지 파이프라인이 끝까지 도는지 확인 (BPE/모델 본 작업 전 smoke test)

## Phase 1 — 코퍼스 준비 (Stage 1: 이어쓰기용)
- 위키문헌(공개 한국어 고전문학), 한국어 위키피디아 덤프 일부, 뉴스 코퍼스 등에서 수 MB~수십 MB 텍스트 확보
- 전처리: 마크업 제거, 공백 정규화, 유니코드 정규화(NFC/NFD) 결정 — BPE 결과에 영향을 주는 부분이라 미리 정해두기

## Phase 2 — BPE 토크나이저 직접 구현
- **base alphabet 선택**: 완성형 한글 음절 그대로(수천 개) vs **자모 단위로 분해**(초성/중성/종성, 약 70~80개) 후 BPE 적용
  - 자모 분해 후 BPE를 돌리면 merge가 의미 있는 단위(접사, 어미 등)로 잘 형성되는 경향 — 직접 비교 실험 추천
- **알고리즘**: base vocab → 인접 쌍 빈도 계산 → 최빈 쌍 merge 반복 → 목표 vocab_size 도달
- **encode/decode** 함수 + roundtrip 검증, 압축률(글자 수 대비 토큰 수) 체크
- vocab_size는 처음엔 작게(예: 1000~2000) 시작해서 나중에 조정
- 체크포인트: 모델과 별개로 BPE 단독 테스트(encode→decode roundtrip) 먼저 통과시키기

## Phase 3 — mini_gpt.py 아키텍처 이식
- `CausalSelfAttention` / `Block` / `MiniGPT` 구조는 거의 그대로 재사용 가능 (vocab_size만 BPE 결과로 교체)
- vocab_size가 커지면 임베딩/출력층 파라미터가 커지므로 `n_embd`, `n_layer`, `block_size`를 한국어 시퀀스 길이에 맞게 재조정
- train/val split, 학습 루프, 주기적 loss 로깅, 체크포인트 저장 — `train()` 패턴 그대로

## Phase 4 — Stage 1 검증 (이어쓰기)
- 학습 후 train/val loss 확인
- `chat()` 스타일 REPL 구현: 한국어 프롬프트 입력 → 이어쓰기 생성 → BPE decode
- 생성된 한국어가 음절/문법적으로 그럴듯한지 확인

## Phase 5 — Stage 2: "완전한 문장 응답"으로 확장
- **데이터**: 한국어 챗봇 Q&A 데이터셋(예: 일상 대화 Q&A 쌍) 또는 직접 소규모 Q&A 데이터 구성
- **포맷팅**: `"질문: ...\n답변: ..."` 같은 명확한 템플릿/구분 토큰 정의 (vocab에 특수 토큰 추가 여부 결정)
- **학습 전략**:
  - A안: Q&A 포맷 데이터로 처음부터 학습
  - B안: Stage 1 가중치에서 이어서 학습 (한국어 문법/유창성 유지 + 응답 패턴 추가 학습)
- **생성 로직 변경**: `generate()`가 고정 길이가 아니라 종료 조건(개행/종료 토큰)까지 생성하도록 수정
- 기대치 관리: 이 규모(수백만 파라미터대)에서는 "똑똑한 답변"보다 "Q→A 턴 구조를 흉내내는" 수준이 현실적 목표

## Phase 6 — FastAPI 서빙
- 서버 시작 시 토크나이저 + 모델 가중치 1회 로드
- 엔드포인트 예: `POST /generate`(이어쓰기 모드), `POST /chat`(Q&A 모드) — Pydantic 스키마, 빈 입력/OOV 처리
- 필요시 간단한 테스트용 HTML 페이지

## 스트레치 골 (여유 있을 때)
- temperature / top-k / top-p 샘플링
- KV cache로 생성 속도 개선
- 파이프라인 검증 후 모델/데이터 규모 확장
- FastAPI `StreamingResponse`로 토큰 단위 스트리밍 출력
