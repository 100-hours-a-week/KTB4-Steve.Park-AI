import sys
import json
import asyncio

from utils import loginUtils
from user import utils as userUtil
from utils import menuUtils

availableCommands = {'login': '--id **** --pwd ****', 'create': '--id **** --pwd ****'}
userId = ""

def LoadAllUserLoginDatas():
	userUtil.LoadAllUserLoginDatas()

async def login():
	global userId
	resultId, result = await loginUtils.login()

	if result == 0:
		userId = resultId
		print("--------------")
		print("로그인 성공!!!")
		print("--------------")
		print()
		
		await menuUtils.LoadMainMenu(userId)

	elif result == 1:
		print()
		print("해당 아이디가 존재하지 않습니다...")
		print()

	elif result == 2:
		print()
		print("해당 계정의 비밀번호가 옳지 않습니다. 다시 한번 확인해주세요...")
		print()

async def create():
	result = await userUtil.createUser()
	
	if result == 0:
		print()
		print("캐릭터 생성에 성공하였습니다. login을 통해 게임에 접속해주세요~!")
		print()
	else:
		print()
		print("캐릭터 생성에 실패하였습니다...")
		print()

async def main():
	print()
	print("##########################################")
	print("#        Welcome To Sloppy RPG...        #")
	print("##########################################")
	print()
	
	LoadAllUserLoginDatas()

	try:
		command = sys.argv[1]
		if command == "login":
			try:
				await login()
			except TypeError as e:
				print(e)
				print("ID와 PWD를 입력해주시기 바랍니다.")
				print(f"올바른 명령어: \"python3 sloppygame.py login {availableCommands['login']}\"")
		
		elif command == "create":
			try:
				await create()
			except TypeError as e:
				print(e)
				print("ID와 PWD를 입력해주시기 바랍니다.")
				print(f"올바른 명령어: \"python3 sloppygame.py create {availableCommands['create']}\"")
		

		else:
			raise IndexError()
	except IndexError:
		print()
		print("-------------------------------------")
		print("Usage python3 sloppygame.py <command>")
		print()
		print("Available Commands List:")
		print()
		for i in availableCommands.keys():
			print(f"   {i} {availableCommands[i]}")
		print()
	except Exception as e:
		print(e)

if __name__ == '__main__':
	asyncio.run(main())
