import sqlite3 as dbapi
import os

alreadyExists = os.path.exists("github.db")

conn = dbapi.connect("github.db")

if not alreadyExists:
	file = open("init_github.sql")
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
	def GetLangUsage(): # Dobimo količino commitov za posamezen jezik 
		sqlCode = """
			SELECT l.name, COUNT(*) AS usage
			FROM repository AS r JOIN language AS l ON (l.id = r.lang_id)
			JOIN "commit" AS c ON (c.repo_id = r.id)
			GROUP BY l.name
		"""
		
		return list(conn.execute(sqlCode).fetchall())


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
	def getAllUsersInfo(): #we get all data of all users
		sqlCode = """
			SELECT username,num_public_repos,num_followers,SUBSTR(join_date,1,10)
			FROM user;
		"""

		return list(conn.execute(sqlCode).fetchall())

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

class Issue:
	def __init__(self,id,title,body,state,dateOpened,userId,repoId):
		self.id = id
		self.title = title
		self.body = body
		self.state = state
		self.dateOpened = dateOpened
		self.userId = userId
		self.repoId = repoId

	def get(self):
		return (self.id,self.title,self.body,self.state,self.dateOpened,self.userId,self.repoId)

	def insert(self):
		sqlCode = """
			INSERT INTO issue
			VALUES (?,?,?,?,?,?,?);
		"""

		conn.execute(sqlCode,self.get())
	
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
			WHERE u.username = ?
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



import requests as r
import json
from secret import secretUsername,secretToken

authUsr = (secretUsername,secretToken)

successful = r.get(f"https://api.github.com/users/{secretUsername}",headers = {"Authorization": f"token {secretToken}"}).status_code == 200
if not successful:
	print("Secret parameters for comunicating with github api are invalid!")
	exit(-1)

encounteredUsers = set(User.getCurrIds())
encounteredRepos = set(Repository.getCurrIds())
encounteredCommits = set(Commit.getCurrShas())
encounteredIssues = set(Issue.getCurrIds())
encounteredLangs = dict(Language.getCurrLangs())
storedUsers = ["LukaFMF","jaanos"]
for user in storedUsers:
	userData = json.loads(r.get(f"https://api.github.com/users/{user}",auth = authUsr).text)

	usr = User(userData["id"],userData["login"],userData["public_repos"],
		userData["followers"],userData["created_at"])

	if usr.id not in encounteredUsers:
		encounteredUsers.add(usr.id)
		usr.insert()

	# dodaj podatke o repozitorijih in prispevkih
	userReposData = json.loads(r.get(userData["repos_url"],auth = authUsr).text)
	for repoData in userReposData:
		if not repoData["fork"]:
			lang = repoData["language"]

			if lang not in encounteredLangs:
				progLang = Language(lang)
				encounteredLangs[lang] = progLang.insert()

			repo = Repository(repoData["id"],repoData["name"],repoData["description"],
				repoData["stargazers_count"],repoData["created_at"],usr.id,encounteredLangs[lang])

			if repo.id not in encounteredRepos:
				encounteredRepos.add(repo.id)
				repo.insert()
			else: # ce imamo podatke o enem repozitoriju, imamo verjetno tudi vse ostale podatke o uporabniku
				break
			

			commitsData = json.loads(r.get(f"https://api.github.com/repos/{usr.username}/{repo.title}/commits",
				auth = authUsr).text)
			for commitData in commitsData:
				if commitData != None and "author" in commitData and commitData["author"] != None:
					commiterUsername = commitData["author"]["login"]
					commiterData = json.loads(r.get(f"https://api.github.com/users/{commiterUsername}",auth = authUsr).text)

					commitUsr = User(commiterData["id"],commiterData["login"],commiterData["public_repos"],
						commiterData["followers"],commiterData["created_at"])

					if commitUsr.id not in encounteredUsers:
						encounteredUsers.add(commitUsr.id)
						commitUsr.insert()

					comData = commitData["commit"]
					commit = Commit(commitData["sha"],comData["message"],comData["author"]["date"],commitUsr.id,repo.id)

					if commit.sha not in encounteredCommits:
						encounteredCommits.add(commit.sha)
						commit.insert()

			# dobi le prvih 20 ali 25 vprasanj
			issuesData = json.loads(r.get(f"https://api.github.com/repos/{usr.username}/{repo.title}/issues",
				auth = authUsr).text)
			for issueData in issuesData:
				if issueData != None and "user" in issueData and issueData["user"] != None:
					issuerUsername = issueData["user"]["login"]
					issuerData = json.loads(r.get(f"https://api.github.com/users/{issuerUsername}",auth = authUsr).text)

					issueUsr = User(issuerData["id"],issuerData["login"],issuerData["public_repos"],
						issuerData["followers"],issuerData["created_at"])

					if issueUsr.id not in encounteredUsers:
						encounteredUsers.add(issueUsr.id)
						issueUsr.insert()

					issue = Issue(issueData["id"],issueData["title"],issueData["body"],
						issueData["created_at"],issueUsr.id,repo.id)

					if issue.id not in encounteredIssues:
						encounteredIssues.add(issue.id)
						issue.insert()
	conn.commit()