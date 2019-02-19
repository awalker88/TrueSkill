from datetime import datetime


class Game:

    def __init__(self, teamOne: list, teamTwo: list, teamOneScore: int, teamTwoScore: int, season: int):
        self.teamOne = teamOne
        self.teamTwo = teamTwo
        self.teamOneScore = teamOneScore
        self.teamTwoScore = teamTwoScore
        self.season = season
        if teamOneScore > teamTwoScore:
            self.winner = teamOne
        elif teamOneScore < teamTwoScore:
            self.winner = teamTwo
        else:
            self.winner = None
        self.date = datetime.now()
        self.gameID = self.create_game_id()

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

        return names + "\n" + outcome + "\n" + time

    def create_game_id(self):
        return True  # TODO: create



