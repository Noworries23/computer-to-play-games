from SushiGo.Card import Card

class SushiGoYOURNAMEPlayer():
    def __init__(self, name = None):
        self.name = "Your names here"
        if name:
            self.name = name
        self.priorities = {
            Card.Type.TEMPURA: 1,
            Card.Type.SASHIMI: 2,
            Card.Type.DUMPLING: 3,
            Card.Type.SINGLE_MAKI: 4,
            Card.Type.DOUBLE_MAKI: 5,
            Card.Type.TRIPLE_MAKI: 6,
            Card.Type.SALMON_NIGIRI: 7,
            Card.Type.SQUID_NIGIRI: 8,
            Card.Type.EGG_NIGIRI: 9,
            Card.Type.PUDDING: 10,
            Card.Type.WASABI: 11,
            Card.Type.CHOPSTICKS: 12
        }
        self.priorities = {k: v for k, v in sorted(self.priorities.items(), key=lambda item: item[1])}

    def choose_move(self, hand, visible_cards, current_round):
        # Return the index of the card to play from hand (from 0 to len(hand)-1)
        #return 0  # Example: always play the first card in hand
        best_card_index = 0
        for i in range(len(hand)):
            if self.priorities[hand[i].type] < self.priorities[hand[best_card_index].type]:
                best_card_index = i

        return best_card_index

