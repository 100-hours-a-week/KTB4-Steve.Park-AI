from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Text
from datetime import datetime

DATABASE_URL = "sqlite+aiosqlite:///datas/community.db"

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class UserTable(Base):
    __tablename__ = "users"
    useremail: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    pwd: Mapped[str] = mapped_column(String)
    lastlogindt: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class BoardTable(Base):
    __tablename__ = "boards"
    idx: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    contents: Mapped[str] = mapped_column(Text)
    viewcount: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[str] = mapped_column(Text, default="[]")
    createdt: Mapped[datetime] = mapped_column(DateTime)
    recentdt: Mapped[datetime] = mapped_column(DateTime)


class BoardCommentTable(Base):
    __tablename__ = "board_comments"
    idx: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ridx: Mapped[int] = mapped_column(Integer, default=0, index=True)
    username: Mapped[str] = mapped_column(String)
    contents: Mapped[str] = mapped_column(Text)
    createdt: Mapped[datetime] = mapped_column(DateTime)
    recentdt: Mapped[datetime] = mapped_column(DateTime)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
