class SolverBrain:
    """
    Rules used by AI to make decisions.
    """

    def think(self, board):
        moves = []

        for y, row in enumerate(board):
            for x, cell in enumerate(row):

                if cell == 0:
                    moves.append((x, y, "open_neighbors"))

                if isinstance(cell, int) and cell > 0:
                    moves.append((x, y, "analyze_probability"))

        return moves

    def choose_move(self, moves):
        if not moves:
            return None

        return moves[0]
