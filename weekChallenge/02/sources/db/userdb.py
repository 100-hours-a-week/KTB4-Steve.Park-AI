from sqlalchemy import select, update
from db.databasemodel import AsyncSessionLocal, UserTable
from utils.models import ReturnFlag as RF, ResponseEntity, UserDetail
from datetime import datetime

async def checkUserNicknameDuplicated(username: str) -> bool:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(UserTable).where(UserTable.username == username)
        )
        return result.scalar_one_or_none() is not None


async def checkUserEmailDuplicated(useremail: str) -> bool:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(UserTable).where(UserTable.useremail == useremail)
        )
        return result.scalar_one_or_none() is not None


async def createUser(user: UserDetail) -> ResponseEntity:
    msg = ResponseEntity()
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                session.add(UserTable(
                    useremail=user.useremail,
                    username=user.username,
                    pwd=user.pwd,
                    lastlogindt=datetime.now()
                ))
    except Exception as e:
        print(e)
        msg.flag = RF.SaveUserDataFailed.value
        msg.msg = RF.SaveUserDataFailed.message
    return msg


async def userLogin(useremail: str, pwd: str) -> ResponseEntity:
    msg = ResponseEntity()
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(UserTable).where(UserTable.useremail == useremail)
        )
        user = result.scalar_one_or_none()

        if user is None:
            msg.flag = RF.UserNotExist.value
            msg.msg = RF.UserNotExist.message
            return msg

        msg.res = UserDetail(
            username=user.username,
            useremail=user.useremail,
            lastlogindt=user.lastlogindt,
            pwd=user.pwd
        )
    return msg

async def userUpdateLastLogin(useremail) -> ResponseEntity:
    msg = ResponseEntity()
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                await session.execute(
                    update(UserTable)
                    .where(UserTable.useremail == useremail)
                    .values(lastlogindt=datetime.now())
                )

    except Exception as e:
        print(e)
        print("유저 데이터 업데이트에 실패하였습니다...")
        msg.flag = RF.SaveUserDataFailed.value
        msg.msg = RF.SaveUserDataFailed.message
        return msg
    
    return msg