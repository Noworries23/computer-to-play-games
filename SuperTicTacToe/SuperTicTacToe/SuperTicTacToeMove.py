from Move import Move

class SuperTicTacToeMove(Move):
    
    """
    A move in Super TicTacToe which includes the player who made the move, the board of choice, and the location
    """
    
    def __init__(self, player, boardx, boardy, positionx, positiony):
        super().__init__()
        self.player = player
        self.boardx = boardx
        self.boardy = boardy
        self.positionx = positionx
        self.positiony = positiony        
    
    def __eq__(self, other):
        return (isinstance(other, SuperTicTacToeMove) and (self.player == other.player) and (self.boardx == other.boardx) and (self.boardy == other.boardy) and (self.positionx == other.positionx) and (self.positiony == other.positiony))


