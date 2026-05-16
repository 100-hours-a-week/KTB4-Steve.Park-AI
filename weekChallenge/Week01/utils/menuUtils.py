import time
from user import utils as userUtil

mainMenu = ['게임 접속', '계정 삭제', '게임 종료']

def LoadMainMenu(userId: str):
	print("---------------------------------")
	print(f"- Welcome, {userId} ")
	print("---------------------------------")
	print()

	for index, i in enumerate(mainMenu, 1):
		print(f"{index}. {i}")

	print()

	userInput = 0

	while True:
		userInput = int(input("메뉴를 선택해주세요: "))
		userInput -= 1

		if userInput >= len(mainMenu):
			print("해당 메뉴는 없습니다.")
		else:
			break

	if userInput == 0:
		print()
		loadingbar = "Loading."
		for i in range(10):
			print(loadingbar, end="\r")
			loadingbar += "."	
			time.sleep(0.5)
		print()
		print("게임 서버가 아직 시작 전입니다. 나중에 접속 부탁드립니다.") 
		print()
	
	elif userInput == 1:
		print(f"정말로 해당 캐릭터 {userId}를 삭제하시겠습니까?")
		print("1. 예.  2. 아니오")
		userChoice = int(input("입력: "))

		if userChoice == 1:
			print("캐릭터 삭제 처리 시작하겠습니다...")
			deleteResult = userUtil.deleteUser(userId)
			if deleteResult == 0:
				print("캐릭터 삭제 완료하였습니다...")
				print("이용해주셔서 감사합니다...")
				print()
			else:
				print("캐릭터 삭제에 오류가 있습니다.\n관리자에게 문의해주세요.")
				print()
		else:
			print()
			LoadMainMenu(userId)
	
	elif userInput == 2:					
		print("********************************************************************************")
		print("* 오늘 하루도 즐겁게 보내시길 바랍니다. Sloppy Game을 방문해주셔서 감사합니다! *")
		print("********************************************************************************")









