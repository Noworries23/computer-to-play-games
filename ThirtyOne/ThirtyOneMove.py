from enum import Enum
from Move import Move
from ThirtyOne.Card import Card

class ThirtyOneDrawChoiceMove(Move):

    class Choice(Enum):
        DRAW_FROM_DECK = 1
        DRAW_FROM_DISCARD = 2
        KNOCK = 3
    
    """
    A move in 31, which includes the player who made the move and the column in which the move was made.
    """
    
    def __init__(self, player, choice):
        super().__init__()
        self.player = player
        self.choice = choice
    
    def __eq__(self, other):
        return (isinstance(other, ThirtyOneDrawChoiceMove) and (self.player == other.player) and (self.choice == other.choice))


class ThirtyOneDiscardMove(Move):
    """
    A move in 31, which includes the player who made the move and the card to be discarded.
    """
    
    def __init__(self, player, card):
        super().__init__()
        self.player = player
        self.card = card
    
    def __eq__(self, other):
        return (isinstance(other, ThirtyOneDiscardMove) and (self.player == other.player) and (self.card == other.card))
    