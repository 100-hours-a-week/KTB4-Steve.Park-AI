from fastapi import APIRouter
from utils.models import UserDetail, ResponseEntity
from . import userUtils

router = APIRouter()

@router.post("/user")
async def signup(user: UserDetail) -> ResponseEntity:
	return await userUtils.signup(user)

@router.post("/session")
async def login(useremail: str, pwd: str) -> ResponseEntity:
	return await userUtils.login(useremail, pwd)