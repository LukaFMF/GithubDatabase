import sqlite3 as dbapi
import os
import time as t

jeZeUstvarjena = os.path.exists("github.db")

conn = dbapi.connect("github.db")

if not jeZeUstvarjena:
	file = open("init.sql")
	sqlCode = file.read()

	conn.executescript(sqlCode)
	
	file.close()

class Language:
	def __init__(self,name):
		self.langName = name

	def insert(self):
		sqlCode = """
			INSERT INTO language(name)
			VALUES (?)
		"""

		cur = conn.cursor()
		cur.execute(sqlCode,(self.langName,))

		return cur.lastrowid

class User:
	def __init__(self,id,username,numPublicRepos,numFollowers,joinDate):
		self.id = id
		self.username = username
		self.numPublicRepos = numPublicRepos
		self.numFollowers = numFollowers
		self.joinDate = joinDate
	
	def get(self):
		return (self.id,self.username,self.numPublicRepos,
			self.numFollowers,self.joinDate)

	def insert(self):
		sqlCode = """
			INSERT INTO user
			VALUES (?,?,?,?,?);
		"""

		conn.execute(sqlCode,self.get())

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
		return (self.id,self.title,self.description,self.numStars,
			self.createDate,self.ownerId,self.langId)

	def insert(self):
		sqlCode = """
			INSERT INTO repository
			VALUES (?,?,?,?,?,?,?);
		"""

		conn.execute(sqlCode,self.get())

class Issue:
	def __init__(self,id,title,state,dateOpened,userId,repoId):
		self.id = id
		self.title = title
		self.state = state
		self.dateOpened = dateOpened
		self.userId = userId
		self.repoId = repoId

class Commit:
	def __init__(self,sha,message,date,userId,repoId):
		self.sha = sha
		self.message = message
		self.date = date
		self.userId = userId
		self.repoId = repoId

	def get(self):
		return (self.sha,self.message,self.date,self.userId,self.repoId)

	def insert(self):
		sqlCode = """
			INSERT INTO "commit"
			VALUES (?,?,?,?,?);
		"""

		conn.execute(sqlCode,self.get())


sqlCode = """
	SELECT * 
	FROM user;
"""
if len(conn.execute(sqlCode).fetchall()) == 0:
	import requests as r
	import json
	from secret import secretUsername,secretToken

	authUsr = (secretUsername,secretToken,)

	def removeCurly(str):
		inx = str.find("{")
		return str[:inx]

	
	encounteredUsers = set()
	encounteredLangs = {}
	storedUsers = ["LukaFMF"]
	for user in storedUsers:
		userData = json.loads(r.get(f"https://api.github.com/users/{user}",auth = authUsr).text)

		usr = User(userData["id"],userData["login"],userData["public_repos"],
			userData["followers"],userData["created_at"])

		if usr.id not in encounteredUsers:
			encounteredUsers.add(usr.id)
			usr.insert()

		# dodaj podatke o repozitorijih in commitih 
		userReposData = json.loads(r.get(userData["repos_url"],auth = authUsr).text)
		for repoData in userReposData:
			if not repoData["fork"]:
				lang = repoData["language"]

				if lang not in encounteredLangs:
					progLang = Language(lang)
					encounteredLangs[lang] = progLang.insert()

				repo = Repository(repoData["id"],repoData["name"],repoData["description"],
					repoData["stargazers_count"],repoData["created_at"],usr.id,encounteredLangs[lang])

				repo.insert()

				commitsData = json.loads(r.get(f"https://api.github.com/repos/{usr.username}/{repo.title}/commits",
					auth = authUsr).text)
				for commitData in commitsData:
					commiterUsername = commitData["author"]["login"]
					commiterData = json.loads(r.get(f"https://api.github.com/users/{commiterUsername}",auth = authUsr).text)

					commitUsr = User(commiterData["id"],commiterData["login"],commiterData["public_repos"],
						commiterData["followers"],commiterData["created_at"])

					if commitUsr.id not in encounteredUsers:
						encounteredUsers.add(commitUsr.id)
						commitUsr.insert()

					comData = commitData["commit"]
					commit = Commit(commitData["sha"],comData["message"],comData["author"]["date"],commitUsr.id,repo.id)

					commit.insert()
					t.sleep(.01)

	conn.commit()

					

					



