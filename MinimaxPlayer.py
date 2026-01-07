from asyncio import open_connection
from imp import cache_from_source
from Player import Player
import random

from TiePlayer import TiePlayer

class MinimaxPlayer(Player):
    def __init__(self, name, depth):
        super().__init__(name)
        self.depth = depth

    def getMove(self, board):
        newMove, value = self.maximizeBoard(board, 0, self)
        return newMove
        
# Get maximum value possible on board
# Returns as ordered pair of move and value
    def maximizeBoard(self, board, depth, player):
        ended = board.getGameEnded()
        if ended:
            result = board.scoreBoard()
            return None, result[player]

        if depth >= self.depth:
            return None, self.scoreBoard(board, player)

        currentPlayer = board.currentPlayer()
        options = board.getPossibleBoardsAndMoves()
        bestOptions = []
        bestValue = float("-inf")
        for option in options:
            newMove, value = self.maximizeBoard(option[0], depth + 1, currentPlayer)
            #value = -value
            # if currentPlayer != option[0].currentPlayer():
            #     value = -value
            if value > bestValue:
                bestOptions = [option]
                bestValue = value
            elif value == bestValue:
                bestOptions.append(option)

        bestOptions.sort(key=lambda x: self.scoreBoard(x[0], player), reverse=True)

        return bestOptions[0][1], -bestValue
    
# Assign a score to a board
# By default, just a random number
# But you need to change this
    def scoreBoard(self, board, player):
        return random.uniform(-1, 1)
        