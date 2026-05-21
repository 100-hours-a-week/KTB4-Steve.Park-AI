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

_MESSAGES: Final[dict] = {
	0:  "Success",
	1:  "Email already exists",
	2:  "Invalid username",
	3:  "Username is required",
	4:  "Incorrect password",
	5:  "Password is required",
	6:  "Invalid email format",
	7:  "Email is required",
	8:  "Failed to save user data",
	9:  "User is not available",
	10: "Username already taken",
	11: "Failed to save post",
	12: "Failed to save comment",
	13: "Post title is required",
	14: "Post content is required",
	15: "Post not found",
	16: "Post ID is required",
	17: "Comment not found",
	18: "Comment content is required",
	19: "No comments found",
}

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

	@property
	def message(self) -> str:
		return _MESSAGES.get(self.value, self.name)
