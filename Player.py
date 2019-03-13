"""Contains info about a single player."""
from random import randint
from datetime import datetime
from trueskill import Rating


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
        self.ranking_score = round(self.skill.mu - (3 * self.skill.sigma), 2)
        self.timestamp = datetime.now()
        self.mu_history = []
        self.sigma_history = []
        dt = datetime.now()
        self.skill_history = {f'{dt.year}-{dt.month}-{dt.day}': self.ranking_score}

    def __str__(self):
        header = "Player Name: " + self.name + "  " + "ID: " + str(self.playerID)
        return f"\n{header} " \
            f"\nWin Rate: {self.get_win_rate()} " \
            f"\nSkill Mean: {round(self.skill.mu, 2)} Skill Variance: {round(self.skill.sigma, 2)}" \
            f"\nRanking Score: {self.ranking_score}\n"

        # TODO: add 'simple' version of print

    def get_win_rate(self):
        if self.wins + self.losses == 0:
            return "No games played"
        else:
            return str(round(100*self.wins / (self.wins + self.losses), 2)) + "%"

    def update_skill(self, new_skill: Rating):
        self.mu_history.append(self.skill.mu)
        self.sigma_history.append(self.skill.sigma)
        self.skill = Rating(new_skill)
        self.ranking_score = round(self.skill.mu - (3 * self.skill.sigma), 2)
        dt = datetime.now()
        self.skill_history[f'{dt.year}-{dt.month}-{dt.day}'] = self.ranking_score

    def get_upsets(self, game_history):
        # todo: create
        for game in game_history:
            which_team = None
            if self in game_history[game].team_one:
                which_team = 1
            elif self in game_history[game].team_two:
                which_team = 2
            print(which_team)

        # thoughts: where is the playerIDs stored in game history, how to recognize whether member in game
        # need to determine what team they were in to get predicted winner (right now stored as string)
        # print top 5? all? ranked by biggest upset? only victories? Top 3 upsets
