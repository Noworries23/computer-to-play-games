from Player import Player
from SushiGo.Card import Card
from SushiGo.SushiGoMove import SushiGoMove

class SushiGoHumanPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def getMove(self, board):

        print('\nCurrent cards displayed:')
        for player, cards in board.played_cards.items():
            print(f"{player.name}'s played cards:")
            for card in cards:
                print(f"\t{card}")

        # Print all cards in your hand
        print('\nYour hand:')
        for i, card in enumerate(board.hands[self]):
            print(f"{i + 1})\t{card}")

        use_chopsticks = False
        for card in board.played_cards[self]:
            if card.type == Card.Type.CHOPSTICKS:
                use_chopsticks = True
                break
        
        print ('\nEnter the card you want to play (1-7):')
        if use_chopsticks:
            print('Or enter two numbers separated by a space to use chopsticks:')
        while True:
            string = input()
            if use_chopsticks and ' ' in string:
                try:
                    index1, index2 = map(int, string.split())
                    if 1 <= index1 <= 7 and 1 <= index2 <= 7:
                        return SushiGoMove(self, board.hands[self][index1 - 1], board.hands[self][index2 - 1])
                except ValueError:
                    pass
            else:
                try:
                    index = int(string)
                    if 1 <= index <= 7:
                        return SushiGoMove(self, board.hands[self][index - 1], None)
                except ValueError:
                    pass
            print('Invalid input. Please try again.')
