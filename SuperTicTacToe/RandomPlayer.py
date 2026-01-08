import Player
import random

class RandomPlayer(Player.Player):
    def __init__(self, name):
        super().__init__(name)

    def getMove(self, board):
        valids = board.getPossibleMoves()
        return random.choice(valids)