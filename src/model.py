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
			reader = csv.reader(file,dialect = f.csvDialectRead)

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
	def getLang(id):
		sqlCode = """
			SELECT name
			FROM language
			WHERE id = ?;
		"""

		return conn.execute(sqlCode,(id,)).fetchone()
	
	@staticmethod
	def getLangUsage():
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
			FROM user AS u JOIN "commit" AS c ON (u.id = c.commiter_id) 
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
	def getLangUsageInOrder(): 
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
			reader = csv.reader(file,dialect = f.csvDialectRead)

			existingUsers = set()
			for row in reader:
				id,_,_,_ = row
				existingUsers.add(int(id))

			return existingUsers
	
	@staticmethod
	def getUserInfo(username):
		sqlCode = """
			SELECT id,username,num_followers,join_date
			FROM user
			WHERE username = ?;
		"""

		return conn.execute(sqlCode,(username,)).fetchone()

	@staticmethod
	def getAllUsersInfo():
		sqlCode = """
			SELECT username,num_followers,join_date
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
		return (self.id,self.title,self.description,self.numStars,
		self.createDate,self.ownerId,self.langId)

	def insert(self):
		sqlCode = """
			INSERT INTO repository
			VALUES (?,?,?,?,?,?,?);
		"""
		conn.execute(sqlCode,self.get())

	@staticmethod
	def makeFrom(repoJson,ownerId,langId):
		description = None
		if repoJson["description"] != None:
			description = f.sanitizeStr(repoJson["description"])

		return Repository(repoJson["id"],repoJson["name"],description,
		repoJson["stargazers_count"],f.extractDate(repoJson["created_at"]),
		ownerId,langId)

	@staticmethod
	def cacheExisting(filename,dialectName):
		with open(f"data/{filename}","r",newline = "",encoding = "utf8") as file:
			reader = csv.reader(file,dialect = f.csvDialectRead)

			existingRepos = set()
			for row in reader:
				id,_,_,_,_,_,_ = row
				existingRepos.add(int(id))

			return existingRepos

	@staticmethod
	def getRepoInfo(username,repoName):
		sqlCode = """
			SELECT r.id,r.title,rO.username,IFNULL(r.description,"/"),r.num_stars,IFNULL(l.name,"/"),r.creation_date
			FROM repository AS r JOIN user AS rO ON (r.owner_id = rO.id) 
			JOIN language AS l ON (r.lang_id = l.id)  
			WHERE rO.username = ? AND r.title = ?;
		"""

		return conn.execute(sqlCode,(username,repoName)).fetchone()

	@staticmethod
	def getAllReposInfo():
		sqlCode = """
			SELECT r.title,rO.username,IFNULL(r.description,"/"),r.num_stars,IFNULL(l.name,"/"),r.creation_date
			FROM repository AS r JOIN user AS rO ON (rO.id = r.owner_id) 
			JOIN language AS l ON (l.id = r.lang_id)
		"""

		return list(conn.execute(sqlCode).fetchall())

	@staticmethod
	def getAllReposOfOwner(username):
		sqlCode = """
			SELECT r.title,IFNULL(r.description,"/"),r.num_stars,IFNULL(l.name,"/"),r.creation_date
			FROM repository AS r JOIN user AS u ON (u.id = r.owner_id) 
			JOIN language AS l ON (r.lang_id = l.id)
			WHERE u.username = ?;
		"""

		return list(conn.execute(sqlCode,(username,)).fetchall())

	# vvv Text interface functions vvv
	@staticmethod
	def getAllReposOfOwnerInOrder(username):
		sqlCode = """
			SELECT r.title,IFNULL(r.description,"/"),r.num_stars,IFNULL(l.name,"/"),r.creation_date
			FROM repository AS r JOIN user AS u ON (u.id = r.owner_id) 
			JOIN language AS l ON (r.lang_id = l.id)
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
		return (self.sha,self.message,self.timestamp,self.commiterId,self.repoId)

	def insert(self):
		sqlCode = """
			INSERT INTO "commit"
			VALUES (?,?,?,?,?);
		"""
		conn.execute(sqlCode,self.get())

	@staticmethod
	def makeFrom(commitJson,commiterId,repoId):
		commitInner = commitJson["commit"]

		msg = None 
		if commitInner["message"] != None:
			msg = f.sanitizeStr(commitInner["message"])

		return Commit(commitJson["sha"],msg,commitInner["author"]["date"],
		commiterId,repoId)

	@staticmethod
	def cacheExisting(filename,dialectName):
		with open(f"data/{filename}","r",newline = "",encoding = "utf8") as file:
			reader = csv.reader(file,dialect = f.csvDialectRead)

			existingCommits = dict()
			for row in reader:
				sha,_,timestamp,_,repoId = row
				existingCommits[sha] = (int(repoId),timestamp)

			return existingCommits

	@staticmethod
	def getAllCommitsByUsername(username):
		sqlCode = """
			SELECT c.sha,c.msg,rO.username,r.title,SUBSTR(c.timestamp,1,10),SUBSTR(c.timestamp,12,8)
			FROM "commit" AS c JOIN user AS u ON (c.commiter_id = u.id) 
			JOIN repository AS r ON(c.repo_id = r.id) JOIN user AS rO ON (r.owner_id = rO.id)
			WHERE u.username = ?;
		"""

		return list(conn.execute(sqlCode,(username,)).fetchall())

	@staticmethod	
	def getAllCommitsOfRepo(username,repoName):
		sqlCode = """
			SELECT c.sha,com.username,c.msg,SUBSTR(c.timestamp,1,10),SUBSTR(c.timestamp,12,8) 
			FROM repository AS r JOIN "commit" AS c ON (r.id = c.repo_id) 
			JOIN user AS com ON (com.id = c.commiter_id) 
			JOIN user AS rO ON (rO.id = r.owner_id)
			WHERE rO.username = ? AND r.title = ?;
		"""

		return list(conn.execute(sqlCode,(username,repoName)).fetchall())

	# vvv Text interface functions vvv
	@staticmethod
	def getAllCommitsByUsernameInOrder(username):
		sqlCode = """
			SELECT c.sha,c.msg,r.title,rO.username,SUBSTR(c.timestamp,1,10),SUBSTR(c.timestamp,12,8)
			FROM "commit" AS c JOIN user AS u ON (c.commiter_id = u.id) 
			JOIN repository AS r ON(c.repo_id = r.id) JOIN user AS rO ON (r.owner_id = rO.id)
			WHERE u.username = ?
			ORDER BY c.timestamp DESC;
		"""

		return list(conn.execute(sqlCode,(username,)).fetchall())

	@staticmethod	
	def getAllCommitsOfRepoInOrder(username,repoName):
		sqlCode = """
			SELECT c.sha,com.username,c.msg,SUBSTR(c.timestamp,1,10),SUBSTR(c.timestamp,12,8) 
			FROM repository AS r JOIN "commit" AS c ON (r.id = c.repo_id) 
			JOIN user AS com ON (com.id = c.commiter_id) 
			JOIN user AS rO ON (rO.id = r.owner_id)
			WHERE rO.username = ? AND r.title = ?
			ORDER BY c.timestamp DESC;
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
		return (self.id,self.title,self.body,self.state,self.numComments,
		self.creationTimestamp,self.issuerId,self.repoId)

	def insert(self):
		sqlCode = """
			INSERT INTO issue
			VALUES (?,?,?,?,?,?,?,?);
		"""
		conn.execute(sqlCode,self.get())
	
	@staticmethod
	def makeFrom(issueJson,issuerId,repoId):
		isOpen = 1 if issueJson["state"] == "open" else 0 

		body = None 
		if issueJson["body"] != None:
			body = f.sanitizeStr(issueJson["body"])

		return Issue(issueJson["id"],issueJson["title"],body,isOpen,
		issueJson["comments"],issueJson["created_at"],issuerId,repoId)

	@staticmethod
	def cacheExisting(filename,dialectName):
		with open(f"data/{filename}","r",newline = "",encoding = "utf8") as file:
			reader = csv.reader(file,dialect = f.csvDialectRead)

			existingIssues = dict()
			for row in reader:
				sha,_,_,_,_,dateOpened,_,repoId = row
				existingIssues[sha] = (int(repoId),dateOpened)

			return existingIssues

	@staticmethod
	def getAllIssuesOfUser(username):
		sqlCode = """
			SELECT i.title,r.title,rO.username,IFNULL(i.body,"/"),i.state,i.num_comments,SUBSTR(i.timestamp_opened,1,10),SUBSTR(i.timestamp_opened,12,8) 
			FROM issue AS i JOIN user AS u ON (i.issuer_id = u.id)
			JOIN repository AS r ON (i.repo_id = r.id)
			JOIN user AS rO ON (r.owner_id = rO.id)
			WHERE u.username = ?;
		"""
		return list(conn.execute(sqlCode,(username,)).fetchall())


	@staticmethod
	def getAllIssuesOfRepo(username,repoName):
		sqlCode = """
			SELECT i.title,u.username,IFNULL(i.body,"/"),i.state,i.num_comments,SUBSTR(i.timestamp_opened,1,10),SUBSTR(i.timestamp_opened,12,8)
			FROM issue AS i JOIN repository AS r ON (i.repo_id = r.id)
			JOIN user AS u ON (i.issuer_id = u.id) 
			JOIN user AS rO ON (rO.id = r.owner_id) 
			WHERE rO.username = ? AND r.title = ?;
		"""
		return list(conn.execute(sqlCode,(username,repoName)).fetchall())

	# vvv Text interface functions vvv
	@staticmethod
	def getAllIssuesOfUserInOrder(username):
		sqlCode = """
			SELECT i.title,r.title,rO.username,IFNULL(i.body,"/"),CASE i.state WHEN 1 THEN "open" ELSE "closed" END,
			i.num_comments,SUBSTR(i.timestamp_opened,1,10),SUBSTR(i.timestamp_opened,12,8) 
			FROM issue AS i JOIN user AS u ON (i.issuer_id = u.id)
			JOIN repository AS r ON (i.repo_id = r.id)
			JOIN user AS rO ON (r.owner_id = rO.id)
			WHERE u.username = ?
			ORDER BY i.timestamp_opened DESC;
		"""
		return list(conn.execute(sqlCode,(username,)).fetchall())

	@staticmethod
	def getAllIssuesOfRepoInOrder(username,repoName):
		sqlCode = """
			SELECT i.title,u.username,IFNULL(i.body,"/"),CASE i.state WHEN 1 THEN "open" ELSE "closed" END,
			i.num_comments,SUBSTR(i.timestamp_opened,1,10),SUBSTR(i.timestamp_opened,12,8)
			FROM issue AS i JOIN repository AS r ON (i.repo_id = r.id)
			JOIN user AS u ON (i.issuer_id = u.id) 
			JOIN user AS rO ON (rO.id = r.owner_id) 
			WHERE rO.username = ? AND r.title = ?
			ORDER BY i.timestamp_opened DESC;
		"""
		return list(conn.execute(sqlCode,(username,repoName)).fetchall())