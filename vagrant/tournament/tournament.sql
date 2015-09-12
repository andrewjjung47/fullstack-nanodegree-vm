-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

\c tournament;

CREATE TABLE Players (
                      id SERIAL PRIMARY KEY,
                      name TEXT
);

CREATE TABLE Matches (
                      win SERIAL references Players(id),
                      loss SERIAL references Players(id)
);


