from ThirtyOne.Card import Card   
import random

class DeckOfCards:

    def __init__(self):
        self.cards = []

    def clone(self):
        new_deck = DeckOfCards()
        new_deck.cards = list(self.cards)
        return new_deck

    def initialize_deck(self):
        for suit in Card.Suit:
            for rank in Card.Rank:
                self.cards.append(Card(suit, rank))
        random.shuffle(self.cards);

    def draw_card(self):
        if len(self.cards) == 0:
            raise ValueError("No cards left in the deck.")
        return self.cards.pop()

    def add_card(self, card):
        self.cards.append(card)

    def get_top_card(self):
        if len(self.cards) == 0:
            return 0
        return self.cards[-1]