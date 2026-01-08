from Player import Player
from SushiGo.SushiGoMove import SushiGoMove

class SushiGoCPUPlayerAdapter(Player):
    def __init__(self, player):
        super().__init__(player.name)
        self.player = player

    def getMove(self, board):
        choice = self.player.choose_move(board.hands[self], board.played_cards, board.current_round)
        if choice == None:
            raise Exception("CPU Player returned None for move.")
        return SushiGoMove(self, board.hands[self][choice])
