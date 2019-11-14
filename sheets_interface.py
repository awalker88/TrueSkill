import pickle as pkl
from datetime import date, timedelta
from os import getcwd, listdir

import pandas as pd
import pygsheets as pyg
from prettytable import PrettyTable


def add_new_game_responses(game_responses_ss: pyg.Worksheet, history, ask_to_add=True):
    """ Pulls all responses from sheet, figures out which ones are new, and returns them formatted for adding to History
    :param game_responses_ss: worksheet to pull responses from
    :param history: History class containing your roster
    :returns: list of new responses that are easily read by add_game(): [[team_one], [team_two], team_one_score,
                                                                          team_two_score, timestamp, notes]
    """
    # load previous game submissions
    if 'previous_game_responses.pkl' not in listdir(getcwd()):
        header = pd.DataFrame(columns=['timestamp', 'team_one', 'team_two', 'team_one_score', 'team_two_score',
                                       'extra_notes'])
        pkl.dump(header, open('previous_game_responses.pkl', 'wb'))
    previous = pkl.load(open('previous_game_responses.pkl', 'rb'))

    # load in all submissions in google sheet
    current = pd.DataFrame(game_responses_ss.get_all_values())
    current.columns = ['timestamp', 'team_one', 'team_two', 'team_one_score', 'team_two_score', 'notes']
    current = current[current.timestamp != '']  # remove blank rows
    current = current[current.timestamp != 'Timestamp']  # gets rid of sheet header row

    # we want just new submissions, so (in set notation), this does: current - previous
    new_submissions_df = pd.concat([current, previous, previous], sort=False).drop_duplicates(keep=False)
    new_submissions = new_submissions_df.values.tolist()

    # delete all games and re-add all the ones in current that aren't new, as the google sheets game list should be
    # the master list. a game may be in current but not in previous if it was an error and I deleted on the google sheet
    history.clear_game_database(verbose=False)
    print("Re-adding old games")
    current_submissions = pd.concat([current, new_submissions_df, new_submissions_df], sort=False).drop_duplicates(keep=False).values.tolist()
    for index, submission in enumerate(current_submissions):
        current_submissions[index] = [submission[1].replace(' ', '').split(','),  # team one
                                      submission[2].replace(' ', '').split(','),  # team two
                                      int(submission[3]),  # team one score
                                      int(submission[4]),  # team two score
                                      submission[0],  # timestamp
                                      submission[5]]  # notes
    for submission in current_submissions:
        history.add_game(team_one=submission[0], team_two=submission[1], team_one_score=submission[2],
                         team_two_score=submission[3], timestamp=submission[4], notes=submission[5])
    history.save_game_database()

    # now that all the old games are re-added and up to date, add new submissions if there are any
    if len(new_submissions) == 0:
        print("No new game submissions.")
    else:
        # format responses into: [[team_one], [team_two], team_one_score, team_two_score, timestamp, notes]
        for index, submission in enumerate(new_submissions):
            new_submissions[index] = [submission[1].replace(' ', '').split(','),  # team one
                                      submission[2].replace(' ', '').split(','),  # team two
                                      int(submission[3]),  # team one score
                                      int(submission[4]),  # team two score
                                      submission[0],  # timestamp
                                      submission[5]]  # notes

        # potential new games
        if ask_to_add:
            table = PrettyTable(field_names=['Team One', 'Team Two', 'Team One Score', 'Team Two Score', 'Timestamp'])
            for submission in new_submissions:
                table.add_row([submission[0], submission[1], submission[2], submission[3], submission[4]])
            print(f"Potential {len(new_submissions)} new game(s)")
            print(table)

        # now that we know everyone is in the system, add the games
        for submission in new_submissions:
            if ask_to_add:
                get = input(f'\nDo you want to add {submission[0]} ({submission[2]}) vs. {submission[1]} ({submission[3]}) '
                            f'(submitted: {submission[4]})? (y/n): ')
                if get.lower() == 'y':
                    history.add_game(team_one=submission[0], team_two=submission[1], team_one_score=submission[2],
                                     team_two_score=submission[3], timestamp=submission[4], notes=submission[5])
            else:
                history.add_game(team_one=submission[0], team_two=submission[1], team_one_score=submission[2],
                                 team_two_score=submission[3], timestamp=submission[4], notes=submission[5])

        # update the game history
        combined = pd.concat([current, previous], ignore_index=True, sort=False)
        combined = combined.drop_duplicates()
        pkl.dump(combined, open('previous_game_responses.pkl', 'wb'))


