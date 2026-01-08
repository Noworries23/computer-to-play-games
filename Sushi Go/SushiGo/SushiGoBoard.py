from re import S
from GameState import GameState
from SushiGo.DeckOfCards import DeckOfCards
from SushiGo.Card import Card
from SushiGo.SushiGoMove import SushiGoMove

from TiePlayer import TiePlayer

BLACK = 0,0,0
RED = 255,0,0
BLUE = 0,0,255
WHITE = 255, 255, 255

class SushiGoBoard(GameState):

    def __init__(self, players):
        super().__init__(players)

        # Basic setup
        self.hands = {player: [] for player in players}
        self.played_cards = {player: [] for player in players}
        self.cards_to_be_played = {player: [] for player in players} # Cards that have been chosen but not revealed
        self.deck = DeckOfCards()
        self.deck.initialize_deck()
        self.scores = {player: 0 for player in players}
        
        self.output = True

        self.setup_round(1)
    
    def setup_round(self, round_number):
        # Clear played cards except pudding
        for entry in self.played_cards.items():
            player, cards = entry
            self.played_cards[player] = [card for card in cards if card.type == Card.Type.PUDDING]

        # Just to be safe
        self.cards_to_be_played = {player: [] for player in self.players}

        # Deal initial hands
        for _ in range(7):
            for player in self.players:
                self.hands[player].append(self.deck.draw_card())

        self.current_player = self.players[0]
        self.current_round = round_number

    def clone(self):
        newBoard = SushiGoBoard(self.players)
        newBoard.hands = {player: list(cards) for player, cards in self.hands.items()}
        newBoard.played_cards = {player: list(cards) for player, cards in self.played_cards.items()}
        newBoard.deck = self.deck.clone()
        newBoard.cards_to_be_played = {player: list(cards) for player, cards in self.cards_to_be_played.items()}
        newBoard.current_player = self.current_player
        newBoard.current_round = self.current_round
        return newBoard
    
    def getPossibleMoves(self):       
        moves = []
        for card in self.hands[self.current_player]:
            moves.append(SushiGoMove(self.current_player, card))
        # Don't forget chopsticks!
        if any(card.type == Card.Type.CHOPSTICKS for card in self.played_cards[self.current_player]):
            for i in range(len(self.hands[self.current_player])):
                for j in range(i + 1, len(self.hands[self.current_player])):
                    first_card = self.hands[self.current_player][i]
                    second_card = self.hands[self.current_player][j]
                    moves.append(SushiGoMove(self.current_player, first_card, second_card))
        return moves

    def checkIsValid(self, move):
        if not isinstance(move, SushiGoMove):
            return False
        if move.player != self.current_player:
            return False
        if move.card not in self.hands[self.current_player]:
            return False
        if move.second_card:
            if not any(card.type == Card.Type.CHOPSTICKS for card in self.played_cards[self.current_player]):
                return False
            if move.second_card not in self.hands[self.current_player]:
                return False
            if move.card == move.second_card:
                return False
        return True

    def doMove(self, move):
        # Normally, just store cards
        self.cards_to_be_played[self.current_player].append(move.card)
        self.hands[self.current_player].remove(move.card)
        if move.second_card:
            self.cards_to_be_played[self.current_player].append(move.second_card)
            self.hands[self.current_player].remove(move.second_card)
        self.current_player = self.next_player()

        # At the end of each hand, reveal cards
        if all(len(self.cards_to_be_played[player]) > 0 for player in self.players):
            for player in self.players:

                # Remove chopsticks from played cards if they are being used
                if len(self.cards_to_be_played[player]) == 2:
                    if self.output:
                        print(f"{player.name} is using chopsticks.")
                    chopsticks_found = False
                    for card in self.played_cards[player]:
                        if card.type == Card.Type.CHOPSTICKS:
                            self.hands[player].append(card)
                            self.played_cards[player].remove(card)
                            chopsticks_found = True
                            break
                    if not chopsticks_found:
                        raise ValueError("Chopsticks not found in played cards when expected.")
                # Play the cards
                for card in self.cards_to_be_played[player]:
                    self.played_cards[player].append(card)
                    if self.output:
                        print(f"{player.name} plays {card}")
                self.cards_to_be_played[player] = []

            # Pass hands
            new_hands = {player: [] for player in self.players}
            for i, player in enumerate(self.players):
                if self.current_round == 1 or self.current_round == 3:
                    next_player = self.players[(i + 1) % len(self.players)]
                else:
                    next_player = self.players[(i - 1) % len(self.players)]
                new_hands[player] = self.hands[next_player]
            for player in self.players:
                self.hands[player] = new_hands[player]

            # Check for end of round
            if len(self.hands[self.players[0]]) == 0:
                #print("End of round!")
                for player in self.players:
                        round_score = self.score_cards(player, self.played_cards[player])
                        self.scores[player] += round_score
                        if self.output:
                            print(f"{player.name} scores {round_score} points this round.  Total score: {self.scores[player]}")

                if self.current_round < 3:
                    if self.output:
                        print(f"Starting round {self.current_round + 1}")
                    self.setup_round(self.current_round + 1)
                else:
                    # Game over
                    if self.output:
                        print("Game ends!")
                    for player in self.players:
                        pudding_score = self.score_pudding(player)
                        self.scores[player] += pudding_score
                        if self.output:
                            print(f"{player.name} scores {pudding_score} points from puddings.  Total score: {self.scores[player]}")
                    pass

        return self
    
    def currentPlayer(self):
        return self.current_player
    
    def next_player(self):
        current_index = self.players.index(self.current_player)
        next_index = (current_index + 1) % len(self.players)
        return self.players[next_index]
        
    def getGameEnded(self):
        if self.current_round == 3 and len(self.hands[self.players[-1]]) == 0:
            scores = self.scoreBoard()
            max_score = max(scores.values())
            winners = [player for player, score in scores.items() if score == max_score]
            if len(winners) == 1:
                return winners[0]
            else:
                return TiePlayer(winners)
        return False
            
    def scoreBoard(self):
        # return the score for each player
        scores = {}
        for player in self.players:
            scores[player] = self.scores[player]
        return scores

    def score_cards(self, player, cards):
        # Implement scoring logic based on Sushi Go rules
        score = 0
        # Maki
        maki_winners, maki_second = self.find_max_maki()
        if player in maki_winners:
            score += 6 // len(maki_winners)
        elif player in maki_second:
            score += 3 // len(maki_second)
        tempura_count = sum(1 for card in cards if card.type == Card.Type.TEMPURA)
        score += (tempura_count // 2) * 5
        sashimi_count = sum(1 for card in cards if card.type == Card.Type.SASHIMI)
        score += (sashimi_count // 3) * 10
        dumpling_count = sum(1 for card in cards if card.type == Card.Type.DUMPLING)
        dumpling_scores = [0, 1, 3, 6, 10, 15]
        score += dumpling_scores[min(dumpling_count, 5)]
        wasabi = []
        nigiri_scores = {Card.Type.SALMON_NIGIRI: 2, Card.Type.SQUID_NIGIRI: 3, Card.Type.EGG_NIGIRI: 1}
        for card in cards:
            if card.type == Card.Type.WASABI:
                wasabi.append(card)
            elif card.type in nigiri_scores.keys():
                if wasabi:
                    wasabi.pop()
                    score += nigiri_scores[card.type] * 3
                else:
                    score += nigiri_scores[card.type]
        return score

    def score_pudding(self, player):
        score = 0
        pudding_winners, pudding_losers = self.find_pudding()
        if pudding_winners is not None:
            if player in pudding_winners:
                score += 6 // len(pudding_winners)
            elif player in pudding_losers:
                score -= 6 // len(pudding_losers)
        return score

    def find_max_maki(self):
        maki_counts = {}
        for player in self.players:
            for card in self.played_cards[player]:
                if card.type == Card.Type.SINGLE_MAKI:
                    maki_counts[player] = maki_counts.get(player, 0) + 1
                elif card.type == Card.Type.DOUBLE_MAKI:
                    maki_counts[player] = maki_counts.get(player, 0) + 2
                elif card.type == Card.Type.TRIPLE_MAKI:
                    maki_counts[player] = maki_counts.get(player, 0) + 3
        maki_counts = sorted(maki_counts.items(), key=lambda x: x[1], reverse=True)
        winners = [player for player, count in maki_counts if count == maki_counts[0][1]]
        second_place = []
        if len(maki_counts) > 1:
            second_place = [player for player, count in maki_counts if count == maki_counts[1][1]]
        return winners, second_place

    def find_pudding(self):
        pudding_counts = {}
        for player in self.players:
            pudding_counts[player] = sum(1 for card in self.played_cards[player] if card.type == Card.Type.PUDDING)
        pudding_counts = sorted(pudding_counts.items(), key=lambda x: x[1], reverse=True)
        if pudding_counts[0][1] == pudding_counts[-1][1]:
            return None, None
        winners = [player for player, count in pudding_counts if count == pudding_counts[0][1]]
        losers = [player for player, count in pudding_counts if count == pudding_counts[-1][1]]
        return winners, losers

    def initializeDrawing(self):
        pass
        
    def drawBoard(self):
        pass

        

