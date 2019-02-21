from datetime import datetime


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
        # TODO: add skills, chance team one wins

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

        toReturn = names + "\n" + outcome + "\n" + time + "\n"
        if self.notes != "":
            toReturn += "Notes:" + self.notes + "\n"
        # TODO: add expected winner to print

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

    def calculate_team_one_odds(self):
        # todo: create
        pass



