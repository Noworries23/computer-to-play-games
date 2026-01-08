from Move import Move

class SushiGoMove(Move):
    
    """
    A move in SushiGo, which includes the player who made the move and the card played
    """
    
    def __init__(self, player, card, second_card = None):
        super().__init__()
        self.player = player
        self.card = card
        self.second_card = second_card

    def __eq__(self, other):
        return (isinstance(other, SushiGoMove) and (self.player == other.player) and (self.card == other.card) and (self.second_card == other.second_card))


