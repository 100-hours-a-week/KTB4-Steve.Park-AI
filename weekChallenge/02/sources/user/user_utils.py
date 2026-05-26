from utils.models import ReturnFlag as RF, ResponseEntity, UserDetail, User
from utils.utils import encryptPwd, decryptPwd
from db import userdb

userInfo = {}

async def signup(user: UserDetail) -> ResponseEntity:
	msg = ResponseEntity()

	if user.username == "" or user.username is None:
		msg.error_code = RF.EmptyUserName.value
		msg.msg = RF.EmptyUserName.message
		return msg

	elif user.pwd == "" or user.pwd is None:
		msg.error_code = RF.EmptyUserPwd.value
		msg.msg = RF.EmptyUserPwd.message
		return msg

	elif user.useremail == "" or user.useremail is None:
		msg.error_code = RF.EmptyUserEmail.value
		msg.msg = RF.EmptyUserEmail.message
		return msg

	elif await userdb.checkUserEmailDuplicated(user.useremail):
		msg.error_code = RF.UserEmailExist.value
		msg.msg = RF.UserEmailExist.message
		return msg

	elif await userdb.checkUserNicknameDuplicated(user.username):
		msg.error_code = RF.UserNameDuplicated.value
		msg.msg = RF.UserNameDuplicated.message
		return msg

	user.pwd = encryptPwd(user.pwd)

	result = await userdb.createUser(user)

	if result.error_code != RF.Success.value:
		msg.error_code = result.error_code
		msg.msg = result.msg
		return msg

	print(f"New User Created : {user}")

	return msg

async def login(useremail: str, pwd: str) -> ResponseEntity:
	global userInfo

	msg = ResponseEntity()

	if useremail == "" or useremail is None:
		msg.error_code = RF.EmptyUserEmail.value
		msg.msg = RF.EmptyUserEmail.message
		return msg

	user = await userdb.userLogin(useremail, pwd)
	if user.error_code != RF.Success.value:
		msg.error_code = user.error_code
		msg.msg = user.msg
		return msg

	decryptedPwd = decryptPwd(user.res.dict().get("pwd", None))
	if decryptedPwd != pwd:
		msg.error_code = RF.InvalidUserPwd.value
		msg.msg = RF.InvalidUserPwd.message
		return msg

	userInfo = user.res.dict()

	await userdb.userUpdateLastLogin(useremail)

	print(f"User Login : {userInfo.get('username', None)}, {userInfo.get('lastlogindt', None)}")

	msg.res = User(
		username=userInfo.get("username", None),
		useremail=userInfo.get("useremail", None),
		lastlogindt=userInfo.get("lastlogindt", None)	
	)

	return msg

# #deprecated
# async def loadAllUserLoginData():
# 	global userLoginDatas
# 	global userNickname

# 	userdata = await fileUtils.loadUserData()
# 	if userdata is not None:
# 		userLoginDatas = userdata

# 		for u in userLoginDatas.values():
# 			userNickname.add(u.username)

# #deprecated
# async def saveUserLoginData() -> int:
# 	global userLoginDatas

# 	return await fileUtils.saveUserData(userLoginDatas)


