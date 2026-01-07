class Player():
    """
    Base class of a player of the game, which can be a person, a computer, or something in between
    """
    
    def __init__(self, name):
        self.name = name

    def getMove(self, board):
        """
        Input:
            board: current board
        Returns:
            move: action taken by current player
        """
        pass