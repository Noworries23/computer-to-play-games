from ThirtyOne.ThirtyOneMove import ThirtyOneDrawChoiceMove
from ThirtyOne.ThirtyOneMove import ThirtyOneDiscardMove
from collections import defaultdict
import itertools
from typing import Optional


# Knock thresholds and adjustments
BASE_KNOCK_THRESHOLD = 27          # Base score required to consider knocking
DECK_LOW_THRESHOLD = 18             # Deck size considered "low"
DECK_MID_THRESHOLD = 20             # Deck size considered "mid"
DECK_LOW_PENALTY = 0               # Adjustment when deck is low (negative = more aggressive)
DECK_MID_PENALTY = -2               # Adjustment when deck is mid
POSITION_LAST_BONUS = 1            # Adjustment if you're last to act (negative = more aggressive)
EARLY_GAME_TURNS = 7                # Number of turns considered "early game"
EARLY_GAME_BONUS = 2.844                # Adjustment in early game (positive = more conservative)

# Draw decision parameters
CERTAINTY_BONUS = 1.071               # Bonus for certain outcomes (discard) vs uncertain (deck)

# Risk assessment for knocking
OPPONENT_WIN_PROB_HIGH = .322       # Max opponent win probability to knock at 29+ score
OPPONENT_WIN_PROB_MID = 0.193         # Max opponent win probability to knock at 27-28 score
OPPONENT_WIN_PROB_LOW = 0.097         # Max opponent win probability to knock at <27 score

# 31 pursuit parameters
GO_FOR_31_MIN_SCORE = 28            # Minimum score to consider going for 31
GO_FOR_31_MIN_PROBABILITY = 0.10    # Minimum probability needed to pursue 31

# =============================================================================
# Helper Functions
# =============================================================================

def card_value(card):
    """Get numeric value of a card (A=11, face=10, etc)"""
    if hasattr(card, "value") and isinstance(card.value, (int, float)):
        return card.value

    r = getattr(card, 'rank', None)
    if isinstance(r, str):
        if r in ["K", "Q", "J"]:
            return 10
        if r == "A":
            return 11
        return int(r)

    if hasattr(r, 'name'):
        name = r.name.upper()
        if name in ("KING", "QUEEN", "JACK"):
            return 10
        if name == "ACE":
            return 11
        try:
            val = int(getattr(r, 'value'))
            return val
        except Exception:
            pass

    try:
        s = str(r)
        if s.upper().startswith('ACE'):
            return 11
        if s.upper().startswith(('KING','QUEEN','JACK')):
            return 10
        return int(s)
    except Exception:
        return 0

def _normalize_suit(card_or_suit) -> Optional[str]:
    """Return suit as one of Hearts, Diamonds, Clubs, Spades or None"""
    if card_or_suit is None:
        return None
    s = getattr(card_or_suit, 'suit', card_or_suit)
    if isinstance(s, str):
        for canonical in ["Hearts","Diamonds","Clubs","Spades"]:
            if s.lower().endswith(canonical.lower()) or s.lower() == canonical.lower():
                return canonical
        return s
    if hasattr(s, 'name'):
        name = s.name.upper()
        if name == 'HEARTS' or name == 'HEART':
            return 'Hearts'
        if name == 'DIAMONDS' or name == 'DIAMOND':
            return 'Diamonds'
        if name == 'CLUBS' or name == 'CLUB':
            return 'Clubs'
        if name == 'SPADES' or name == 'SPADE':
            return 'Spades'
    return str(s)

def _normalize_rank(card_or_rank) -> Optional[str]:
    """Return rank as 'A', 'K', 'Q', 'J', '10', '2', ... or None"""
    if card_or_rank is None:
        return None
    r = getattr(card_or_rank, 'rank', card_or_rank)
    if isinstance(r, str):
        return r
    if hasattr(r, 'name'):
        name = r.name.upper()
        mapping = {
            'ACE': 'A', 'KING': 'K', 'QUEEN': 'Q', 'JACK': 'J', 'TEN': '10',
            'TWO': '2','THREE':'3','FOUR':'4','FIVE':'5','SIX':'6','SEVEN':'7',
            'EIGHT':'8','NINE':'9'
        }
        return mapping.get(name, str(getattr(r, 'value', name)))
    return str(r)

class SimpleCard:
    """Lightweight card object for EV simulation"""
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
    def __str__(self):
        return f"{self.rank} of {self.suit}"

def best_score_from_cards(cards):
    """Calculate best possible score from a hand (max suit total)"""
    suit_scores = defaultdict(int)
    for c in cards:
        suit_scores[c.suit] += card_value(c)
    return max(suit_scores.values()) if suit_scores else 0

