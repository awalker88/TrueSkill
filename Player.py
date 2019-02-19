"""Contains info about a single player."""
from random import randint
from datetime import datetime


class Player:

    def __init__(self, name, skill=0):
        self.playerID = name.replace(" ", "") + str(randint(10, 100))
        self.name = name
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.skill = skill
        self.dateCreated = datetime.now()

    def __str__(self):
        header = "Player Name: " + self.name + "  " + "ID: " + str(self.playerID)
        return header + "\n" + "Win Rate: " + str(self.get_win_rate()) + "%"  # TODO: add skill

    def get_win_rate(self):
        if self.wins + self.losses == 0:
            return 0.0
        else:
            return 100*self.wins / (self.wins + self.losses)

    def get_upsets(self, gameHistory):
        # todo: create
        pass
