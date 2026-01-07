from Player import Player
from ThirtyOne.ThirtyOneMove import ThirtyOneDiscardMove, ThirtyOneDrawChoiceMove

class ThirtyOneCPUPlayerAdapter(Player):
    def __init__(self, player):
        super().__init__(player.name)
        self.player = player

    def getMove(self, board):
        if board.current_turn_type == board.TurnType.DRAW_CHOICE:
            return ThirtyOneDrawChoiceMove(self, self.player.choose_draw_move(board.hands[self], board.discard.get_top_card(), board.move_storage))
        else:
            return ThirtyOneDiscardMove(self, self.player.choose_discard_move(board.hands[self], board.discard.get_top_card(), board.move_storage))