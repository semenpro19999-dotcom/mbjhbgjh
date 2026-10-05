class Board:
    def __init__(self):
        self.grid = [
            [0, 1, 1],
            [1, '*', 1],
            [1, 1, 0]
        ]

        self.height = len(self.grid)
        self.width = len(self.grid[0])

    def get_neighbors(self, x, y):
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

    def show(self):
        for row in self.grid:
            print(row)
