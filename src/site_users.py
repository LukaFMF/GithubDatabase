import sqlite3 as dbapi
import os
from hashlib import pbkdf2_hmac,sha256

alreadyExists = os.path.exists("github_users.db")

userConn = dbapi.connect("github_users.db")

if not alreadyExists:
	file = open("init_site_users.sql")
	sqlCode = file.read()

	userConn.executescript(sqlCode)
	
	file.close()

salt = b'\xdd\x99\x11\x1e.\xd6\xc5t\xe9\x1atGT\x8e`\xfd\xa4\x03ks\x19K\xbaK\x881F>\xe0\x1dF\xda'
iters = 50000
def createNewUser(username,password,admin):
	hashedPw = pbkdf2_hmac("sha256",bytes(password,"ascii"),salt,iters) 
	sqlCode = """
		INSERT INTO site_user(username,password,admin)
		VALUES (?,?,?);
	"""
	
	userConn.execute(sqlCode,(username,hashedPw,admin))
	userConn.commit()

def attemptLogin(username,password):
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

userConn.commit()