"""Contains info about a single player."""
from random import randint
from datetime import datetime


class Player:

    def __init__(self, name, playerID="", wins=0, losses=0, draws=0, skill=0):
        if playerID == "":
            self.playerID = name.replace(" ", "") + str(randint(10, 100))  # playerID is name plus 2 random digits
        else:
            self.playerID = playerID
        self.name = name
        self.wins = wins
        self.losses = losses
        self.draws = draws
        self.skill = skill
        self.dateCreated = datetime.now()

    def __str__(self):
        header = "Player Name: " + self.name + "  " + "ID: " + str(self.playerID)
        return header + "\n" + "Win Rate: " + str(self.get_win_rate()) + "%"  # TODO: add skill

        # TODO: add simple version of print

    def get_win_rate(self):
        if self.wins + self.losses == 0:
            return 0.0
        else:
            return 100*self.wins / (self.wins + self.losses)

    def get_upsets(self, gameHistory):
        # todo: create
        pass
