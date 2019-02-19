from Player import Player
from Game import Game
import pickle
from History import History

h = History()

h.clear_game_history()
h.add_game(["Andrew85", "Erin15"], ["Jesse48", "Sierra69"], 21, 19, 1)

h.print_game_history()