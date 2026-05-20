from pydantic import BaseModel, EmailStr
from enum import Enum
from datetime import datetime
from typing import Any, Final

BOARD_PAGE_SIZE: Final[int] = 10
SECRET_KEY: Final[str] = "week02fastapites"

class ResponseEntity(BaseModel):
	flag: int = 0
	msg: str = "Success"
	res: Any = None

class User(BaseModel):
	username: str
	useremail: EmailStr
	lastlogindt: datetime

class UserDetail(User):
	pwd: str

class Board(BaseModel):
	idx: int
	username: str
	title: str
	contents: str
	viewcount: int = 0
	commentcount: int = 0
	likes: list
	createdt: datetime
	recentdt: datetime

class BoardComment(BaseModel):
	idx: int
	ridx: int = 0
	username: str
	contents: str
	createdt: datetime
	recentdt: datetime

class ReturnFlag(int, Enum):
	Success = 0,
	UserEmailExist = 1,
	InvalidUserName = 2,
	EmptyUserName = 3,
	InvalidUserPwd = 4,
	EmptyUserPwd = 5,
	InvalidUserEmail = 6,
	EmptyUserEmail = 7,
	SaveUserDataFailed = 8,
	UserNotExist = 9,
	UserNameDuplicated = 10,

	SaveBoardDataFailed = 11,
	SaveBoardCommentDataFailed = 12,
	BoardTitleEmpty = 13,
	BoardContentsEmpty = 14,
	InvalidBoardIdx = 15,
	EmptyBoardIdx = 16,
	InvalidBoardCommentIdx = 17,
	BoardCommentContentsEmpty = 18,
	BoardCommentNotExist = 19
