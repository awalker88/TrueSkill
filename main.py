from History import History
from random import randint
h = History()
import pickle as pkl

fresh = True
if fresh:
    h.clear_game_history()
    h.clear_roster()
    h.add_player("andrew", playerID="andrew01")
    h.add_player("erin", playerID="erin01")
    h.add_player("jesse", playerID="jesse01")
    h.add_player("sierra", playerID="sierra01")
    h.add_player("bob", playerID="bob01")
    h.add_player("alice", playerID="alice01")
    h.add_player("john", playerID="john01")
    h.add_player("ken", playerID="ken01")
    h.add_player("walt", playerID="walt01")
    h.add_player("holly", playerID="holly01")
    h.add_player("marie", playerID="marie01")
    h.add_player("dean", playerID="dean01")
    h.add_player("jeff", playerID="jeff01")
    h.add_player("abed", playerID="abed01")
    h.add_player("troy", playerID="troy01")
    h.add_player("britta", playerID="britta01")
    h.add_player("annie", playerID="annie01")
    h.add_player("pierce", playerID="pierce01")
    h.add_player("Cole Karczewski", playerID="colekarczewski01")
    r = {}
    i = 1
    for player in h.roster:
        r[i] = player
        i += 1
    h.suppress = True
    for j in range(100):
        p1 = r[randint(1, 18)]
        p2 = r[randint(1, 18)]
        t1s = randint(1, 22)
        t2s = randint(1, 22)
        while t1s == t2s:
            t2s = randint(1, 22)
        h.add_game([p1], [p2], t1s, t2s)
    h.print_game_history()
    h.print_roster()

    h.roster['andrew01'].skill_history['2019-03-11'] = 300
    h.roster['andrew01'].skill_history['2019-03-12'] = 400
    h.roster['andrew01'].skill_history['2019-03-13'] = 600
    print(h.roster['andrew01'].skill_history)

    h.roster['erin01'].skill_history['2019-03-11'] = 200
    h.roster['erin01'].skill_history['2019-03-12'] = 500
    h.roster['erin01'].skill_history['2019-03-13'] = 900

    h.roster['abed01'].skill_history['2019-03-11'] = 700
    h.roster['abed01'].skill_history['2019-03-13'] = 750

    pkl.dump(h.roster, open(h.roster_name, "wb"))


tournament = False
if tournament:
    h.tournament([["andrew01"],
                  ["erin01"],
                  ["jesse01"],
                  ["bob01"],
                  ["alice01"],
                  ["john01"],
                  ["walt01"],
                  ["holly01"],
                  ["marie01"],
                  ["dean01"],
                  ["jeff01"],
                  ["abed01"],
                  ["troy01"],
                  ["britta01"],
                  ["annie01"],
                  ["ken01"],
                  ["pierce01"]])
