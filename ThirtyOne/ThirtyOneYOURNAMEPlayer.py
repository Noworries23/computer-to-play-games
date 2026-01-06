from ThirtyOne.ThirtyOneMove import ThirtyOneDrawChoiceMove
from ThirtyOne.ThirtyOneMove import ThirtyOneDiscardMove

class ThirtyOneYOURNAMEPlayer():
    def __init__(self):
        super().__init__()
        self.name = "Your names here"

    def choose_draw_move(self, cards, top_discard):
        # Example strategy: always draw from the deck
        return ThirtyOneDrawChoiceMove.Choice.DRAW_FROM_DECK

    def choose_discard_move(self, cards, top_discard):
        # Example strategy: discard the first card in hand
        card_to_discard = cards[0]
        return card_to_discard

