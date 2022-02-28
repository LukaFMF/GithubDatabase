from model import *
import bottle

@bottle.route("/<filename:re:.*\.css>","GET")
def getStylesheetFile(filename):
	return bottle.static_file(filename,root='style/')

@bottle.route("/","GET")
def mainPage():
	return bottle.template("main.html",users=User.getAllUsernames())

@bottle.route("/users","GET")
def allUsers():
	return bottle.template("main.html",users=User.getAllUsernames())

@bottle.route("/users/<username>","GET")
def specificUser(username):
	user = User.getUserInfo(username)
	if user == None:
		return bottle.template("userNotFound.html")

	userRepos = Repository.getAllReposOfOwner(user[1])
	commits = Commit.getAllCommitsByUsername(user[1])
	return bottle.template("user.html",user=user,repos = userRepos,commits = commits)

@bottle.route("/repos/<username>/<repoName>","GET")
def specificRepo(username,repoName):
	user = User.getUserInfo(username)
	if user == None:
		return bottle.template("userNotFound.html")

	repo = Repository.getRepoInfo(user[1],repoName)
	if repo == None:
		return bottle.template("repoNotFound.html")
	
	l = Language.getLang(repo[6])
	lang = "/" if l == None or l == (None,) else l[0]
	commits = Repository.getAllCommitsOfRepo(username,repoName)

	commiters = dict()
	for commit in commits:
		commiters[commit[3]] = None
	
	for commiter in commiters.keys():
		commiters[commiter] = User.getUsernameById(commiter)[0]
	
	i = 0
	while i < len(commits):
		currCommit = commits[i]
		commits[i] = (currCommit[0],currCommit[1],currCommit[2],commiters[currCommit[3]])
		i += 1 

	return bottle.template("repo.html",repoData = repo,owner=user[1],lang = lang,commits = commits)
	


bottle.run(reloader=True,debug=True)