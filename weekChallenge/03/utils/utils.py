def printanswer(num: int, answer: list | str):
	print(f"#{num} Quest:")
	if type(answer) == list:
		for a in answer:
			print(a)
			print()
	else:
		print(answer)
		print()