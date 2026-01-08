from SushiGo.Card import Card   
import random

class DeckOfCards:

    def __init__(self):
        self.cards = []
        self.initialize_deck()

    def clone(self):
        new_deck = DeckOfCards()
        new_deck.cards = list(self.cards)
        return new_deck

    def initialize_deck(self):
        card_amounts = {
            Card.Type.TEMPURA: 14,
            Card.Type.SASHIMI: 14,
            Card.Type.DUMPLING: 14,
            Card.Type.SINGLE_MAKI: 6,
            Card.Type.DOUBLE_MAKI: 12,
            Card.Type.TRIPLE_MAKI: 8,
            Card.Type.SALMON_NIGIRI: 10,
            Card.Type.SQUID_NIGIRI: 5,
            Card.Type.EGG_NIGIRI: 5,
            Card.Type.PUDDING: 10,
            Card.Type.WASABI: 6,
            Card.Type.CHOPSTICKS: 4
        }
        for card_type, amount in card_amounts.items():
            for _ in range(amount):
                self.cards.append(Card(card_type))
        random.shuffle(self.cards)

    def draw_card(self):
        if len(self.cards) == 0:
            raise ValueError("No cards left in the deck.")
        return self.cards.pop()