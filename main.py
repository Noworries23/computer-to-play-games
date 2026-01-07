from GameEngine import GameEngine
from RandomPlayer import RandomPlayer
from TiePlayer import TiePlayer

from SuperTicTacToe.SuperTicTacToeBoard import SuperTicTacToeBoard
from SuperTicTacToe.SuperTicTacToeHumanPlayer import SuperTicTacToeHumanPlayer
from SuperTicTacToe.SuperTicTacToeYOURNAMEPlayer import SuperTicTacToeYOURNAMEPlayer

#import all files in ThirtyOne/StudentFiles here

all_players = []

def set_seeds():
    scores = run_game(all_players)

    run_many_times(all_players, 10)
    # sorted_scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))

    # for item in sorted_scores.items():
    #     print(f"Player {item[0].name}: {item[1]} points")

def run_many_times(players, nTimes):
    score_count = {player: 0 for player in players}
    for i in range(nTimes):
        scores = run_game(players)
        sorted_scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))
        counter = len(players)
        for item in sorted_scores.items():
            score_count[item[0]] += counter
            counter -= 1
            
    score_count = dict(sorted(score_count.items(), key=lambda item: item[1], reverse=True))
    for player in score_count:
        print(f"Player {player.name}: {score_count[player]} total points over {nTimes} games")

def run_game(players):
    board = SuperTicTacToeBoard(players[0], players[1])

    engine = GameEngine(board)

    winner = engine.run(True)
    print(f"Winner: {winner.name}")
    scores = board.scoreBoard()
    return scores

def default_run():
    player1 = SuperTicTacToeYOURNAMEPlayer("Dr. Dong")
    player2 = SuperTicTacToeYOURNAMEPlayer()
    
    run_game([player1, player2])

    # for player in scores:
    #     print(f"Player {player.name}: {scores[player]} points")


if __name__ == "__main__":
    default_run()
    # set_seeds()