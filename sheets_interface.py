import pygsheets as pyg
import pandas as pd
from pandas import DataFrame
import numpy as np
import pickle as pkl
import os


def main():
    roster = pkl.load(open('roster.pkl', "rb"))

    roster_list = [['Player ID', 'Name', 'Win Rate', 'Skill Mean', 'Skill Variance', 'Ranking Score', 'Games Played']]
    for key in roster:
        p = roster[key]
        roster_list.append([key, p.name, p.get_win_rate(), round(p.skill.mu, 2), round(p.skill.sigma, 2), p.rankingScore,
                            p.wins + p.losses + p.draws])
    roster_np = np.array(roster_list)

    # connect to google sheets
    wkbk = make_connection('Ping Pong Rankings')

    # read new responses
    if 'previous_form_response.pkl' not in os.getcwd():
        pass

    # update player list
    update_player_list(roster_np, wkbk)


def make_connection(sheet_name):
    gc = pyg.authorize()
    return gc.open(sheet_name)


def read_form_responses(wkbk):
    form_sheet = wkbk.worksheet_by_title("Form Responses").get_as_df()
    form_sheet = form_sheet[form_sheet.timestamp != '']  # drop rows that have blank timestamp


def update_rankings(roster):
    pass


def update_champions_list(roster):
    pass


def update_top_upsets(roster):
    pass


def update_player_list(roster, sheet):
    p_sh = sheet.worksheet_by_title("Player List")
    p_sh.update_values('A1', roster.tolist())


main()
