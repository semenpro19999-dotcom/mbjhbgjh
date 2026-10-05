import random
from board import Board


class Solver:
    """
    Решатель Сапёра.
    
    Правила:
    1. Если клетка=0, все закрытые соседи безопасны
    2. Если число = кол-во закрытых соседей, все они мины
    3. Если число = кол-во флагов-соседей, остальные соседи безопасны
    4. Если нет гарантированных ходов — вероятностный анализ
    """

    def __init__(self, board):
        self.board = board

    def get_next_move(self):
        """
        Возвращает следующий ход: ('open', x, y) или ('flag', x, y).
        None если ходов нет.
        """
        if self.board is None:
            return None

        # 1. Гарантированно безопасные клетки
        safe = self.find_safe_moves()
        if safe:
            x, y = safe[0]
            return ('open', x, y)

        # 2. Гарантированные мины (для флагания)
        mines = self.find_confirmed_mines()
        if mines:
            x, y = mines[0]
            return ('flag', x, y)

        # 3. Вероятностный анализ
        best = self.find_best_probability_move()
        if best:
            return ('open', best[0], best[1])

        return None

    def find_safe_moves(self):
        """Находит гарантированно безопасные клетки."""
        safe = set()

        for y in range(self.board.height):
            for x in range(self.board.width):
                cell = self.board.grid[y][x]

                if not isinstance(cell, int) or cell < 0:
                    continue

                # Правило 1: клетка = 0 → все закрытые соседи безопасны
                if cell == 0:
                    for nx, ny in self.board.get_closed_neighbors(x, y):
                        safe.add((nx, ny))
                    continue

                # Правило 3: число = кол-во флагов → остальные соседи безопасны
                flagged = self.board.get_flagged_neighbors(x, y)
                closed = self.board.get_closed_neighbors(x, y)

                if len(flagged) == cell and len(closed) > len(flagged):
                    for nx, ny in closed:
                        if self.board.grid[ny][nx] != 'F':
                            safe.add((nx, ny))

        return list(safe)

    def find_confirmed_mines(self):
        """Находит гарантированные мины."""
        mines = set()

        for y in range(self.board.height):
            for x in range(self.board.width):
                cell = self.board.grid[y][x]

                if not isinstance(cell, int) or cell <= 0:
                    continue

                # Правило 2: число = кол-во закрытых соседей → все они мины
                closed = self.board.get_closed_neighbors(x, y)
                flagged = self.board.get_flagged_neighbors(x, y)

                remaining = cell - len(flagged)
                unknown = [c for c in closed if self.board.grid[c[1]][c[0]] == '?']

                if remaining > 0 and len(unknown) == remaining:
                    for nx, ny in unknown:
                        mines.add((nx, ny))

        return list(mines)

    def find_best_probability_move(self):
        """Находит клетку с минимальной вероятностью мины."""
        # Собираем все закрытые клетки
        closed_cells = []
        for y in range(self.board.height):
            for x in range(self.board.width):
                if self.board.grid[y][x] == '?':
                    closed_cells.append((x, y))

        if not closed_cells:
            return None

        # Для каждой закрытой клетки оцениваем риск
        best_cell = None
        best_risk = 1.0  # Начинаем с максимального риска

        for cx, cy in closed_cells:
            risk = self._estimate_mine_probability(cx, cy)
            if risk < best_risk:
                best_risk = risk
                best_cell = (cx, cy)

        return best_cell

    def _estimate_mine_probability(self, x, y):
        """Оценивает вероятность того, что клетка — мина."""
        max_risk = 0.0

        # Смотрим на все соседние числа
        for nx, ny in self.board.get_neighbors(x, y):
            cell = self.board.grid[ny][nx]
            if not isinstance(cell, int) or cell <= 0:
                continue

            closed = self.board.get_closed_neighbors(nx, ny)
            flagged = self.board.get_flagged_neighbors(nx, ny)

            unknown = [c for c in closed if self.board.grid[c[1]][c[0]] == '?']

            if len(unknown) == 0:
                continue

            remaining_mines = cell - len(flagged)
            if remaining_mines <= 0:
                continue

            # Вероятность = оставшиеся мины / неизвестные клетки
            risk = remaining_mines / len(unknown)
            max_risk = max(max_risk, risk)

        # Если нет соседних чисел — базовая вероятность
        if max_risk == 0.0:
            # Подсчитаем общие мины (приблизительно)
            total_cells = self.board.width * self.board.height
            closed_count = sum(
                1 for row in self.board.grid for c in row if c == '?'
            )
            flagged_count = sum(
                1 for row in self.board.grid for c in row if c == 'F'
            )
            # Предполагаем ~15% мин на поле
            estimated_mines = int(total_cells * 0.15) - flagged_count
            if closed_count > 0 and estimated_mines > 0:
                max_risk = estimated_mines / closed_count
            elif closed_count > 0:
                max_risk = 0.15

        return max_risk

    def run(self):
        """Для отладки."""
        print("🧠 Solver running")
        self.board.show()
        move = self.get_next_move()
        print("✅ Next move:", move)
