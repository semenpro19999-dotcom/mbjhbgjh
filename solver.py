class Solver:
    def __init__(self, board):
        self.board = board

    def find_safe_moves(self):
        safe_moves = []

        for y in range(self.board.height):
            for x in range(self.board.width):

                cell = self.board.grid[y][x]

                if isinstance(cell, int) and cell == 0:
                    for nx, ny in self.board.get_neighbors(x, y):
                        if self.board.grid[ny][nx] == '*':
                            safe_moves.append((nx, ny))

        return safe_moves

    def run(self):
        print("🧠 Solver running")

        self.board.show()

        moves = self.find_safe_moves()

        print("✅ Safe moves:", moves)
