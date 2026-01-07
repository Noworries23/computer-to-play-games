from MinimaxPlayer import MinimaxPlayer
from SuperTicTacToe.SuperTicTacToeMove import SuperTicTacToeMove
import random

MINIMAX_DEPTH = 4 # Do not change this

class SuperTicTacToeDeenPlayer(MinimaxPlayer):
    def __init__(self):
        super().__init__("Minimax AI", MINIMAX_DEPTH)

    def scoreBoard(self, board, player):
        """
        Evaluate the board state for the given player.
        Higher scores favor the player, lower scores favor opponent.
        """
        # Check terminal states
        if board.master_board.winner == player:
            return 1000  # Player won
        elif board.master_board.winner is not None:
            return -1000  # Opponent won
        
        score = 0
        opponent = board.players[1] if board.players[0] == player else board.players[0]
        
        # Score the master board state
        score += self._score_board_state(board.master_board, player, opponent) * 100
        
        # Score all sub-boards
        for row in range(3):
            for col in range(3):
                sub_board = board.sub_boards[row][col]
                # Only score if sub-board isn't won yet
                if sub_board.winner is None:
                    score += self._score_board_state(sub_board, player, opponent) * 10
                else:
                    # Give bonus for winning sub-boards, penalty for opponent winning
                    if sub_board.winner == player:
                        score += 50
                    else:
                        score -= 50
                
                # Bonus for controlling center sub-boards
                if row == 1 and col == 1:
                    score += self._score_board_state(sub_board, player, opponent) * 5
        
        return score
    
    def _score_board_state(self, board, player, opponent):
        """Score a single 3x3 board based on line control."""
        score = 0
        
        # Check all lines (rows, columns, diagonals)
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
        
        # Evaluate each line
        for line in lines:
            player_count = sum(1 for cell in line if cell == player)
            opponent_count = sum(1 for cell in line if cell == opponent)
            empty_count = sum(1 for cell in line if cell is None)
            
            # Winning line is best
            if player_count == 3:
                score += 10
            # Two in a row with one empty = strong position
            elif player_count == 2 and empty_count == 1:
                score += 3
            # One in a row with two empty = okay
            elif player_count == 1 and empty_count == 2:
                score += 1
            
            # Block opponent's winning moves
            if opponent_count == 3:
                score -= 10
            elif opponent_count == 2 and empty_count == 1:
                score -= 4  # Block harder than we attack
            elif opponent_count == 1 and empty_count == 2:
                score -= 0.5
        
        return score

