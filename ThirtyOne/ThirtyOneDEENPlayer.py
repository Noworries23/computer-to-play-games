from ThirtyOne.ThirtyOneMove import ThirtyOneDrawChoiceMove
from ThirtyOne.ThirtyOneMove import ThirtyOneDiscardMove
from collections import defaultdict
import itertools

# -----------------------------
# Helper Functions
# -----------------------------

def card_value(card):
    """Get numeric value of a card (A=11, face=10, etc)"""
    if hasattr(card, "value"):
        return card.value
    if card.rank in ["K", "Q", "J"]:
        return 10
    if card.rank == "A":
        return 11
    return int(card.rank)

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

# -----------------------------
# Algorithmic 31 Bot V5
# -----------------------------

class Algorithmic31BotV5():
    def __init__(self):
        super().__init__()
        self.name = "Algorithmic31BotV5"
        
        # Track game state
        self.seen_cards = set()  # (suit, rank) tuples
        self.turn_count = 0
        self.total_players = 0
        self.my_position = 0  # 0-indexed position in turn order
        
    # -----------------------------
    # State Tracking
    # -----------------------------
    
    def update_state(self, board, my_hand):
        """Update internal state from board information"""
        # Track all visible cards (discard pile + my hand)
        self.seen_cards.clear()
        
        # Add all cards from discard pile
        if hasattr(board, 'discard') and hasattr(board.discard, 'cards'):
            for card in board.discard.cards:
                self.seen_cards.add((card.suit, card.rank))
        
        # Add my hand
        for card in my_hand:
            self.seen_cards.add((card.suit, card.rank))
        
        # Track game metadata
        if hasattr(board, 'players'):
            self.total_players = len(board.players)
            if hasattr(board, 'current_player'):
                self.my_position = board.players.index(board.current_player)
        
        self.turn_count += 1
    
    def get_remaining_cards(self):
        """Return dictionary of unseen cards per suit"""
        # Build complete deck with ENUM format to match seen_cards
        all_cards_in_deck = []
        
        # Get enum classes from first card in hand (if available)
        # Otherwise we'll need to handle string matching
        
        # Strategy: Check what format seen_cards uses, match that
        suits_str = ["Hearts", "Diamonds", "Clubs", "Spades"]
        ranks_str = [str(n) for n in range(2, 11)] + ["J", "Q", "K", "A"]
        
        remaining = {}
        for suit_str in suits_str:
            remaining[suit_str] = []
            for rank_str in ranks_str:
                # Check both string and enum format
                is_seen = False
                for seen_suit, seen_rank in self.seen_cards:
                    # Compare by string representation
                    suit_match = (str(seen_suit).endswith(suit_str.upper()) or 
                                 str(seen_suit) == suit_str)
                    rank_match = (str(seen_rank).endswith(rank_str.upper()) or 
                                 str(seen_rank) == rank_str or
                                 (rank_str.isdigit() and str(seen_rank).endswith(self._number_to_name(rank_str))))
                    if suit_match and rank_match:
                        is_seen = True
                        break
                
                if not is_seen:
                    remaining[suit_str].append(rank_str)
        
        return remaining
    
    def _number_to_name(self, num_str):
        """Convert numeric string to card name"""
        names = {
            "2": "TWO", "3": "THREE", "4": "FOUR", "5": "FIVE",
            "6": "SIX", "7": "SEVEN", "8": "EIGHT", "9": "NINE",
            "10": "TEN", "J": "JACK", "Q": "QUEEN", "K": "KING", "A": "ACE"
        }
        return names.get(num_str, num_str)
    
    def get_deck_size(self, board):
        """Get actual remaining deck size"""
        if hasattr(board, 'deck') and hasattr(board.deck, 'cards'):
            return len(board.deck.cards)
        return 52 - len(self.seen_cards)
    
    # -----------------------------
    # EV Calculations
    # -----------------------------
    
    def calculate_exact_deck_ev(self, hand):
        """Calculate exact expected value of drawing from deck"""
        remaining = self.get_remaining_cards()
        total_unseen = sum(len(ranks) for ranks in remaining.values())
        
        if total_unseen == 0:
            return best_score_from_cards(hand)
        
        total_ev = 0
        for suit, ranks in remaining.items():
            for rank in ranks:
                # Simulate drawing this specific card
                simulated_card = type(hand[0])(rank, suit)
                possible_hand = hand + [simulated_card]
                
                # Find best 3-card combo after drawing
                best_score = max(
                    best_score_from_cards(list(combo)) 
                    for combo in itertools.combinations(possible_hand, 3)
                )
                
                # Weight by probability
                total_ev += best_score / total_unseen
        
        return total_ev
    
    def calculate_discard_ev(self, hand, top_discard):
        """Calculate exact value of drawing from discard (certain outcome)"""
        possible_hand = hand + top_discard
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
        
        # Count cards that could give opponent a winning hand
        # Conservative estimate: assume opponents have 20-25 points already
        winning_threshold = my_score + 1
        dangerous_cards = 0
        
        for suit, ranks in remaining.items():
            for rank in ranks:
                value = 11 if rank == "A" else 10 if rank in ["J","Q","K"] else int(rank)
                # If adding this card could push opponent from ~20 to winning
                if value >= 10:  # High-value cards are dangerous
                    dangerous_cards += 1
        
        # Each opponent has (total_players - 1) chances
        single_opponent_fail_prob = 1 - (dangerous_cards / total_unseen)
        all_opponents_fail_prob = single_opponent_fail_prob ** (self.total_players - 1)
        
        return 1 - all_opponents_fail_prob
    
    def should_go_for_31(self, hand, board):
        """Determine if we should try for 31 instead of knocking"""
        current_score = best_score_from_cards(hand)
        
        if current_score >= 31:
            return False  # Already at/above 31
        
        if current_score < 26:
            return False  # Too far away
        
        # Calculate how many cards in deck give us 31
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
        
        # Go for 31 if probability is reasonable (>10%) and we're close
        return probability_of_31 > 0.10 and current_score >= 28
    
    # -----------------------------
    # Decision Logic
    # -----------------------------
    
    def decide_knock_threshold(self, board):
        """Dynamic knock threshold based on game state"""
        base_threshold = 27
        
        # Adjust for deck depletion
        deck_size = self.get_deck_size(board)
        if deck_size <= 10:
            base_threshold -= 2  # More aggressive when deck is low
        elif deck_size <= 20:
            base_threshold -= 1
        
        # Adjust for position (later position = safer to knock lower)
        if self.my_position == self.total_players - 1:
            base_threshold -= 1  # Last player can knock more aggressively
        
        # Adjust for early game (be conservative)
        if self.turn_count <= 3:
            base_threshold += 1
        
        return base_threshold
    
    def should_knock(self, my_score, board):
        """Comprehensive knock decision"""
        threshold = self.decide_knock_threshold(board)
        
        if my_score < threshold:
            return False
        
        # Don't knock if going for 31 is viable
        if self.should_go_for_31([], board):  # Will recalculate with actual hand
            return False
        
        # Calculate risk: can opponents beat me?
        opponent_win_prob = self.calculate_opponent_winning_probability(my_score, board)
        
        # Knock if we have good score AND low risk of being beaten
        if my_score >= 29:
            return opponent_win_prob < 0.4  # Very strong hand, knock unless high risk
        elif my_score >= 27:
            return opponent_win_prob < 0.3  # Good hand, knock if low risk
        else:
            return opponent_win_prob < 0.2  # Marginal hand, only knock if very safe
    
    # -----------------------------
    # Main API
    # -----------------------------
    
    def choose_draw_move(self, hand, top_discard, board=None):
        """Main decision: KNOCK, DRAW_FROM_DECK, or DRAW_FROM_DISCARD"""
        
        # DEBUG OUTPUT (comment out for production)
        # print(f"\n=== BOT DEBUG ===")
        # print(f"Hand: {[str(c) for c in hand]}")
        # print(f"Current score: {best_score_from_cards(hand)}")
        
        # Fix top_discard format
        if top_discard and not isinstance(top_discard, list):
            top_discard = [top_discard]
        
        # Update state
        if board:
            self.update_state(board, hand)
            # remaining = self.get_remaining_cards()
            # total_remaining = sum(len(ranks) for ranks in remaining.values())
            # print(f"Seen cards: {len(self.seen_cards)}")
            # print(f"Unseen cards: {total_remaining}")
            # print(f"Someone knocked: {board.player_who_knocked != -1}")
        
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
            if self.should_knock(current_score, board):
                return ThirtyOneDrawChoiceMove.Choice.KNOCK
        
        # 3. COMPARE DRAW OPTIONS
        if top_discard:
            ev_discard = self.calculate_discard_ev(hand, top_discard)
        else:
            ev_discard = current_score
        
        ev_deck = self.calculate_exact_deck_ev(hand)
        
        # Add risk adjustment: prefer certainty when values are close
        CERTAINTY_BONUS = 0.5  # Prefer known outcome when close
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
        
        # Find card whose removal leaves best hand
        for card in hand:
            remaining = [c for c in hand if c != card]
            score = best_score_from_cards(remaining)
            
            if score > best_remaining_score:
                best_remaining_score = score
                best_choice = card
        
        return best_choice


# -----------------------------
# Player Class Wrapper
# -----------------------------

class ThirtyOneYOURNAMEPlayer():
    def __init__(self):
        super().__init__()
        self.bot = Algorithmic31BotV5()
        self.name = self.bot.name
    
    def choose_draw_move(self, cards, top_discard, board=None):
        return self.bot.choose_draw_move(cards, top_discard, board)
    
    def choose_discard_move(self, cards, top_discard):
        return self.bot.choose_discard_move(cards, top_discard)