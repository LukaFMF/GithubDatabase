from model import *

def getInput(maxOptions):
	try:
		choice = int(input("Choice: "))
		if choice > maxOptions or choice < 0:
			raise Exception()
		print()
		return choice
	except:
		print("Invalid input!\n")
		return -1

def displayTable(header,cellSizes,data):
	""" len of header must match len cellSizes and each row in data """
	strFn = lambda n: f"{{:<{n}}}"
	newCellSizes = tuple([max(cellSizes[i],len(header[i])) for i in range(len(cellSizes))])
	modelRow = "|".join(map(strFn,newCellSizes)) # create generic row 
	print(modelRow.format(*header))
	totalContentWidth = sum(newCellSizes)
	print("-" * (totalContentWidth + len(cellSizes) - 1)) # add len of "|" chars
	for row in data:
		trimmedRow = (repr(str(row[i]))[1:-1][:newCellSizes[i]] for i in range(len(row)))
		print(modelRow.format(*trimmedRow))
	print()



def displayUsers():
	print("Display data about user:")

	usernames = User.getAllUsernamesInOrder()
	while True:
		for i,user in enumerate(usernames):
			print(f"{i + 1}) {user}")
		print()

		print("0) Back")

		choice = getInput(len(usernames))
		if choice == 0:
			break

		if choice != -1:
			username = usernames[choice - 1]
			userInfo = User.getUserInfo(username)
			favLang = Language.getFavoriteLangOfUser(username)

			# repos commits issues
			repos = Repository.getAllReposOfOwnerInOrder(username)
			commits = Commit.getAllCommitsByUsernameInOrder(username)
			issues = Issue.getAllIssuesOfUserInOrder(username)
			
			while True:
				print(f"ID: {userInfo[0]}")
				print(f"Username: {userInfo[1]}")
				print(f"Favorite programming language: {favLang}")
				print(f"Number of public repositories: {userInfo[2]}")
				print(f"Number of commits: {len(commits)}")
				print(f"Number of issues submitted: {len(issues)}")
				print(f"Number of followers: {userInfo[3]}")
				print(f"Join date: {userInfo[4]}")
				print()

				repoHeader = ("Title","Description","Num. stars","Prog. language","Date created")
				repoSizes = (25,45,14,15,12)
				print("Repositories:")
				if len(repos) != 0:
					displayTable(repoHeader,repoSizes,repos)

				commitHeader = ("Sha","Message","Repo. title","Repo. owner","Date created","Time created")
				commitSizes = (40,45,25,25,12,8)
				if len(commits) > 15:
					print("Fifteen most recent commits:")
					displayTable(commitHeader,commitSizes,commits[:15])
				elif len(commits) != 0:
					print("Commits:")
					displayTable(commitHeader,commitSizes,commits)

				issueHeader = ("Title","Repo. title","Repo. owner","Issue body","Date opened","Time opened")
				issueSizes = (25,25,25,45,12,8)
				if len(issues) > 15:
					print("Fifteen most recent issues:")
					displayTable(issueHeader,issueSizes,issues[:15])
				elif len(issues) != 0:
					print("Issues:")
					displayTable(issueHeader,issueSizes,issues)

				print("0) Back to users")

				choice = getInput(0)

				if choice != -1:
					break

			
def displayRepos():
	print("Display data about repository:")

	repoNamesAndOwners = Repository.getAllReposAndOwnersInOrder()
	while True:
		for i,repo in enumerate(repoNamesAndOwners):
			print(f"{i + 1}) {repo[0]}/{repo[1]}")
		print()

		print("0) Back")

		choice = getInput(len(repoNamesAndOwners))
		if choice == 0:
			break

		if choice != -1:
			ownerName = repoNamesAndOwners[choice - 1][0]
			repoName = repoNamesAndOwners[choice - 1][1]

			repoInfo = Repository.getRepoInfo(ownerName,repoName)
			commits = Commit.getAllCommitsOfRepoInOrder(ownerName,repoName)
			issues =  Issue.getAllIssuesOfRepoInOrder(ownerName,repoName)
			while True:
				print(f"ID: {repoInfo[0]}")
				print(f"Title: {repoInfo[2]}")
				print(f"Owner: {repoInfo[1]}")
				print(f"Description: {repoInfo[3]}")
				print(f"Number of commits: {len(commits)}")
				print(f"Number of issues: {len(issues)}")
				print(f"Number of stars: {repoInfo[4]}")
				print(f"Programing language: {repoInfo[5]}")
				print(f"Creation date: {repoInfo[6]}")
				print()

				commitHeader = ("Sha","Commiter","Message","Date created","Time created")
				commitSizes = (40,25,45,12,8)
				if len(commits) > 15:
					print("Fifteen most recent commits:")
					displayTable(commitHeader,commitSizes,commits[:15])
				elif len(commits) != 0:
					print("Commits:")
					displayTable(commitHeader,commitSizes,commits)

				issueHeader = ("Title","Issuer","Issue body","Date opened","Time opened")
				issueSizes = (25,25,45,12,8)
				if len(issues) > 15:
					print("Fifteen most recent issues:")
					displayTable(issueHeader,issueSizes,issues[:15])
				elif len(issues) != 0:
					print("Issues:")
					displayTable(issueHeader,issueSizes,issues)

				print("0) Back to repositories")

				choice = getInput(0)

				if choice != -1:
					break


def displayLangs():
	langData = Language.getLangUsageInOrder()
	while True:
		langHeader = ("Programming language","Number of repos. language is used in","Number of commits language is used in")
		langSizes = (15,10,10)
		if len(langData) != 0:
			print("Languages:")
			displayTable(langHeader,langSizes,langData)

		print("0) Back")

		choice = getInput(0)
		if choice != -1:
			break

def textInterface():
	while True:
		print("Retrieve data about:")
		print("1) Users")
		print("2) Repositories")
		print("3) Programing languages")
		print()
		print("0) Exit")

		choice = getInput(3)
		if choice == 0:
			break
		elif choice == 1:
			displayUsers()
		elif choice == 2:
			displayRepos()
		elif choice == 3:
			displayLangs()


try:
	textInterface()
finally:
	conn.close()
