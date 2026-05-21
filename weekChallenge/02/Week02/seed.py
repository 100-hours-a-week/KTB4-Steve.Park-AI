import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "sources"))

from db.databasemodel import AsyncSessionLocal, BoardTable, BoardCommentTable, init_db
import json

POSTS = [
    ("FastAPI 처음 써봤는데 진짜 편하네요", "uvicorn으로 서버 띄우고 Swagger 자동 생성되는 거 보고 충격받았습니다. Django보다 훨씬 가볍고 빠른 느낌이에요. 비동기 지원도 기본이라 DB 쿼리 최적화하기도 편하고요. 앞으로 사이드 프로젝트는 다 FastAPI로 갈 것 같습니다."),
    ("SQLAlchemy async 세션 관리 팁 공유", "async with AsyncSessionLocal() as session 패턴을 쓸 때 session.begin()을 같이 쓰면 자동 커밋이 됩니다. 하지만 update/delete는 명시적으로 session.commit()을 해줘야 반영되더라고요. 이 차이 때문에 한참 헤맸습니다."),
    ("Ollama로 로컬 AI 돌려보신 분 계세요?", "gemma4:e2b 모델 ollama로 로컬에서 돌려봤는데 생각보다 빠르네요. M2 맥북에서 응답 3~5초 정도 나옵니다. OpenAI 호환 API로 연결할 수 있어서 기존 코드 거의 안 고쳐도 되는 게 장점이에요."),
    ("AES-CBC 암호화 구현 후기", "pycryptodome으로 AES-CBC 구현했습니다. IV를 랜덤으로 생성해서 암호문 앞에 붙이고 Base64 인코딩해서 DB에 저장하는 방식인데, 복호화할 때 앞 16바이트 잘라서 IV 추출하는 게 포인트입니다. 처음엔 IV 관리를 어떻게 해야 할지 몰라서 고생했어요."),
    ("Python Enum에서 커스텀 프로퍼티 쓰는 방법", "int, Enum을 같이 상속하면 Enum 멤버가 int처럼 동작합니다. 여기에 @property를 추가하면 .value로 코드값, .message로 커스텀 메시지를 따로 뽑을 수 있어요. 에러 코드 관리할 때 진짜 유용한 패턴인 것 같습니다."),
    ("FastAPI에서 정적 파일 서빙하기", "StaticFiles를 마지막에 마운트해야 API 라우트랑 충돌이 안 납니다. app.mount('/', StaticFiles(directory='views'), name='static')을 include_router 다음에 넣어야 해요. 순서가 중요하다는 걸 몰라서 한참 삽질했습니다."),
    ("게시판 페이지네이션 구현 방법", "offset 방식으로 페이지네이션을 구현했는데, 데이터가 많아지면 느려지는 단점이 있습니다. cursor 기반 페이지네이션이 성능상 더 좋다는데 아직 구현은 못 해봤어요. 혹시 SQLAlchemy에서 cursor 페이지네이션 구현해보신 분 계신가요?"),
    ("비동기 Python 처음 배울 때 헷갈렸던 것들", "async/await가 멀티스레딩이 아니라는 걸 처음엔 몰랐어요. 이벤트 루프 기반으로 I/O 대기 시간을 활용하는 거라서, CPU 집약적인 작업엔 별로 효과가 없습니다. DB 쿼리나 HTTP 요청처럼 I/O가 많은 곳에서 진가를 발휘하더라고요."),
    ("Pydantic v2로 마이그레이션 후기", "v1에서 v2로 넘어오면서 .dict() 대신 .model_dump()를 써야 하고, validator 데코레이터도 바뀌었습니다. 에러 메시지가 훨씬 명확해진 건 좋은데, 마이그레이션 가이드 꼼꼼히 읽어야 해요. 자동 마이그레이션 툴도 있으니 참고하세요."),
    ("SQLite에서 PostgreSQL로 마이그레이션할 때 주의사항", "개발은 SQLite로 하고 프로덕션은 PostgreSQL 쓰려고 했는데, 타입 차이가 꽤 있습니다. TEXT 기본값, autoincrement 문법, BOOLEAN 처리 방식이 달라요. SQLAlchemy ORM을 제대로 쓰면 엔진만 바꿔도 되는 경우가 많습니다."),
    ("JWT 인증 vs 세션 인증 비교", "FastAPI에서 JWT는 stateless라 서버 부하가 적고, 세션은 서버에서 상태를 관리해야 합니다. 이 프로젝트에선 간단히 username을 세션처럼 쓰고 있는데, 실제 서비스라면 JWT + refresh token 방식이 더 안전하겠죠."),
    ("Python 패키지 구조 잡는 방법", "__init__.py 파일이 있어야 패키지로 인식됩니다. 상대 import(from . import module)와 절대 import(from package import module)의 차이도 중요해요. sys.path에 경로를 추가하면 어디서든 임포트 가능한데, 이게 만능은 아닙니다."),
    ("웹 개발 스택 추천해주세요", "백엔드는 FastAPI, 프론트엔드는 React나 Vue를 많이 쓰더라고요. 혼자 하는 사이드 프로젝트라면 vanilla JS로 충분하고, 팀 프로젝트라면 TypeScript 적극 추천합니다. 데이터베이스는 PostgreSQL이 무난하고요."),
    ("CORS 에러 해결하는 방법", "FastAPI에서 CORSMiddleware 추가할 때 allow_origins=[\"*\"]는 개발용으로만 쓰세요. 프로덕션에서는 실제 도메인을 명시해야 보안에 안전합니다. credentials가 필요하면 allow_credentials=True도 추가해야 해요."),
    ("코드 리뷰 받고 느낀 점", "처음 코드 리뷰를 받았을 때 변수명이 너무 짧다는 피드백을 많이 받았습니다. idx, msg 같은 약어보다 index, message처럼 명확하게 쓰는 게 좋다고 하더라고요. 그래도 프레임워크에서 쓰는 관례는 따라가는 게 맞는 것 같습니다."),
    ("테스트 코드 작성 습관 들이기", "pytest로 FastAPI 테스트 작성하면 TestClient로 실제 API 호출을 시뮬레이션할 수 있습니다. DB는 테스트용 SQLite 인메모리 DB를 따로 쓰면 격리가 됩니다. 처음엔 귀찮은데 나중에 리팩토링할 때 정말 도움이 됩니다."),
    ("Git 브랜치 전략 어떻게 쓰세요?", "개인 프로젝트는 main 하나로 관리하고, 팀 프로젝트는 feature/fix/hotfix 브랜치를 나눠서 씁니다. PR 기반으로 main에 머지하는 방식이 가장 안전한 것 같아요. git rebase vs merge는 팀마다 의견이 달라서 합의가 중요합니다."),
    ("도커 처음 써보는 분들을 위한 정리", "Dockerfile 작성하고 docker build -t myapp . 하면 이미지 만들어집니다. docker run -p 8000:8000 myapp 으로 실행하면 로컬에서 테스트 가능해요. docker-compose는 여러 서비스 묶을 때 쓰는 건데, DB랑 앱 서버를 같이 올릴 때 진짜 편합니다."),
    ("API 문서화 자동화 경험 공유", "FastAPI는 Swagger UI가 자동으로 생성돼서 /docs로 접속하면 바로 테스트 가능합니다. response_model을 잘 정의하면 응답 스키마도 자동으로 보여줘요. docstring 작성하면 Swagger에도 반영되니까 주석 대신 docstring을 쓰는 게 좋습니다."),
    ("Python 가상환경 관리 방법", "venv, conda, poetry, uv 등 여러 가지가 있는데 저는 최근에 uv로 갈아탔습니다. 설치 속도가 pip보다 10배 이상 빠르고, lock 파일도 자동으로 관리해줘요. requirements.txt도 export 가능해서 기존 프로젝트랑도 호환됩니다."),
    ("비밀번호 저장 어떻게 하세요?", "평문으로 저장하면 절대 안 됩니다. bcrypt나 argon2 같은 단방향 해시 함수를 써야 해요. 이 프로젝트에선 AES 대칭키 암호화를 쓰고 있는데, 엄밀히 말하면 단방향 해시가 더 안전합니다. 실제 서비스라면 passlib 라이브러리 추천해요."),
    ("FastAPI 의존성 주입 패턴", "Depends()를 쓰면 라우터마다 공통 로직을 주입할 수 있습니다. 인증 체크, DB 세션 관리, 페이지네이션 파라미터 공통화 등에 유용해요. async def get_db() -> AsyncSession: yield session 패턴이 가장 많이 쓰입니다."),
    ("한국어 검색 기능 구현하기", "SQLite는 한국어 full-text search가 약합니다. PostgreSQL의 tsvector/tsquery나 Elasticsearch를 쓰면 더 정확한 한국어 검색이 가능해요. 간단한 프로젝트라면 LIKE '%검색어%' 쿼리로도 충분하긴 합니다."),
    ("클린 아키텍처 적용 후기", "라우터/비즈니스 로직/DB 레이어를 분리하니까 테스트 작성이 훨씬 쉬워졌습니다. DB 레이어만 모킹하면 비즈니스 로직 테스트가 가능하고, 나중에 DB를 바꿔도 영향 범위가 최소화됩니다. 처음엔 파일이 많아서 복잡해 보이는데 익숙해지면 관리가 편해요."),
    ("오늘 배운 것: Python dataclass vs Pydantic", "dataclass는 표준 라이브러리라 의존성이 없고, Pydantic은 유효성 검사와 직렬화가 강력합니다. API 요청/응답 모델엔 Pydantic, 내부 데이터 구조엔 dataclass를 쓰는 게 일반적인 패턴인 것 같아요. 둘 다 알아두면 상황에 맞게 선택할 수 있습니다."),
    ("2주차 위클리 챌린지 완료 후기", "FastAPI로 게시판 API 만들면서 SQLAlchemy 비동기 ORM, AES 암호화, Ollama AI 연동까지 한 번에 배웠습니다. 처음엔 막막했는데 레이어 분리 구조 잡고 나니까 기능 추가가 훨씬 쉬워졌어요. 3주차도 파이팅입니다!"),
]

