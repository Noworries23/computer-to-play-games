import random
import time


class GameEngine():
    """
    An engine to run a game
    """
    
    def __init__(self, gameState):
        """
        Input:
            game: a gamestate
        """
        self.board = gameState

    def randomMove(self):
        """
        Finds and applies a random move
        """
        valids = self.board.getPossibleMoves()
        return random.choice(valids)

    def nextMove(self):
        """
        Finds and applies the next move
        """
        try:
            move = self.board.getNextMove()
        except:
            move = self.randomMove() # In case an exception is thrown
        if not self.board.checkIsValid(move):
            move = self.randomMove()
        self.board = self.board.doMove(move)
        
    def run(self, visualize=True, pause=0):
        """
        Runs the game
        """
        if visualize:
            self.board.initializeDrawing()
            self.board.drawBoard()
            
        while not self.board.getGameEnded():
            self.nextMove()
            if visualize:
                self.board.drawBoard()
            time.sleep(pause)

        return self.board.getGameEnded()
    
