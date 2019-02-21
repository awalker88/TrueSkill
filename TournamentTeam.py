

class TournamentTeam:

    def __init__(self, teamMembers: list):
        self.teamMembers = teamMembers
        self.name = self.get_name()
        self.seed = 0
        self.skill = self.get_skill()
        self.numByes = 0

    def get_skill(self):
        teamSkill = 0
        for player in self.teamMembers:
            teamSkill += player.skill
        return teamSkill / len(self.teamMembers)

    def get_name(self):
        name = ""
        for player in self.teamMembers:
            name += player.playerID + ", "
        name = name[:-2]  # drops last comma
        return name
