from model import *
from site_users import *
import bottle


def secretKeyGen():
	from random import choices
	return "".join(choices("0123456789abcdf",k = 64))

secretCkKey = secretKeyGen()

def getAccountCookie():
	return bottle.request.get_cookie("account",secret=secretCkKey)

@bottle.route("/<filename:re:.*\.css>","GET")
def getStylesheetFile(filename):
	return bottle.static_file(filename,root='static/styles/')

@bottle.route("/<filename:re:(.*\.jpg)|(.*\.png)|(.*\.gif)>","GET")
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
	users = User.getAllUsernames()
	repos = Repository.getAllReposAndOwners()
	return bottle.template("main.html",title = "baza podatkov",users = users,repos = repos,account = getAccountCookie())

@bottle.route("/search/","GET")
@bottle.route("/search","GET")
def search():
	value = bottle.request.query.get("search")
	category = bottle.request.query.get("category")
	if category == "users":
		username = value 
		user = User.getUserInfo(username)
		if user == None:
			return bottle.template("userNotFound.html")

		bottle.redirect(f"/users/{username}")
	elif category == "repos":
		split = value.split("/")
		if len(split) != 2:
			return bottle.template("repoNotFound.html")

		username,repoName = split
		user = User.getUserInfo(username)
		if user == None:
			return bottle.template("userNotFound.html")

		repo = Repository.getRepoInfo(username,repoName)
		if repo == None:
			return bottle.template("repoNotFound.html")

		bottle.redirect(f"/repos/{username}/{repoName}")
	bottle.redirect("/")
		

@bottle.route("/users/","GET")
@bottle.route("/users","GET")
def users():
	return bottle.template("users.html",title = "uporabniki",users=User.getAllUsersInfo(),account = getAccountCookie())

@bottle.route("/users/<username>/","GET")
@bottle.route("/users/<username>","GET")
def user(username): 
	user = User.getUserInfo(username)
	if user == None: # ali uporabnik sploh obstaja
		return bottle.redirect(f"/userNotFound?username={username}")

	userRepos = Repository.getAllReposOfOwner(user[1])
	userCommits = Commit.getAllCommitsByUsername(user[1])
	userIssues = Issue.getAllIssuesOfUser(user[1]) # added issues
	favLang = Language.getFavoriteLangOfUser(username)
	return bottle.template("user.html",title = user[1],user=user,favLang = favLang,repos = userRepos,
	commits = userCommits,issues = userIssues,account = getAccountCookie())

@bottle.route("/repos/","GET")
@bottle.route("/repos","GET")
def repos():
	return bottle.template("repos.html",title = "repozitoriji",repos=Repository.getAllReposInfo(),account = getAccountCookie())

@bottle.route("/repos/<username>/<repoName>/","GET")
@bottle.route("/repos/<username>/<repoName>","GET")
def repo(username,repoName):
	user = User.getUserInfo(username)
	if user == None:
		return bottle.redirect(f"/userNotFound?username={username}")

	repo = Repository.getRepoInfo(username,repoName)
	if repo == None:
		return bottle.redirect(f"/repoNotFound?username={username}&repoName={repoName}")
	
	commits = Commit.getAllCommitsOfRepo(username,repoName)
	issues = Issue.getAllIssuesOfRepo(username, repoName)
	return bottle.template("repo.html",title= f"{username}/{repoName}",repoData = repo,commits = commits,
	issues = issues,account = getAccountCookie())

@bottle.route("/langs/","GET")
@bottle.route("/langs","GET")
def languages():
	langData = Language.getLangUsage() # dobimo tabelo z 2 elementoma, jezik in količino commitov v njem.
	return bottle.template("languages.html", title="programski jeziki", langData = langData,account = getAccountCookie())

@bottle.route("/login/","GET")
@bottle.route("/login","GET")
def login():
	accCookie = getAccountCookie()
	if accCookie != None: # if logged in you cant do it again
		bottle.redirect("/")

	username = bottle.request.query.get("username")
	failedLogin = bottle.request.query.get("loginFailed")
	return bottle.template("login.html",title="prijava",username = username,failedLogin = failedLogin,account = accCookie)

@bottle.route("/login/","POST")
@bottle.route("/login","POST")
def loginForm():
	username = bottle.request.forms.get("username")
	password = bottle.request.forms.get("password")

	if attemptLogin(username,password):
		bottle.response.set_cookie("account",username,secret=secretCkKey)
		bottle.redirect("/")
	bottle.redirect(f"/login?username={username}&loginFailed=0")

@bottle.route("/logout/","POST")
@bottle.route("/logout","POST")
def logout():
	bottle.response.delete_cookie("account")
	bottle.redirect("/")

@bottle.route("/register/","GET")
@bottle.route("/register","GET")
def register():
	accCookie = getAccountCookie()
	if accCookie != None: # if logged in you cant register
		bottle.redirect("/")

	username = bottle.request.query.get("username")
	failedRegistration = bottle.request.query.get("registrationFailed")
	return bottle.template("register.html",title= "registracija",username = username,
	failedRegistration = failedRegistration,account = accCookie)

@bottle.route("/register/","POST")
@bottle.route("/register","POST")
def registerForm():
	username = bottle.request.forms.get("username")
	password = bottle.request.forms.get("password")
	cPassword = bottle.request.forms.get("conf_password")

	if not validUsername(username): # username is invaild(len or illegal chars)
		bottle.redirect("/register?registrationFailed=0")
	elif not isUsernameFree(username): # username is already taken
		bottle.redirect("/register?registrationFailed=1")
	elif not validPassword(password): # password is invaild(len or illegal chars)
		bottle.redirect(f"/register?username={username}&registrationFailed=2")
	elif password != cPassword: # confirmation password doesnt match
		bottle.redirect(f"/register?username={username}&registrationFailed=3")

	# after validation, we create a new user
	createNewUser(username,password,0) 

	if attemptLogin(username,password):
		bottle.response.set_cookie("account",username,secret=secretCkKey)
		bottle.redirect("/")
	bottle.redirect("/login?loginFailed=0")

@bottle.route("/userNotFound/","GET")
@bottle.route("/userNotFound","GET")
def userNotFound():
	username = bottle.request.query.get("username")
	return bottle.template("userNotFound.html",title = f"uporabnik ne obstaja",username = username,account=getAccountCookie())

@bottle.route("/repoNotFound/","GET")
@bottle.route("/repoNotFound","GET")
def repoNotFound():
	username = bottle.request.query.get("username")
	repoName = bottle.request.query.get("repoName")

	return bottle.template("repoNotFound.html",title = f"repozitorij ne obstaja",username = username,repoName = repoName,
	account=getAccountCookie())

bottle.TEMPLATE_PATH.insert(0,'static/views')
bottle.run(reloader=True,debug=True)
userConn.close()
conn.close()