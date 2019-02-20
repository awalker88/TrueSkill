import pickle as pkl
from random import randint

from Player import Player
from Game import Game


class History:

    def __init__(self):
        self.rosterName = "roster.pkl"
        self.gameHistoryName = "gameHistory.pkl"
        self.roster = {}
        self.roster = pkl.load(open(self.rosterName, "rb"))
        self.gameHistory = pkl.load(open(self.gameHistoryName, "rb"))
        self.currentSeason = 1

    def add_player(self, name):
        """ Inputs: Player name as string
            Outputs: none"""
        newPlayer = Player(name)
        self.roster[newPlayer.playerID] = newPlayer
        pkl.dump(self.roster, open(self.rosterName, "wb"))  # update pickle file after change

    def remove_player(self, playerID):
        """ Inputs: playerID as string
            Outputs: True if successful, False if player couldn't be found

            Searches roster for player with matching id, then removes them from dictionary and from pkl file
            """
        if self.roster[playerID] is not None:
            del self.roster[playerID]
            pkl.dump(self.roster, open(self.rosterName, "wb"))  # update pickle file after change
            return True
        print("Could not find player with ID:", playerID)
        return False

    def add_game(self, teamOne, teamTwo, teamOneScore, teamTwoScore, season):
        """ Inputs: teamOne, teamTwo as lists of playerIDs; teamOneScore, teamTwoScore, season as ints
            Outputs: none

            Adds game to game history, updates Players to have another win/loss/draw
            """
        # Game class requires lists of Players, but add_game only requires playerIDs, so we'll need to
        # make new teams composed of Player classes
        pTeamOne = []
        for playerID in teamOne:
            pTeamOne.append(self.roster[playerID])
        pTeamTwo = []
        for playerID in teamTwo:
            pTeamTwo.append(self.roster[playerID])

        newGame = Game(pTeamOne, pTeamTwo, teamOneScore, teamTwoScore, season)
        self.gameHistory[newGame.gameID] = newGame
        pkl.dump(self.gameHistory, open(self.gameHistoryName, "wb"))  # update pickle file after change

        # update player wins/losses/draws
        for playerID in teamOne + teamTwo:
            if newGame.winner is None:
                self.roster[playerID].draws += 1
            elif playerID in newGame.winner:
                self.roster[playerID].wins += 1
            else:
                self.roster[playerID].losses += 1

    def remove_game(self, gameID):
        """ Inputs: gameID as string
            Outputs: True if successful, False if game with gameID could not be found

            Finds game in gameHistory and deletes it, then updates players so they have one less win/loss/draw
            """
        if self.gameHistory[gameID] is not None:
            teamOne = self.gameHistory[gameID].teamOne
            teamTwo = self.gameHistory[gameID].teamTwo
            winner = self.gameHistory[gameID].winner
            del self.gameHistory[gameID]
            pkl.dump(self.gameHistory, open(self.gameHistoryName, "wb"))  # update pickle file after change
            # update player wins/losses
            for playerID in teamOne + teamTwo:
                if winner is None:
                    self.roster[playerID].draws -= 1
                elif playerID in winner:
                    self.roster[playerID].wins -= 1
                else:
                    self.roster[playerID].losses -= 1
            return True
        print("Could not find game with ID:", gameID)
        return False

    def print_roster(self):
        for playerID in self.roster:
            print(self.roster[playerID], "\n")

    def clear_roster(self):
        """ Inputs: None
            Outputs: None

            Overwrites roster pkl file and then sets History's roster equal to empty roster pkl file
            """
        emptyDict = {}
        pkl.dump(emptyDict, open(self.rosterName, "wb"))
        self.roster = pkl.load(open(self.rosterName, "rb"))
        print("Roster cleared.\n")

    def print_game_history(self):
        for gameID in self.gameHistory:
            print(self.gameHistory[gameID], "\n")

    def clear_game_history(self):
        """ Inputs: None
            Outputs: None

            Overwrites gameHistory pkl file and then sets History's roster equal to empty roster pkl file
            """
        emptyDict = {}
        pkl.dump(emptyDict, open(self.gameHistoryName, "wb"))
        self.gameHistory = pkl.load(open(self.gameHistoryName, "rb"))
        print("Game History cleared.\n")

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



