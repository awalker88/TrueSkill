import pickle as pkl
from random import shuffle
from math import ceil, log2
import trueskill as ts
from prettytable import PrettyTable

from Player import Player
from Game import Game
from TournamentTeam import TournamentTeam


class History:

    def __init__(self, rosterName="roster.pkl", gameHistoryName="gameHistory.pkl"):
        self.rosterName = rosterName
        self.gameHistoryName = gameHistoryName
        self.roster = pkl.load(open(self.rosterName, "rb"))
        self.gameHistory = pkl.load(open(self.gameHistoryName, "rb"))
        self.currentSeason = 1
        self.suppress = False

        MU = 1000.
        SIGMA = MU / 3
        BETA = SIGMA / 2
        TAU = SIGMA / 100
        self.env = ts.TrueSkill(mu=MU, sigma=SIGMA, beta=BETA, tau=TAU, draw_probability=0.02)

    def add_player(self, name, playerID="", wins=0, losses=0, draws=0, skill=0):
        """ Inputs: Player name as string
            Outputs: none"""
        skill = self.env.create_rating()
        newPlayer = Player(name, skill, playerID, wins, losses, draws)
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

    def add_game(self, teamOne, teamTwo, teamOneScore, teamTwoScore):
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

        newGame = Game(pTeamOne, pTeamTwo, teamOneScore, teamTwoScore, self.currentSeason)
        self.gameHistory[newGame.gameID] = newGame
        pkl.dump(self.gameHistory, open(self.gameHistoryName, "wb"))  # update gameHistory pickle file after change

        # update player wins/losses/draws
        for player in pTeamOne + pTeamTwo:
            if newGame.winner is None:
                self.roster[player.playerID].draws += 1
            elif player in newGame.winner:
                self.roster[player.playerID].wins += 1
            else:
                self.roster[player.playerID].losses += 1

        # create rating groups (ts.rate() function takes in lists of dictionaries)
        rating_groups = []
        teamOneSkillDict = {}
        for player in pTeamOne:
            teamOneSkillDict[player] = player.skill
        teamTwoSkillDict = {}
        for player in pTeamTwo:
            teamTwoSkillDict[player] = player.skill
        rating_groups.append(teamOneSkillDict)
        rating_groups.append(teamTwoSkillDict)

        # update skills for players
        if newGame.winner == pTeamOne:
            rating_groups = ts.rate(rating_groups, [0, 1])
        else:
            rating_groups = ts.rate(rating_groups, [1, 0])
        for team in rating_groups:
            for player in team:
                player.update_skill(team[player])

        pkl.dump(self.roster, open(self.rosterName, "wb"))  # update roster pickle file after updating player skills

        if not self.suppress:
            print(f"Game with ID '{newGame.gameID}' added.")

    def remove_game(self, gameID):
        """ Inputs: gameID as string
            Outputs: True if successful, False if game with gameID could not be found

            Finds game in gameHistory and deletes it, then updates players so they have one less win/loss/draw
            IMPORTANT NOTE: This will not revert changes to players' skills or rating scores
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
        table = PrettyTable()
        table.field_names = ['Player ID', 'Name', 'Win Rate', 'Skill Mean', 'Skill Variance', 'Ranking Score',
                             'Games Played']
        for playerID in self.roster:
            p = self.roster[playerID]
            table.add_row([p.playerID, p.name, p.get_win_rate(), round(p.skill.mu, 2), round(p.skill.sigma, 2),
                           round(p.rankingScore, 2), p.wins + p.losses + p.draws])
        print(table)

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
        table = PrettyTable()
        table.field_names = ['Game ID', 'Team One', 'Team Two', 'Score', 'Predicted Winner', 'Actual Winner']
        for gameID in self.gameHistory:
            g = self.gameHistory[gameID]
            if g.t1WinProb > 50.0:
                predWinner = f"Team One ({round(g.t1WinProb, 2)})"
            else:
                predWinner = f"Team Two ({round(100 - g.t1WinProb, 2)})"
            if g.teamOneScore > g.teamTwoScore:
                actualWinner = "Team One"
            elif g.teamOneScore < g.teamTwoScore:
                actualWinner = "Team Two"
            else:
                actualWinner = "Draw"
            table.add_row([gameID, g.get_team_name(g.teamOne), g.get_team_name(g.teamTwo),
                           f"{g.teamOneScore}-{g.teamTwoScore}", predWinner, actualWinner])

        print(table)

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

        Runs a single elimination bracket between every team in teams.
        """
        print("-------------------TOURNAMENT START-------------------")
        sortedTeams = []
        # add skill and TournamentTeams to our list
        for team in teams:
            playerTeam = []  # convert playerIDs into Player objects
            for playerID in team:
                playerTeam.append(self.roster[playerID])
            newTeam = TournamentTeam(playerTeam)
            sortedTeams.append([newTeam.rankingScore, newTeam])
        sortedTeams.sort(reverse=True)
        # add seed number
        table = PrettyTable()
        table.field_names = ["Seed", "Player ID(s)", "Ranking Score"]
        for seed, team in enumerate(sortedTeams, 1):
            team.insert(0, seed)
            team[2].seed = seed
            table.add_row([seed, team[2].name, team[2].rankingScore])
        print(table)
        # teams are now in format [seedNum, skill, TournamentTeam object]

        gameNumber = 1
        for rnd in range(ceil(log2(len(sortedTeams)))):
            print(f"\nROUND: {rnd + 1}")
            advancers = []  # list of lists of advancing teams in form: [teamSeed, teamSkill, TournamentTeam object]

            # if there aren't an even number of teams, pick random bye from teams that have received fewest num of byes
            if len(sortedTeams) % 2 != 0:
                shuffle(sortedTeams)  # shuffle teams so if tie, it won't just choose the last team with fewest byes
                lowestNumByes, bye = 1000, 1000
                for i in range(len(sortedTeams)):
                    if sortedTeams[i][2].numByes < lowestNumByes:
                        bye = i  # bye is this teams position in sortedTeams if they have had the lowest byes so far
                        lowestNumByes = sortedTeams[i][2].numByes
                byersThisRnd = sortedTeams.pop(bye)
                # get names of team that got a bye
                byersNames = byersThisRnd[2].get_name()
                print(f"\nTeam: {byersNames} will receive a bye this round.")
                byersThisRnd[2].numByes += 1

                advancers.append(byersThisRnd)
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

                print(f"Remaining game numbers left: {remainingGameNums}\n")
                while True:
                    try:
                        nextFinished = int(input("What game would you like to report finished?: "))
                        remainingGameNums.index(nextFinished)
                        break
                    except Exception:
                        print("Invalid game number")

                gameIndex = 0
                for game in gamesLeft:
                    if game[0] == nextFinished:
                        teamOne = game[1][2]
                        teamTwo = game[2][2]
                        teamOneScore = int(input(f"What is the score for {game[1][2].name}?: "))
                        teamTwoScore = int(input(f"What is the score for {game[2][2].name}?: "))
                        teamOneIDs = []
                        # get player id's to pass to self.add_game()
                        for player in teamOne.teamMembers:
                            teamOneIDs.append(player.playerID)
                        teamTwoIDs = []
                        for player in teamTwo.teamMembers:
                            teamTwoIDs.append(player.playerID)

                        self.add_game(teamOneIDs, teamTwoIDs, teamOneScore, teamTwoScore)
                        if teamOneScore > teamTwoScore:
                            advancers.append(game[1])
                        else:
                            advancers.append(game[2])
                        gamesLeft.pop(gameIndex)
                    gameIndex += 1
            sortedTeams = advancers

        print(f"\nThe winner(s) of this tournament are {advancers[0][2].name}. Congratulations!")
        print("--------------------TOURNAMENT END--------------------")
