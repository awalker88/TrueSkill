import pickle as pkl
from random import randint, shuffle
from math import ceil, log2

from Player import Player
from Game import Game
from TournamentTeam import TournamentTeam


class History:

    def __init__(self):
        self.rosterName = "roster.pkl"
        self.gameHistoryName = "gameHistory.pkl"
        self.roster = {}
        self.roster = pkl.load(open(self.rosterName, "rb"))
        self.gameHistory = pkl.load(open(self.gameHistoryName, "rb"))
        self.currentSeason = 1

    def add_player(self, name, playerID="", wins=0, losses=0, draws=0, skill=0):
        """ Inputs: Player name as string
            Outputs: none"""
        newPlayer = Player(name, playerID, wins, losses, draws, skill)
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
        """
        :param teams: list of lists of playerIDs
        :return: None
        """
        sortedTeams = []
        # add skill and TournamentTeams to our list
        for team in teams:
            playerTeam = []  # convert playerIDs into Player objects
            for playerID in team:
                playerTeam.append(self.roster[playerID])
            newTeam = TournamentTeam(playerTeam)
            sortedTeams.append([newTeam.skill, newTeam])
        sortedTeams.sort()
        sortedTeams.reverse()
        # add seed number
        for seed, team in enumerate(sortedTeams, 1):
            team.insert(0, seed)
            team[2].seed = seed
        # teams are now in format [seedNum, skill, TournamentTeam object]

        # TODO: finish, add functionality to print tournament history
        gameNumber = 1
        for rnd in range(ceil(log2(len(sortedTeams)))):
            print(f"\nROUND: {rnd + 1}")
            advancers = []  # list of [teamOneSeed, teamOneSkill, TournamentTeam object]s

            # if there aren't an even number of teams, pick random bye from teams that have received fewest num of byes
            if len(sortedTeams) % 2 != 0:
                # shuffle teams so if there's a tie on who has the lowest bye, it won't just choose the last team
                shuffle(sortedTeams)
                lowestNumByes = 1000
                bye = 1000
                for i in range(len(sortedTeams)):
                    if sortedTeams[i][2].numByes < lowestNumByes:
                        bye = i  # bye = this teams position in sortedTeams if they have had the lowest byes so far
                        lowestNumByes = sortedTeams[i][2].numByes
                byers = sortedTeams.pop(bye)
                # get names of team that got a bye
                byersNames = ""
                for player in byers[2].teamMembers:
                    byersNames += player.playerID + ", "
                byersNames = byersNames[:-2]  # drops last comma
                print(f"\nTeam: {byersNames} will receive a bye this round.")
                byers[2].numByes += 1

                advancers.append(byers)
                sortedTeams.sort()

            # create matches for this round
            gamesLeft = []
            for i in range(int(len(sortedTeams) / 2)):
                gamesLeft.append([gameNumber, sortedTeams[i], sortedTeams[len(sortedTeams) - 1 - i]])
                gameNumber += 1
                # games now in format [gameNum, [teamOneSeed, teamOneSkill, TournamentTeam object], [teamTwoSeed, ... ]]

            while len(gamesLeft) > 0:
                # print remaining games
                print("\nRemaining games in this round:")
                remainingGameNums = []
                for game in gamesLeft:
                    remainingGameNums.append(game[0])
                    teamOne = game[1][2].name
                    teamTwo = game[2][2].name
                    print(f"Game {game[0]}: {teamOne} vs. {teamTwo}")

                # ask what game you'd like to report finished
                print("Remaining game numbers left:", remainingGameNums,"\n")
                nextFinished = int(input("What game would you like to report finished?: "))
                while nextFinished not in remainingGameNums:
                    print("Invalid game number")
                    nextFinished = int(input("What game would you like to report finished?: "))
                gameIndex = 0
                for game in gamesLeft:
                    if game[0] == nextFinished:
                        teamOne = game[1][2]
                        teamTwo = game[2][2]
                        teamOneScore = int(input(f"What is the score for {game[1][2].name}?: "))
                        teamTwoScore = int(input(f"What is the score for {game[2][2].name}?: "))
                        teamOneIDs = []
                        for player in teamOne.teamMembers:
                            teamOneIDs.append(player.playerID)
                        teamTwoIDs = []
                        for player in teamTwo.teamMembers:
                            teamTwoIDs.append(player.playerID)

                        self.add_game(teamOneIDs, teamTwoIDs, teamOneScore, teamTwoScore,
                                      self.currentSeason)
                        # TODO: update player skills
                        if teamOneScore > teamTwoScore:
                            advancers.append(game[1])  # adds team one to advancers
                        else:
                            advancers.append(game[2])  # adds team two to advancers
                        gamesLeft.pop(gameIndex)
                    gameIndex += 1
            sortedTeams = advancers

        print(f"\nThe winner(s) of this tournament are {advancers[0][2].name}. Congratulations!")







