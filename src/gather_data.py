import requests as r
import json
import csv
import os

import functions as f
from model import *

# there should be a file named "secret.py",
# that contains username and token, which 
# will be used to access github API
from secret import secretUsername,secretToken
authSecret = (secretUsername,secretToken)

# vvv Helpful functions vvv
def makeGithubRequest(query):
	""" 
	Uses "https://api.github.com" as base and 
	appends query to make a request. Returns status 
	code(200 - ok, 404 - not found,...) and response 
	contents as dict (created from json)
	"""

	apiRootUrl = "https://api.github.com"
	header = {"accept": "application/vnd.github.v3+json"}
	authResponse = r.get(f"{apiRootUrl}{query}",
	headers = header,auth = authSecret)

	jsonContent = json.loads(authResponse.text)
	return authResponse.status_code,jsonContent

def mostRecentActionDate(searchRepoId,existingActions):
	"""
	Returns the date of the most recent action(commit or issue)
	in repository identified by searchRepoId
	"""
	
	mostRecentDate = None
	for actionId,(repoId,actionDate) in existingActions.items():
		if repoId == searchRepoId:
			if mostRecentDate == None or actionDate > mostRecentDate:
				mostRecentDate = actionDate

	return mostRecentDate
# ^^^ Helpful functions ^^^

code,authData = makeGithubRequest("/user")
if code != 200: # auth failure
	print("Invalid auth tonken! Exiting...")
	exit(-1)

print(f"Authenticated as {authData['login']}!")
wantedUsernames = ["matijapretnar","jaanos","LukaFMF","anzeozimek","lapajnea",
"Martina333","HanaL123","anaberdnik","titoo1234","Argonfmf","benisa21"]


redownloadData = f.getInputYN("Redownload all data?")

storageFilenames = ("languages.csv","users.csv","repositories.csv","commits.csv","issues.csv")

# if some files are missing, we recreate them
for filename in storageFilenames:
	if not os.path.exists(f"data/{filename}"):
		# create empty file or empty it if it exists
		f.emptyFile(f"data/{filename}")

encounteredLangs = dict()
encounteredUsers = set()
encounteredRepos = set()
encounteredCommits = dict() 
encounteredIssues = dict()

if not redownloadData:
	# create a record of data, that has already been transferred
	encounteredLangs = Language.cacheExisting(storageFilenames[0],csvDialectName)
	encounteredUsers = User.cacheExisting(storageFilenames[1],csvDialectName)
	encounteredRepos = Repository.cacheExisting(storageFilenames[2],csvDialectName)
	encounteredCommits = Commit.cacheExisting(storageFilenames[3],csvDialectName)
	encounteredIssues = Issue.cacheExisting(storageFilenames[4],csvDialectName)

# language id is the only id we dont get from api so we make our own
currLangId = 1 if len(encounteredLangs) == 0 else (
max(encounteredLangs.values()) + 1)

langs = []
users = []
repos = []
commits = []
issues = []

