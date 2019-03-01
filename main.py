from History import History

h = History()

fresh = True
if fresh:
    h.clear_game_history()
    h.clear_roster()
    h.add_player("andrew", playerID="andrew01")
    h.add_player("erin", playerID="erin01")
    h.add_player("jesse", playerID="jesse01")
    h.add_player("bob", playerID="bob01")
    h.add_player("alice", playerID="alice01")
    h.add_player("Cole Karczewski", playerID="colekarczewski01")


print(h.roster["andrew01"])
h.add_game(["andrew01"], ["erin01"], 21, 23)
print(h.roster["andrew01"])

h.add_game(["andrew01"], ["jesse01"], 23, 21)
print(h.roster["andrew01"])

h.print_roster()

h.print_game_history()

p1 = h.roster['andrew01']
p1.get_upsets(h.gameHistory)

tournament = False
if tournament:
    h.tournament([["andrew01", "jesse01"], ["erin01"], ["bob01", "alice01"]])



