from GameEngine import GameEngine
from RandomPlayer import RandomPlayer
from ThirtyOne.ThirtyOneYOURNAMEPlayer import ThirtyOneYOURNAMEPlayer
from TiePlayer import TiePlayer
from MinimaxPlayer import MinimaxPlayer

from ThirtyOne.ThirtyOneCPUPlayerAdapter import ThirtyOneCPUPlayerAdapter
from ThirtyOne.ThirtyOneHumanPlayer import ThirtyOneHumanPlayer
from ThirtyOne.ThirtyOneBoard import ThirtyOneBoard

player1 = ThirtyOneHumanPlayer("Human")
player2 = RandomPlayer("Random bot 1")
player3 = ThirtyOneCPUPlayerAdapter(ThirtyOneYOURNAMEPlayer())

board = ThirtyOneBoard([player1, player2, player3])

engine = GameEngine(board)

winner = engine.run(True)

print("\n Final scores:")
scores = board.scoreBoard()
for player in scores:
    print(f"Player {player.name}: {scores[player]} points")

if isinstance(winner, TiePlayer):
    print("The game was a tie between " + winner.players.__str__())
else:
    print (f"The winner is player {winner.name}")
