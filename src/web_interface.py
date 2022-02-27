from model import *
import bottle

@bottle.route("/","GET")
def mainPage():
	return bottle.template("main.html",users=User.getAllUsernames())


bottle.run(reloader=True,debug=True)