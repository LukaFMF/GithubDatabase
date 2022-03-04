from model import *
import bottle

@bottle.route("/<filename:re:.*\.css>","GET")
def getStylesheetFile(filename):
	return bottle.static_file(filename,root='static/styles/')

@bottle.route("/<filename:re:(.*\.jpg)|(.*\.png)>","GET")
def getImageFile(filename):
	return bottle.static_file(filename,root='static/images/')

@bottle.route("/<filename:re:.*\.ttf>","GET")
def getImageFile(filename):
	return bottle.static_file(filename,root='static/fonts/')

@bottle.route("/","GET")
def main():
	return bottle.template("main.html",title = "baza podatkov",users=User.getAllUsernames())

@bottle.route("/users/","GET")
@bottle.route("/users","GET")
def users():
	return bottle.template("users.html",title = "uporabniki",users=User.getAllUsernames())

@bottle.route("/users/<username>/","GET")
@bottle.route("/users/<username>","GET")
def user(username):
	user = User.getUserInfo(username)
	if user == None: # ali uporabnik sploh obstaja
		return bottle.template("userNotFound.html")

	userRepos = Repository.getAllReposOfOwner(user[1])
	userCommits = Commit.getAllCommitsByUsername(user[1])
	return bottle.template("user.html",title = user[1],user=user,repos = userRepos,commits = userCommits)

@bottle.route("/repos/","GET")
@bottle.route("/repos","GET")
def repos():
	return bottle.template("repos.html",title = "repozitoriji",repos=Repository.getInfoAllRepos())

@bottle.route("/repos/<username>/<repoName>/","GET")
@bottle.route("/repos/<username>/<repoName>","GET")
def repo(username,repoName):
	user = User.getUserInfo(username)
	if user == None:
		return bottle.template("userNotFound.html")

	repo = Repository.getRepoInfo(username,repoName)
	if repo == None:
		return bottle.template("repoNotFound.html")
	
	commits = Repository.getAllCommitsOfRepo(username,repoName)
	return bottle.template("repo.html",title= f"{username}/{repoName}",repoData = repo,commits = commits)
	

bottle.TEMPLATE_PATH.insert(0,'static/views')
bottle.run(reloader=True,debug=True)
conn.close()