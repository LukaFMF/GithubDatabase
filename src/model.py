import sqlite3 as dbapi
import os
import csv

conn = dbapi.connect("db/github.db")

def createTablesFromScriptInMainDb(scriptPath):
	"""
	Creates tables in db/github.db from code 
	contained in scriptPath
	"""
	file = open(scriptPath)
	sqlCode = file.read()
	file.close()

	conn.executescript(sqlCode)

import functions as f

class Language:
	def __init__(self,id,name):
		self.id = id
		self.name = name

	def get(self):
		return (self.id,self.name)

	def insert(self):
		sqlCode = """
			INSERT INTO language
			VALUES (?,?);
		"""
		conn.execute(sqlCode,self.get())

	@staticmethod
	def cacheExisting(filename,dialectName):
		with open(f"data/{filename}","r",newline = "",encoding = "utf8") as file:
			reader = csv.reader(file,dialect = dialectName)

			existingLangs = dict()
			for row in reader:
				langId,name = row

				# languages can be None, which gets converted to empty string 
				# when writing to a file, we need to convert it back
				if len(name) == 0:
					name = None
				
				existingLangs[name] = int(langId)

			return existingLangs

	@staticmethod
	def getCurrLangs():
		sqlCode = """
			SELECT name,id
			FROM language;
		"""

		return list(conn.execute(sqlCode).fetchall())

	@staticmethod
	def getLang(id):
		sqlCode = """
			SELECT name
			FROM language
			WHERE id = ?;
		"""

		return conn.execute(sqlCode,(id,)).fetchone()
	
	@staticmethod
	def getLangUsage(): # Dobimo količino commitov za posamezen jezik 
		sqlCode = """
			SELECT l.name,COUNT(DISTINCT r.id),COUNT(DISTINCT c.sha)
			FROM repository AS r JOIN language AS l ON (l.id = r.lang_id)
			JOIN "commit" AS c ON (c.repo_id = r.id)
			WHERE l.name IS NOT NULL
			GROUP BY l.name;
		"""
		
		return list(conn.execute(sqlCode).fetchall())

	@staticmethod
	def getFavoriteLangOfUser(username):
		sqlCode = """
			SELECT l.name,COUNT(DISTINCT c.sha) AS usage
			FROM user AS u JOIN "commit" AS c ON (u.id = c.user_id) 
			JOIN repository AS r ON (c.repo_id = r.id) 
			JOIN language AS l ON (l.id = r.lang_id) 
			WHERE u.username = ? AND l.name IS NOT NULL
			GROUP BY l.name
			ORDER BY usage DESC
			LIMIT 1;
		"""

		res = conn.execute(sqlCode,(username,)).fetchone()
		if res == None:
			return "/"
		return res[0]

	# vvv Text interface functions vvv
	@staticmethod
	def getLangUsageInOrder(): # Dobimo količino commitov za posamezen jezik 
		sqlCode = """
			SELECT l.name,COUNT(DISTINCT r.id),COUNT(DISTINCT c.sha)
			FROM repository AS r JOIN language AS l ON (l.id = r.lang_id)
			JOIN "commit" AS c ON (c.repo_id = r.id)
			WHERE l.name IS NOT NULL
			GROUP BY l.name
			ORDER BY l.name ASC;
		"""
		
		return list(conn.execute(sqlCode).fetchall())

class User:
	def __init__(self,id,username,numFollowers,joinDate):
		self.id = id
		self.username = username
		self.numFollowers = numFollowers
		self.joinDate = joinDate
	
	def get(self):
		return (self.id,self.username,self.numFollowers,self.joinDate)

	def insert(self):
		sqlCode = """
			INSERT INTO user
			VALUES (?,?,?,?);
		"""
		conn.execute(sqlCode,self.get())
	
	@staticmethod
	def makeFrom(userJson):
		return User(userJson["id"],userJson["login"],
		userJson["followers"],f.extractDate(userJson["created_at"]))

	@staticmethod
	def cacheExisting(filename,dialectName):
		with open(f"data/{filename}","r",newline = "",encoding = "utf8") as file:
			reader = csv.reader(file,dialect = dialectName)

			existingUsers = set()
			for row in reader:
				id,_,_,_ = row
				existingUsers.add(int(id))

			return existingUsers

	@staticmethod
	def getCurrIds():
		sqlCode = """
			SELECT id 
			FROM user;
		"""

		return list(map(lambda el: el[0],conn.execute(sqlCode).fetchall()))
	
	@staticmethod
	def getUserInfo(username):
		sqlCode = """
			SELECT id,username,num_public_repos,num_followers,SUBSTR(join_date,1,10)
			FROM user
			WHERE username = ?;
		"""

		return conn.execute(sqlCode,(username,)).fetchone()

	@staticmethod
	def getAllUsersInfo():
		sqlCode = """
			SELECT username,num_public_repos,num_followers,SUBSTR(join_date,1,10)
			FROM user;
		"""

		return list(conn.execute(sqlCode).fetchall())

	# vvv Text interface functions vvv
	@staticmethod
	def getAllUsernamesInOrder():
		sqlCode = """
			SELECT username
			FROM user
			ORDER BY username ASC;
		"""

		return list(map(lambda el: el[0],conn.execute(sqlCode).fetchall()))

