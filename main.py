from History import History
import trueskill as ts
from trueskill import BETA, rate
from Game import Game

h = History()
h.clear_roster()

h.add_player("andrew", playerID="andrew97")
h.add_player("erin", playerID="erin98")
h.add_player("jesse", playerID="jesse12")
h.add_player("sierra", playerID="sierra14")
h.add_player("michelle", playerID="michelle24")
h.add_player("brad", playerID="brad41")
h.add_player("devin", playerID="devin45")
h.add_player("isabelle", playerID="isabelle59")
h.add_player("ruth", playerID="ruth95")
h.add_player("ken", playerID="ken62")

p1 = h.roster["andrew97"]
p2 = h.roster["erin98"]
p3 = h.roster["jesse12"]
p4 = h.roster["sierra14"]

g = Game([p1], [p2], 21, 19, 1)
print(p1)

# rating_groups = [{p1: p1.skill}, {p2: p2.skill}]
#
# for i in range(1):
#     rating_groups = rate(rating_groups, ranks=[0, 1])
#
# for team in rating_groups:
#     for player in team:
#         player.skill = team[player]

