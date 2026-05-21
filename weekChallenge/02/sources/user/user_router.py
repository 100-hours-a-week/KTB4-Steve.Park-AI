from fastapi import APIRouter
from fastapi.responses import FileResponse, RedirectResponse
from utils.models import UserDetail, ResponseEntity
from . import userUtils

router = APIRouter()

@router.get("/login",  response_class=FileResponse)
def login_page():
	return "views/user/login.html"

@router.get("/join",   response_class=FileResponse)
def join_page():
	return "views/user/join.html"

@router.post("/user")
async def signup(user: UserDetail) -> ResponseEntity:
	return await userUtils.signup(user)

@router.post("/session")
async def login(useremail: str, pwd: str) -> ResponseEntity:
	return await userUtils.login(useremail, pwd)