def best_suit_and_score(cards):
    """Return (suit, score) tuple for best suit in hand"""
    suit_scores = defaultdict(int)
    for c in cards:
        suit_scores[c.suit] += card_value(c)
    if not suit_scores:
        return None, 0
    best = max(suit_scores.items(), key=lambda x: x[1])
    return best[0], best[1]

# =============================================================================
# Algorithmic 31 Bot
# =============================================================================

class Algorithmic31BotV5():
    def __init__(self):
        super().__init__()
        self.name = "Algorithmic31BotV5"
        
        # Track game state
        self.seen_cards = set()  # (suit, rank) tuples
        self.turn_count = 0
        self.total_players = 0
        self.my_position = 0
    
    def update_state(self, board, my_hand):
        """Update internal state from board information"""
        self.seen_cards.clear()
        
        # Add all cards from discard pile
        if hasattr(board, 'discard') and hasattr(board.discard, 'cards'):
            for card in board.discard.cards:
                suit = _normalize_suit(card)
                rank = _normalize_rank(card)
                self.seen_cards.add((suit, rank))
        
        # Add my hand
        for card in my_hand:
            suit = _normalize_suit(card)
            rank = _normalize_rank(card)
            self.seen_cards.add((suit, rank))
        
        # Track game metadata
        if hasattr(board, 'players'):
            self.total_players = len(board.players)
            if hasattr(board, 'current_player'):
                self.my_position = board.players.index(board.current_player)
        
        self.turn_count += 1
    
    def get_remaining_cards(self):
        """Return dictionary of unseen cards per suit"""
        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        ranks = [str(n) for n in range(2, 11)] + ["J", "Q", "K", "A"]
        
        remaining = {s: [] for s in suits}
        for s in suits:
            for r in ranks:
                if (s, r) not in self.seen_cards:
                    remaining[s].append(r)
        return remaining
    
    def get_deck_size(self, board):
        """Get actual remaining deck size"""
        if hasattr(board, 'deck') and hasattr(board.deck, 'cards'):
            return len(board.deck.cards)
        return 52 - len(self.seen_cards)
    
    def calculate_exact_deck_ev(self, hand):
        """Calculate exact expected value of drawing from deck"""
        remaining = self.get_remaining_cards()
        total_unseen = sum(len(ranks) for ranks in remaining.values())
        
        if total_unseen == 0:
            return best_score_from_cards(hand)
        
        total_ev = 0
        for suit, ranks in remaining.items():
            for rank in ranks:
                simulated_card = SimpleCard(rank, suit)
                possible_hand = hand + [simulated_card]
                
                best_score = max(
                    best_score_from_cards(list(combo))
                    for combo in itertools.combinations(possible_hand, 3)
                )
                
                total_ev += best_score / total_unseen
        
        return total_ev
    
    def calculate_discard_ev(self, hand, top_discard):
        """Calculate exact value of drawing from discard (certain outcome)"""
        if top_discard is None:
            return best_score_from_cards(hand)
        card = top_discard[0] if isinstance(top_discard, list) and top_discard else top_discard
        if card is None:
            return best_score_from_cards(hand)
        if isinstance(card, tuple) and len(card) == 2:
            suit, rank = card
            card = SimpleCard(rank, suit)
        possible_hand = hand + [card]
        return max(
            best_score_from_cards(list(combo))
            for combo in itertools.combinations(possible_hand, 3)
        )
    
    def calculate_opponent_winning_probability(self, my_score, board):
        """Estimate probability that ANY opponent can beat my_score in one draw"""
        remaining = self.get_remaining_cards()
        total_unseen = sum(len(ranks) for ranks in remaining.values())
        
        if total_unseen == 0:
            return 0.0
        
        dangerous_cards = 0
        for suit, ranks in remaining.items():
            for rank in ranks:
                value = 11 if rank == "A" else 10 if rank in ["J","Q","K"] else int(rank)
                if value >= 10:
                    dangerous_cards += 1
        
        single_opponent_fail_prob = 1 - (dangerous_cards / total_unseen)
        all_opponents_fail_prob = single_opponent_fail_prob ** (self.total_players - 1)
        
        return 1 - all_opponents_fail_prob
    
    def should_go_for_31(self, hand, board):
        """Determine if we should try for 31 instead of knocking"""
        current_score = best_score_from_cards(hand)
        
        if current_score >= 31 or current_score < 26:
            return False
        
        best_suit, suit_score = best_suit_and_score(hand)
        if best_suit is None:
            return False
        
        needed_value = 31 - suit_score
        remaining = self.get_remaining_cards()
        
        cards_that_give_31 = 0
        for rank in remaining.get(best_suit, []):
            value = 11 if rank == "A" else 10 if rank in ["J","Q","K"] else int(rank)
            if value == needed_value:
                cards_that_give_31 += 1
        
        total_unseen = sum(len(ranks) for ranks in remaining.values())
        if total_unseen == 0:
            return False
        
        probability_of_31 = cards_that_give_31 / total_unseen
        
        return probability_of_31 > GO_FOR_31_MIN_PROBABILITY and current_score >= GO_FOR_31_MIN_SCORE
    
    def decide_knock_threshold(self, board):
        """Dynamic knock threshold based on game state"""
        threshold = BASE_KNOCK_THRESHOLD
        
        # Adjust for deck depletion
        deck_size = self.get_deck_size(board)
        if deck_size <= DECK_LOW_THRESHOLD:
            threshold += DECK_LOW_PENALTY
        elif deck_size <= DECK_MID_THRESHOLD:
            threshold += DECK_MID_PENALTY
        
        # Adjust for position
        if self.my_position == self.total_players - 1:
            threshold += POSITION_LAST_BONUS
        
        # Adjust for early game
        if self.turn_count <= EARLY_GAME_TURNS:
            threshold += EARLY_GAME_BONUS
        
        return threshold
    
    def should_knock(self, my_score, hand, board):
        """Comprehensive knock decision"""
        threshold = self.decide_knock_threshold(board)
        
        if my_score < threshold:
            return False
        
        if self.should_go_for_31(hand, board):
            return False
        
        opponent_win_prob = self.calculate_opponent_winning_probability(my_score, board)
        
        if my_score >= 29:
            return opponent_win_prob < OPPONENT_WIN_PROB_HIGH
        elif my_score >= 27:
            return opponent_win_prob < OPPONENT_WIN_PROB_MID
        else:
            return opponent_win_prob < OPPONENT_WIN_PROB_LOW
    
    def choose_draw_move(self, hand, top_discard, board=None):
        """Main decision: KNOCK, DRAW_FROM_DECK, or DRAW_FROM_DISCARD"""
        
        # Normalize top_discard
        if isinstance(top_discard, list):
            top_discard = top_discard[0] if top_discard else None
        
        # Update state
        if board:
            self.update_state(board, hand)
        
        current_score = best_score_from_cards(hand)
        
        # Check if someone already knocked
        someone_knocked = (hasattr(board, 'player_who_knocked') and 
                          board.player_who_knocked != -1)
        
        # 1. INSTANT WIN: If we can reach 31 from discard, take it
        if top_discard:
            ev_discard = self.calculate_discard_ev(hand, top_discard)
            if ev_discard >= 31:
                return ThirtyOneDrawChoiceMove.Choice.DRAW_FROM_DISCARD
        
        # 2. KNOCK DECISION (only if no one has knocked yet)
        if not someone_knocked:
            if self.should_knock(current_score, hand, board):
                return ThirtyOneDrawChoiceMove.Choice.KNOCK
        
        # 3. COMPARE DRAW OPTIONS
        if top_discard:
            ev_discard = self.calculate_discard_ev(hand, top_discard)
        else:
            ev_discard = current_score
        
        ev_deck = self.calculate_exact_deck_ev(hand)
        
        # Add certainty bonus
        ev_discard_adjusted = ev_discard + CERTAINTY_BONUS
        
        # 4. MAKE DECISION
        if ev_discard_adjusted >= ev_deck:
            return ThirtyOneDrawChoiceMove.Choice.DRAW_FROM_DISCARD
        else:
            return ThirtyOneDrawChoiceMove.Choice.DRAW_FROM_DECK
    
    def choose_discard_move(self, hand, top_discard):
        """Choose which card to discard"""
        best_choice = None
        best_remaining_score = -1
        
        for card in hand:
            remaining = [c for c in hand if c != card]
            score = best_score_from_cards(remaining)
            
            if score > best_remaining_score:
                best_remaining_score = score
                best_choice = card
        
        return best_choice


# =============================================================================
# Player Class Wrapper
# =============================================================================

class ThirtyOneDeenPlayer():
    def __init__(self):
        super().__init__()
        self.bot = Algorithmic31BotV5()
        self.name = self.bot.name
    
    def choose_draw_move(self, cards, top_discard, board=None):
        return self.bot.choose_draw_move(cards, top_discard, board)
    
    def choose_discard_move(self, cards, top_discard):
        return self.bot.choose_discard_move(cards, top_discard)