def add_new_players(player_responses_ss: pyg.Worksheet, history, ask_to_add=True):
    """
    Retrieves and checks new playerID requests
    :param player_responses_ss:
    :param history: History class that we pull the roster from
    :return: list of new [timestamp, name]s
    """
    # load
    if 'previous_playerID_responses.pkl' not in listdir(getcwd()):
        header = pd.DataFrame(columns=['timestamp', 'name'])
        pkl.dump(header, open('previous_playerID_responses.pkl', 'wb'))
    previous = pkl.load(open('previous_playerID_responses.pkl', 'rb'))

    # load in new playerID submissions
    current = pd.DataFrame(player_responses_ss.get_all_values())
    current.columns = ['timestamp', 'name']
    current = current[current.timestamp != '']  # remove blank rows
    current = current[current.timestamp != 'Timestamp']  # gets rid of sheet header row

    # in set notation, this does: current - previous
    new_submissions_df = pd.concat([current, previous, previous], sort=False).drop_duplicates(keep=False)
    new_submissions = new_submissions_df.values.tolist()

    # delete all players and re-add all the ones in current that aren't new, as the google sheets player list should be
    # the master list. a player may be in current but not in previous if it was an error and I deleted that player
    # on the google sheet
    history.clear_roster(verbose=False)
    print("Re-adding old players")
    current_submissions = pd.concat([current, new_submissions_df, new_submissions_df], sort=False).drop_duplicates(keep=False).values.tolist()
    for submission in current_submissions:
        history.add_player(submission[1])
    history.save_roster()

    # now that all the old players are re-added and up to date, add new submissions if there are any
    if len(new_submissions) == 0:
        print("No new players")
    else:
        if ask_to_add:
            print("Current roster:")
            history.print_roster()
        for submission in new_submissions:
            # see if anyone else in the roster has that exact name
            for playerID in history.roster:
                if history.roster[playerID].name == submission[1]:
                    print(f"\nThere is already a player with name {submission[1]}, make sure it's not duplicate.")
            if ask_to_add:
                get = input(f'\nDo you want to add {submission[1]} (submitted: {submission[0]})? (y/n)?')
                if get.lower() == 'y':
                    history.add_player(submission[1])
            else:
                history.add_player(submission[1])

    # TODO: add reset players part (and explanation why!)
    combined = pd.concat([current, previous], ignore_index=True, sort=False)
    combined = combined.drop_duplicates()
    pkl.dump(combined, open('previous_playerID_responses.pkl', 'wb'))


def update_rankings(rankings_ss: pyg.Worksheet, history, first_rankings_cell, last_rankings_cell):
    """
    Gets top players in a history's roster and updates the ranking table in rankings_ss
    :param rankings_ss: google sheet with rankings table
    :param history: History class with roster you want to pull from
    :param first_rankings_cell: top left cell of your rankings table
    :param last_rankings_cell: top right cell of your rankings table
    :return:
    """
    ranking_list = []
    for playerID in history.roster:
        player = history.roster[playerID]
        ranking_list.append([player.ranking_score, player.name, player.playerID])

    ranking_list.sort()
    ranking_list.reverse()
    for i, lst in enumerate(ranking_list):
        lst.insert(0, i + 1)
        lst[1], lst[2], lst[3] = lst[2], lst[3], lst[1]  # format for output to chart

    rankings_ss.clear(first_rankings_cell, last_rankings_cell[0] + '1000')  # clears range to paste player rankings
    model_cell = pyg.Cell('A1')
    rankings_ss.get_values(first_rankings_cell, last_rankings_cell[0] + '1000', returnas='range') \
        .apply_format(model_cell)  # format range to be blank
    rankings_ss.update_values(first_rankings_cell, ranking_list)  # TODO: Fix when there are no players and rl is empty
    print('rankings_ss updated')


def update_skill_by_day(skill_by_day_ss: pyg.Worksheet, start_date, history):
    """
    updates skill history sheet with new dates and players
    :param skill_by_day_ss: google sheet to update
    :param start_date: date you want to first track skill history from
    :param history: History class containing players and games
    :return: None
    """
    base = date.today()
    num_days = base - start_date

    date_header = ['playerID']
    for i in range(num_days.days + 1):
        date_header.append(str(start_date + timedelta(i)))

    date_df = pd.DataFrame(columns=date_header)
    date_df['playerID'] = [history.roster[key].playerID for key in history.roster]

    date_header.pop(0)  # removes playerID column so it's just dates again
    # loop through and add skill for that day if it exists, else repeat the previous date's skill
    for index in range(len(date_df)):
        playerID = date_df['playerID'][index]
        player = history.roster[playerID]
        # all players start at 0 until their first non-zero ranking score, then their latest is... their latest
        # this way the graph will look consistent across time even if players don't play every day
        latest_ranking = 0
        for col in date_header:
            if col in player.skill_by_day:
                date_df[col][index] = player.skill_by_day[col]
                latest_ranking = player.skill_by_day[col]
            else:
                date_df[col][index] = latest_ranking

    skill_by_day_ss.clear()
    skill_by_day_ss.update_values('A1', [date_df.columns.values.tolist()])
    skill_by_day_ss.update_values('A2', date_df.values.tolist())
    print('skill_by_day updated')


