import pygsheets as pyg
import pandas as pd
import pickle as pkl
from os import getcwd, listdir
from time import sleep
from datetime import date, timedelta

# TODO: create Top Upsets sheet
# TODO: add player with longest winning streak (and losing?) to Rankings Pages
# TODO: make sure adding games locally updates the google sheet too
# TODO: add easy to read game history sheet (highlight winner)
# TODO: write intro/instructions for sheet


def new_game_responses(game_responses_sht, roster):
    """ Pulls the new responses from sheet and returns a list well-formatted for adding to History
    :param game_responses_sht: worksheet to pull new responses from
    :param roster: roster of players from History class
    :returns: list that is easily read by add_game(), looks like [[team_one], [team_two], team_one_score,
                                                                   team_two_score, timestamp, notes]
    """
    # load previous game submissions
    if 'previous_game_responses.pkl' not in listdir(getcwd()):
        header = pd.DataFrame(columns=['timestamp', 'team_one', 'team_two', 'team_one_score', 'team_two_score',
                                       'extra_notes'])
        pkl.dump(header, open('previous_game_responses.pkl', 'wb'))
    previous = pkl.load(open('previous_game_responses.pkl', 'rb'))

    # load in new game submissions
    current = pd.DataFrame(game_responses_sht.get_all_values())
    current.columns = ['timestamp', 'team_one', 'team_two', 'team_one_score', 'team_two_score', 'notes']
    current = current[current.timestamp != '']  # remove blank rows
    current = current[current.timestamp != 'Timestamp']  # gets rid of sheet header row

    # in set notation, this does current - previous
    new_submissions = pd.concat([current, previous, previous], sort=False).drop_duplicates(keep=False)

    # format responses into: [[team_one], [team_two], team_one_score, team_two_score, timestamp, notes]
    new_submissions = new_submissions.values.tolist()
    lst = []
    for submission in new_submissions:
        lst.append([submission[1].replace(' ', '').split(','),  # team one
                    submission[2].replace(' ', '').split(','),  # team two
                    int(submission[3]),                         # team one score
                    int(submission[4]),                         # team two score
                    submission[0],                              # timestamp
                    submission[5]])                             # notes

    # print out players if playerID not in roster
    is_new = False
    for response in lst:
        for playerID in response[0] + response[1]:
            if playerID not in roster:
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

    return lst


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


def get_new_players(player_responses_sht, history):
    """
    Retrieves and checks new playerID requests
    :param player_responses_sht:
    :param roster:
    :return: list of new [timestamp, name]s
    """
    # load
    if 'previous_playerID_responses.pkl' not in listdir(getcwd()):
        header = pd.DataFrame(columns=['timestamp', 'name'])
        pkl.dump(header, open('previous_playerID_responses.pkl', 'wb'))
    previous = pkl.load(open('previous_playerID_responses.pkl', 'rb'))

    # load in new playerID submissions
    current = pd.DataFrame(player_responses_sht.get_all_values())
    current.columns = ['timestamp', 'name']
    current = current[current.timestamp != '']  # remove blank rows
    current = current[current.timestamp != 'Timestamp']  # gets rid of sheet header row

    # in set notation, this does: current - previous
    to_add = []
    new_submissions = pd.concat([current, previous, previous], sort=False).drop_duplicates(keep=False)
    for submission in new_submissions.values:
        # see if anyone else in the roster has that exact name
        for playerID in history.roster:
            if history.roster[playerID].name == submission[1]:
                print(f"There is already a player with name {submission[1]}, make sure it's not duplicate.")
        #
        history.print_roster()
        get = input(f'Do you want to add {submission[1]} (submitted: {submission[0]})? Current roster is above. (y/n)?')
        if get.lower() == 'y':
            to_add.append(submission)

    combined = pd.concat([current, previous], ignore_index=True, sort=False)
    combined = combined.drop_duplicates()
    pkl.dump(combined, open('previous_playerID_responses.pkl', 'wb'))

    return to_add


def add_new_players(new_playerID_responses, history):
    if not new_playerID_responses:
        print("No new playerID responses")
    else:
        print(f"{len(new_playerID_responses)} new player response(s)")
        for response in new_playerID_responses:
            history.add_player(response[1])


