from GameState import GameState
from ThirtyOne.DeckOfCards import DeckOfCards
from enum import Enum
from ThirtyOne.ThirtyOneMove import ThirtyOneDrawChoiceMove
from ThirtyOne.ThirtyOneMove import ThirtyOneDiscardMove

from TiePlayer import TiePlayer

BLACK = 0,0,0
RED = 255,0,0
BLUE = 0,0,255
WHITE = 255, 255, 255

class ThirtyOneBoard(GameState):

    class TurnType(Enum):
        DRAW_CHOICE = 1
        DISCARD = 2
    
    def __init__(self, players):
        super().__init__(players)

        # Basic setup
        self.hands = {player: [] for player in players}
        self.deck = DeckOfCards()
        self.deck.initialize_deck()
        self.discard = DeckOfCards()

        # Deal initial hands
        for _ in range(3):
            for player in players:
                self.hands[player].append(self.deck.draw_card())
        self.discard.add_card(self.deck.draw_card())

        self.current_player = players[0]
        self.current_turn_type = ThirtyOneBoard.TurnType.DRAW_CHOICE
        self.player_who_knocked = -1 # index of the player who knocked, -1 if none have
        
    def clone(self):
        newBoard = ThirtyOneBoard(self.players)
        newBoard.hands = {player: list(cards) for player, cards in self.hands.items()}
        newBoard.deck = self.deck.clone()
        newBoard.discard = self.discard.clone()
        newBoard.current_player = self.current_player
        newBoard.current_turn_type = self.current_turn_type
        newBoard.player_who_knocked = self.player_who_knocked
        return newBoard
    
    def getPossibleMoves(self):       
        if self.current_turn_type == ThirtyOneBoard.TurnType.DRAW_CHOICE:
            possibleMoves = []
            possibleMoves.append(ThirtyOneDrawChoiceMove(self.current_player, ThirtyOneDrawChoiceMove.Choice.DRAW_FROM_DECK))
            possibleMoves.append(ThirtyOneDrawChoiceMove(self.current_player, ThirtyOneDrawChoiceMove.Choice.DRAW_FROM_DISCARD))
            if self.player_who_knocked == -1:
                possibleMoves.append(ThirtyOneDrawChoiceMove(self.current_player, ThirtyOneDrawChoiceMove.Choice.KNOCK))
        else:
            possibleMoves = []
            for card in self.hands[self.current_player]:
                possibleMoves.append(ThirtyOneDiscardMove(self.current_player, card))
        return possibleMoves
    
    def checkIsValid(self, move):
        if isinstance(move, ThirtyOneDrawChoiceMove):
            if move.player != self.current_player:
                return False
            if self.current_turn_type != ThirtyOneBoard.TurnType.DRAW_CHOICE:
                return False
            if move.choice == ThirtyOneDrawChoiceMove.Choice.KNOCK:
                if self.player_who_knocked != -1:
                    return False
            return True
        else:
            if move.player != self.current_player:
                return False
            if self.current_turn_type != ThirtyOneBoard.TurnType.DISCARD:
                return False
            if move.card not in self.hands[self.current_player]:
                return False
            return True

    def doMove(self, move):
        if isinstance(move, ThirtyOneDrawChoiceMove):
            if move.choice == ThirtyOneDrawChoiceMove.Choice.DRAW_FROM_DECK:
                self.hands[self.current_player].append(self.deck.draw_card())
                self.current_turn_type = ThirtyOneBoard.TurnType.DISCARD
                print (f"{self.current_player.name} drew from deck.")
            elif move.choice == ThirtyOneDrawChoiceMove.Choice.DRAW_FROM_DISCARD:
                self.hands[self.current_player].append(self.discard.cards.pop())
                self.current_turn_type = ThirtyOneBoard.TurnType.DISCARD
                print (f"{self.current_player.name} drew from discard pile.")
            elif move.choice == ThirtyOneDrawChoiceMove.Choice.KNOCK:
                self.player_who_knocked = self.players.index(self.current_player)
                print (f"{self.current_player.name} has knocked.")
                self.current_player = self.next_player()
        else:
            self.hands[self.current_player].remove(move.card)
            self.discard.add_card(move.card)
            print (f"{self.current_player.name} discarded {move.card}.")
            self.current_player = self.next_player()
            self.current_turn_type = ThirtyOneBoard.TurnType.DRAW_CHOICE

        # Reset deck if needed
        if len(self.deck.cards) == 0:
            for card in self.discard.cards:
                self.deck.cards.append(card)
            self.deck.cards.pop()
            self.discard.cards = [self.discard.cards[-1]]

        return self
    
    def currentPlayer(self):
        return self.current_player
    
    def next_player(self):
        current_index = self.players.index(self.current_player)
        next_index = (current_index + 1) % len(self.players)
        return self.players[next_index]
    
    def get_card_value(self, card):
        if card.rank.name in ['JACK', 'QUEEN', 'KING']:
            return 10
        elif card.rank.name == 'ACE':
            return 11
        else:
            return int(card.rank.value)

    def get_hand_value(self, hand):
        suit_totals = {}
        for card in hand:
            suit = card.suit
            value = self.get_card_value(card)
            if suit not in suit_totals:
                suit_totals[suit] = 0
            suit_totals[suit] += value
        return max(suit_totals.values()) if suit_totals else 0
        
    def getGameEnded(self):
        # Check for knock condition
        if self.player_who_knocked != -1:
            if self.current_player == self.players[self.player_who_knocked]:
                # Game ends, determine winner
                best_value = -1
                winners = []
                for player in self.players:
                    hand_value = self.get_hand_value(self.hands[player])
                    if hand_value > best_value:
                        best_value = hand_value
                        winners = [player]
                    elif hand_value == best_value:
                        winners.append(player)
                if len(winners) == 1:
                    return winners[0]
                elif len(winners) > 1:
                    return TiePlayer(winners)
                else:
                    raise "Not sure how you got here!"
            else:
                return False

        # Check for 31 condition
        for player in self.players:
            winners = []
            if self.get_hand_value(self.hands[player]) == 31:
                winners.append(player)
        if len(winners) == 1:
            return winners[0]
        elif len(winners) > 1:
            return TiePlayer(winners)
            
        return False               
       
    def scoreBoard(self):
        # return the score for each player
        scores = {}
        for player in self.players:
            scores[player] = self.get_hand_value(self.hands[player])
        return scores

        
    def initializeDrawing(self):
        pass
        # self.screen = pygame.display.set_mode((640, 480))

        # self.width = 640
        # self.height = 480
        # self.radius = 480 / 20
        # self.box_size = 480 / (self.rows + 2)
        # self.left_disp_offset = self.box_size * 2
        # self.top_disp_offset = self.box_size

        # self.game_closed = False     
        
    def drawBoard(self):
        pass
        # if not self.game_closed:
            # for event in pygame.event.get():
            #     if event.type == pygame.QUIT:
            #         self.game_closed = True
            #         pygame.quit()

            # # Reset screen
            # self.screen.fill(BLACK)

            # # Drawing the grid
            # my_font = pygame.font.SysFont("monospace", 20)
            # for row_num in range(self.rows + 1):
            #     row_start = (self.left_disp_offset, self.top_disp_offset + (self.box_size * row_num))
            #     row_end = (self.left_disp_offset + (self.box_size * self.cols), self.top_disp_offset + (self.box_size * row_num))
            #     pygame.draw.line(self.screen, WHITE, row_start, row_end)
            # for col_num in range(self.cols + 1):
            #     col_start = (self.left_disp_offset + (self.box_size * col_num), self.top_disp_offset)
            #     col_end = (self.left_disp_offset + (self.box_size * col_num), self.top_disp_offset + (self.box_size * self.rows))
            #     if col_num > 0:
            #         col_label = my_font.render(str(col_num), 1, WHITE)
            #         self.screen.blit(col_label, (self.left_disp_offset + (self.box_size * col_num) - self.box_size / 2, self.height - 40))
            #     pygame.draw.line(self.screen, WHITE, col_start, col_end)

            # # Drawing pieces
            # for col_num, col in enumerate(self.columns):
            #     for row_num, element in enumerate(col):
            #         pos = (int(self.box_size * (col_num + 0.5)) + self.left_disp_offset,
            #                int(self.box_size * ((NROWS - row_num - 1) + 0.5)) + self.top_disp_offset)
            #         if element == self.players[0]:
            #             color = RED
            #         else:
            #             color = BLUE

            #         pygame.draw.circle(self.screen, color, pos, self.radius)
            # pygame.display.flip()
            #pygame.time.wait(1000)
        