for wantedUsername in wantedUsernames:
	print(f"Retrieving user data for {wantedUsername}... ",end="")
	code,wantedUserData = makeGithubRequest(f"/users/{wantedUsername}")

	if code != 200:
		print("Failed! Skipping...")
		continue
	print("OK")
	
	wantedUser = User.makeFrom(wantedUserData)

	if wantedUser.id not in encounteredUsers:
		encounteredUsers.add(wantedUser.id)
		users.append(wantedUser)
	
	print(f"\tRetrieving repositories for user {wantedUsername}... ",end="",flush = True)
	i = 1
	userReposData = []
	while True:
		code,pageUserReposData = makeGithubRequest(
		f"/users/{wantedUsername}/repos?sort=created&directoin=asc&page={i}&per_page=100")

		if code != 200:
			print("Failed! Skipping...")
			break
		elif len(pageUserReposData) == 0: # all data was retrived
			print("OK")
			break

		# only add repos that are not forks
		userReposData.extend(filter(lambda repoData: not repoData["fork"],
		pageUserReposData))
		i += 1

	for repoData in userReposData:
		langName = repoData["language"]

		if langName not in encounteredLangs:
			encounteredLangs[langName] = currLangId
			langs.append(Language(currLangId,langName))
			currLangId += 1

		repo = Repository.makeFrom(repoData,wantedUser.id,
		encounteredLangs[langName])

		if repo.id not in encounteredRepos:
			encounteredRepos.add(repo.id)
			repos.append(repo)

		print(f"\t\tRetrieving commits of {wantedUsername}/{repo.title}... ",end="",flush = True)
		i = 1
		repoCommitsData = []
		recentCommitDate = mostRecentActionDate(repo.id,encounteredCommits)
		commitsSince = f"since={recentCommitDate}" if recentCommitDate != None else "" 
		while True:
			code,pageRepoCommitsData = makeGithubRequest(
			f"/repos/{wantedUsername}/{repo.title}/commits?{commitsSince}&page={i}&per_page=100")

			if code != 200:
				print("Failed! Skipping...")
				break
			elif len(pageRepoCommitsData) == 0: # all data was retrived
				print("OK")
				break

			# filter commits if author is missing
			repoCommitsData.extend(filter(lambda commitData: commitData["author"] != None,
			pageRepoCommitsData)) 
			i += 1

		for commitData in repoCommitsData:
			print(f"\t\t\tProcessing commit {commitData['sha']}... ",end="")
			commiterId = commitData["author"]["id"]

			if commiterId not in encounteredUsers:
				code,commiterData = makeGithubRequest(
				f"/users/{commitData['author']['login']}")

				if code != 200:
					print("Failed! Skipping...")
					break

				commiter = User.makeFrom(commiterData)

				encounteredUsers.add(commiter.id)
				users.append(commiter)

			commit = Commit.makeFrom(commitData,commiterId,repo.id)

			if commit.sha not in encounteredCommits:
				encounteredCommits[commit.sha] = (repo.id,commit.timestamp)
				commits.append(commit)
			print("OK")

		print(f"\t\tRetrieving issues of {wantedUsername}/{repo.title}... ",end="",flush = True)
		i = 1
		repoIssuesData = []
		recentIssueDate = mostRecentActionDate(repo.id,encounteredIssues)
		issuesSince = f"since={recentIssueDate}" if recentIssueDate != None else "" 
		while True:
			code,pageRepoIssuesData = makeGithubRequest(
			f"/repos/{wantedUsername}/{repo.title}/issues?{issuesSince}&state=all&page={i}&per_page=100")

			if code != 200:
				print("Failed! Skipping...")
				break
			elif len(pageRepoIssuesData) == 0: # all data was retrived
				print("OK")
				break

			repoIssuesData.extend(pageRepoIssuesData)
			i += 1

		for issueData in repoIssuesData:
			print(f"\t\t\tProcessing issue {issueData['id']}... ",end="")
			issuerId = issueData["user"]["id"]

			if issuerId not in encounteredUsers:
				code,issuerData = makeGithubRequest(
				f"/users/{issueData['user']['login']}")

				if code != 200:
					print("Failed! Skipping...")
					break

				issuer = User.makeFrom(issuerData)

				encounteredUsers.add(issuer.id)
				users.append(issuer)

			issue = Issue.makeFrom(issueData,issuerId,repo.id)

			if issue.id not in encounteredIssues:
				encounteredIssues[issue.id] = (repo.id,issue.creationTimestamp)
				issues.append(issue)
			print("OK")

fileMode = "w"
if not redownloadData:
	fileMode = "a"

# collect all data in one place
allData = (langs,users,repos,commits,issues)
for i in range(len(allData)):
	print(f"Writing data to data/{storageFilenames[i]}... ",end="")
	f.writeCsvData(storageFilenames[i],allData[i],fileMode)
	print("OK")

