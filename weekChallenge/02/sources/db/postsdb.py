import json
from sqlalchemy import select, func, delete, update
from db.databasemodel import AsyncSessionLocal, BoardTable, BoardCommentTable
from utils.models import ReturnFlag as RF, ResponseEntity, Board, BoardComment, BOARD_PAGE_SIZE
from datetime import datetime

async def getBoardTotalCount() -> ResponseEntity:
    msg = ResponseEntity()
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(func.count()).select_from(BoardTable))
        msg.res = result.scalar()

    return msg

async def getBoardList(count: int) -> ResponseEntity:
    msg = ResponseEntity()
    async with AsyncSessionLocal() as session:
        board_result = await session.execute(
            select(BoardTable).order_by(BoardTable.createdt.desc()).offset(count).limit(BOARD_PAGE_SIZE)
        )
        boards = board_result.scalars().all()

        comment_result = await session.execute(
            select(BoardCommentTable.ridx, func.count().label("cnt"))
            .group_by(BoardCommentTable.ridx)
        )
        comment_counts = {row.ridx: row.cnt for row in comment_result}

        msg.res = [Board(
            idx=b.idx,
            username=b.username,
            title=b.title,
            contents=b.contents,
            viewcount=b.viewcount,
            commentcount=comment_counts.get(b.idx, 0),
            likes=json.loads(b.likes),
            createdt=b.createdt,
            recentdt=b.recentdt
        ) for b in boards]

    return msg

async def getBoardDetail(idx: int) -> ResponseEntity:
    msg = ResponseEntity()
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(BoardTable).where(BoardTable.idx == idx)
        )
        board = result.scalar_one_or_none()

        if board is None:
            msg.flag = RF.InvalidBoardIdx.value
            msg.msg = RF.InvalidBoardIdx.message
            return msg

        msg.res = Board(
            idx=board.idx,
            username=board.username,
            title=board.title,
            contents=board.contents,
            viewcount=board.viewcount,
            likes=json.loads(board.likes),
            createdt=board.createdt,
            recentdt=board.recentdt
        )

    return msg


async def getBoardComments(idx: int) -> ResponseEntity:
    msg = ResponseEntity()
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(BoardCommentTable).where(BoardCommentTable.ridx == idx)
        )
        msg.res = [BoardComment(
            idx=c.idx,
            ridx=c.ridx,
            username=c.username,
            contents=c.contents,
            createdt=c.createdt,
            recentdt=c.recentdt
        ) for c in result.scalars().all()]

    return msg

async def writeBoard(board: Board) -> ResponseEntity:
    msg = ResponseEntity()
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                session.add(BoardTable(
                    username=board.username,
                    title=board.title,
                    contents=board.contents,
                    viewcount=0,
                    likes=json.dumps([]),
                    createdt=datetime.now(),
                    recentdt=datetime.now()
                ))
    except Exception as e:
        print(e)
        msg.flag = RF.SaveBoardDataFailed.value
        msg.msg = RF.SaveBoardDataFailed.message

    return msg

async def updateBoard(idx: int, board: Board) -> ResponseEntity:
    msg = ResponseEntity()
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(BoardTable)
            .where(BoardTable.idx == idx)
            .values(title=board.title, contents=board.contents, recentdt=datetime.now())
        )
        await session.commit()

    return msg

async def deleteBoard(idx: int) -> ResponseEntity:
    msg = ResponseEntity()
    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(BoardTable).where(BoardTable.idx == idx)
        )
        await session.execute(
            delete(BoardCommentTable).where(BoardCommentTable.ridx == idx)
        )
        await session.commit()

    return msg

async def getBoardCommentDetail(idx: int) -> ResponseEntity:
    msg = ResponseEntity()
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(BoardCommentTable).where(BoardCommentTable.idx == idx)
        )
        boardComment = result.scalar_one_or_none()

        if boardComment is None:
            msg.flag = RF.InvalidBoardCommentIdx.value
            msg.msg = RF.InvalidBoardCommentIdx.message
            return msg

        boardCommentDetail = BoardComment(
            idx=boardComment.idx,
            ridx=boardComment.ridx,
            username=boardComment.username,
            contents=boardComment.contents,
            createdt=boardComment.createdt,
            recentdt=boardComment.recentdt
        )

        msg.res = boardCommentDetail

    return msg

async def writeBoardComment(boardComment: BoardComment) -> ResponseEntity:
    msg = ResponseEntity()
    
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                session.add(BoardCommentTable(
                    ridx=boardComment.ridx,
                    username=boardComment.username,
                    contents=boardComment.contents,
                    createdt=datetime.now(),
                    recentdt=datetime.now()
                ))
    except Exception as e:
        print(e)
        msg.flag = RF.SaveBoardCommentDataFailed.value
        msg.msg = RF.SaveBoardCommentDataFailed.message

    return msg

async def updateBoardComment(idx: int, boardComment: BoardComment) -> ResponseEntity:
    msg = ResponseEntity()
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(BoardCommentTable)
            .where(BoardCommentTable.idx == idx)
            .values(contents=boardComment.contents, recentdt=datetime.now())
        )
        await session.commit()

    return msg

async def deleteBoardComment(idx: int) -> ResponseEntity:
    msg = ResponseEntity()
    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(BoardCommentTable).where(BoardCommentTable.idx == idx)
        )
        await session.commit()

    return msg

async def updateBoardView(idx: int) -> ResponseEntity:
    msg = ResponseEntity()
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(BoardTable)
            .where(BoardTable.idx == idx)
            .values(viewcount=BoardTable.viewcount + 1)
        )
        await session.commit()

    return msg


async def updateBoardLikes(idx: int, likeuser: str) -> ResponseEntity:
    msg = ResponseEntity()
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(BoardTable.likes).where(BoardTable.idx == idx)
        )
        likes = json.loads(result.scalar_one())

        if likeuser in likes:
            likes.remove(likeuser)
        else:
            likes.append(likeuser)

        await session.execute(
            update(BoardTable)
            .where(BoardTable.idx == idx)
            .values(likes=json.dumps(likes))
        )
        await session.commit()

        msg.res = len(likes)

    return msg
