WHITE = 255, 255, 255
RED = 255,0,0
BLUE = 0,0,255

NCOLS = 3
NROWS = 3

class SingleTicTacToeBoard:
	def __init__(self):
		self.board = [[None for _ in range(3)] for _ in range(3)]
		self.winner = None
		self.is_full = False

	def clone(self):
		new_board = SingleTicTacToeBoard()
		new_board.board = [list(row) for row in self.board]
		new_board.winner = self.winner
		new_board.is_full = self.is_full
		return new_board

	def make_move(self, player, row, col):
		if self.board[row][col] == None and self.winner is None:
			self.board[row][col] = player
			if self.check_winner(player, row, col):
				self.winner = player
			elif all(cell != None for row in self.board for cell in row):
				self.is_full = True

	def check_winner(self, player, row, col):
		# Check row
		if all(self.board[row][c] == player for c in range(3)):
			return True
		# Check column
		if all(self.board[r][col] == player for r in range(3)):
			return True
		# Check diagonals
		if row == col and all(self.board[i][i] == player for i in range(3)):
			return True
		if row + col == 2 and all(self.board[i][2 - i] == player for i in range(3)):
			return True
		return False

	def draw_board(self, pygame, screen, left_disp_offset, top_disp_offset, box_size, thickness, players):
		for row_num in range(1, NROWS):
			row_start = (left_disp_offset, top_disp_offset + (box_size * row_num))
			row_end = (left_disp_offset + (box_size * NCOLS), top_disp_offset + (box_size * row_num))
			pygame.draw.line(screen, WHITE, row_start, row_end, thickness)
		for col_num in range(1, NCOLS):
			col_start = (left_disp_offset + (box_size * col_num), top_disp_offset)
			col_end = (left_disp_offset + (box_size * col_num), top_disp_offset + (box_size * NROWS))
			# if col_num > 0:
			# 	col_label = my_font.render(str(col_num), 1, WHITE)
			# 	self.screen.blit(col_label, (self.left_disp_offset + (self.box_size * col_num) - self.box_size / 2, self.height - 40))
			pygame.draw.line(screen, WHITE, col_start, col_end, thickness)
			radius = box_size / 2
		for row in range(NROWS):
			for col in range(NCOLS):
				mark = self.board[row][col]
				if mark is not None:
					pos = (int(box_size * (row + 0.5)) + left_disp_offset,
							int(box_size * (col + 0.5)) + top_disp_offset)
					rad = radius * .9
					if mark == players[0]:
						color = RED
						pygame.draw.line(screen, color, (pos[0] - rad, pos[1] - rad), (pos[0] + rad, pos[1] + rad), int(rad / 3))
						pygame.draw.line(screen, color, (pos[0] - rad, pos[1] + rad), (pos[0] + rad, pos[1] - rad), int(rad / 3))
					else:
						color = BLUE
						pygame.draw.circle(screen, color, pos, rad, int(rad / 3))
