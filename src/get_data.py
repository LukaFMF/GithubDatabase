import requests as r
import json
from secret import secretUsername,secretToken

authUsr = (secretUsername,secretToken,)

def removeCurly(str):
	inx = str.find("{")
	return str[:inx]

storedUsers = [1]
for user in storedUsers:
	data = r.get("https://api.github.com/users/LukaFMF",auth = authUsr).text
	sl = json.loads(data)
	print(sl)

	id = sl["id"]
	usename = sl["login"]
	num_public_repos = sl["public_repos"]
	followers = sl["followers"]
	join_date = sl["created_at"]

	# dodamo podatke v bazo


	# dodaj podatke o repozitorijih in commitih 
	reposSl = json.loads(r.get(sl["repos_url"],auth = authUsr).text)
	for repo in reposSl:
		if not repo["fork"]:
			# v bazo dodamo repozitorij
			commitsUrl = removeCurly(repo["commits_url"])
			commitsSl = json.loads(r.get(commitsUrl,auth = authUsr).text)
			print(commitsSl)




