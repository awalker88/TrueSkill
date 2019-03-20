import pygsheets as pyg
from History import History
from datetime import date, datetime
import sheets_interface


# configuration
h = History()
spreadsheet_name = 'IBM Rochester Ping Pong'
frc = 'C3'  # change if rankings table is moved
lrc = 'F' + str((2 + len(h.roster)))
update_time_cell = 'H15'  # cell that contains time of the last refresh

# connect to worksheets
gc = pyg.authorize()

workbook: pyg.Spreadsheet = gc.open(spreadsheet_name)
rankings_ss: pyg.Worksheet = workbook.worksheet_by_title('Rankings')
champion_ss: pyg.Worksheet = workbook.worksheet_by_title('Weekly Champions')
player_list_ss: pyg.Worksheet = workbook.worksheet_by_title('Player List')
game_responses_ss: pyg.Worksheet = workbook.worksheet_by_title('Game Responses')
playerID_responses_ss: pyg.Worksheet = workbook.worksheet_by_title('Player ID Responses')
skill_history_ss: pyg.Worksheet = workbook.worksheet_by_title('Skill History')
game_list_ss: pyg.Worksheet = workbook.worksheet_by_title('Game List')

# add new players
sheets_interface.add_new_players(playerID_responses_ss, h)

# add new games
new_games = sheets_interface.get_new_game_responses(game_responses_ss, h)
sheets_interface.add_new_game_responses(new_games, h)

# update Rankings page
sheets_interface.update_rankings(rankings_ss, h, frc, lrc)

# update Skill History page
sheets_interface.update_skill_history(skill_history_ss, date(2019, 3, 11), h)

# update Champions page
sheets_interface.update_champions_list(champion_ss, rankings_ss, frc, lrc)

# update Player List page
sheets_interface.update_player_list(player_list_ss, h)

# update Game List page
sheets_interface.update_game_list(game_list_ss, h)

# update 'Last Updated' cell
now = datetime.now()
rankings_ss.update_value(update_time_cell, f'{now.strftime("%m-%d-%Y %H:%M:%S")}')
