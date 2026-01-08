class GameState():
    """
    A base class of the state of the game, including the board and the player whose turn it is
    """
    def __init__(self, players):
        self.players = players
        pass

    def clone(self):
        """
        Returns:
            board: a deep clone of the current board
        """
        pass
    
    def getNextMove(self):
        """
        Returns:
            move: action taken by current player
        """
        return self.currentPlayer().getMove(self.clone())
    
    def getPossibleMoves(self):
        """
        Returns:
            possibleMoves: a list of all possible moves
        """
        pass
    
    def getPossibleBoards(self):
        """
        Returns:
            possibleBoards: a list of all possible boards
        """
        
        possibleBoards = []
        possibleMoves = self.getPossibleMoves()
        for move in possibleMoves:
            newBoard = self.clone()
            newBoard.doMove(move)
            possibleBoards.append(newBoard)
        return possibleBoards

    def getPossibleBoardsAndMoves(self):
        """
        Returns:
            A list of ordered pairs of boards and moves
        """
        
        possibleBoards = []
        possibleMoves = self.getPossibleMoves()
        for move in possibleMoves:
            newBoard = self.clone()
            newBoard.doMove(move)
            possibleBoards.append((newBoard, move))
        return possibleBoards

    def checkIsValid(self, move):
        """
        Input:
            move: action taken by current player

        Returns:
            valid: True if move is valid; False otherwise
        """
        pass

    def currentPlayer(self):
        """
        Returns:
            nextPlayer: the player who is currently ready to play
        """
        pass

    def doMove(self, move):
        """
        Input:
            move: action taken by current player
        """
        pass
    
    def getGameEnded(self):
        """
        Input:
            board: current board

        Returns:
            r: 0 if game has not ended; otherwise, the player object who won
               
        """
        pass
    
    def scoreBoard(self):
        """
        Returns:
            score: the score of the current board, as a map of Players to scores
        """
        pass

    def initializeDrawing(self):
        """
        Initializes the drawing
        """
        pass
    
    def drawBoard(self):
        """
        Draws the board
        """
        pass