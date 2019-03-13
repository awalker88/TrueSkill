import pygsheets as pyg
import pandas as pd
import pickle as pkl
from os import getcwd, listdir, remove
from History import History
from time import sleep
import numpy as np
import datetime


def main():
    # make roster
    h = History()
    h.clear_game_history()

    # connect to worksheets
    gc = pyg.authorize()
    workbook: pyg.Spreadsheet = gc.open('Ping Pong Rankings')
    rankings_sheet: pyg.Worksheet = workbook.worksheet_by_title('Rankings')
    # champions_sheet: pyg.Worksheet = workbook.worksheet_by_title('Previous Champions')
    # top_upsets_sheet: pyg.Worksheet = workbook.worksheet_by_title('Top Upsets')
    # player_list_sheet: pyg.Worksheet = workbook.worksheet_by_title('Player List')
    form_responses: pyg.Worksheet = workbook.worksheet_by_title('Form Responses')

    # get new responses
    # new_responses = get_new_responses(form_responses, h.roster)
    #
    # # add new responses as Games to History
    # if not new_responses:
    #     print("No new responses")
    # else:
    #     for response in new_responses:
    #         h.add_game(response[0], response[1], response[2], response[3], response[4])

    # update Rankings sheet
    update_rankings(rankings_sheet, h.roster)

    # update Champions sheet

    # update Top Upsets sheet

    # update Skill History



def get_new_responses(form_response_sht, roster):
    """ Pulls the new responses from sheet and returns a list well-formatted for adding to History
    :param form_response_sht: worksheet to pull new responses from
    :param roster: roster of players from History class
    :returns: list that is easily read by add_game(), looks like [[team_one], [team_two], team_one_score,
                                                                   team_two_score, timestamp, notes]
    """
    # load previous game submissions
    if 'previous_form_response.pkl' not in listdir(getcwd()):
        header = pd.DataFrame(columns=['timestamp', 'team_one', 'team_two', 'team_one_score', 'team_two_score',
                                       'extra_notes'])
        pkl.dump(header, open('previous_form_response.pkl', 'wb'))
    previous = pkl.load(open('previous_form_response.pkl', 'rb'))

    # load in new game submissions
    current = pd.DataFrame(form_response_sht.get_all_values())
    new_header = current.iloc[0]  # grab the first row for the header
    current = current[1:]  # take the data less the header row
    current.columns = new_header  # set the header row as the df header
    current.columns = ['timestamp', 'team_one', 'team_two', 'team_one_score', 'team_two_score', 'notes']
    current = current[current.timestamp != '']  # remove blank rows

    # relative difference between current and previous
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
    pkl.dump(combined, open('previous_form_response.pkl', 'wb'))

    return lst


def update_rankings(rankings_sht, roster):
    ranking_list = []
    for playerID in roster:
        player = roster[playerID]
        ranking_list.append([player.ranking_score, player.name, player.playerID])

    ranking_list.sort()
    ranking_list.reverse()
    for i, lst in enumerate(ranking_list):
        lst.insert(0, i + 1)
        lst[1], lst[2], lst[3] = lst[2], lst[3], lst[1]  # format for output to chart

    rankings_sht.clear('F3', 'I1000')  # clears range to paste player rankings
    model_cell = pyg.Cell('A1')
    rankings_sht.get_values('F3', 'I1000', returnas='range').apply_format(model_cell)  # format range to be blank
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

    rankings_sht.get_values('F3', 'I' + str((2 + len(roster))), returnas='range').apply_format(model_cell)
    rankings_sht.update_values('F3', ranking_list)


def update_champions_list(roster):
    pass


def update_top_upsets(roster):
    pass


def update_skill_history(start_date, roster):
    base = datetime.datetime.today()
    num_days = base - start_date
    date_list = [base - datetime.timedelta(days=x) for x in range(0, num_days)]
    print(date_list)


def update_player_list(roster, player_list: pyg.Worksheet):
    player_list.update_values('A1', roster.tolist())


main()
