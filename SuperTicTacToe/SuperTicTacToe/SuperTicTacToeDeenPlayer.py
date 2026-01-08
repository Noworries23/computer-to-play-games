from MinimaxPlayer import MinimaxPlayer
from SuperTicTacToe.SuperTicTacToeMove import SuperTicTacToeMove
import multiprocessing as mp
from functools import partial
import random

MINIMAX_DEPTH = 5
NUM_WORKERS = 8  # Adjust based on your CPU cores

class SuperTicTacToeDeenPlayer(MinimaxPlayer):
    def __init__(self):
        super().__init__("Parallel Minimax AI", MINIMAX_DEPTH)
        self.use_parallel = True  # Set to False to disable parallelization

    def scoreBoard(self, board, player):
        """
        Evaluate the board state for the given player.
        Higher scores favor the player, lower scores favor opponent.
        """
        # Check terminal states first (fast path)
        if board.master_board.winner == player:
            return 10000  # Increased from 1000
        elif board.master_board.winner is not None:
            return -10000  # Opponent won
        
        score = 0
        opponent = board.players[1] if board.players[0] == player else board.players[0]
        
        # Score the master board state (most important)
        score += self._score_board_state(board.master_board, player, opponent) * 150
        
        # Score all sub-boards
        for row in range(3):
            for col in range(3):
                sub_board = board.sub_boards[row][col]
                
                if sub_board.winner is None:
                    # Active sub-board scoring
                    sub_score = self._score_board_state(sub_board, player, opponent)
                    
                    # Strategic position multipliers
                    multiplier = 10
                    if row == 1 and col == 1:  # Center
                        multiplier = 20
                    elif (row, col) in [(0,0), (0,2), (2,0), (2,2)]:  # Corners
                        multiplier = 15
                    
                    score += sub_score * multiplier
                else:
                    # Won/lost sub-board bonuses
                    if sub_board.winner == player:
                        base_bonus = 80
                        # Extra bonus for strategic positions
                        if row == 1 and col == 1:
                            base_bonus = 150
                        elif (row, col) in [(0,0), (0,2), (2,0), (2,2)]:
                            base_bonus = 100
                        score += base_bonus
                    else:
                        base_penalty = 80
                        if row == 1 and col == 1:
                            base_penalty = 150
                        elif (row, col) in [(0,0), (0,2), (2,0), (2,2)]:
                            base_penalty = 100
                        score -= base_penalty
        
        return score
    
    def _score_board_state(self, board, player, opponent):
        """Score a single 3x3 board based on line control."""
        score = 0
        
        # Pre-compute lines for efficiency
        lines = self._get_lines(board)
        
        # Evaluate each line
        for line in lines:
            player_count = sum(1 for cell in line if cell == player)
            opponent_count = sum(1 for cell in line if cell == opponent)
            empty_count = 3 - player_count - opponent_count
            
            # Pure lines (no opponent pieces)
            if opponent_count == 0:
                if player_count == 3:
                    score += 100  # Win
                elif player_count == 2:
                    score += 10   # Two in a row
                elif player_count == 1:
                    score += 1    # One in a row
            
            # Block opponent
            if player_count == 0:
                if opponent_count == 3:
                    score -= 100
                elif opponent_count == 2:
                    score -= 15  # Blocking is critical
                elif opponent_count == 1:
                    score -= 1
        
        return score
    
    def _get_lines(self, board):
        """Get all rows, columns, and diagonals from a 3x3 board."""
        lines = []
        
        # Rows
        for row in range(3):
            lines.append([board.board[row][col] for col in range(3)])
        
        # Columns
        for col in range(3):
            lines.append([board.board[row][col] for row in range(3)])
        
        # Diagonals
        lines.append([board.board[i][i] for i in range(3)])
        lines.append([board.board[i][2-i] for i in range(3)])
        
        return lines
    
    # =========================================================================
    # PARALLEL MINIMAX IMPLEMENTATION
    # =========================================================================
    
    def getMove(self, board):
        """
        Override to use parallel minimax at root level.
        """
        possible_moves = board.getPossibleMoves()
        
        if not possible_moves:
            return None
        
        if len(possible_moves) == 1:
            return possible_moves[0]
        
        # Use parallel search if enabled and worthwhile
        if self.use_parallel and len(possible_moves) > 4:
            return self._parallel_minimax_search(board, possible_moves)
        else:
            # Fall back to sequential minimax
            return self._sequential_minimax_search(board, possible_moves)
    
    def _parallel_minimax_search(self, board, possible_moves):
        """Parallel search: evaluate each root move in separate process."""
        # Create worker pool
        with mp.Pool(processes=min(NUM_WORKERS, len(possible_moves))) as pool:
            # Evaluate each move in parallel
            eval_func = partial(
                _evaluate_move_wrapper,
                board=board,
                depth=self.max_depth - 1,
                alpha=float('-inf'),
                beta=float('inf'),
                player=board.currentPlayer()
            )
            
            results = pool.map(eval_func, possible_moves)
        
        # Find best move
        best_score = max(results)
        best_moves = [move for move, score in zip(possible_moves, results) if score == best_score]
        
        return random.choice(best_moves)
    
    def _sequential_minimax_search(self, board, possible_moves):
        """Standard sequential minimax search."""
        best_score = float('-inf')
        best_moves = []
        alpha = float('-inf')
        beta = float('inf')
        
        for move in possible_moves:
            board_copy = board.clone()
            board_copy.doMove(move)
            
            score = self._minimax(
                board_copy,
                self.max_depth - 1,
                alpha,
                beta,
                False,
                board.currentPlayer()
            )
            
            if score > best_score:
                best_score = score
                best_moves = [move]
                alpha = score
            elif score == best_score:
                best_moves.append(move)
        
        return random.choice(best_moves) if best_moves else possible_moves[0]
    
    def _minimax(self, board, depth, alpha, beta, maximizing, original_player):
        """Standard minimax with alpha-beta pruning."""
        # Check terminal conditions
        winner = board.getGameEnded()
        if winner is not False:
            if winner == original_player:
                return 10000 + depth  # Win sooner is better
            elif winner is None:
                return 0  # Draw
            else:
                return -10000 - depth  # Lose later is better
        
        if depth == 0:
            return self.scoreBoard(board, original_player)
        
        possible_moves = board.getPossibleMoves()
        
        if maximizing:
            max_eval = float('-inf')
            for move in possible_moves:
                board_copy = board.clone()
                board_copy.doMove(move)
                eval_score = self._minimax(board_copy, depth - 1, alpha, beta, False, original_player)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:
            min_eval = float('inf')
            for move in possible_moves:
                board_copy = board.clone()
                board_copy.doMove(move)
                eval_score = self._minimax(board_copy, depth - 1, alpha, beta, True, original_player)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval


# =========================================================================
# HELPER FUNCTION FOR PARALLEL PROCESSING
# =========================================================================

def _evaluate_move_wrapper(move, board, depth, alpha, beta, player):
    """
    Wrapper function for parallel move evaluation.
    Must be at module level for multiprocessing to pickle it.
    """
    # Create a temporary player instance for evaluation
    temp_player = SuperTicTacToeDeenPlayer()
    
    # Clone board and make move
    board_copy = board.clone()
    board_copy.doMove(move)
    
    # Evaluate with minimax
    score = temp_player._minimax(
        board_copy,
        depth,
        alpha,
        beta,
        False,  # After our move, opponent's turn (minimizing)
        player
    )
    
    return score