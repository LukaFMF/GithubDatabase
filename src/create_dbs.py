import functions as f

# Main db
print("Creating db/github.db:")
f.emptyFile("db/github.db")

from model import *

print("\tCreating tables...",end = "",flush = True)
createTablesFromScriptInMainDb("static/sql_scripts/create_github_db.sql")
print("OK")

print("\tReading data...",end = "",flush = True)
# read data from files
languages = f.readCsvData("languages.csv",Language)
users = f.readCsvData("users.csv",User)
repositories = f.readCsvData("repositories.csv",Repository)
commits = f.readCsvData("commits.csv",Commit)
issues = f.readCsvData("issues.csv",Issue)
print("OK")

print("\tInserting data...",end = "",flush = True)
# write data to database
for lang in languages:
	lang.insert()

for user in users:
	user.insert()

for repo in repositories:
	repo.insert()

for commit in commits:
	commit.insert()

for issue in issues:
	issue.insert()
print("OK")

print("\tCommiting changes...",end = "",flush = True)
# commit changes and close connection to db
conn.commit()
conn.close()
print("OK")

print("")

# Site users db
print("Creating db/github_web_users.db:")
f.emptyFile("db/github_web_users.db")

from site_users import *

print("\tCreating table...",end = "",flush = True)
createTablesFromScriptInWebUsersDb("static/sql_scripts/create_web_users_db.sql")
print("OK")

print("\tInserting users...",end = "",flush = True)
# add admin user
createNewUser("luka","abcd1234",True)
print("OK")

print("\tCommiting changes...",end = "",flush = True)
# commit changes and close connection to db
userConn.commit()
userConn.close()
print("OK")