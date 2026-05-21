import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "sources"))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from user import user_router
from posts import posts_router
from db.databasemodel import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
	print("Fast API Server Starts...")
	await init_db()
	yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router.router)
app.include_router(posts_router.router)

@app.get("/", response_class=RedirectResponse, status_code=302)
def root():
	return "/login"

# CSS / JS / 기타 정적 파일 — 항상 마지막에 마운트
app.mount("/", StaticFiles(directory="views"), name="static")