def update_rankings(rankings_sht, roster, first_rankings_cell, last_rankings_cell):
    ranking_list = []
    for playerID in roster:
        player = roster[playerID]
        ranking_list.append([player.ranking_score, player.name, player.playerID])

    ranking_list.sort()
    ranking_list.reverse()
    for i, lst in enumerate(ranking_list):
        lst.insert(0, i + 1)
        lst[1], lst[2], lst[3] = lst[2], lst[3], lst[1]  # format for output to chart

    rankings_sht.clear(first_rankings_cell, last_rankings_cell[0] + '1000')  # clears range to paste player rankings
    model_cell = pyg.Cell('A1')
    rankings_sht.get_values(first_rankings_cell, last_rankings_cell[0] + '1000', returnas='range')\
        .apply_format(model_cell)  # format range to be blank
    model_cell.borders = {"top": {
                                "style": "SOLID",
                                "width": 1,
                                "color": {}},
                          "bottom": {
                              "style": "SOLID",
                              "width": 1,
                              "color": {}},
                          "left": {
                              "style": "SOLID",
                              "width": 1,
                              "color": {}},
                          "right": {
                              "style": "SOLID",
                              "width": 1,
                              "color": {}}}

    rankings_sht.get_values(first_rankings_cell, last_rankings_cell, returnas='range').apply_format(model_cell)
    rankings_sht.update_values(first_rankings_cell, ranking_list)  # TODO: Fix when there are no players and rl is empty


def update_skill_history(skill_history, start_date, roster):
    base = date.today()
    num_days = base - start_date

    date_header = ['playerID']
    for i in range(num_days.days + 1):
        date_header.append(str(start_date + timedelta(i)))

    date_df = pd.DataFrame(columns=date_header)
    date_df['playerID'] = [roster[key].playerID for key in roster]

    date_header.pop(0)  # removes playerID column so it's just dates again
    # loop through and add skill for that day if it exists, else repeat the previous date's skill
    for index in range(len(date_df)):
        playerID = date_df['playerID'][index]
        player = roster[playerID]
        # all players start at 0 until their first non-zero ranking score, then their latest is... their latest
        # this way the graph will look consistent across time even if players don't play every day
        latest_ranking = 0
        for col in date_header:
            if col in player.skill_history:
                date_df[col][index] = player.skill_history[col]
                latest_ranking = player.skill_history[col]
            else:
                date_df[col][index] = latest_ranking

    skill_history.clear()
    skill_history.update_values('A1', [date_df.columns.values.tolist()])
    skill_history.update_values('A2', date_df.values.tolist())


def update_champions_list(champions_sheet, rankings_sheet, first_rankings_cell, last_rankings_cell):
    """
    if date when run is 7 or more days since latest entry in Previous Champions sheet, adds champion based on current
    champion
    :param champions_sheet: sheet with previous champions
    :param rankings_sheet: sheet with current rankings
    :param roster: roster of Players
    :return: None
    """
    current = pd.DataFrame(champions_sheet.get_all_values())
    current = current[1:]  # gets rid of header row
    current.columns = ['week', 'champion', 'playerID', 'rating']
    current = current[current.week != '']  # remove blank rows
    latest_week = current['week'][len(current)]
    split = latest_week.split("/")
    latest_week = date(2000+int(split[2]), int(split[0]), int(split[1]))  # note: have to modify after the year 2099
    if (date.today() - latest_week).days >= 7:
        # if it's been a week since we last crowned a champion, crown a new one
        champion = rankings_sheet.get_values(first_rankings_cell, last_rankings_cell[0] + first_rankings_cell[1:])
        last_monday = str(date.today() - timedelta(days=date.today().weekday()))
        champion[0][0] = f"{last_monday[5:7]}/{last_monday[8:10]}/{last_monday[2:4]}"
        combined = pd.concat([current, pd.DataFrame(champion, columns=['week', 'champion', 'playerID', 'rating'])])
        champions_sheet.update_values('A2', combined.values.tolist())
        print(f"New Champion: {champion}")
    else:
        print("Not time for a new champion yet.")


def update_top_upsets(roster):
    pass


def update_player_list(player_list_sheet: pyg.Worksheet, roster):
    roster_list = [['PlayerID', 'Name', 'Win Rate', 'Wins', 'Losses', 'Draws', 'Games Played',
                    'Rating Score', 'Points Scored', 'Points Lost', 'Average Points Per Game', 'Average Point Margin',
                    'Current Winning Streak', 'Longest Winning Streak', 'Current Losing Streak',
                    'Longest Losing Streak']]
    for playerID in roster:
        roster_list.append([playerID,
                            roster[playerID].name,
                            roster[playerID].get_win_rate(),
                            roster[playerID].wins,
                            roster[playerID].losses,
                            roster[playerID].draws,
                            roster[playerID].games_played,
                            roster[playerID].ranking_score,
                            roster[playerID].points_scored,
                            roster[playerID].points_lost,
                            roster[playerID].average_ppg,
                            roster[playerID].average_point_margin,
                            roster[playerID].current_winning_streak,
                            roster[playerID].longest_winning_streak,
                            roster[playerID].current_losing_streak,
                            roster[playerID].longest_losing_streak
                            ])
    player_list_sheet.clear('A1', 'P101')
    player_list_sheet.update_values('A1', roster_list)

def update_game_list(game_list):
    pass
