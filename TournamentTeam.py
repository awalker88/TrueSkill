

class TournamentTeam:

    def __init__(self, team_members: list):
        self.team_members = team_members
        self.name = self.get_name()
        self.seed = 0
        self.ranking_score = self.get_skill()
        self.num_byes = 0

    def get_skill(self):
        team_skill = 0
        for player in self.team_members:
            team_skill += player.ranking_score
        return team_skill / len(self.team_members)

    def get_name(self):
        name = ""
        for player in self.team_members:
            name += player.playerID + ", "
        name = name[:-2]  # drops last comma
        return name
