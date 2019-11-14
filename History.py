import os
import pickle as pkl
from math import ceil, log2
from random import shuffle

import trueskill as ts
from pandas import DataFrame
from prettytable import PrettyTable

from Game import Game
from Player import Player
from TournamentTeam import TournamentTeam


class History:
    def __init__(self, roster_name="roster.pkl", game_database_name="game_database.pkl"):
        # load roster database
        self.roster_name = roster_name
        if os.path.getsize(self.roster_name) > 0:
            self.roster = pkl.load(open(self.roster_name, "rb"))
        else:
            self.clear_roster()

        # load game database
        self.game_database_name = game_database_name
        if os.path.getsize(self.game_database_name) > 0:
            self.game_database = pkl.load(open(self.game_database_name, "rb"))
        else:
            self.clear_game_database()

        self.num_players = len(self.roster)
        self.num_games = len(self.game_database)
        self.current_season = 1  # TODO: Add support for soft reset of ranks with seasons
        self.verbose = False

        MU = 1000.
        SIGMA = MU / 3
        BETA = SIGMA / 2
        TAU = SIGMA / 100
        self.env = ts.TrueSkill(mu=MU, sigma=SIGMA, beta=BETA, tau=TAU, draw_probability=0.02)

        if len(self.roster) > 90:
            print("Warning! The google sheet might only be configured to have less than 100 players. Pls fix.")

    def add_player(self, name):
        """
        :param name: string of first and last name
        :return: None
        """
        skill = self.env.create_rating()
        new_player = Player(name, skill, self.num_players + 1)
        self.roster[new_player.playerID] = new_player
        self.num_players = len(self.roster)
        self.save_roster()
        if self.verbose:
            print(f'New player added: {new_player.name} ({new_player.playerID})')

    def add_game(self, team_one, team_two, team_one_score, team_two_score, timestamp=None, notes=''):
        """
        Adds a Game to game_database.pkl
        :param team_one: list of playerIDs
        :param team_two: list of playerIDs
        :param team_one_score: team one's score as int
        :param team_two_score: team two's score as int
        :param timestamp: string date in form MM/DD/YYYY hh:mm:ss or None to generate timestamp with current datetime
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

        new_game = Game(p_team_one, p_team_two, team_one_score, team_two_score, self.current_season, self.env.beta,
                        timestamp=timestamp, notes=notes)
        self.game_database[new_game.gameID] = new_game
        self.save_game_database()

        # update player wins/losses/draws
        for playerID in team_one:
            self.roster[playerID].update_stats_after_game(team_one_score, team_two_score)
        for playerID in team_two:
            self.roster[playerID].update_stats_after_game(team_two_score, team_one_score)

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
        if (team_one_score + team_two_score > 42) and (abs(team_one_score - team_two_score) <= 2):
            # count as a draw (for skill updating) if the score had to go more than 22-20, as players are likely
            # similar if it was that close
            rating_groups = self.env.rate(rating_groups, [0, 0])
        elif new_game.winner == p_team_one:
            rating_groups = self.env.rate(rating_groups, [0, 1])
        else:
            rating_groups = self.env.rate(rating_groups, [1, 0])
        for team in rating_groups:
            for player in team:
                player.update_skill(team[player], timestamp)

        # get team skills
        for team in rating_groups:
            mu = 0.
            sigma = 0.
            for player in team:
                mu += player.skill.mu
                sigma += player.skill.sigma
                new_game.team_skills_after_game.append(ts.Rating(mu / len(team), sigma / len(team)))

        self.save_roster()  # update roster pickle file after updating player skills

        if self.verbose:
            print(f"Game with ID '{new_game.gameID}' added.")

        self.num_games = len(self.game_database)

    def print_roster(self):
        """
        Prints a nice table of every player in this history's database
        :return:
        """
        if len(self.game_database) == 0:
            print('No players in roster')
            exit()
        table = PrettyTable()
        table.field_names = ['Player ID', 'Name', 'Win Rate', 'Skill Mean', 'Skill Variance', 'Ranking Score',
                             'Games Played']
        for playerID in self.roster:
            p = self.roster[playerID]
            table.add_row([p.playerID, p.name, p.get_win_percentage(), round(p.skill.mu, 2), round(p.skill.sigma, 2),
                           round(p.ranking_score, 2), p.games_played])
        print(table)

    def print_game_database(self):
        """
        Prints a nice table of every game in this history's database
        :return: None
        """
        if len(self.game_database) == 0:
            print('No games in database')
            exit()
        table = PrettyTable()
        table.field_names = ['Game ID', 'Team One', 'Team Two', 'Score', 'Predicted Winner', 'Actual Winner']
        for gameID in self.game_database:
            g = self.game_database[gameID]
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

    def clear_roster(self, verbose=True):
        """
        Overwrites roster pickle file and then sets History's roster equal to empty roster pickle file
        :return: None
        """
        self.roster = {}
        empty_df = DataFrame([[]])
        self.save_roster()
        pkl.dump(empty_df, open("previous_playerID_responses.pkl", "wb"))
        self.roster = pkl.load(open(self.roster_name, "rb"))
        self.num_players = len(self.roster)
        if verbose:
            print("Roster cleared.")

    def clear_game_database(self, verbose=True):
        """
        Overwrites game_database pkl file and then sets History's roster equal to empty roster pkl file
        :return: None
        """
        # clear game_database
        self.game_database = {}
        self.save_game_database()
        self.num_games = len(self.game_database)
        if verbose:
            print("Game Database cleared.")

        # reset player stats
        for playerID in self.roster:
            self.roster[playerID].reset_stats(new_skill=self.env.create_rating())
        self.save_roster()

        # clear previous responses
        pkl.dump(DataFrame([[]]), open("previous_game_responses.pkl", "wb"))
        if verbose:
            print("previous_game_responses.pkl cleared.")

    def save_roster(self):
        """
        saves the current roster back to the roster pkl file
        :return: None
        """
        pkl.dump(self.roster, open(self.roster_name, "wb"))

    def save_game_database(self):
        """
        saves the current game_database back to the game_database pkl file
        :return: None
        """
        pkl.dump(self.game_database, open(self.game_database_name, "wb"))

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

        game_number = 1
        for rnd in range(ceil(log2(len(sorted_teams)))):
            print(f"\nROUND: {rnd + 1}")
            advancers = []  # list of lists of advancing teams in form: [teamSeed, teamSkill, TournamentTeam object]

            # if there aren't an even number of teams, pick random bye from teams that have received fewest num of byes
            if len(sorted_teams) % 2 != 0:
                shuffle(sorted_teams)  # shuffle teams so if tie, it won't just choose the last team with fewest byes
                lowest_num_byes, bye = 1000, 1000
                for i in range(len(sorted_teams)):
                    if sorted_teams[i][2].num_byes < lowest_num_byes:
                        bye = i  # bye is this teams position in sorted_teams if they have had the lowest byes so far
                        lowest_num_byes = sorted_teams[i][2].num_byes
                byers_this_rnd = sorted_teams.pop(bye)
                # get names of team that got a bye
                byers_names = byers_this_rnd[2].get_name()
                print(f"\nTeam: {byers_names} will receive a bye this round.")
                byers_this_rnd[2].num_byes += 1

                advancers.append(byers_this_rnd)
                sorted_teams.sort()

            # create matches for this round
            games_left = []
            for i in range(int(len(sorted_teams) / 2)):
                games_left.append([game_number, sorted_teams[i], sorted_teams[len(sorted_teams) - 1 - i]])
                game_number += 1
                # games now in format [gameNum, [teamOneSeed, teamOneSkill, TournamentTeam object], [teamTwoSeed, ... ]]

            while len(games_left) > 0:
                # print remaining games
                print("\nRemaining games in this round:")
                remaining_game_nums = []
                for game in games_left:
                    remaining_game_nums.append(game[0])
                    team_one = game[1][2].name
                    team_two = game[2][2].name
                    print(f"Game {game[0]}: {team_one} vs. {team_two}")

                print(f"Remaining game numbers left: {remaining_game_nums}\n")
                while True:
                    try:
                        next_finished = int(input("What game would you like to report finished?: "))
                        remaining_game_nums.index(next_finished)
                        break
                    except ValueError:
                        print("Invalid game number")

                game_index = 0
                for game in games_left:
                    if game[0] == next_finished:
                        team_one = game[1][2]
                        team_two = game[2][2]
                        team_one_score = int(input(f"What is the score for {game[1][2].name}?: "))
                        team_two_score = int(input(f"What is the score for {game[2][2].name}?: "))
                        team_one_IDs = []
                        # get player id's to pass to self.add_game()
                        for player in team_one.team_members:
                            team_one_IDs.append(player.playerID)
                        team_two_IDs = []
                        for player in team_two.team_members:
                            team_two_IDs.append(player.playerID)

                        self.add_game(team_one_IDs, team_two_IDs, team_one_score, team_two_score)
                        if team_one_score > team_two_score:
                            advancers.append(game[1])
                        else:
                            advancers.append(game[2])
                        games_left.pop(game_index)
                    game_index += 1
            sorted_teams = advancers

        print(f"\nThe winner(s) of this tournament are {advancers[0][2].name}. Congratulations!")
        print("--------------------TOURNAMENT END--------------------")
