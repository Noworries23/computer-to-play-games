from GameEngine import GameEngine
from RandomPlayer import RandomPlayer
from TiePlayer import TiePlayer

from SuperTicTacToe.SuperTicTacToeBoard import SuperTicTacToeBoard
from SuperTicTacToe.SuperTicTacToeHumanPlayer import SuperTicTacToeHumanPlayer
from SuperTicTacToe.SuperTicTacToeYOURNAMEPlayer import SuperTicTacToeYOURNAMEPlayer
from SuperTicTacToe.SuperTicTacToeDeenPlayer import SuperTicTacToeDeenPlayer

def run_test_suite(num_games=100):
    # Initialize your model and the opponent
    # Testing against RandomPlayer is standard for a baseline win rate
    my_model = SuperTicTacToeDeenPlayer()
    opponent = SuperTicTacToeYOURNAMEPlayer() 
    players = [my_model, opponent]

    stats = {
        "wins": 0,
        "losses": 0,
        "ties": 0
    }

    print(f"Starting benchmark: {num_games} games...")

    for i in range(num_games):
        # We alternate who goes first each game for a fair test
        p1, p2 = (players[0], players[1]) if i % 2 == 0 else (players[1], players[0])
        
        board = SuperTicTacToeBoard(p1, p2)
        engine = GameEngine(board)

        # Set run(False) to disable the interface for maximum speed
        winner = engine.run(True)

        if winner == my_model:
            stats["wins"] += 1
        elif winner is None:
            stats["ties"] += 1
        else:
            stats["losses"] += 1

        # Optional: Print progress every 10 games
        if (i + 1) % 1 == 0:
            print(f"Completed {i + 1}/{num_games} games...")

    # Calculate Results
    win_rate = (stats["wins"] / num_games) * 100
    
    print("\n" + "="*30)
    print(f"RESULTS FOR {my_model.name}")
    print("="*30)
    print(f"Total Games: {num_games}")
    print(f"Wins:        {stats['wins']}")
    print(f"Losses:      {stats['losses']}")
    print(f"Ties:        {stats['ties']}")
    print(f"Win Rate:    {win_rate:.2f}%")
    print("="*30)

if __name__ == "__main__":
    run_test_suite(100)