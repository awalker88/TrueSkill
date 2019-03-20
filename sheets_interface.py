import pygsheets as pyg
import pandas as pd
import pickle as pkl
from os import getcwd, listdir
from time import sleep
from datetime import date, timedelta


def get_new_game_responses(game_responses_ss, history):
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
    new_submissions = pd.concat([current, previous, previous], sort=False).drop_duplicates(keep=False)

    # format responses into: [[team_one], [team_two], team_one_score, team_two_score, timestamp, notes]
    new_submissions = new_submissions.values.tolist()
    formatted_new_submissions = []
    for submission in new_submissions:
        formatted_new_submissions.append([submission[1].replace(' ', '').split(','),  # team one
                                          submission[2].replace(' ', '').split(','),  # team two
                                          int(submission[3]),  # team one score
                                          int(submission[4]),  # team two score
                                          submission[0],  # timestamp
                                          submission[5]])  # notes

    # print out players if playerID not in roster
    is_new = False
    for response in formatted_new_submissions:
        for playerID in response[0] + response[1]:
            if playerID not in history.roster:
                print(f"Could not find player with ID: {playerID}")
                is_new = True
    if is_new:
        print("\nPlease add new players to the roster or delete games with unknown players and re-run.\n")
        sleep(0.5)  # makes error message look better
        raise KeyError

    # combine new and old
    combined = pd.concat([current, previous], ignore_index=True, sort=False)
    combined = combined.drop_duplicates()
    pkl.dump(combined, open('previous_game_responses.pkl', 'wb'))

    return formatted_new_submissions


def add_new_game_responses(new_game_responses, history):
    """
    add new responses as Games to History
    :param new_game_responses: list of list of the new responses
    :param history:
    :return: None
    """
    if not new_game_responses:
        print("No new game responses")
    else:
        print(f"{len(new_game_responses)} new response(s)")
        for response in new_game_responses:
            history.add_game(response[0], response[1], response[2], response[3], response[4])


def add_new_players(player_responses_ss, history):
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
    new_submissions = pd.concat([current, previous, previous], sort=False).drop_duplicates(keep=False)
    if len(new_submissions) == 0:
        print("No new players")
    history.print_roster()
    for submission in new_submissions.values:
        # see if anyone else in the roster has that exact name
        for playerID in history.roster:
            if history.roster[playerID].name == submission[1]:
                print(f"\nThere is already a player with name {submission[1]}, make sure it's not duplicate.")
        #
        get = input(f'\nDo you want to add {submission[1]} (submitted: {submission[0]})? (y/n)?')
        if get.lower() == 'y':
            history.add_player(submission[1])

    combined = pd.concat([current, previous], ignore_index=True, sort=False)
    combined = combined.drop_duplicates()
    pkl.dump(combined, open('previous_playerID_responses.pkl', 'wb'))


def update_rankings(rankings_ss, h, first_rankings_cell, last_rankings_cell):
    """
    Gets top players in a history's roster and updates the ranking table in rankings_ss
    :param rankings_ss: google sheet with rankings table
    :param h: History class with roster you want to pull from
    :param first_rankings_cell: top left cell of your rankings table
    :param last_rankings_cell: top right cell of your rankings table
    :return:
    """
    ranking_list = []
    for playerID in h.roster:
        player = h.roster[playerID]
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


def update_skill_history(skill_history_ss, start_date, h):
    """
    updates skill history sheet with new dates and players
    :param skill_history_ss: google sheet to update
    :param start_date: date you want to first track skill history from
    :param h: History class containing players and games
    :return: None
    """
    base = date.today()
    num_days = base - start_date

    date_header = ['playerID']
    for i in range(num_days.days + 1):
        date_header.append(str(start_date + timedelta(i)))

    date_df = pd.DataFrame(columns=date_header)
    date_df['playerID'] = [h.roster[key].playerID for key in h.roster]

    date_header.pop(0)  # removes playerID column so it's just dates again
    # loop through and add skill for that day if it exists, else repeat the previous date's skill
    for index in range(len(date_df)):
        playerID = date_df['playerID'][index]
        player = h.roster[playerID]
        # all players start at 0 until their first non-zero ranking score, then their latest is... their latest
        # this way the graph will look consistent across time even if players don't play every day
        latest_ranking = 0
        for col in date_header:
            if col in player.skill_history:
                date_df[col][index] = player.skill_history[col]
                latest_ranking = player.skill_history[col]
            else:
                date_df[col][index] = latest_ranking

    skill_history_ss.clear()
    skill_history_ss.update_values('A1', [date_df.columns.values.tolist()])
    skill_history_ss.update_values('A2', date_df.values.tolist())


