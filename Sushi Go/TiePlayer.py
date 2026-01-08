from Player import Player

class TiePlayer(Player):

    def __init__(self, players):
        super().__init__("Tie")
        self.players = players

    def getMove(self, board):
        raise "This should never get called!"