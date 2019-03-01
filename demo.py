from History import History

h = History()
h.suppress = True

make_new_roster_and_game_history = True
print_roster = False
print_game_history = False
run_sample_games = True
run_sample_tournament = False

if make_new_roster_and_game_history:
    h.clear_game_history()
    h.clear_roster()
    h.add_player("andrew", playerID="andrew01")
    h.add_player("erin", playerID="erin01")
    h.add_player("jesse", playerID="jesse01")
    h.add_player("sierra", playerID="sierra01")
    h.add_player("michelle", playerID="michelle01")
    h.add_player("brad", playerID="brad01")
    h.add_player("bob", playerID="bob01")
    h.add_player("alice", playerID="alice01")

if print_roster:
    h.print_roster()

if print_game_history:
    h.print_game_history()

if run_sample_games:
    print("Before 1st game")
    print("---------------")
    print(h.roster["andrew01"])

    print("After 1st game (andrew01 losses to erin01)")
    print("------------------------------------------")
    h.add_game(["andrew01"], ["erin01"], 12, 21, )
    print(h.roster["andrew01"])

    print("After 2nd game (jesse01 losses to andrew01)")
    print("-------------------------------------------")
    h.add_game(["andrew01"], ["jesse01"], 23, 21)
    print(h.roster["andrew01"])

if print_game_history:
    h.print_game_history()

if run_sample_tournament:
    h.tournament([["andrew01", "jesse01"],
                  ["erin01"],
                  ["bob01", "alice01"],
                  ["sierra01", "michelle01"],
                  ['brad01']])

# Enter additional games here