def update_champions_list(champions_ss, rankings_ss, first_rankings_cell, last_rankings_cell):
    """
    if date when run is 7 or more days since latest entry in Previous Champions sheet, adds champion based on current
    champion
    :param champions_ss: sheet with previous champions
    :param rankings_ss: sheet with current rankings
    :param first_rankings_cell: cells to pull champion info from
    :param last_rankings_cell: cells to pull champion info from
    :return: None
    """
    # update champion list
    current = pd.DataFrame(champions_ss.get_all_values())
    current = current[1:]  # gets rid of header row from sheet
    current.columns = ['week', 'champion', 'playerID', 'rating']
    current = current[current.week != '']  # remove blank rows
    latest_week = current['week'][len(current)]
    split = latest_week.split("/")
    latest_week = date(int(split[2]), int(split[0]), int(split[1]))  # note: have to modify after the year 2099
    # check we need to crown a champion
    if (date.today() - latest_week).days >= 7:
        no_players = False
        top_player_is_zero = False
        # checks if a champion even can be crowned
        if rankings_ss.get_value(first_rankings_cell) == '':
            no_players = True
            print('No players in Rankings sheet. No champion.')

        if int(rankings_ss.get_value(last_rankings_cell)) == 0:
            print('Top player has not played any games. No champion.')
            top_player_is_zero = True

        # if it's been a week since we last crowned a champion, crown a new one
        last_monday = str(date.today() - timedelta(days=date.today().weekday()))
        if no_players or top_player_is_zero:
            new_champion = [[last_monday, 'No champion', 'No champion', 'NA']]
        else:
            new_champion = rankings_ss.get_values(first_rankings_cell, last_rankings_cell[0] + first_rankings_cell[1:])
        new_champion[0][0] = f"{last_monday[5:7]}/{last_monday[8:10]}/{last_monday[2:4]}"
        combined = pd.concat([current, pd.DataFrame(new_champion, columns=['week', 'champion', 'playerID', 'rating'])])
        champions_ss.update_values('A2', combined.values.tolist())
        print(f"New Champion added: {new_champion}")
    else:
        print("Not time for a new champion yet.")


def update_player_list(player_list_ss: pyg.Worksheet, h):
    """

    :param player_list_ss: google sheet you want to update
    :param h: History class with roster of players
    :return: None
    """
    roster_list = [['PlayerID', 'Name', 'Win Rate', 'Wins', 'Losses', 'Draws', 'Games Played',
                    'Rating Score', 'Points Scored', 'Points Lost', 'Average Points Per Game', 'Average Point Margin',
                    'Current Winning Streak', 'Longest Winning Streak', 'Current Losing Streak',
                    'Longest Losing Streak']]
    for playerID in h.roster:
        roster_list.append([playerID,
                            h.roster[playerID].name,
                            h.roster[playerID].get_win_percentage(),
                            h.roster[playerID].wins,
                            h.roster[playerID].losses,
                            h.roster[playerID].draws,
                            h.roster[playerID].games_played,
                            h.roster[playerID].ranking_score,
                            h.roster[playerID].points_scored,
                            h.roster[playerID].points_lost,
                            h.roster[playerID].average_ppg,
                            h.roster[playerID].average_point_margin,
                            h.roster[playerID].current_winning_streak,
                            h.roster[playerID].longest_winning_streak,
                            h.roster[playerID].current_losing_streak,
                            h.roster[playerID].longest_losing_streak
                            ])
    player_list_ss.clear('A1', 'P101')
    player_list_ss.update_values('A1', roster_list)


def update_game_list(game_list_sheet, history):
    """
    Updates 'Game List' sheet to include every game in history's game history
    :param game_list_sheet: sheet to be updated
    :param history: History class containing the game history
    :return: None
    """
    game_database = history.game_database

    game_list_sheet.clear()

    formatted = [['Timestamp', 'Team One', 'Team Two', 'Team One Score', 'Team Two Score']]
    for game_key in game_database:
        game = game_database[game_key]
        formatted.append([game.timestamp, game.get_team_name(1), game.get_team_name(2), game.team_one_score,
                          game.team_two_score])

    game_list_sheet.update_values('A1', formatted)
