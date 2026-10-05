class MinesweeperEngine:
    def __init__(self):
        self.running = False

    def start(self):
        self.running = True
        print('Minesweeper AI engine started')

    def stop(self):
        self.running = False
        print('Minesweeper AI stopped')
