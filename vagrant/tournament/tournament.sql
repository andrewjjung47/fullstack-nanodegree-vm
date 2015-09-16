-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE tournament;

CREATE DATABASE tournament;

\c tournament;

CREATE TABLE Players (
                      id SERIAL PRIMARY KEY,
                      name TEXT
);

CREATE TABLE Matches (
                      id SERIAL PRIMARY KEY,
                      winner INTEGER references Players(id),
                      loser INTEGER references Players(id)
);

CREATE VIEW Wins AS (
                      SELECT Players.id, name, count(winner) AS wins
                      FROM Players LEFT JOIN Matches
                      ON Players.id = Matches.winner
                      GROUP BY Players.id
);

CREATE VIEW Losses AS (
                       SELECT Players.id, name, count(loser) AS losses
                       FROM Players LEFT JOIN Matches
                       ON Players.id = Matches.loser
                       GROUP BY Players.id
);

CREATE VIEW Standing AS (
                         SELECT Wins.id, Wins.name, wins, (wins + losses) AS matches
                         FROM Wins JOIN Losses
                         ON Wins.id = Losses.id
                         ORDER BY wins DESC
);

CREATE VIEW Bye As (
                    SELECT winner
                    FROM Matches
                    WHERE loser IS NULL
);