class Repository:
	def __init__(self,id,title,description,numStars,createDate,ownerId,langId):
		self.id = id
		self.title = title
		self.description = description
		self.numStars = numStars
		self.createDate = createDate
		self.ownerId = ownerId
		self.langId = langId

	def get(self):
		return (self.id,self.title,f.sanitizeStr(self.description),
		self.numStars,f.extractDate(self.createDate),self.ownerId,self.langId)

	def insert(self):
		sqlCode = """
			INSERT INTO repository
			VALUES (?,?,?,?,?,?,?);
		"""
		conn.execute(sqlCode,self.get())

	@staticmethod
	def makeFrom(repoJson,ownerId,langId):
		return Repository(repoJson["id"],repoJson["name"],
		repoJson["description"],repoJson["stargazers_count"],
		repoJson["created_at"],ownerId,langId)

	@staticmethod
	def cacheExisting(filename,dialectName):
		with open(f"data/{filename}","r",newline = "",encoding = "utf8") as file:
			reader = csv.reader(file,dialect = dialectName)

			existingRepos = set()
			for row in reader:
				id,_,_,_,_,_,_ = row
				existingRepos.add(int(id))

			return existingRepos

	@staticmethod
	def getCurrIds():
		sqlCode = """
			SELECT id 
			FROM repository;
		"""

		return list(map(lambda el: el[0],conn.execute(sqlCode).fetchall()))

	@staticmethod
	def getRepoInfo(username,repoName):
		sqlCode = """
			SELECT r.id,rO.username,r.title,IFNULL(r.description,"/"),r.num_stars,IFNULL(l.name,"/"),SUBSTR(r.date_created,1,10)
			FROM repository AS r JOIN user AS rO ON (r.owner_id = rO.id) 
			JOIN language AS l ON (r.lang_id = l.id)  
			WHERE rO.username = ? AND r.title = ?;
		"""

		return conn.execute(sqlCode,(username,repoName)).fetchone()

	@staticmethod
	def getAllReposInfo():
		sqlCode = """
			SELECT r.title,rO.username,IFNULL(r.description,"/"),r.num_stars,IFNULL(l.name,"/"),SUBSTR(r.date_created,1,10)
			FROM repository AS r JOIN user AS rO ON (rO.id = r.owner_id) 
			JOIN language AS l ON (l.id = r.lang_id)
		"""

		return list(conn.execute(sqlCode).fetchall())

	@staticmethod
	def getAllReposOfOwner(username):
		sqlCode = """
			SELECT r.title,IFNULL(r.description,"/"),r.num_stars,IFNULL(l.name,"/"),SUBSTR(r.date_created,1,10)
			FROM repository AS r JOIN user AS u ON (u.id = r.owner_id) JOIN 
			language AS l ON (r.lang_id = l.id)
			WHERE u.username = ?;
		"""

		return list(conn.execute(sqlCode,(username,)).fetchall())

	# vvv Text interface functions vvv
	@staticmethod
	def getAllReposOfOwnerInOrder(username):
		sqlCode = """
			SELECT r.title,IFNULL(r.description,"/"),r.num_stars,IFNULL(l.name,"/"),SUBSTR(r.date_created,1,10)
			FROM repository AS r JOIN user AS u ON (u.id = r.owner_id) JOIN 
			language AS l ON (r.lang_id = l.id)
			WHERE u.username = ?
			ORDER BY r.title ASC;
		"""

		return list(conn.execute(sqlCode,(username,)).fetchall())

	@staticmethod
	def getAllReposAndOwnersInOrder():
		sqlCode = """
			SELECT rO.username,r.title
			FROM repository AS r JOIN user AS rO ON (rO.id = r.owner_id)
			ORDER BY rO.username ASC,r.title ASC;
		"""

		return list(conn.execute(sqlCode).fetchall())

