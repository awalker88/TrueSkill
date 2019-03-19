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
        """
        formatted string representation of the game
        :return: string
        Ex. 'andrew1 (21) vs erin1 (14)
             Winner(s): andrew1
             Date: 2019-03-19 14:21:12
             Team one win prob: 85.46%
        """
        names = f"{self.get_team_name(1)} ({self.team_one_score} vs. {self.get_team_name(2)} ({self.team_two_score})"

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
        """
        Creates gameID based on players names, score, and current timestamp
        :return: None
        """
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
        """
        Calculates the pre-match probability of team one winning against team two
        :return: odds of team one as a decimal between 0 and 1, rounded to ten thousandth's place
        """
        delta_mu = sum(r.skill.mu for r in self.team_one) - sum(r.skill.mu for r in self.team_two)
        sum_sigma = sum(r.skill.sigma ** 2 for r in itertools.chain(self.team_one, self.team_two))
        size = len(self.team_one) + len(self.team_two)
        denom = math.sqrt(size * (ts.BETA * ts.BETA) + sum_sigma)
        env = ts.global_env()
        return round(env.cdf(delta_mu / denom), 4)

    def get_team_name(self, team_num):
        """
        Formatted team name of either team one or two
        :param team_num: 1 or 2, depending on which team's names you want
        :return: string of team members playerID's (ex. ['andrew1', 'erin2'] -> 'andrew1, erin2'
        """
        name = ""
        if team_num == 1:
            for player in self.team_one:
                name += player.playerID + ", "
            name = name[:-2]  # drops last comma
            return name
        elif team_num == 2:
            for player in self.team_two:
                name += player.playerID + ", "
            name = name[:-2]  # drops last comma
            return name
        else:
            print("team_num must be either 1 or 2")
            raise ValueError




