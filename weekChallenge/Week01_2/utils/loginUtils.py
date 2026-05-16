import argparse
import asyncio

from user import utils as userUtil

async def login() -> tuple[str, int]:
	parser = argparse.ArgumentParser(description="ML Workflow CLI")
	subparsers = parser.add_subparsers(dest="command")

	login_parser = subparsers.add_parser("login", help="로그인")
	login_parser.add_argument("--id", required=True, type=str, help="아이디")
	login_parser.add_argument("--pwd", required=True, type=str, help="비밀번호")

	try:
		args = parser.parse_args()

		print(f"USER ID : {args.id}")

		if args.pwd is None:
			print("USER PWD : ")
		else:
			print(f"USER PWD : *********")

		print()
		
		userLoginData, result = userUtil.getUserLoginData(args.id, args.pwd)

		await asyncio.sleep(1)
		return userLoginData, result

	except SystemExit:
		print()
		print(" ------------------------------")
		print("|Login Failed. ID is required. |")
		print(" ------------------------------")
		print()
		return "", -1