class Commit:
	def __init__(self,sha,message,timestamp,commiterId,repoId):
		self.sha = sha
		self.message = message
		self.timestamp = timestamp
		self.commiterId = commiterId
		self.repoId = repoId

	def get(self):
		return (self.sha,f.sanitizeStr(self.message),
		self.timestamp,self.commiterId,self.repoId)

	def insert(self):
		sqlCode = """
			INSERT INTO "commit"
			VALUES (?,?,?,?,?);
		"""
		conn.execute(sqlCode,self.get())

	@staticmethod
	def makeFrom(commitJson,commiterId,repoId):
		commitInner = commitJson["commit"]
		return Commit(commitJson["sha"],commitInner["message"],
		commitInner["author"]["date"],commiterId,repoId)

	@staticmethod
	def cacheExisting(filename,dialectName):
		with open(f"data/{filename}","r",newline = "",encoding = "utf8") as file:
			reader = csv.reader(file,dialect = dialectName)

			existingCommits = dict()
			for row in reader:
				sha,_,timestamp,_,repoId = row
				existingCommits[sha] = (int(repoId),timestamp)

			return existingCommits

	@staticmethod
	def getCurrShas():
		sqlCode = """
			SELECT sha 
			FROM "commit";
		"""

		return list(map(lambda el: el[0],conn.execute(sqlCode).fetchall()))

	@staticmethod
	def getAllCommitsByUsername(username):
		sqlCode = """
			SELECT c.sha,c.msg,rO.username,r.title,SUBSTR(c.date_created,1,10),SUBSTR(c.date_created,12,8)
			FROM "commit" AS c JOIN user AS u ON (c.user_id = u.id) 
			JOIN repository AS r ON(c.repo_id = r.id) JOIN user AS rO ON (r.owner_id = rO.id)
			WHERE u.username = ?;
		"""

		return list(conn.execute(sqlCode,(username,)).fetchall())

	@staticmethod	
	def getAllCommitsOfRepo(username,repoName):
		sqlCode = """
			SELECT c.sha,com.username,c.msg,SUBSTR(c.date_created,1,10),SUBSTR(c.date_created,12,8) 
			FROM repository AS r JOIN "commit" AS c ON (r.id = c.repo_id) 
			JOIN user AS com ON (com.id = c.user_id) 
			JOIN user AS rO ON (rO.id = r.owner_id)
			WHERE rO.username = ? AND r.title = ?;
		"""

		return list(conn.execute(sqlCode,(username,repoName)).fetchall())

	# vvv Text interface functions vvv
	@staticmethod
	def getAllCommitsByUsernameInOrder(username):
		sqlCode = """
			SELECT c.sha,c.msg,r.title,rO.username,SUBSTR(c.date_created,1,10),SUBSTR(c.date_created,12,8)
			FROM "commit" AS c JOIN user AS u ON (c.user_id = u.id) 
			JOIN repository AS r ON(c.repo_id = r.id) JOIN user AS rO ON (r.owner_id = rO.id)
			WHERE u.username = ?
			ORDER BY c.date_created DESC;
		"""

		return list(conn.execute(sqlCode,(username,)).fetchall())

	@staticmethod	
	def getAllCommitsOfRepoInOrder(username,repoName):
		sqlCode = """
			SELECT c.sha,com.username,c.msg,SUBSTR(c.date_created,1,10),SUBSTR(c.date_created,12,8) 
			FROM repository AS r JOIN "commit" AS c ON (r.id = c.repo_id) 
			JOIN user AS com ON (com.id = c.user_id) 
			JOIN user AS rO ON (rO.id = r.owner_id)
			WHERE rO.username = ? AND r.title = ?
			ORDER BY c.date_created DESC;
		"""

		return list(conn.execute(sqlCode,(username,repoName)).fetchall())

