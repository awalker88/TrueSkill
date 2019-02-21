from Player import Player
from Game import Game
import pickle
from History import History

h = History()
h.clear_roster()

# TODO: add players to player roster
h.add_player("andrew", "andrew97", skill=100)
h.add_player("erin", "erin98", skill=150)
h.add_player("jesse", "jesse12", skill=200)
h.add_player("sierra", "sierra14", skill=250)
h.add_player("michelle", "michelle24", skill=300)
h.add_player("brad", "brad41", skill=350)
h.add_player("devin", "devin45", skill=400)
h.add_player("isabelle", "isabelle59", skill=450)
h.add_player("ruth", "ruth95", skill=500)
h.add_player("ken", "ken62", skill=550)


# h.tournament([["andrew97", "erin98"],
#               ["jesse12", "sierra14"],
#               ["michelle24", "brad41"],
#               ["devin45", "isabelle59"],
#               ["ruth95", "ken62"]])

h.tournament([["andrew97"], ["erin98"],
              ["jesse12"], ["sierra14"],
              ["michelle24"], ["brad41"],
              ["devin45"], ["isabelle59"],
              ["ruth95"], ["ken62"]])
