#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def queryNoFetch(query):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()


def queryFetchOne(query):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchone()
    conn.commit()
    conn.close()

    return results


def queryFetchAll(query):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.commit()
    conn.close()

    return results


def deleteMatches():
    """Remove all the match records from the database."""
    queryNoFetch("DELETE FROM Matches;")


def deletePlayers():
    """Remove all the player records from the database."""
    queryNoFetch("DELETE FROM Players;")


def countPlayers():
    """Returns the number of players currently registered."""
    count = queryFetchOne("SELECT count(*) FROM Players;")[0]

    return count


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    # Check if name contains apostrophe
    name = name.replace("'", "''")

    queryNoFetch("INSERT INTO Players (name) VALUES ('%s');" % name)


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    return queryFetchAll("SELECT * FROM Standing;")


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    queryNoFetch("INSERT INTO Matches (winner, loser) VALUES (%s, %s)" %
                 (winner, loser if loser else 'null'))


def getPreviousByes():
    results = queryFetchAll("SELECT * FROM Bye")

    # Process results into list of id, instead of list of tuples of id
    return [id_tuple[0] for id_tuple in results]


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings()
    nextRound = []

    # If there is odd number of players, give 'bye' to a player highest in rank
    # who has yet to receive one.
    if len(standings) % 2 == 1:
        previous_byes = getPreviousByes()

        for player in standings:
            if player[0] not in previous_byes:
                nextRound.append((player[0], player[1], None, None))
                standings.remove(player)
                break

    for rank in range(0, len(standings), 2):
        pair = (standings[rank][0], standings[rank][1],
                standings[rank + 1][0], standings[rank + 1][1])
        nextRound.append(pair)

    return nextRound
