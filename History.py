import pickle as pkl
from random import shuffle
from math import ceil, log2
import trueskill as ts
from prettytable import PrettyTable
from pandas import DataFrame

from Player import Player
from Game import Game
from TournamentTeam import TournamentTeam


class History:

    def __init__(self, roster_name="roster.pkl", game_history_name="game_history.pkl"):
        self.roster_name = roster_name
        self.game_history_name = game_history_name
        self.roster = pkl.load(open(self.roster_name, "rb"))
        self.game_history = pkl.load(open(self.game_history_name, "rb"))
        self.num_players = len(self.roster)
        self.num_games = len(self.game_history)
        self.current_season = 1  # TODO: Add support for soft reset of ranks with seasons
        self.suppress_messages = False

        MU = 1000.
        SIGMA = MU / 3
        BETA = SIGMA / 2
        TAU = SIGMA / 100
        self.env = ts.TrueSkill(mu=MU, sigma=SIGMA, beta=BETA, tau=TAU, draw_probability=0.02)

        if len(self.roster) > 90:
            print("Warning! The google sheet might only be configured to have less than 100 players. Pls fix.")

    def add_player(self, name, playerID="", wins=0, losses=0, draws=0):
        """
        :param name: string of first and last name
        :param playerID: can be manually set, otherwise created in Player class
        :param wins: can be manually set, otherwise created in Player class
        :param losses: can be manually set, otherwise created in Player class
        :param draws: can be manually set, otherwise created in Player class
        :return: None
        """
        skill = self.env.create_rating()
        new_player = Player(name, skill, self.num_players + 1, playerID, wins, losses, draws)
        self.roster[new_player.playerID] = new_player
        self.num_players = len(self.roster)
        pkl.dump(self.roster, open(self.roster_name, "wb"))  # update pickle file after change
        print(f'New player added: {new_player.name} ({new_player.playerID})')

    def remove_player(self, playerID):
        """
        Searches roster for player with matching id, then removes them from dictionary and from pkl file
        :param playerID: string
        :return: True if successful, False otherwise
        """
        if self.roster[playerID] is not None:
            del self.roster[playerID]
            self.num_players = len(self.roster)
            pkl.dump(self.roster, open(self.roster_name, "wb"))  # update pickle file after change
            print(f"Player {playerID} removed.")
            return True
        print("Could not find player with ID:", playerID)
        return False

    def add_game(self, team_one, team_two, team_one_score, team_two_score, notes=''):
        """
        Adds a Game to game_history.pkl
        :param team_one: list of playerIDs
        :param team_two: list of playerIDs
        :param team_one_score: team one's score as int
        :param team_two_score: team two's score as int
        :param notes: optional notes about the game
        :return: None
        """
        # Game class requires lists of Players, but add_game only requires playerIDs, so we'll need to
        # make new teams composed of Player classes
        p_team_one = []
        for playerID in team_one:
            p_team_one.append(self.roster[playerID])
        p_team_two = []
        for playerID in team_two:
            p_team_two.append(self.roster[playerID])

        new_game = Game(p_team_one, p_team_two, team_one_score, team_two_score, self.current_season, notes)
        self.game_history[new_game.gameID] = new_game
        pkl.dump(self.game_history, open(self.game_history_name, "wb"))  # update game_history pickle file after change

        # update player wins/losses/draws
        for playerID in team_one:
            self.roster[playerID].update_after_game(team_one_score, team_two_score)
        for playerID in team_two:
            self.roster[playerID].update_after_game(team_two_score, team_one_score)

        # create rating groups (ts.rate() function takes in lists of dictionaries)
        rating_groups = []
        team_one_skill_dict = {}
        for player in p_team_one:
            team_one_skill_dict[player] = player.skill
        team_two_skill_dict = {}
        for player in p_team_two:
            team_two_skill_dict[player] = player.skill
        rating_groups.append(team_one_skill_dict)
        rating_groups.append(team_two_skill_dict)

        # update skills for players
        if new_game.winner == p_team_one:
            rating_groups = ts.rate(rating_groups, [0, 1])
        else:
            rating_groups = ts.rate(rating_groups, [1, 0])
        for team in rating_groups:
            for player in team:
                player.update_skill(team[player])

        pkl.dump(self.roster, open(self.roster_name, "wb"))  # update roster pickle file after updating player skills

        if not self.suppress_messages:
            print(f"Game with ID '{new_game.gameID}' added.")

        self.num_games = len(self.game_history)

    def remove_game(self, gameID):
        """
        Finds game in game_history and deletes it, then updates players so they have one less win/loss/draw
            IMPORTANT NOTE: This will not revert changes to players' skills or rating scores
        :param gameID: string
        :return: True if game is removed, False otherwise
        """
        if self.game_history[gameID] is not None:
            team_one = self.game_history[gameID].team_one
            team_two = self.game_history[gameID].team_two
            winner = self.game_history[gameID].winner
            del self.game_history[gameID]
            pkl.dump(self.game_history, open(self.game_history_name, "wb"))  # update pickle file after change
            # update player wins/losses
            for playerID in team_one + team_two:
                if winner is None:
                    self.roster[playerID].draws -= 1
                elif playerID in winner:
                    self.roster[playerID].wins -= 1
                else:
                    self.roster[playerID].losses -= 1
            return True
        print("Could not find game with ID:", gameID)
        self.num_games = len(self.game_history)
        return False

    def print_roster(self):
        table = PrettyTable()
        table.field_names = ['Player ID', 'Name', 'Win Rate', 'Skill Mean', 'Skill Variance', 'Ranking Score',
                             'Games Played']
        for playerID in self.roster:
            p = self.roster[playerID]
            table.add_row([p.playerID, p.name, p.get_win_rate(), round(p.skill.mu, 2), round(p.skill.sigma, 2),
                           round(p.ranking_score, 2), p.games_played])
        print(table)

    def clear_roster(self):
        """
        Overwrites roster pickle file and then sets History's roster equal to empty roster pickle file
        :return: None
        """
        empty_dict = {}
        empty_df = DataFrame([[]])
        pkl.dump(empty_dict, open(self.roster_name, "wb"))
        pkl.dump(empty_df, open("previous_playerID_responses.pkl", "wb"))
        self.roster = pkl.load(open(self.roster_name, "rb"))
        self.num_players = len(self.roster)
        print("Roster cleared.\n")

    def print_game_history(self):
        table = PrettyTable()
        table.field_names = ['Game ID', 'Team One', 'Team Two', 'Score', 'Predicted Winner', 'Actual Winner']
        for gameID in self.game_history:
            g = self.game_history[gameID]
            if g.t1_win_prob > 50.0:
                pred_winner = f"Team One ({round(g.t1_win_prob, 2)})"
            else:
                pred_winner = f"Team Two ({round(100 - g.t1_win_prob, 2)})"
            if g.team_one_score > g.team_two_score:
                actual_winner = "Team One"
            elif g.team_one_score < g.team_two_score:
                actual_winner = "Team Two"
            else:
                actual_winner = "Draw"
            table.add_row([gameID, g.get_team_name(g.team_one), g.get_team_name(g.team_two),
                           f"{g.team_one_score}-{g.team_two_score}", pred_winner, actual_winner])

        print(table)

    def clear_game_history(self):
        """
        Overwrites game_history pkl file and then sets History's roster equal to empty roster pkl file
        :return: None
        """
        empty_dict = {}
        empty_df = DataFrame([[]])
        pkl.dump(empty_dict, open(self.game_history_name, "wb"))
        pkl.dump(empty_df, open("previous_game_responses.pkl", "wb"))
        self.game_history = pkl.load(open(self.game_history_name, "rb"))
        self.num_games = len(self.game_history)
        print("Game History cleared.\n")

    def tournament(self, teams: list):
        """
        :param teams: list of lists of playerIDs
        :return: None

        Runs a single elimination bracket between every team in teams.
        """
        print("-------------------TOURNAMENT START-------------------")
        sorted_teams = []
        # add skill and TournamentTeams to our list
        for team in teams:
            player_team = []  # convert playerIDs into Player objects
            for playerID in team:
                player_team.append(self.roster[playerID])
            new_team = TournamentTeam(player_team)
            sorted_teams.append([new_team.ranking_score, new_team])
        sorted_teams.sort(reverse=True)
        # add seed number
        table = PrettyTable()
        table.field_names = ["Seed", "Player ID(s)", "Ranking Score"]
        for seed, team in enumerate(sorted_teams, 1):
            team.insert(0, seed)
            team[2].seed = seed
            table.add_row([seed, team[2].name, team[2].ranking_score])
        print(table)
        # teams are now in format [seedNum, skill, TournamentTeam object]

        gameNumber = 1
        for rnd in range(ceil(log2(len(sorted_teams)))):
            print(f"\nROUND: {rnd + 1}")
            advancers = []  # list of lists of advancing teams in form: [teamSeed, teamSkill, TournamentTeam object]

            # if there aren't an even number of teams, pick random bye from teams that have received fewest num of byes
            if len(sorted_teams) % 2 != 0:
                shuffle(sorted_teams)  # shuffle teams so if tie, it won't just choose the last team with fewest byes
                lowestNumByes, bye = 1000, 1000
                for i in range(len(sorted_teams)):
                    if sorted_teams[i][2].num_byes < lowestNumByes:
                        bye = i  # bye is this teams position in sorted_teams if they have had the lowest byes so far
                        lowestNumByes = sorted_teams[i][2].num_byes
                byersThisRnd = sorted_teams.pop(bye)
                # get names of team that got a bye
                byersNames = byersThisRnd[2].get_name()
                print(f"\nTeam: {byersNames} will receive a bye this round.")
                byersThisRnd[2].num_byes += 1

                advancers.append(byersThisRnd)
                sorted_teams.sort()

            # create matches for this round
            gamesLeft = []
            for i in range(int(len(sorted_teams) / 2)):
                gamesLeft.append([gameNumber, sorted_teams[i], sorted_teams[len(sorted_teams) - 1 - i]])
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
            sorted_teams = advancers

        print(f"\nThe winner(s) of this tournament are {advancers[0][2].name}. Congratulations!")
        print("--------------------TOURNAMENT END--------------------")
