"""Contains info about a single player."""

class Player:
    def __init__(self, playerID, name):
        self.playerID = playerID
        self.name = name
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.winRate = self.wins / (self.wins + self.losses)


    def print(self):
        header = "Player Name: " + self.name + "        " + "ID: " + self.playerID






