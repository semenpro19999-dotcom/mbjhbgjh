class Board:
    """
    Представляет игровое поле Сапёра.
    
    Значения клеток:
    - '?' : закрытая клетка
    - '*' : мина (известная/отмеченная)
    - 'F' : флаг (помеченная мина)
    - 0-8 : открытая клетка с числом мин-соседей
    """

    def __init__(self, grid=None):
        if grid is not None:
            self.grid = grid
        else:
            self.grid = []

        self.height = len(self.grid)
        self.width = len(self.grid[0]) if self.height > 0 else 0

    def get_neighbors(self, x, y):
        """Возвращает координаты всех соседних клеток."""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx = x + dx
                ny = y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append((nx, ny))
        return neighbors

    def get_closed_neighbors(self, x, y):
        """Возвращает только закрытые соседние клетки."""
        return [(nx, ny) for nx, ny in self.get_neighbors(x, y)
                if self.grid[ny][nx] == '?']

    def get_flagged_neighbors(self, x, y):
        """Возвращает соседей, помеченных флагом."""
        return [(nx, ny) for nx, ny in self.get_neighbors(x, y)
                if self.grid[ny][nx] == 'F']

    def get_cell(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None

    def show(self):
        for row in self.grid:
            display = []
            for cell in row:
                if cell == '?':
                    display.append('■')
                elif cell == '*':
                    display.append('💣')
                elif cell == 'F':
                    display.append('🚩')
                elif cell == 0:
                    display.append('·')
                else:
                    display.append(str(cell))
            print(' '.join(display))
