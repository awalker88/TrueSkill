# TODO: make sure can delete

class Season:

    def __init__(self, seasonNumber, initialPlayers: list = []):
        self.seasonNumber = seasonNumber
        self.roster = []

        for player in initialPlayers:
            self.roster.append(player)

