from Player import Player
from ThirtyOne.ThirtyOneMove import ThirtyOneDrawChoiceMove
from ThirtyOne.ThirtyOneMove import ThirtyOneDiscardMove

class ThirtyOneHumanPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def getMove(self, board):

        # Print all cards in your hand
        print('\nYour hand:')
        for card in board.hands[self]:
            print(card)

        top_card = board.discard.get_top_card()
        if top_card == 0:
            top_card = 'Empty'
        print('\nTop of discard pile:', top_card, '\n')

        if board.current_turn_type == board.TurnType.DRAW_CHOICE:
            print('1) Draw from deck    2) Draw from discard pile    3) Knock')
            while True:
                choice = input()
                if choice == '1':
                    return ThirtyOneDrawChoiceMove(self, ThirtyOneDrawChoiceMove.Choice.DRAW_FROM_DECK)
                elif choice == '2':
                    return ThirtyOneDrawChoiceMove(self, ThirtyOneDrawChoiceMove.Choice.DRAW_FROM_DISCARD)
                elif choice == '3':
                    return ThirtyOneDrawChoiceMove(self, ThirtyOneDrawChoiceMove.Choice.KNOCK)
                else:
                    print('Invalid choice')
        else:
            print('Select a card to discard (1, 2, 3, or 4):')
            while True:
                choice = input()
                if choice in ['1', '2', '3', '4']:
                    card_to_discard = board.hands[self][int(choice) - 1]
                    return ThirtyOneDiscardMove(self, card_to_discard)
                else:
                    print('Invalid choice')
