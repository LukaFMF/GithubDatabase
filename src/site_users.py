import sqlite3 as dbapi
import os
from random import randint
from hashlib import pbkdf2_hmac,sha256

alreadyExists = os.path.exists("github_users.db")

userConn = dbapi.connect("github_users.db")

if not alreadyExists:
	file = open("init_site_users.sql")
	sqlCode = file.read()

	userConn.executescript(sqlCode)
	
	file.close()


def createNewUser(username,password,admin):
	salt = os.urandom(64)
	iters = 64000 + randint(0,1000)
	hashedPw = pbkdf2_hmac("sha256",bytes(password,"ascii"),salt,iters) 
	sqlCode = """
		INSERT INTO site_user(username,"password",salt,num_iters,"admin")
		VALUES (?,?,?,?,?);
	"""
	
	userConn.execute(sqlCode,(username,hashedPw,salt,iters,admin))
	userConn.commit()

def attemptLogin(username,password):
	# get user info
	sqlCode = """
		SELECT salt,num_iters
		FROM site_user
		WHERE username = ?;
	"""
	userPwInfo = userConn.execute(sqlCode,(username,)).fetchone()
	if userPwInfo == None:
		return False
	
	salt,iters = userPwInfo
	hashedPw = pbkdf2_hmac("sha256",bytes(password,"ascii"),salt,iters)

	sqlCode = """
		SELECT username
		FROM site_user
		WHERE username = ? AND password = ?;
	"""
	
	return userConn.execute(sqlCode,(username,hashedPw)).fetchone() != None

def checkIfUsernameIsAvailable(username):
	sqlCode = """
		SELECT *
		FROM site_user
		WHERE username = ?;
	"""

	return userConn.execute(sqlCode,(username,)).fetchone() == None 

# createNewUser("luka","abcd",1)
userConn.commit()