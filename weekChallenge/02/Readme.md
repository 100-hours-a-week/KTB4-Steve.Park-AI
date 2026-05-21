# Week 02 - Community Board API

> KTB 위클리 챌린지 2주차 — FastAPI 기반 커뮤니티 게시판 서버

---

## 목표

REST API 기반 커뮤니티 게시판 백엔드 구현

- 회원가입 / 로그인 (AES-CBC 암호화)
- 게시글 CRUD / 댓글 CRUD / 좋아요 토글 / 조회수 집계
- SQLite + SQLAlchemy 비동기 ORM 기반 데이터 영속성
- Ollama(gemma4:e2b) 연동 AI 게시글 및 댓글 요약
- 페이지 라우팅 기반 HTML/CSS/JS 프론트엔드

---

## 프로젝트 구조

```
Week02/
├── main.py                        # FastAPI 앱 진입점, 라우터 등록
├── seed.py                        # 테스트용 게시글/댓글 랜덤 데이터 생성 스크립트
├── views/                         # 프론트엔드 정적 파일
│   ├── index.html                 # 루트 진입점 (로그인 페이지로 리다이렉트)
│   ├── app.js                     # 공통 API 유틸 및 인증 헬퍼
│   ├── css/
│   │   └── style.css              # 전체 공용 스타일 (다크 테마)
│   ├── user/
│   │   ├── login.html             # 로그인 페이지
│   │   └── join.html              # 회원가입 페이지
│   └── posts/
│       ├── posts.html             # 게시글 목록 (페이지네이션)
│       ├── post-write.html        # 게시글 작성 / 수정
│       └── post-detail.html       # 게시글 상세 / 댓글 / 좋아요 / AI 요약
└── sources/                       # 백엔드 소스
    ├── user/
    │   ├── user_router.py         # 유저 페이지 및 API 라우터
    │   └── userUtils.py           # 유저 비즈니스 로직
    ├── posts/
    │   ├── posts_router.py        # 게시판 페이지 및 API 라우터
    │   └── postsUtils.py          # 게시판 비즈니스 로직
    ├── ai/
    │   └── aiUtils.py             # Ollama 연동 AI 요약 기능
    ├── db/
    │   ├── databasemodel.py       # SQLAlchemy 테이블 모델 정의
    │   ├── postsdb.py             # 게시판 DB 쿼리
    │   └── userdb.py              # 유저 DB 쿼리
    ├── datas/
    │   └── community.db           # SQLite 데이터베이스 파일
    └── utils/
        ├── models.py              # Pydantic 모델, ReturnFlag Enum
        └── utils.py               # AES-CBC 암호화/복호화 유틸
```

---

## 설치 및 실행

**의존성 설치**

```bash
pip install fastapi uvicorn sqlalchemy aiosqlite pycryptodome openai
```

**서버 실행**

```bash
fastapi dev main.py
```

또는

```bash
uvicorn main:app --reload
```

**브라우저 접속**

```
http://localhost:8000
```

**Ollama 실행 (AI 기능 사용 시)**

```bash
ollama serve
ollama pull gemma4:e2b
```

**테스트 데이터 생성**

```bash
python seed.py
```

> `seed.py`는 테스트용 게시글과 댓글을 DB에 삽입하는 스크립트입니다.
> 서버를 실행하지 않아도 동작하며, 중복 실행 시 데이터가 추가되므로 주의하세요.

---

## 페이지 라우트

| URL | 설명 |
|---|---|
| `/` | 로그인 페이지로 자동 리다이렉트 |
| `/login` | 로그인 |
| `/join` | 회원가입 |
| `/board` | 게시글 목록 |
| `/write` | 게시글 작성 / 수정 |
| `/detail?idx={idx}` | 게시글 상세 |

---

## API 엔드포인트

### 유저

| 메서드 | 경로 | 설명 |
|---|---|---|
| POST | `/user` | 회원가입 |
| POST | `/session` | 로그인 |

