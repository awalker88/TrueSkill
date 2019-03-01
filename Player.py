"""Contains info about a single player."""
from random import randint
from datetime import datetime
from trueskill import Rating, MU


class Player:

    def __init__(self, name, skill, playerID="", wins=0, losses=0, draws=0):
        if playerID == "":
            self.playerID = name.replace(" ", "") + str(randint(10, 100))  # playerID is name plus 2 random digits
        else:
            self.playerID = playerID
        self.name = name
        self.wins = wins
        self.losses = losses
        self.draws = draws
        self.skill = Rating(skill)
        self.rankingScore = round(self.skill.mu - (3 * self.skill.sigma), 2)
        self.dateCreated = datetime.now()
        self.muHistory = []
        self.sigmaHistory = []

    def __str__(self):
        header = "Player Name: " + self.name + "  " + "ID: " + str(self.playerID)
        return f"\n{header} " \
            f"\nWin Rate: {self.get_win_rate()} " \
            f"\nSkill Mean: {round(self.skill.mu,2)} Skill Variance: {round(self.skill.sigma,2)}" \
            f"\nRanking Score: {self.rankingScore}\n"

        # TODO: add 'simple' version of print

    def get_win_rate(self):
        if self.wins + self.losses == 0:
            return "No games played"
        else:
            return str(100*self.wins / (self.wins + self.losses)) + "%"

    def update_skill(self, newSkill: Rating):
        self.muHistory.append(self.skill.mu)
        self.sigmaHistory.append(self.skill.sigma)
        self.skill = Rating(newSkill)
        self.rankingScore = round(self.skill.mu - (3 * self.skill.sigma), 2)

    def get_upsets(self, gameHistory):
        # todo: create
        for game in gameHistory:
            whichTeam = None
            if self in gameHistory[game].teamOne:
                whichTeam = 1
            elif self in gameHistory[game].teamTwo:
                whichTeam = 2
            print(whichTeam)

        # thoughts: where is the playerIDs stored in game history, how to recognize whether member in game
        # need to determine what team they were in to get predicted winner (right now stored as string)
        # print top 5? all? ranked by biggest upset? only victories? Top 3 upsets
