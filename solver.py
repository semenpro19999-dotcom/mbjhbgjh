"""
Продвинутый решатель Сапёра с constraint propagation.

Правила:
1. Базовые: ноль, все мины найдены, все флаги расставлены
2. Constraint propagation: анализ групп клеток
3. Subset analysis: паттерны 1-2-1, 1-2-2-1
4. Вероятностный анализ как последний resort
"""

from board import Board


class Solver:
    def __init__(self, board):
        self.board = board

    def get_next_move(self):
        """
        Возвращает следующий ход: ('open', x, y) или ('flag', x, y).
        None если ходов нет.
        """
        if self.board is None:
            return None

        # 1. Гарантированно безопасные клетки (базовые правила)
        safe = self.find_safe_moves()
        if safe:
            return ('open', safe[0][0], safe[0][1])

        # 2. Гарантированные мины (для флагания)
        mines = self.find_confirmed_mines()
        if mines:
            return ('flag', mines[0][0], mines[0][1])

        # 3. Constraint propagation (продвинутая логика)
        safe, mines = self.constraint_propagation()
        if safe:
            return ('open', safe[0][0], safe[0][1])
        if mines:
            return ('flag', mines[0][0], mines[0][1])

        # 4. Вероятностный анализ (последний resort)
        best = self.find_best_probability_move()
        if best:
            return ('open', best[0], best[1])

        return None

    def find_safe_moves(self):
        """Базовые правила: находит гарантированно безопасные клетки."""
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
        """Базовые правила: находит гарантированные мины."""
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

    def constraint_propagation(self):
        """
        Продвинутая логика: анализ ограничений.
        
        Для каждой пары соседних чисел проверяем:
        - Если одно число "видит" подмножество клеток другого,
          то разность может дать информацию.
        """
        safe = set()
        mines = set()

        # Собираем все числа и их ограничения
        constraints = []
        for y in range(self.board.height):
            for x in range(self.board.width):
                cell = self.board.grid[y][x]
                if isinstance(cell, int) and cell > 0:
                    closed = self.board.get_closed_neighbors(x, y)
                    flagged = self.board.get_flagged_neighbors(x, y)
                    unknown = [c for c in closed if self.board.grid[c[1]][c[0]] == '?']
                    remaining = cell - len(flagged)
                    if unknown and remaining > 0:
                        constraints.append((set(unknown), remaining))

        # Анализируем пары ограничений
        for i, (cells1, mines1) in enumerate(constraints):
            for j, (cells2, mines2) in enumerate(constraints):
                if i >= j:
                    continue

                # Проверяем подмножество
                if cells1.issubset(cells2):
                    # cells1 ⊆ cells2
                    # mines1 мин в cells1, mines2 мин в cells2
                    # Значит в (cells2 - cells1) должно быть (mines2 - mines1) мин
                    diff = cells2 - cells1
                    diff_mines = mines2 - mines1

                    if diff_mines == 0:
                        # Все клетки в diff безопасны
                        safe.update(diff)
                    elif diff_mines == len(diff):
                        # Все клетки в diff — мины
                        mines.update(diff)

                elif cells2.issubset(cells1):
                    # cells2 ⊆ cells1
                    diff = cells1 - cells2
                    diff_mines = mines1 - mines2

                    if diff_mines == 0:
                        safe.update(diff)
                    elif diff_mines == len(diff):
                        mines.update(diff)

        return list(safe), list(mines)

    def find_best_probability_move(self):
        """
        Находит клетку с минимальной вероятностью мины.
        
        Использует комбинированный подход:
        1. Локальная вероятность (от соседних чисел)
        2. Глобальная вероятность (от общего количества мин)
        3. Предпочтение клеток на границе (больше информации)
        """
        closed_cells = []
        for y in range(self.board.height):
            for x in range(self.board.width):
                if self.board.grid[y][x] == '?':
                    closed_cells.append((x, y))

        if not closed_cells:
            return None

        # Глобальная статистика
        total_cells = self.board.width * self.board.height
        flagged_count = sum(1 for row in self.board.grid for c in row if c == 'F')
        closed_count = len(closed_cells)
        
        # Оцениваем оставшиеся мины (примерно 12-15% для beginner)
        estimated_mines_remaining = max(1, int(total_cells * 0.12) - flagged_count)
        global_risk = estimated_mines_remaining / closed_count if closed_count > 0 else 0.5

        best_cell = None
        best_score = float('inf')

        for cx, cy in closed_cells:
            # Локальный риск (от соседних чисел)
            local_risk = self._estimate_local_risk(cx, cy)
            
            # Если нет локальной информации, используем глобальную
            if local_risk == 0.0:
                risk = global_risk
            else:
                # Комбинируем локальную и глобальную оценки
                risk = max(local_risk, global_risk * 0.5)
            
            # Бонус за "граничные" клетки (соседствуют с открытыми)
            # Они дают больше информации
            open_neighbors = sum(
                1 for nx, ny in self.board.get_neighbors(cx, cy)
                if isinstance(self.board.grid[ny][nx], int)
            )
            info_bonus = 1.0 - (open_neighbors / 8.0) * 0.2  # до 20% бонуса
            
            # Итоговая оценка: риск * информационный бонус
            score = risk * info_bonus
            
            if score < best_score:
                best_score = score
                best_cell = (cx, cy)

        return best_cell

    def _estimate_local_risk(self, x, y):
        """Оценивает локальный риск от соседних чисел."""
        max_risk = 0.0

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

            risk = remaining_mines / len(unknown)
            max_risk = max(max_risk, risk)

        return max_risk

    def _estimate_mine_probability(self, x, y):
        """Оценивает вероятность того, что клетка — мина (для отладки)."""
        return self._estimate_local_risk(x, y)

    def run(self):
        """Для отладки."""
        print("🧠 Solver running")
        self.board.show()
        move = self.get_next_move()
        print("✅ Next move:", move)
