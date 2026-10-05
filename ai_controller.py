from vision import Vision
from solver import Solver
from clicker import Clicker
from safety import SafetySystem


class AIController:
    def __init__(self):
        self.vision = Vision()
        self.solver = Solver(None)
        self.clicker = Clicker()
        self.safety = SafetySystem()

    def start(self):
        print("🤖 AI controller started")

        while self.safety.running:
            board = self.vision.capture_board()

            if board is None:
                print("Waiting for board...")
                break

            self.solver.board = board
            move = self.solver.get_next_move()

            if move is None:
                print("No safe moves")
                break

            self.clicker.click(move[0], move[1])
