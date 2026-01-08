from Player import Player
from SuperTicTacToe.SuperTicTacToeMove import SuperTicTacToeMove

class SuperTicTacToeHumanPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def get_indices(self, string):
        while True:
            x, y = map(int, string.split(","))
            if 0 <= x < 3 and 0 <= y < 3:
                return x, y
            else:
                print("Invalid coordinates. Please enter again.")

    def getMove(self, board):
        if board.current_board is None:
            while True:
                print("Choose your board in the format x,y")
                board_input = input()
                try:
                    boardx, boardy = self.get_indices(board_input)
                    break
                except ValueError:
                    print("Invalid input format. Please enter again.")

        else:
            boardx, boardy = board.get_indices(board.current_board)
            print(f"Current board is {boardx},{boardy}")

        print("Choose the position you want to go in the format x,y")
        position = input()
        positionx, positiony = self.get_indices(position)

        return SuperTicTacToeMove(self, boardx, boardy, positionx, positiony)