class Issue:
	def __init__(self,id,title,body,state,numComments,creationTimestamp,issuerId,repoId):
		self.id = id
		self.title = title
		self.body = body
		self.state = state
		self.numComments = numComments 
		self.creationTimestamp = creationTimestamp
		self.issuerId = issuerId
		self.repoId = repoId

	def get(self):
		return (self.id,self.title,f.sanitizeStr(self.body),self.state,
		self.numComments,self.creationTimestamp,self.issuerId,self.repoId)

	def insert(self):
		sqlCode = """
			INSERT INTO issue
			VALUES (?,?,?,?,?,?,?,?);
		"""
		conn.execute(sqlCode,self.get())
	
	@staticmethod
	def makeFrom(issueJson,issuerId,repoId):
		isOpen = 1 if issueJson["state"] == "open" else 0 
		return Issue(issueJson["id"],issueJson["title"],issueJson["body"],isOpen,
		issueJson["comments"],issueJson["created_at"],issuerId,repoId)

	@staticmethod
	def cacheExisting(filename,dialectName):
		with open(f"data/{filename}","r",newline = "",encoding = "utf8") as file:
			reader = csv.reader(file,dialect = dialectName)

			existingIssues = dict()
			for row in reader:
				sha,_,_,_,_,dateOpened,_,repoId = row
				existingIssues[sha] = (int(repoId),dateOpened)

			return existingIssues

	@staticmethod
	def getCurrIds():
		sqlCode = """
			SELECT id 
			FROM issue;
		"""

		return list(map(lambda el: el[0],conn.execute(sqlCode).fetchall()))

	@staticmethod
	def getAllIssuesOfUser(username):  #dobimo podatke: naslov vprašanja, naslov repozitorija, lastnik repozitorija, stanje, datum, avtor vprašanja
		sqlCode = """
			SELECT i.title,r.title,rO.username,IFNULL(i.body,"/"),SUBSTR(i.date_opened,1,10),SUBSTR(i.date_opened,12,8) 
			FROM issue AS i JOIN user AS u ON (i.user_id = u.id)
			JOIN repository AS r ON (i.repo_id = r.id)
			JOIN user AS rO ON (r.owner_id = rO.id)
			WHERE u.username = ?;
		"""
		return list(conn.execute(sqlCode,(username,)).fetchall())


	@staticmethod
	def getAllIssuesOfRepo(username,repoName):
		sqlCode = """
			SELECT i.title,u.username,IFNULL(i.body,"/"),SUBSTR(i.date_opened,1,10),SUBSTR(i.date_opened,12,8)
			FROM issue AS i JOIN repository AS r ON (i.repo_id = r.id)
			JOIN user AS u ON (i.user_id = u.id) 
			JOIN user AS rO ON (rO.id = r.owner_id) 
			WHERE rO.username = ? AND r.title = ?;
		"""
		return list(conn.execute(sqlCode,(username,repoName)).fetchall())

	# vvv Text interface functions vvv
	@staticmethod
	def getAllIssuesOfUserInOrder(username):  #dobimo podatke: naslov vprašanja, naslov repozitorija, lastnik repozitorija, stanje, datum, avtor vprašanja
		sqlCode = """
			SELECT i.title,r.title,rO.username,IFNULL(i.body,"/"),SUBSTR(i.date_opened,1,10),SUBSTR(i.date_opened,12,8) 
			FROM issue AS i JOIN user AS u ON (i.user_id = u.id)
			JOIN repository AS r ON (i.repo_id = r.id)
			JOIN user AS rO ON (r.owner_id = rO.id)
			WHERE u.username = ?
			ORDER BY i.date_opened DESC;
		"""
		return list(conn.execute(sqlCode,(username,)).fetchall())

	@staticmethod
	def getAllIssuesOfRepoInOrder(username,repoName):
		sqlCode = """
			SELECT i.title,u.username,IFNULL(i.body,"/"),SUBSTR(i.date_opened,1,10),SUBSTR(i.date_opened,12,8)
			FROM issue AS i JOIN repository AS r ON (i.repo_id = r.id)
			JOIN user AS u ON (i.user_id = u.id) 
			JOIN user AS rO ON (rO.id = r.owner_id) 
			WHERE rO.username = ? AND r.title = ?
			ORDER BY i.date_opened DESC;
		"""
		return list(conn.execute(sqlCode,(username,repoName)).fetchall())

# if __name__ == "__main__":
# 	import requests as r
# 	import json
# 	from secret import secretUsername,secretToken

# 	authUsr = (secretUsername,secretToken)

# 	successful = r.get(f"https://api.github.com/users/{secretUsername}",headers = {"Authorization": f"token {secretToken}"}).status_code == 200
# 	if not successful:
# 		print("Secret parameters for comunicating with github api are invalid!")
# 		exit(-1)

# 	encounteredUsers = set(User.getCurrIds())
# 	encounteredRepos = set(Repository.getCurrIds())
# 	encounteredCommits = set(Commit.getCurrShas())
# 	encounteredIssues = set(Issue.getCurrIds())
# 	encounteredLangs = dict(Language.getCurrLangs())
# 	storedUsers = ["matijapretnar","jaanos","LukaFMF","anzeozimek","lapajnea","Martina333","HanaL123","anaberdnik","titoo1234","Argonfmf","benisa21"]
# 	print("Fetching data... ")
# 	for user in storedUsers:
# 		userData = json.loads(r.get(f"https://api.github.com/users/{user}",auth = authUsr).text)

