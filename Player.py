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
        self.games_played = self.wins + self.losses + self.draws
        self.skill = Rating(skill)
        self.ranking_score = round(self.skill.mu - (3 * self.skill.sigma), 2)
        self.timestamp = datetime.now()
        self.mu_history = []
        self.sigma_history = []
        dt = datetime.now()
        formatted_month = '%02d' % dt.month
        self.skill_history = {f'{dt.year}-{formatted_month}-{dt.day}': self.ranking_score}
        self.current_winning_streak = 0
        self.current_losing_streak = 0
        self.longest_winning_streak = 0
        self.longest_losing_streak = 0
        self.points_scored = 0
        self.points_lost = 0
        if self.games_played == 0:
            self.average_ppg = 0
        else:
            self.average_ppg = round(self.points_scored / self.games_played, 2)
        if self.games_played == 0:
            self.average_point_margin = 0
        else:
            self.average_point_margin = round((self.points_scored - self.points_lost) / self.games_played, 2)

    def __str__(self):
        header = "Player Name: " + self.name + "  " + "ID: " + str(self.playerID)
        return f"\n{header} " \
            f"\nWin Rate: {self.get_win_rate()} " \
            f"\nSkill Mean: {round(self.skill.mu, 2)} Skill Variance: {round(self.skill.sigma, 2)}" \
            f"\nRanking Score: {self.ranking_score}\n"

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
        formatted_month = '%02d' % dt.month
        self.skill_history[f'{dt.year}-{formatted_month}-{dt.day}'] = self.ranking_score

    def update_after_game(self, players_score, opponents_score):
        self.games_played += 1
        self.points_scored += players_score
        self.points_lost += opponents_score
        self.average_ppg = round(self.points_scored / self.games_played, 2)
        self.average_point_margin = round((self.points_scored - self.points_lost) / self.games_played, 2)
        if players_score > opponents_score:
            self.wins += 1
            self.current_losing_streak = 0
            self.current_winning_streak += 1
            if self.current_winning_streak > self.longest_winning_streak:
                self.longest_winning_streak = self.current_winning_streak
        elif players_score < opponents_score:
            self.losses += 1
            self.current_winning_streak = 0
            self.current_losing_streak += 1
            if self.current_losing_streak > self.longest_losing_streak:
                self.longest_losing_streak = self.current_losing_streak
        else:
            self.draws += 1
