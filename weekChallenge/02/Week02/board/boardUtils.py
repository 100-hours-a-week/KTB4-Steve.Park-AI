from utils.models import ResponseEntity, Board, BoardComment, ReturnFlag as RF
from db import boarddb

async def getBoardList(count: int) -> ResponseEntity:
	return await boarddb.getBoardList(count)

async def getBoardDetail(idx: int) -> ResponseEntity:
	result = await boarddb.getBoardDetail(idx)
	if result.flag != RF.Success.value:
		return result

	await boarddb.updateBoardView(idx)

	comments_result = await boarddb.getBoardComments(idx)
	comments = comments_result.res or []

	board = result.res
	board.commentcount = len(comments)

	result.res = {"board": board, "comments": comments}
	return result

async def writeBoard(board: Board) -> ResponseEntity:
	msg = ResponseEntity()
	if board.title == "" or board.title is None:
		msg.flag = RF.BoardTitleEmpty.value
		msg.msg = RF.BoardTitleEmpty.name
		return msg
	
	elif board.contents == "" or board.contents is None:
		msg.flag = RF.BoardContentsEmpty.value
		msg.msg = RF.BoardContentsEmpty.name
		return msg
	
	return await boarddb.writeBoard(board)

async def updateBoard(idx:int, board: Board) -> ResponseEntity:
	msg = ResponseEntity()

	boarddetail = await boarddb.getBoardDetail(idx)
	if boarddetail.flag != RF.Success.value:
		msg.flag = boarddetail.flag
		msg.msg = boarddetail.msg
		return msg
	
	elif board.title == "" or board.title is None:
		msg.flag = RF.BoardTitleEmpty.value
		msg.msg = RF.BoardTitleEmpty.name
		return msg
	
	elif board.contents == "" or board.contents is None:
		msg.flag = RF.BoardContentsEmpty.value
		msg.msg = RF.BoardContentsEmpty.name
		return msg
	
	msg = await boarddb.updateBoard(idx, board)

	return msg

async def deleteBoard(idx: int) -> ResponseEntity:
	msg = ResponseEntity()
	boarddetail = await boarddb.getBoardDetail(idx)
	if boarddetail.flag != RF.Success.value:
		msg.flag = boarddetail.flag
		msg.msg = boarddetail.msg
		return msg
	
	msg = await boarddb.deleteBoard(idx)

	return msg

async def writeBoardComment(idx: int, comment: BoardComment) -> ResponseEntity:
	msg = ResponseEntity()
	
	boarddetail = await boarddb.getBoardDetail(idx)
	if boarddetail.flag != RF.Success.value:
		msg.flag = boarddetail.flag
		msg.msg = boarddetail.msg
		return msg
	
	elif comment.contents == "" or comment.contents is None:
		msg.flag = RF.BoardCommentContentsEmpty.value
		msg.msg = RF.BoardCommentContentsEmpty.name
		return msg
	
	comment.ridx = idx
	msg = await boarddb.writeBoardComment(comment)
	
	return msg

async def updateBoardComment(idx: int, ridx: int, comment: BoardComment) -> ResponseEntity:
	msg = ResponseEntity()
	
	boarddetail = await boarddb.getBoardDetail(idx)
	if boarddetail.flag != RF.Success.value:
		msg.flag = boarddetail.flag
		msg.msg = boarddetail.msg
		return msg
	
	if comment.contents == "" or comment.contents is None:
		msg.flag = RF.BoardCommentContentsEmpty.value
		msg.msg = RF.BoardCommentContentsEmpty.name
		return msg
	
	commentdetail = await boarddb.getBoardCommentDetail(ridx)
	if commentdetail.flag != RF.Success.value:
		msg.flag = commentdetail.flag
		msg.msg = commentdetail.msg
		return msg

	msg = await boarddb.updateBoardComment(ridx, comment)
	
	return msg

async def deleteBoardComment(idx: int, ridx: int) -> ResponseEntity:
	msg = ResponseEntity()
	
	boarddetail = await boarddb.getBoardDetail(idx)
	if boarddetail.flag != RF.Success.value:
		msg.flag = boarddetail.flag
		msg.msg = boarddetail.msg
		return msg
	
	boardcomment = await boarddb.getBoardCommentDetail(ridx)
	if boardcomment.flag != RF.Success.value:
		msg.flag = boardcomment.flag
		msg.msg = boardcomment.msg
		return msg
	
	msg = await boarddb.deleteBoardComment(ridx)
	
	return msg

async def updateBoardLikes(idx: int, username: str) -> ResponseEntity:
	msg = ResponseEntity()
	boarddetail = await boarddb.getBoardDetail(idx)
	if boarddetail.flag != RF.Success.value:
		msg.flag = boarddetail.flag
		msg.msg = boarddetail.msg
		return msg
	
	msg = await boarddb.updateBoardLikes(idx, username)
	
	return msg
