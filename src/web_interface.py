from model import *
from site_users import *
import bottle


def secretKeyGen():
	from random import choices
	return "".join(choices("0123456789abcdf",k = 64))

secretCkKey = secretKeyGen()

@bottle.route("/<filename:re:.*\.css>","GET")
def getStylesheetFile(filename):
	return bottle.static_file(filename,root='static/styles/')

@bottle.route("/<filename:re:(.*\.jpg)|(.*\.png)>","GET")
def getImageFile(filename):
	return bottle.static_file(filename,root='static/images/')

@bottle.route("/<filename:re:.*\.ttf>","GET")
def getFontFile(filename):
	return bottle.static_file(filename,root='static/fonts/')

@bottle.route("/<filename:re:.*\.js>","GET")
def getScriptFile(filename):
	return bottle.static_file(filename,root='static/scripts/')

@bottle.route("/","GET")
def main():
	username = bottle.request.get_cookie("account",secret=secretCkKey)
	return bottle.template("main.html",title = "baza podatkov",username = username)

@bottle.route("/users/","GET")
@bottle.route("/users","GET")
def users():
	return bottle.template("users.html",title = "uporabniki",users=User.getAllUsersInfo())

@bottle.route("/users/<username>/","GET")
@bottle.route("/users/<username>","GET")
def user(username): 
	user = User.getUserInfo(username)
	if user == None: # ali uporabnik sploh obstaja
		return bottle.template("userNotFound.html")

	userRepos = Repository.getAllReposOfOwner(user[1])
	userCommits = Commit.getAllCommitsByUsername(user[1])
	userIssues = Issue.getAllIssuesOfUser(user[1]) # added issues
	return bottle.template("user.html",title = user[1],user=user,repos = userRepos,commits = userCommits,issues = userIssues)

@bottle.route("/repos/","GET")
@bottle.route("/repos","GET")
def repos():
	return bottle.template("repos.html",title = "repozitoriji",repos=Repository.getAllReposInfo())

@bottle.route("/repos/<username>/<repoName>/","GET")
@bottle.route("/repos/<username>/<repoName>","GET")
def repo(username,repoName):
	user = User.getUserInfo(username)
	if user == None:
		return bottle.template("userNotFound.html")

	repo = Repository.getRepoInfo(username,repoName)
	if repo == None:
		return bottle.template("repoNotFound.html")
	
	commits = Commit.getAllCommitsOfRepo(username,repoName)
	issues = Issue.getAllIssuesOfRepo(username, repoName)
	return bottle.template("repo.html",title= f"{username}/{repoName}",repoData = repo,commits = commits,issues = issues)

@bottle.route("/languages/","GET")
@bottle.route("/languages","GET")
def languages():
	langsAndVolume = Language.GetLangUsage() # dobimo tabelo z 2 elementoma, jezik in količino commitov v njem.
	return bottle.template("languages.html", title="programski jeziki", languages = langsAndVolume)

@bottle.route("/login/","GET")
@bottle.route("/login","GET")
def login():
	username = bottle.request.get_cookie("account",secret=secretCkKey)
	invalid = bottle.request.query.get("invalidLogIn")
	return bottle.template("login.html",title="prijava",invalid = invalid,username=username)

@bottle.route("/login/","POST")
@bottle.route("/login","POST")
def loginForm():
	username = bottle.request.forms.get("username")
	password = bottle.request.forms.get("password")

	if attemptLogin(username,password):
		bottle.response.set_cookie("account",username,secret=secretCkKey)
		bottle.redirect("/")
	bottle.redirect("/login?invalidLogIn=1")

@bottle.route("/register/","GET")
@bottle.route("/register","GET")
def register():
	return bottle.template("register.html",title= "registracija")

@bottle.route("/register/","POST")
@bottle.route("/register","POST")
def registerForm():
	pass


bottle.TEMPLATE_PATH.insert(0,'static/views')
bottle.run(reloader=True,debug=True)
conn.close()