### 게시판

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/posts/count` | 게시글 전체 수 조회 |
| GET | `/posts?count={n}` | 게시글 목록 조회 (10개씩 페이지네이션) |
| GET | `/posts/{idx}` | 게시글 상세 조회 (조회수 증가) |
| POST | `/posts` | 게시글 작성 |
| PUT | `/posts/{idx}` | 게시글 수정 |
| DELETE | `/posts/{idx}` | 게시글 삭제 (댓글 일괄 삭제) |

### 댓글

| 메서드 | 경로 | 설명 |
|---|---|---|
| POST | `/posts/{idx}/comments` | 댓글 작성 |
| PUT | `/posts/{idx}/comments/{ridx}` | 댓글 수정 |
| DELETE | `/posts/{idx}/comments/{ridx}` | 댓글 삭제 |

### 좋아요 / AI 요약

| 메서드 | 경로 | 설명 |
|---|---|---|
| PATCH | `/posts/{idx}?username={username}` | 좋아요 토글 (추가/취소) |
| GET | `/posts/{idx}/summary` | AI 게시글 요약 |
| GET | `/posts/{idx}/comments/summary` | AI 댓글 전체 요약 |

---

## 응답 형식

모든 API는 동일한 `ResponseEntity` 구조로 응답합니다.

```json
{
  "error_code": 0,
  "msg": "Success",
  "res": null
}
```

| 필드 | 설명 |
|---|---|
| `error_code` | 0 = 성공, 그 외 = 오류 코드 |
| `msg` | 결과 메시지 |
| `res` | 응답 데이터 |

---

## 주요 기능

### 비밀번호 보안

- `pycryptodome`의 AES-CBC 방식으로 암호화
- IV + 암호문을 Base64 인코딩하여 DB에 저장
- 평문 비밀번호는 어디에도 저장되지 않음

### 게시글 조회수

- `GET /posts/{idx}` 호출 시 조회수 증가 후 증가된 값 반환
- 수정 / 삭제 / 댓글 작성 등 내부 검증 호출에는 조회수 미반영

### 좋아요

- 유저명 기준 중복 방지 (같은 유저가 다시 요청하면 취소)
- 좋아요 목록은 JSON 배열로 DB에 저장

### 페이지네이션

- 게시글 목록은 최신순(createdt DESC)으로 정렬
- 10개씩 페이지 단위로 표시
- `«  ‹  1 2 3 4 5  ›  »` 형태의 페이지 창 이동 지원

### AI 요약 (Ollama)

- `gemma4:e2b` 모델 사용
- 게시글 제목 + 본문을 3문장 이내로 요약
- 댓글 전체를 종합하여 3문장 이내로 요약

### 작성자 권한 제어

- 게시글/댓글 수정·삭제 버튼은 작성자에게만 표시
- 수정 페이지 직접 접근 시 작성자가 다르면 접근 차단

---

## 회고

<details>
<summary><b>기획 단계</b></summary>
FastAPI로 REST API 서버를 구현하는 과제였다. 처음에는 파일 I/O 기반으로 시작했지만
DB를 사용하는 방향으로 전환하면서 SQLAlchemy의 비동기 ORM을 처음 접하게 됐다.
라우터 / 비즈니스 로직 / DB 쿼리 를 레이어로 분리하는 구조를 잡는 것이 이번 과제의 핵심이었다.
</details>

<details>
<summary><b>개발 단계</b></summary>
SQLAlchemy async session 관리, session.begin() vs session.commit() 차이,
ORM 방식과 직접 쿼리(update/delete) 방식의 차이를 직접 겪으며 이해하게 됐다.
Ollama를 OpenAI 호환 API로 연결하는 부분에서 base_url, 모델명, 엔드포인트 차이로
여러 번 오류를 겪었고, 비동기 클라이언트(AsyncOpenAI)와 동기 클라이언트(OpenAI)의
차이도 이번에 체감했다.
</details>
