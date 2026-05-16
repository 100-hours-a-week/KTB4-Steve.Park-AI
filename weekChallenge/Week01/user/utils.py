import json
import argparse

from Crypto.Cipher import AES
from base64 import b64encode, b64decode

userLoginDatas = {}
secretKey = 'abcdefghijktb4ai'

def pad(text) -> str:
	return text + (16 - len(text) % 16) * chr(16 - len(text) % 16)

def unpad(text) -> str:
	return text[:-ord(text[-1])]

def encryptPwd(pwd: str) -> str:
	global secretKey

	if pwd is None or pwd == "":
		return pwd
	
	encrypted = pad(pwd)
	encodingKey = secretKey.encode('utf-8')
	cipher = AES.new(encodingKey, AES.MODE_CBC)
	ct_bytes = cipher.encrypt(encrypted.encode('utf-8'))
	iv = b64encode(cipher.iv).decode('utf-8')
	ct = b64encode(ct_bytes).decode('utf-8')

	return iv + ct

def decryptPwd(pwd: str) -> str:
	global secretKey

	if pwd is None or pwd == "":
		return pwd

	decryptKey = secretKey.encode('utf-8')
	iv = pwd[:24]
	ct = pwd[24:]
	iv = b64decode(iv)
	ct = b64decode(ct)
	cipher = AES.new(decryptKey, AES.MODE_CBC, iv)
	pt = unpad(cipher.decrypt(ct).decode('utf-8'))
	return pt	
	
def createUser() -> int:
	global loginUserDatas

	parser = argparse.ArgumentParser(description="ML Workflow CLI")
	subparsers = parser.add_subparsers(dest="command")
	create_parser = subparsers.add_parser("create", help="생성")
	create_parser.add_argument("--id", required=True, type=str, help="아이디")
	create_parser.add_argument("--pwd", required=True, type=str, help="비밀번호")
	
	try:
		args = parser.parse_args()
		if args.id is None:
			print("ID를 입력해주세요...")
		elif args.pwd is None:
			print("PWD를 입력해주세요...")
		
		userId, result = getUserLoginData(args.id, args.pwd)
		
		if result != 1:
			print("이미 존재하는 ID입니다. 새로운 ID를 입력해주세요.")
		else:
			userLoginDatas[args.id] = encryptPwd(args.pwd)
			saveResult = saveUserData()
			return saveResult	

	except SystemExit:
 		print()
 		print(" ------------------------------------")
 		print("|Create User Failed. ID is required. |")
 		print(" ------------------------------------")
 		print()
 		return "", -1

def getUserLoginData(userId: str, userPwd: str) -> tuple[str, int]:
	global loginUserDatas

	loginSuccess = 0
	idNotExist = 1
	pwdNotCorrect = 2

	pwd = userLoginDatas.get(userId, None)
	if pwd is None:
		return None, 1
	else:
		decryptedPwd = decryptPwd(pwd)
		if userPwd != decryptedPwd:
			return None, 2

	return userId, 0


def getAllUserDatas() -> dict[str, str]:
	global userLoginDatas

	return userLoginDatas

def LoadAllUserLoginDatas():
	global userLoginDatas
	try:
		with open('user/userLoginData.json', 'r', encoding='utf-8') as file:
			jsonData = json.load(file)
			userLoginDatas = jsonData['Users']
	except FileNotFoundError:
		print()
		print("-----------------------------------------")
		print("User Data Failed to Load -> No File Exist")
		print("-----------------------------------------")
		print()

def deleteUser(userId: str) -> int:
	result = deleteUserLoginData(userId)
	return result

def deleteUserLoginData(userId: str) -> int:
	global userLoginDatas

	removed = userLoginDatas.pop(userId, None)
	result = 0

	if removed is not None:
		saveResult = saveUserData()
		if saveResult == 0:
			return result		
		return -1
	else:
		print("해당 계정은 존재하지 않아 삭제가 불가능합니다.")
		return -1		

def saveUserData() -> int:
	global userLoginDatas

	failResult = -1
	successResult = 0

	try:
		with open('user/userLoginData.json', 'w', encoding='utf-8') as file:
			json.dump({'Users':userLoginDatas}, file, ensure_ascii=False)
	except BaseException as e:
		print("유저 저장에 오류가 발생하였습니다.")
		print(e)	
		return failResult

	return successResult


