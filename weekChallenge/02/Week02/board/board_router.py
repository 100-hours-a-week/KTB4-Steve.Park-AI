from fastapi import APIRouter
from utils.models import ResponseEntity, Board, BoardComment
from . import boardUtils
from ai import aiUtils

router = APIRouter()

@router.get("/posts")
async def getBoardList(count: int) -> ResponseEntity:
	return await boardUtils.getBoardList(count)

@router.get("/posts/{idx}")
async def getBoardDetail(idx: int) -> ResponseEntity:
	return await boardUtils.getBoardDetail(idx)

@router.post("/posts")
async def writeBoard(board: Board) -> ResponseEntity:
	return await boardUtils.writeBoard(board)

@router.put("/posts/{idx}")
async def updateBoard(idx:int, board: Board) -> ResponseEntity:
	return await boardUtils.updateBoard(idx, board)

@router.delete("/posts/{idx}")
async def deleteBoard(idx: int) -> ResponseEntity:
	return await boardUtils.deleteBoard(idx)

@router.post("/posts/{idx}/comments")
async def writeBoardComment(idx: int, comment: BoardComment) -> ResponseEntity:
	return await boardUtils.writeBoardComment(idx, comment)

@router.put("/posts/{idx}/comments/{ridx}")
async def updateBoardComment(idx: int, ridx: int, comment: BoardComment) -> ResponseEntity:
	return await boardUtils.updateBoardComment(idx, ridx, comment)

@router.delete("/posts/{idx}/comments/{ridx}")
async def deleteBoardComment(idx: int, ridx: int) -> ResponseEntity:
	return await boardUtils.deleteBoardComment(idx, ridx)

@router.patch("/posts/{idx}")
async def updateBoardLikes(idx: int, username: str) -> ResponseEntity:
	return await boardUtils.updateBoardLikes(idx, username)

@router.get("/posts/{idx}/summary")
async def getGemmaPostSummary(idx: int) -> ResponseEntity:
	return await aiUtils.getGemmaPostSummary(idx)

@router.get("/posts/{idx}/comments/summary")
async def getGemmaPostCommentSummary(idx: int) -> ResponseEntity:
	return await aiUtils.getGemmaPostCommentSummary(idx)