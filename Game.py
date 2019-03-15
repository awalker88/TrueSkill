from datetime import datetime
import itertools
import math
import trueskill as ts


class Game:

    def __init__(self, team_one, team_two, team_one_score, team_two_score, season, timestamp, notes):
        self.team_one = team_one  # teams should be lists of playerIDs
        self.team_two = team_two
        self.team_one_score = team_one_score
        self.team_two_score = team_two_score
        self.season = season
        self.notes = notes
        if team_one_score > team_two_score:
            self.winner = team_one
        elif team_one_score < team_two_score:
            self.winner = team_two
        else:
            self.winner = None
        if timestamp is None:
            self.timestamp = datetime.now()
        else:
            self.timestamp = timestamp
        self.gameID = self.create_game_id()
        self.t1_win_prob = round(self.win_probability_team_one() * 100, 2)
        self.t2_win_prob = 100 - self.t1_win_prob

    def __str__(self):
        names = ""

        for player in self.team_one:
            names += player.name + ", "
        names = names[:-2]  # drops last comma
        names += f" ({self.team_one_score}) vs. "

        for player in self.team_two:
            names += player.name + ", "
        names = names[:-2]  # drops last comma
        names += f" ({self.team_two_score})"

        outcome = "Winner(s): "
        for player in self.winner:
            outcome += player.name + ", "
        outcome = outcome[:-2]  # drops last comma

        time = "Date: " + str(self.timestamp)

        win_prob = f"Team one win prob: {self.t1_win_prob}"

        to_return = names + "\n" + outcome + "\n" + time + "\n" + win_prob + "\n"
        if self.notes != "":
            to_return += "Notes:" + self.notes + "\n"

        return to_return

    def create_game_id(self):
        """ Creates gameID based on players names, score, and current timestamp """
        now = datetime.now()
        game_details = ""
        for player in self.team_one:
            game_details += player.name[0].lower()
        game_details += str(self.team_one_score)
        for player in self.team_two:
            game_details += player.name[0].lower()
        game_details += str(self.team_two_score)
        time_details = now.strftime("%Y%m%d%H%M%S")
        return game_details + time_details

    def win_probability_team_one(self):
        delta_mu = sum(r.skill.mu for r in self.team_one) - sum(r.skill.mu for r in self.team_two)
        sum_sigma = sum(r.skill.sigma ** 2 for r in itertools.chain(self.team_one, self.team_two))
        size = len(self.team_one) + len(self.team_two)
        denom = math.sqrt(size * (ts.BETA * ts.BETA) + sum_sigma)
        env = ts.global_env()
        return round(env.cdf(delta_mu / denom), 4)

    def get_team_name(self, team):
        name = ""
        for player in team:
            name += player.playerID + ", "
        name = name[:-2]  # drops last comma
        return name



