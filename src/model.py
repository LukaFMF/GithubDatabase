class Language:
	def __init__(self,id,name):
		self.id = id
		self.langName = name


class User:
	def __init__(self,id,username,numPublicRepos,numFollowers,joinDate):
		self.id = id
		self.username = username
		self.numPublicRepos = numPublicRepos
		self.numFollowers = numFollowers
		self.joinDate = joinDate





class Repository:
	def __init__(self,id,title,description,createDate,numStars,ownerId,langId):
		self.id = id
		self.title = title
		self.description = description
		self.createDate = createDate
		self.numStars = numStars
		self.ownerId = ownerId
		self.langId = langId

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

