from fastapi import APIRouter
from fastapi.responses import FileResponse
from utils.models import ResponseEntity, Board, BoardComment
from . import posts_utils
from ai import ai_utils

router = APIRouter()

@router.get("/board",  response_class=FileResponse)
def board_page():
	return "views/posts/posts.html"

@router.get("/write",  response_class=FileResponse)
def write_page():
	return "views/posts/post_write.html"

@router.get("/detail", response_class=FileResponse)
def detail_page():
	return "views/posts/post_detail.html"

@router.get("/posts/count")
async def getBoardCount() -> ResponseEntity:
	return await posts_utils.getBoardCount()

@router.get("/posts")
async def getBoardList(count: int) -> ResponseEntity:
	return await posts_utils.getBoardList(count)

@router.get("/posts/{idx}")
async def getBoardDetail(idx: int) -> ResponseEntity:
	return await posts_utils.getBoardDetail(idx)

@router.post("/posts")
async def writeBoard(board: Board) -> ResponseEntity:
	return await posts_utils.writeBoard(board)

@router.put("/posts/{idx}")
async def updateBoard(idx:int, board: Board) -> ResponseEntity:
	return await posts_utils.updateBoard(idx, board)

@router.delete("/posts/{idx}")
async def deleteBoard(idx: int) -> ResponseEntity:
	return await posts_utils.deleteBoard(idx)

@router.post("/posts/{idx}/comments")
async def writeBoardComment(idx: int, comment: BoardComment) -> ResponseEntity:
	return await posts_utils.writeBoardComment(idx, comment)

@router.put("/posts/{idx}/comments/{ridx}")
async def updateBoardComment(idx: int, ridx: int, comment: BoardComment) -> ResponseEntity:
	return await posts_utils.updateBoardComment(idx, ridx, comment)

@router.delete("/posts/{idx}/comments/{ridx}")
async def deleteBoardComment(idx: int, ridx: int) -> ResponseEntity:
	return await posts_utils.deleteBoardComment(idx, ridx)

@router.patch("/posts/{idx}")
async def updateBoardLikes(idx: int, username: str) -> ResponseEntity:
	return await posts_utils.updateBoardLikes(idx, username)

@router.get("/posts/{idx}/summary")
async def getGemmaPostSummary(idx: int) -> ResponseEntity:
	return await ai_utils.getGemmaPostSummary(idx)

@router.get("/posts/{idx}/comments/summary")
async def getGemmaPostCommentSummary(idx: int) -> ResponseEntity:
	return await ai_utils.getGemmaPostCommentSummary(idx)