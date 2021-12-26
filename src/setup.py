import sqlite3 as dbapi
import os

jeZeUstvarjena = os.path.exists("github.db")

conn = dbapi.connect("github.db")

if not jeZeUstvarjena:
	file = open("init.sql")
	sqlCode = "".join(file.readlines())

	conn.executescript(sqlCode)

	file.close()

conn.close()