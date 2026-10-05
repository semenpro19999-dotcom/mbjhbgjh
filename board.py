class Board:
    def __init__(self):
        self.grid = [
            [0, 1, 1],
            [1, '*', 1],
            [1, 1, 0]
        ]

    def show(self):
        for row in self.grid:
            print(row)
