#DB를 사용함으로써 파일 입출력은 필요없어졌습니다. 따라서 파일 입출력과 관련된 코드는 사용안합니다.

import json
from sqlalchemy import select
from db.databasemodel import AsyncSessionLocal, UserTable, BoardTable, BoardCommentTable
from utils.models import ReturnFlag, UserDetail, Board, BoardComment


async def saveUserData(userLoginData: dict) -> int:
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                for email, user in userLoginData.items():
                    existing = await session.get(UserTable, email)
                    if existing:
                        existing.username = user.username
                        existing.pwd = user.pwd
                        existing.lastlogindt = user.lastlogindt
                    else:
                        session.add(UserTable(
                            useremail=user.useremail,
                            username=user.username,
                            pwd=user.pwd,
                            lastlogindt=user.lastlogindt
                        ))
    except Exception as e:
        print(e)
        print("유저 데이터 저장에 실패하였습니다...")
        return ReturnFlag.SaveUserDataFailed.value
    return ReturnFlag.Success.value


async def loadUserData() -> dict[str, UserDetail] | None:
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(UserTable))
            users = result.scalars().all()
            if not users:
                return None
            return {u.useremail: UserDetail(
                username=u.username,
                useremail=u.useremail,
                pwd=u.pwd,
                lastlogindt=u.lastlogindt
            ) for u in users}
    except Exception as e:
        print(e)
        return None


async def saveBoardData(boardList: list) -> int:
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                for board in boardList:
                    existing = await session.get(BoardTable, board.idx)
                    if existing:
                        existing.username = board.username
                        existing.title = board.title
                        existing.contents = board.contents
                        existing.viewcount = board.viewcount
                        existing.likes = json.dumps(board.likes)
                        existing.recentdt = board.recentdt
                    else:
                        session.add(BoardTable(
                            idx=board.idx,
                            username=board.username,
                            title=board.title,
                            contents=board.contents,
                            viewcount=board.viewcount,
                            likes=json.dumps(board.likes),
                            createdt=board.createdt,
                            recentdt=board.recentdt
                        ))
    except Exception as e:
        print(e)
        print("게시물 저장에 실패하였습니다.")
        return ReturnFlag.SaveBoardDataFailed.value
    return ReturnFlag.Success.value


async def saveBoardCommentData(boardCommentList: list) -> int:
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                for comment in boardCommentList:
                    existing = await session.get(BoardCommentTable, comment.idx)
                    if existing:
                        existing.ridx = comment.ridx
                        existing.username = comment.username
                        existing.contents = comment.contents
                        existing.recentdt = comment.recentdt
                    else:
                        session.add(BoardCommentTable(
                            idx=comment.idx,
                            ridx=comment.ridx,
                            username=comment.username,
                            contents=comment.contents,
                            createdt=comment.createdt,
                            recentdt=comment.recentdt
                        ))
    except Exception as e:
        print(e)
        print("게시물 댓글 저장에 실패하였습니다.")
        return ReturnFlag.SaveBoardCommentDataFailed.value
    return ReturnFlag.Success.value


async def loadBoardData() -> tuple:
    boardList = None
    boardCommentList = None

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(BoardTable))
            boardList = [Board(
                idx=b.idx,
                username=b.username,
                title=b.title,
                contents=b.contents,
                viewcount=b.viewcount,
                commentcount=0,
                likes=json.loads(b.likes),
                createdt=b.createdt,
                recentdt=b.recentdt
            ) for b in result.scalars().all()]

            result = await session.execute(select(BoardCommentTable))
            boardCommentList = [BoardComment(
                idx=c.idx,
                ridx=c.ridx,
                username=c.username,
                contents=c.contents,
                createdt=c.createdt,
                recentdt=c.recentdt
            ) for c in result.scalars().all()]

        return (boardList, boardCommentList)
    except Exception as e:
        print(e)
        if boardList is not None:
            return (boardList, boardCommentList)
        print("불러올 게시물이 없습니다...")

    return ([], [])
