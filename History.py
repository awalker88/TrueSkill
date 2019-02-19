import pandas as pd
import pickle
from Player import Player
from Game import Game

class History:

    def __init__(self):
        self.roster = self.load_roster()
        self.numPlayers = 0
        self.gameHistory = []
        self.numGames = 0
        self.currentSeason = 1

    def add_player(self, name):
        newPlayer = Player(name)
        self.roster[newPlayer.playerID] = Player
        self.numPlayers += 1

    def remove_player(self, playerID):
        if self.roster[playerID] is not None:
            del self.roster[playerID]
            self.numPlayers -= 1
            return True
        print("Could not find player with ID:", playerID)
        return False

    def create_game_history(self):
        # TODO: create
        gameHistory = {}
        return gameHistory

    def add_game(self, teamOne, teamTwo, teamOneScore, teamTwoScore, season):
        # TODO: check
        newGame = Game(teamOne, teamTwo, teamOneScore, teamTwoScore, season)
        self.gameHistory[newGame.gameID] = newGame
        self.numGames += 1

    def load_roster(self, filename):
        # TODO: create
        roster = {}
        return roster

    def print_roster(self):
        for player in self.roster:  # TODO: convert to dict
            print("Name:", player.name, "  ID:", player.playerID, "Wins:", player.wins, "Losses:", player.losses,
                  "Winrate:", str(player.get_win_rate()) + "%")

    def tournament(self, teams: list):
        # sort teams by their average skill
        sortedTeams = []
        for team in teams:
            teamSkill = 0
            for player in team:
                teamSkill += player.skill
            teamSkill = teamSkill / len(team)
            sortedTeams.append([teamSkill, team])
        sortedTeams.sort()

        # TODO: finish
        # if there aren't an even number of teams, pick random bye
        if len(sortedTeams) % 2 != 0:
            bye = randint(0, len(sortedTeams))



