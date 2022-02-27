from model import *

def getInput(maxOptions):
	try:
		choice = int(input("Izbira: "))
		if choice > maxOptions or choice < 1:
			raise Exception()
		print()
		return choice
	except:
		print("Neveljaven vnos!")
		return 0


def displayUsers():
	print("Podatke o katerem uporabniku zelite?")

	usernames = User.getAllUsernames()
	while True:
		for i,user in enumerate(usernames):
			print(f"{i + 1}) {user}")

		print()
		lastOpition = len(usernames) + 1
		print(f"{lastOpition}) Nazaj")

		choice = getInput(lastOpition)
		if choice == lastOpition:
			break

		if choice != 0:
			userInfo = User.getUserInfo(usernames[choice - 1])
			while True:
				print(f"ID: {userInfo[0]}")
				print(f"Uporabnisko ime: {userInfo[1]}")
				print(f"Stevilo javnih repozitorjev: {userInfo[2]}")
				print(f"Stevilo sledilcev: {userInfo[3]}")
				print(f"Datum pridruzitve: {userInfo[4]}")
				print()
				print("1) Nazaj na uporabnike")

				choice = getInput(1)

				if choice != 0:
					break

			
def displayRepos():
	print("Podatke o katerem repozitoriju zelite?")

	repos = Repository.getAllRepoNamesAndIds()
	while True:
		for i,repo in enumerate(repos):
			print(f"{i + 1}) {repo[1]}")

		print()
		lastOpition = len(repos) + 1
		print(f"{lastOpition}) Nazaj")

		choice = getInput(lastOpition)
		if choice == lastOpition:
			break

		if choice != 0:
			repoInfo = Repository.getRepoInfo(repos[choice - 1][0])
			while True:
				print(f"ID: {repoInfo[0]}")
				print(f"Naslov: {repoInfo[1]}")
				print(f"Opis: {repoInfo[2]}")
				print(f"Stevilo zvezdic: {repoInfo[3]}")
				print(f"Datum nastanka: {repoInfo[4]}")
				print(f"Lastnik: {repoInfo[5]}")
				print(f"Programski jezik: {repoInfo[6]}")
				print()
				print("1) Nazaj na repozitorje")

				choice = getInput(1)

				if choice != 0:
					break




def textInterface():
	while True:
		print("Podatke o cem zelite?")
		print("1) Osebe")
		print("2) Repozitoriji")
		print("3) Izhod")

		choice = getInput(3)
		if choice == 1:
			displayUsers()
		elif choice == 2:
			displayRepos()
		elif choice == 3:
			break

try:
	textInterface()
finally:
	conn.close()
