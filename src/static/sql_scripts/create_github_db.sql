CREATE TABLE language(
	id INTEGER PRIMARY KEY,
	name TEXT UNIQUE
);

CREATE TABLE user(
	id INTEGER PRIMARY KEY,
	username TEXT UNIQUE NOT NULL,
	num_followers INTEGER NOT NULL,
	join_date DATE NOT NULL
);

CREATE TABLE repository(
	id INTEGER PRIMARY KEY,
	title TEXT NOT NULL,
	description TEXT,
	num_stars INTEGER NOT NULL,
	creation_date DATE NOT NULL,
	owner_id INTEGER REFERENCES user(id),
	lang_id INTEGER REFERENCES language(id)
);

CREATE TABLE "commit"( -- commit is a keyword in sqlite3
	sha TEXT PRIMARY KEY,
	msg TEXT,
	"timestamp" TIMESTAMP NOT NULL,
	commiter_id INTEGER NOT NULL REFERENCES user(id),
	repo_id INTEGER NOT NULL REFERENCES repository(id)
);

CREATE TABLE issue(
	id INTEGER PRIMARY KEY,
	title TEXT NOT NULL,
	body TEXT,
	"state" INTEGER NOT NULL CHECK("state" IN (0,1)), -- 1 = open,0 = closed
	num_comments INTEGER NOT NULL,
	creation_timestamp TIMESTAMP NOT NULL,
	issuer_id INTEGER NOT NULL REFERENCES user(id),
	repo_id INTEGER NOT NULL REFERENCES repository(id)
);
