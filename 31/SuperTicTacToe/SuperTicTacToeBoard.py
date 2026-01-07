from re import I
from SuperTicTacToe.SuperTicTacToeMove import SuperTicTacToeMove
from GameState import GameState
from SuperTicTacToe.SingleTicTacToeBoard import SingleTicTacToeBoard
from enum import Enum
import pygame

from TiePlayer import TiePlayer
pygame.init()

BLACK = 0,0,0


NROWS = 3
NCOLS = 3

pygame.font.init()

class SuperTicTacToeBoard(GameState):

    def __init__(self, player1, player2):
        super().__init__([player1, player2])

        # Basic setup
        self.master_board = SingleTicTacToeBoard()
        self.sub_boards = [[SingleTicTacToeBoard() for _ in range(3)] for _ in range(3)]
        self.current_player = self.players[0]
        self.current_board = None
        
    def clone(self):
        newBoard = SuperTicTacToeBoard(self.players[0], self.players[1])
        newBoard.master_board = self.master_board.clone()
        newBoard.sub_boards = []
        for x in range(3):
            for y in range(3):
                if len(newBoard.sub_boards) <= x:
                    newBoard.sub_boards.append([])
                newBoard.sub_boards[x].append(self.sub_boards[x][y].clone())
        newBoard.current_player = self.current_player
        if self.current_board is None:
            newBoard.current_board = None
        else:
            row,col = self.get_indices(self.current_board)
            newBoard.current_board = newBoard.sub_boards[row][col]
        return newBoard
    
    def getPossibleMoves(self):       
        possible_moves = []
        if self.current_board == None:
            possible_boards = [board for row in self.sub_boards for board in row]
        else:
            possible_boards = [self.current_board]

        for board in possible_boards:
            if board.winner is None and not board.is_full:
                boardx, boardy = self.get_indices(board)
                for row in range(3):
                    for col in range(3):
                        if board.board[row][col] is None:
                            possible_moves.append(SuperTicTacToeMove(self.current_player, boardx, boardy, row, col))
        return possible_moves

    def checkIsValid(self, move):
        if move.player != self.current_player:
            return False
        if self.current_board is not None:
            if self.current_board != self.sub_boards[move.boardx][move.boardy]:
                return False
        if self.sub_boards[move.boardx][move.boardy].board[move.positionx][move.positiony] is not None:
            return False
        return True

    def get_indices(self, board):
        if board is None:
            return None, None
        for row in range(3):
            for col in range(3):
                if board is self.sub_boards[row][col]:
                    return row, col
        raise Exception("Board not found!")

    def doMove(self, move):
        self.sub_boards[move.boardx][move.boardy].make_move(move.player, move.positionx, move.positiony)
        if self.sub_boards[move.boardx][move.boardy].winner is not None:
            self.master_board.make_move(move.player, move.boardx, move.boardy)

        if self.sub_boards[move.positionx][move.positiony].winner is None and not self.sub_boards[move.positionx][move.positiony].is_full:
            self.current_board = self.sub_boards[move.positionx][move.positiony]
        else:
            self.current_board = None

        self.current_player = self.next_player()
        return self
    
    def currentPlayer(self):
        return self.current_player

    def next_player(self):
        current_index = self.players.index(self.current_player)
        next_index = (current_index + 1) % len(self.players)
        return self.players[next_index]
        
    def getGameEnded(self):
        if self.master_board.winner is not None:
            return self.master_board.winner
            
        return False               
       
    def scoreBoard(self):
        # return the score for each player
        scores = {}
        winner = self.getGameEnded()
        if winner is False:
            return {player: 0 for player in self.players}
        else:
            for player in self.players:
                if player == winner:
                    scores[player] = 1
                else:
                    scores[player] = -1 # -1 for losing player
            return scores

        
    def initializeDrawing(self):
        self.width = 1000
        self.height = 750
        self.screen = pygame.display.set_mode((self.width, self.height))

        self.box_size = self.height / (NCOLS + 2)
        self.small_box_factor = 3
        self.small_box_size = self.box_size / self.small_box_factor
        self.small_box_drawing_size = self.small_box_size * .85
        self.left_disp_offset = self.box_size * 2
        self.top_disp_offset = self.box_size
        self.small_box_left_offset = self.small_box_size / 5
        self.small_box_top_offset = self.small_box_size / 5

        self.game_closed = False     

    def drawBoard(self):
        if self.game_closed:
            return
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_closed = True
                pygame.quit()

        # Reset screen
        self.screen.fill(BLACK)

        # Drawing the grid
        for row in range(NROWS):
            for col in range(NCOLS):
                self.sub_boards[row][col].draw_board(pygame, self.screen,
                                                    self.left_disp_offset + row * self.box_size + self.small_box_left_offset,
                                                    self.top_disp_offset + col * self.box_size + self.small_box_top_offset,
                                                    self.small_box_drawing_size,
                                                    1, self.players)
        
        self.master_board.draw_board(pygame, self.screen, self.left_disp_offset, self.top_disp_offset, self.box_size, 3, self.players)

        pygame.display.flip()
        pygame.time.wait(1000)
        

