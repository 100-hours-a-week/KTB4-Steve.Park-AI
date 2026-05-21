from utils.models import ResponseEntity, Board, BoardComment, ReturnFlag as RF
from db import postsdb

async def getBoardCount() -> ResponseEntity:
	return await postsdb.getBoardTotalCount()

async def getBoardList(count: int) -> ResponseEntity:
	return await postsdb.getBoardList(count)

async def getBoardDetail(idx: int) -> ResponseEntity:
	result = await postsdb.getBoardDetail(idx)
	if result.flag != RF.Success.value:
		return result

	await postsdb.updateBoardView(idx)

	comments_result = await postsdb.getBoardComments(idx)
	comments = comments_result.res or []

	board = result.res
	board.viewcount += 1
	board.commentcount = len(comments)

	result.res = {"board": board, "comments": comments}
	return result

async def writeBoard(board: Board) -> ResponseEntity:
	msg = ResponseEntity()
	if board.title == "" or board.title is None:
		msg.flag = RF.BoardTitleEmpty.value
		msg.msg = RF.BoardTitleEmpty.message
		return msg
	
	elif board.contents == "" or board.contents is None:
		msg.flag = RF.BoardContentsEmpty.value
		msg.msg = RF.BoardContentsEmpty.message
		return msg
	
	return await postsdb.writeBoard(board)

async def updateBoard(idx:int, board: Board) -> ResponseEntity:
	msg = ResponseEntity()

	boarddetail = await postsdb.getBoardDetail(idx)
	if boarddetail.flag != RF.Success.value:
		msg.flag = boarddetail.flag
		msg.msg = boarddetail.msg
		return msg
	
	elif board.title == "" or board.title is None:
		msg.flag = RF.BoardTitleEmpty.value
		msg.msg = RF.BoardTitleEmpty.message
		return msg
	
	elif board.contents == "" or board.contents is None:
		msg.flag = RF.BoardContentsEmpty.value
		msg.msg = RF.BoardContentsEmpty.message
		return msg
	
	msg = await postsdb.updateBoard(idx, board)

	return msg

async def deleteBoard(idx: int) -> ResponseEntity:
	msg = ResponseEntity()
	boarddetail = await postsdb.getBoardDetail(idx)
	if boarddetail.flag != RF.Success.value:
		msg.flag = boarddetail.flag
		msg.msg = boarddetail.msg
		return msg
	
	msg = await postsdb.deleteBoard(idx)

	return msg

async def writeBoardComment(idx: int, comment: BoardComment) -> ResponseEntity:
	msg = ResponseEntity()
	
	boarddetail = await postsdb.getBoardDetail(idx)
	if boarddetail.flag != RF.Success.value:
		msg.flag = boarddetail.flag
		msg.msg = boarddetail.msg
		return msg
	
	elif comment.contents == "" or comment.contents is None:
		msg.flag = RF.BoardCommentContentsEmpty.value
		msg.msg = RF.BoardCommentContentsEmpty.message
		return msg
	
	comment.ridx = idx
	msg = await postsdb.writeBoardComment(comment)
	
	return msg

async def updateBoardComment(idx: int, ridx: int, comment: BoardComment) -> ResponseEntity:
	msg = ResponseEntity()
	
	boarddetail = await postsdb.getBoardDetail(idx)
	if boarddetail.flag != RF.Success.value:
		msg.flag = boarddetail.flag
		msg.msg = boarddetail.msg
		return msg
	
	if comment.contents == "" or comment.contents is None:
		msg.flag = RF.BoardCommentContentsEmpty.value
		msg.msg = RF.BoardCommentContentsEmpty.message
		return msg
	
	commentdetail = await postsdb.getBoardCommentDetail(ridx)
	if commentdetail.flag != RF.Success.value:
		msg.flag = commentdetail.flag
		msg.msg = commentdetail.msg
		return msg

	msg = await postsdb.updateBoardComment(ridx, comment)
	
	return msg

async def deleteBoardComment(idx: int, ridx: int) -> ResponseEntity:
	msg = ResponseEntity()
	
	boarddetail = await postsdb.getBoardDetail(idx)
	if boarddetail.flag != RF.Success.value:
		msg.flag = boarddetail.flag
		msg.msg = boarddetail.msg
		return msg
	
	boardcomment = await postsdb.getBoardCommentDetail(ridx)
	if boardcomment.flag != RF.Success.value:
		msg.flag = boardcomment.flag
		msg.msg = boardcomment.msg
		return msg
	
	msg = await postsdb.deleteBoardComment(ridx)
	
	return msg

async def updateBoardLikes(idx: int, username: str) -> ResponseEntity:
	msg = ResponseEntity()
	boarddetail = await postsdb.getBoardDetail(idx)
	if boarddetail.flag != RF.Success.value:
		msg.flag = boarddetail.flag
		msg.msg = boarddetail.msg
		return msg
	
	msg = await postsdb.updateBoardLikes(idx, username)
	
	return msg
