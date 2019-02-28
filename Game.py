from datetime import datetime
import itertools
import math
import trueskill as ts


class Game:

    def __init__(self, teamOne: list, teamTwo: list, teamOneScore: int, teamTwoScore: int, season: int, notes: str = ""):
        self.teamOne = teamOne  # teams should be lists of playerIDs
        self.teamTwo = teamTwo
        self.teamOneScore = teamOneScore
        self.teamTwoScore = teamTwoScore
        self.season = season
        self.notes = notes
        if teamOneScore > teamTwoScore:
            self.winner = teamOne
        elif teamOneScore < teamTwoScore:
            self.winner = teamTwo
        else:
            self.winner = None
        self.date = datetime.now()
        self.gameID = self.create_game_id()
        self.t1WinProb = self.win_probability_team_one() * 100

    def __str__(self):
        names = ""

        for player in self.teamOne:
            names += player.name + ", "
        names = names[:-2]  # drops last comma
        names += f" ({self.teamOneScore}) vs. "

        for player in self.teamTwo:
            names += player.name + ", "
        names = names[:-2]  # drops last comma
        names += f" ({self.teamTwoScore})"

        outcome = "Winner(s): "
        for player in self.winner:
            outcome += player.name + ", "
        outcome = outcome[:-2]  # drops last comma

        time = "Date: " + str(self.date)

        winProb = f"Team one win prob: {self.t1WinProb * 100"

        toReturn = names + "\n" + outcome + "\n" + time + "\n"
        if self.notes != "":
            toReturn += "Notes:" + self.notes + "\n"



        return toReturn

    def create_game_id(self):
        """ Creates gameID based on players names, score, and current timestamp """
        now = datetime.now()
        gameDetails = ""
        for player in self.teamOne:
            gameDetails += player.name[0].lower()
        gameDetails += str(self.teamOneScore)
        for player in self.teamTwo:
            gameDetails += player.name[0].lower()
        gameDetails += str(self.teamTwoScore)
        timeDetails = now.strftime("%Y%m%d%H%M")
        return gameDetails + timeDetails

    def win_probability_team_one(self):
        delta_mu = sum(r.mu for r in self.teamOne) - sum(r.mu for r in self.teamTwo)
        sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(self.teamOne, self.teamTwo))
        size = len(self.teamOne) + len(self.teamTwo)
        denom = math.sqrt(size * (ts.BETA * ts.BETA) + sum_sigma)
        env = ts.global_env()
        return round(env.cdf(delta_mu / denom), 4)



