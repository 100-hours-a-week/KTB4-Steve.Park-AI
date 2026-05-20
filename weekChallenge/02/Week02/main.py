from fastapi import FastAPI
from contextlib import asynccontextmanager
from user import user_router
from board import board_router
from db.databasemodel import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
	print("Fast API Server Starts...")
	await init_db()
	yield

app = FastAPI(lifespan=lifespan)

app.include_router(user_router.router)
app.include_router(board_router.router)

@app.get("/")
def read_root():
	return {"Hello": "FastAPI Weekly Challenge"}

