from GameEngine import GameEngine
from RandomPlayer import RandomPlayer
from TiePlayer import TiePlayer

# from SuperTicTacToe.SuperTicTacToeBoard import SuperTicTacToeBoard
# from SuperTicTacToe.SuperTicTacToeHumanPlayer import SuperTicTacToeHumanPlayer
# from SuperTicTacToe.SuperTicTacToeYOURNAMEPlayer import SuperTicTacToeYOURNAMEPlayer

from SushiGo.SushiGoBoard import SushiGoBoard
from SushiGo.SushiGoHumanPlayer import SushiGoHumanPlayer
from SushiGo.SushiGoCPUPlayerAdapter import SushiGoCPUPlayerAdapter
from SushiGo.SushiGoYOURNAMEPlayer import SushiGoYOURNAMEPlayer
from SushiGo.Card import Card

all_players = []

def set_seeds():
    scores = run_game(all_players)

    run_many_times(all_players, 10)
    # sorted_scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))

    # for item in sorted_scores.items():
    #     print(f"Player {item[0].name}: {item[1]} points")

def run_many_times(players, nTimes, output = True):
    score_count = {player: 0 for player in players}
    for i in range(nTimes):
        scores = run_game(players, output)
        sorted_scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))
        counter = len(players)
        for item in sorted_scores.items():
            score_count[item[0]] += counter
            counter -= 1
            
    score_count = dict(sorted(score_count.items(), key=lambda item: item[1], reverse=True))
    for player in score_count:
        print(f"Player {player.name}: {score_count[player]} total points over {nTimes} games")

def run_game(players, print = True):
    board = SushiGoBoard(players)
    board.output = print

    engine = GameEngine(board)

    engine.run(True)
    #print(f"Winner: {winner.name}")
    scores = board.scoreBoard()
    return scores

def default_run(output = True):
    player1 = SushiGoHumanPlayer("Dr. Dong")
    player2 = RandomPlayer("Random bot 1")
    player3 = RandomPlayer("Random bot 2")
    player4 = SushiGoCPUPlayerAdapter(SushiGoYOURNAMEPlayer())
    player5 = RandomPlayer("Random bot 3")

    scores = run_game([player1, player2, player3, player4, player5], output)

    for player in scores:
        print(f"Player {player.name}: {scores[player]} points")

def run_tests(output = True):
    player1 = SushiGoCPUPlayerAdapter(SushiGoYOURNAMEPlayer("Sashimi"))
    player1.player.priorities[Card.Type.SASHIMI] = 0
    player2 = SushiGoCPUPlayerAdapter(SushiGoYOURNAMEPlayer("Dumpling"))
    player2.player.priorities[Card.Type.DUMPLING] = 0
    player3 = SushiGoCPUPlayerAdapter(SushiGoYOURNAMEPlayer("Tempura"))
    player3.player.priorities[Card.Type.TEMPURA] = 0
    player4 = SushiGoCPUPlayerAdapter(SushiGoYOURNAMEPlayer("Pudding"))
    player4.player.priorities[Card.Type.PUDDING] = 0
    player5 = RandomPlayer("Random bot")

    players = [player1, player2, player3, player4, player5]

    scores = run_many_times(players, 100, output)

if __name__ == "__main__":
     default_run()
    # set_seeds()
    #run_tests(False)