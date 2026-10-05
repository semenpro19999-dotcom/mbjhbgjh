class SolverBrain:
    """
    Дополнительные эвристики для принятия решений.
    Используется когда базовый Solver не находит гарантированных ходов.
    """

    def think(self, board):
        """Анализирует доску и возвращает рекомендации."""
        moves = []

        for y, row in enumerate(board.grid):
            for x, cell in enumerate(row):
                if cell == 0:
                    # Рядом с нулём — открываем соседей
                    for nx, ny in board.get_closed_neighbors(x, y):
                        moves.append((nx, ny, "safe_zero_neighbor", 0.0))

                elif isinstance(cell, int) and cell > 0:
                    closed = board.get_closed_neighbors(x, y)
                    flagged = board.get_flagged_neighbors(x, y)

                    if len(closed) > 0:
                        remaining = cell - len(flagged)
                        risk = remaining / len(closed) if closed else 1.0
                        for nx, ny in closed:
                            if board.grid[ny][nx] == '?':
                                moves.append((nx, ny, "probability", risk))

        # Сортируем: сначала безопасные (риск 0), потом по риску
        moves.sort(key=lambda m: m[3])
        return moves

    def choose_move(self, moves):
        """Выбирает лучший ход из списка."""
        if not moves:
            return None

        # Берём ход с минимальным риском
        return (moves[0][0], moves[0][1])
