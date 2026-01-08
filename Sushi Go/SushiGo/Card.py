from enum import Enum

class Card:

    class Type(Enum):
        TEMPURA = 1
        SASHIMI = 2
        DUMPLING = 3
        SINGLE_MAKI = 4
        DOUBLE_MAKI = 5
        TRIPLE_MAKI = 6
        SALMON_NIGIRI = 7
        SQUID_NIGIRI = 8
        EGG_NIGIRI = 9
        PUDDING = 10
        WASABI = 11
        CHOPSTICKS = 12

    def __init__(self, type):
        self.type = type

    def __str__(self):
        return self.type.name.replace("_", " ").title()