# 		usr = User(userData["id"],userData["login"],userData["public_repos"],
# 			userData["followers"],userData["created_at"])

# 		# print(f"User: {user}")
# 		if usr.id not in encounteredUsers:
# 			encounteredUsers.add(usr.id)
# 			usr.insert()

# 		# dodaj podatke o repozitorijih in prispevkih
# 		userReposData = json.loads(r.get(userData["repos_url"],auth = authUsr).text)
# 		for repoData in userReposData:
# 			if not repoData["fork"]:
# 				lang = repoData["language"]

# 				if lang not in encounteredLangs:
# 					progLang = Language(lang)
# 					encounteredLangs[lang] = progLang.insert()

# 				repo = Repository(repoData["id"],repoData["name"],repoData["description"],
# 					repoData["stargazers_count"],repoData["created_at"],usr.id,encounteredLangs[lang])

# 				# print(f"\tRepo: {repoData['name']}")
# 				if repo.id not in encounteredRepos:
# 					encounteredRepos.add(repo.id)
# 					repo.insert()
# 				else: # ce imamo podatke o enem repozitoriju, imamo verjetno tudi vse ostale podatke o uporabniku
# 					break
				
# 				i = 1
# 				commitsData = []
# 				while True:
# 					pageCommitsData = json.loads(r.get(f"https://api.github.com/repos/{usr.username}/{repo.title}/commits?page={i}&per_page=100",
# 						auth = authUsr).text)
					
# 					if not isinstance(pageCommitsData,list) or len(pageCommitsData) == 0:
# 						break
# 					commitsData.extend(pageCommitsData)
# 					i += 1

# 				for commitData in commitsData:
# 					if commitData != None and "author" in commitData and commitData["author"] != None:
# 						commiterUsername = commitData["author"]["login"]
# 						commiterData = json.loads(r.get(f"https://api.github.com/users/{commiterUsername}",auth = authUsr).text)

# 						commitUsr = User(commiterData["id"],commiterData["login"],0,
# 							commiterData["followers"],commiterData["created_at"])

# 						if commitUsr.id not in encounteredUsers:
# 							encounteredUsers.add(commitUsr.id)
# 							commitUsr.insert()

# 						comData = commitData["commit"]
# 						commit = Commit(commitData["sha"],comData["message"],comData["author"]["date"],commitUsr.id,repo.id)

# 						# print(f"\t\tCommit: {commitData['sha']}")
# 						if commit.sha not in encounteredCommits:
# 							encounteredCommits.add(commit.sha)
# 							commit.insert()

# 				i = 1
# 				issuesData = []
# 				while True:
# 					pageIssuesData = json.loads(r.get(f"https://api.github.com/repos/{usr.username}/{repo.title}/issues?page={i}&per_page=100",
# 					auth = authUsr).text)

# 					if not isinstance(pageIssuesData,list) or len(pageIssuesData) == 0:
# 						break
# 					issuesData.extend(pageIssuesData)
# 					i += 1

# 				for issueData in issuesData:
# 					if issueData != None and "user" in issueData and issueData["user"] != None:
# 						issuerUsername = issueData["user"]["login"]
# 						issuerData = json.loads(r.get(f"https://api.github.com/users/{issuerUsername}",auth = authUsr).text)

# 						issueUsr = User(issuerData["id"],issuerData["login"],0,
# 							issuerData["followers"],issuerData["created_at"])

# 						if issueUsr.id not in encounteredUsers:
# 							encounteredUsers.add(issueUsr.id)
# 							issueUsr.insert()

# 						issue = Issue(issueData["id"],issueData["title"],issueData["body"],
# 							issueData["created_at"],issueUsr.id,repo.id)

# 						# print(f"\t\tIssue: {issueData['id']}")
# 						if issue.id not in encounteredIssues:
# 							encounteredIssues.add(issue.id)
# 							issue.insert()
# 		# print(f"Calculation number of repos...")
# 		sqlCode = """
# 			UPDATE user AS u
# 			SET num_public_repos = (
# 				SELECT COUNT(*)
# 				FROM repository AS rO
# 				WHERE u.id = rO.owner_id
# 			)
# 			WHERE id = ?;
# 		"""
# 		conn.execute(sqlCode,(usr.id,))
# 		conn.commit()