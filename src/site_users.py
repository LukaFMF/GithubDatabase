import sqlite3 as dbapi
import os
from random import randint
from hashlib import pbkdf2_hmac,sha256

userConn = dbapi.connect("db/github_web_users.db")

def createTablesFromScriptInWebUsersDb(scriptPath):
	"""
	Creates tables in db/github_web_users.db from code 
	contained in scriptPath
	"""
	file = open(scriptPath)
	sqlCode = file.read()
	file.close()

	userConn.executescript(sqlCode)

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

def isUsernameFree(username):
	sqlCode = """
		SELECT *
		FROM site_user
		WHERE username = ?;
	"""

	return userConn.execute(sqlCode,(username,)).fetchone() == None

def validUsername(username):
	""" Username must be 3 - 15 chars long and contain only letters and numbers """
	usrLen = len(username)
	if usrLen < 3 or usrLen > 15:
		return False

	return username.isalnum()

def validPassword(password):
	""" Password must be 6 - 32 chars long and contain only letters and numbers """
	pwLen = len(password)
	if pwLen < 6 or pwLen > 32:
		return False

	return password.isalnum()
