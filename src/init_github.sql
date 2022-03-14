CREATE TABLE user(
	id INTEGER PRIMARY KEY,
	username TEXT UNIQUE NOT NULL,
	num_public_repos INTEGER NOT NULL,
	num_followers INTEGER NOT NULL,
	join_date TIMESTAMP NOT NULL
);

CREATE TABLE language(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	"name" TEXT UNIQUE
);

CREATE TABLE repository(
	id INTEGER PRIMARY KEY,
	title TEXT NOT NULL,
	"description" TEXT,
	num_stars INTEGER NOT NULL,
	date_created TIMESTAMP NOT NULL,
	owner_id INTEGER REFERENCES user(id),
	lang_id INTEGER REFERENCES language(id)
);

CREATE TABLE "commit"(
	sha TEXT PRIMARY KEY,
	msg TEXT,
	date_created TIMESTAMP NOT NULL,
	"user_id" INTEGER NOT NULL REFERENCES user(id),
	repo_id INTEGER NOT NULL  REFERENCES repository(id)
);

CREATE TABLE issue(
	id INTEGER PRIMARY KEY,
	title TEXT NOT NULL,
	body TEXT,
	date_opened TIMESTAMP NOT NULL,
	"user_id" INTEGER NOT NULL REFERENCES user(id),
	repo_id INTEGER NOT NULL REFERENCES repository(id)
);