def update_skill_by_game(skill_by_game_ss: pyg.Worksheet, history):
    player_list = []
    max_games = 0
    header = ['playerID']
    for playerID in history.roster:
        skill_by_game = history.roster[playerID].skill_by_game
        if len(skill_by_game) > max_games:
            max_games = len(skill_by_game)

        # want to make sure that all
        player_list.append(skill_by_game)

        skill_by_game.insert(0, playerID)

        # format header so it reads player ID, Game 1, Game 2, ...
        header = [f'Game {i}' for i in range(1, max_games + 1)]
        header.insert(0, 'playerID')

    skill_by_game_ss.clear()
    skill_by_game_ss.update_values('A1', [header])
    skill_by_game_ss.update_values('A2', player_list)
    print('skill_by_game updated')


def update_champions_list(champions_ss, start_date: str, history):
    # make sure that start date is a monday
    split_date = start_date.split('-')
    start_date = date(int(split_date[0]), int(split_date[1]), int(split_date[2]))
    if date.isoweekday(start_date) != 1:
        print('start_date_str is not a monday. will be converted to previous monday.')
        start_date = start_date - timedelta(date.isoweekday(start_date) - 1)

    # get list of dates that need champions
    today = date.today()
    new_champion_dates = []  # list of dates as strings where a champion should have been declared

    new_champion_date = start_date
    while today - new_champion_date >= timedelta(0):
        new_champion_dates.append(new_champion_date.strftime('%Y-%m-%d'))
        new_champion_date += timedelta(7)

    # find champion on each date
    champions_list = [['Week', 'Player Name', 'Player ID', 'Ranking Score']]
    for monday in new_champion_dates:
        potential_champion = ['', '']  # store highest skilled person we've seen so far
        highest_skill = 0
        for playerID in history.roster:
            player = history.roster[playerID]
            skill_on_monday = player.get_skill_on_day(monday)
            if skill_on_monday > highest_skill:
                potential_champion = [player.name, player.playerID]
                highest_skill = skill_on_monday
        champions_list.append([monday, potential_champion[0], potential_champion[1], highest_skill])

    # update champions tab
    champions_ss.clear('A1', 'D100')
    champions_ss.update_values('A1', champions_list)
    print('champions_list updated')


def update_player_list(player_list_ss: pyg.Worksheet, history):
    """
    :param player_list_ss: google sheet you want to update
    :param history: History class with roster of players
    :return: None
    """
    roster_list = [['PlayerID', 'Name', 'Win Rate', 'Games Played', 'Wins', 'Losses', 'Draws',
                    'Rating Score', 'Raw Skill', 'Uncertainty', 'Points Scored', 'Points Lost',
                    'Average Points Per Game', 'Average Point Margin', 'Current Winning Streak',
                    'Longest Winning Streak', 'Current Losing Streak', 'Longest Losing Streak']]
    for playerID in history.roster:
        roster_list.append([playerID,
                            history.roster[playerID].name,
                            history.roster[playerID].get_win_percentage(),
                            history.roster[playerID].games_played,
                            history.roster[playerID].wins,
                            history.roster[playerID].losses,
                            history.roster[playerID].draws,
                            history.roster[playerID].ranking_score,
                            round(history.roster[playerID].skill.mu, 2),
                            round(history.roster[playerID].skill.sigma, 2),
                            history.roster[playerID].points_scored,
                            history.roster[playerID].points_lost,
                            history.roster[playerID].average_ppg,
                            history.roster[playerID].average_point_margin,
                            history.roster[playerID].current_winning_streak,
                            history.roster[playerID].longest_winning_streak,
                            history.roster[playerID].current_losing_streak,
                            history.roster[playerID].longest_losing_streak])
    player_list_ss.clear('A1', 'P101')
    player_list_ss.update_values('A1', roster_list)
    print('player_list updated')


def update_game_list(game_list_sheet, history):
    """
    Updates 'Game List' sheet to include every game in history's game history
    :param game_list_sheet: sheet to be updated
    :param history: History class containing the game history
    :return: None
    """
    game_database = history.game_database

    game_list_sheet.clear()

    formatted = [['Timestamp', 'Team One', 'Team Two', 'Team One Score', 'Team Two Score', 'Team One Win Probability']]
    for game_key in game_database:
        game = game_database[game_key]
        formatted.append([game.timestamp, game.get_team_name(1), game.get_team_name(2), game.team_one_score,
                          game.team_two_score, round(game.t1_win_prob / 100, 4)])
    game_list_sheet.update_values('A1', formatted)
    print('game_list updated')

