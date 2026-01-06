from enum import Enum

class Card:

    class Suit(Enum):
        CLUBS = 1
        DIAMONDS = 2
        SPADES = 3
        HEARTS = 4

    class Rank(Enum):
        ACE = 1
        TWO = 2
        THREE = 3
        FOUR = 4
        FIVE = 5
        SIX = 6
        SEVEN = 7
        EIGHT = 8
        NINE = 9
        TEN = 10
        JACK = 11
        QUEEN = 12
        KING = 13

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank.name.lower()} of {self.suit.name.lower()}"