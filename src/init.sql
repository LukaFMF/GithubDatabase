CREATE TABLE oseba(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	uporabnisko_ime TEXT UNIQUE NOT NULL
);

CREATE TABLE programski_jezik(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	ime TEXT UNIQUE
);

CREATE TABLE repozitorij(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	naslov TEXT NOT NULL,
	jezik_id INTEGER REFERENCES programski_jezik(id)
);

CREATE TABLE prispevek(
	sha TEXT UNIQUE PRIMARY KEY,
	oseba_id INTEGER NOT NULL REFERENCES oseba(id),
	repo_id INTEGER NOT NULL  REFERENCES repozitorij(id),
	datum TIMESTAMP NOT NULL,
	sporocilo TEXT
);

CREATE TABLE vprasanje(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	oseba_id INTEGER NOT NULL REFERENCES oseba(id),
	repo_id INTEGER NOT NULL REFERENCES repozitorij(id),
	datum TIMESTAMP NOT NULL,
	besedilo TEXT
);