COMMENTS = [
    (1, "steve",   "저도 FastAPI 처음 썼을 때 Swagger 자동 생성에 감동받았어요!"),
    (1, "john",    "Django REST Framework보다 확실히 가볍네요. 덕분에 저도 전환 고민 중입니다."),
    (1, "alice",   "비동기 처리 때문에 uvicorn 대신 hypercorn 쓰는 분도 있더라고요."),
    (2, "bob",     "session.begin() vs session.commit() 차이 저도 많이 헷갈렸어요. 좋은 팁 감사합니다!"),
    (2, "steve",   "add()는 begin()으로 auto commit, execute()는 명시적 commit 필요하다는 거죠?"),
    (3, "charlie", "M1에서도 ollama 잘 돌아가요. llama3.2 모델 추천합니다."),
    (3, "alice",   "gemma 말고 mistral도 써보셨나요? 한국어가 좀 더 자연스럽다는 얘기를 들었어요."),
    (4, "david",   "IV 랜덤 생성 부분에서 저도 막혔었는데 이렇게 해결하는군요!"),
    (5, "steve",   "이 패턴 ReturnFlag에 적용하면 에러 메시지 관리가 진짜 깔끔해지겠네요."),
    (6, "eve",     "StaticFiles 순서 문제 저도 삽질했습니다. 항상 마지막에 마운트!"),
    (6, "john",    "html=True 옵션 주면 index.html 자동 서빙도 되더라고요."),
    (7, "frank",   "cursor 페이지네이션은 마지막 id를 where 조건으로 쓰는 방식으로 구현하면 됩니다."),
    (7, "steve",   "keyset pagination이라고도 하죠. 성능 차이가 꽤 크더라고요."),
    (8, "alice",   "asyncio.gather()로 여러 비동기 작업 병렬 실행하는 것도 배워두면 좋아요!"),
    (9, "bob",     "v2 마이그레이션 진짜 힘들었어요. orm_mode=True가 from_attributes=True로 바뀐 거 찾느라..."),
    (10, "charlie","Alembic으로 마이그레이션 관리하면 DB 변경이 훨씬 수월합니다."),
    (11, "david",  "이 프로젝트에 JWT 붙이면 더 완성도가 높아질 것 같아요!"),
    (12, "steve",  "__init__.py 없어도 되는 namespace package도 있다는 거 알고 계셨나요?"),
    (13, "eve",    "저는 백엔드 FastAPI + 프론트 Next.js 조합 써보고 있는데 꽤 잘 맞아요."),
    (14, "frank",  "allow_origins 실수로 * 쓴 채로 배포하면... 알아서 조심하세요."),
    (15, "alice",  "코드 리뷰 문화가 팀 실력을 올리는 것 같아요. 저도 적극 받으려고 합니다."),
    (16, "john",   "pytest-asyncio 쓰면 비동기 테스트도 쉽게 작성할 수 있어요!"),
    (17, "bob",    "저는 GitHub Flow 씁니다. 심플해서 개인 프로젝트에 딱 맞아요."),
    (18, "charlie","docker-compose로 FastAPI + PostgreSQL + Redis 한 번에 올리면 개발 환경 세팅이 편합니다."),
    (19, "david",  "response_model_exclude_unset=True 옵션도 같이 쓰면 응답이 더 깔끔해져요."),
    (20, "steve",  "uv 진짜 빠르죠! pip install이 답답하게 느껴질 정도예요."),
    (21, "eve",    "argon2가 bcrypt보다 최신 표준이라 가능하면 argon2 쓰는 걸 추천해요."),
    (22, "frank",  "Depends로 현재 로그인 유저 정보 주입하는 패턴이 정말 깔끔합니다."),
    (24, "alice",  "클린 아키텍처 처음엔 오버엔지니어링 같았는데 팀으로 일하니까 진가를 알겠더라고요."),
    (25, "john",   "3주차도 화이팅입니다! 같이 열심히 해봐요 :)"),
    (25, "steve",  "2주차 고생 많으셨어요! 결과물이 정말 완성도 높네요."),
]

async def seed():
    await init_db()

    async with AsyncSessionLocal() as session:
        async with session.begin():
            for i, (title, contents) in enumerate(POSTS, start=1):
                session.add(BoardTable(
                    username="steve",
                    title=title,
                    contents=contents,
                    viewcount=i * 3,
                    likes=json.dumps(["alice", "bob"] if i % 3 == 0 else (["john"] if i % 2 == 0 else [])),
                    createdt=datetime.now(),
                    recentdt=datetime.now(),
                ))

    async with AsyncSessionLocal() as session:
        async with session.begin():
            for (ridx, username, contents) in COMMENTS:
                session.add(BoardCommentTable(
                    ridx=ridx,
                    username=username,
                    contents=contents,
                    createdt=datetime.now(),
                    recentdt=datetime.now(),
                ))

    print(f"Seeded {len(POSTS)} posts and {len(COMMENTS)} comments.")

if __name__ == "__main__":
    asyncio.run(seed())
