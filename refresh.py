from datetime import date, datetime

import pygsheets as pyg

import sheets_interface
from History import History

# TODO: fix adding game, player notification

# configuration
spreadsheet_name = 'IBM Rochester Ping Pong'
frc = 'C3'  # change if rankings table is moved
update_time_cell = 'I15'  # cell that contains time of the last refresh

# connect to worksheets
gc = pyg.authorize()

workbook: pyg.Spreadsheet = gc.open(spreadsheet_name)
rankings_ss: pyg.Worksheet = workbook.worksheet_by_title('Rankings')
champion_ss: pyg.Worksheet = workbook.worksheet_by_title('Weekly Champions')
player_list_ss: pyg.Worksheet = workbook.worksheet_by_title('Player List')
game_responses_ss: pyg.Worksheet = workbook.worksheet_by_title('Game Responses')
playerID_responses_ss: pyg.Worksheet = workbook.worksheet_by_title('Player ID Responses')
skill_by_day_ss: pyg.Worksheet = workbook.worksheet_by_title('Skill By Day')
skill_by_game_ss: pyg.Worksheet = workbook.worksheet_by_title('Skill By Game')
game_list_ss: pyg.Worksheet = workbook.worksheet_by_title('Game List')

h = History()

lrc = 'F' + str((2 + len(h.roster)))

# add new players
sheets_interface.add_new_players(playerID_responses_ss, h, ask_to_add=True)

# add new games
new_games = sheets_interface.add_new_game_responses(game_responses_ss, h, ask_to_add=True)

# update Rankings page
sheets_interface.update_rankings(rankings_ss, h, frc, lrc)

# update Skill By Day page
sheets_interface.update_skill_by_day(skill_by_day_ss, date(2019, 3, 19), h)

# update Skill By Game page
sheets_interface.update_skill_by_game(skill_by_game_ss, h)

# update Champions page
sheets_interface.update_champions_list(champion_ss, start_date='2019-03-25', history=h)

# update Player List page
sheets_interface.update_player_list(player_list_ss, h)

# update Game List page
sheets_interface.update_game_list(game_list_ss, h)

# update 'Last Updated' cell
now = datetime.now()
rankings_ss.update_value(update_time_cell, f'{now.strftime("%m-%d-%Y %H:%M:%S")}')
