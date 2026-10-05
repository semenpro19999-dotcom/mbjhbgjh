from board import Board
from solver import Solver


def main():
    print("🤖 Minesweeper AI started")

    board = Board()
    solver = Solver(board)

    solver.run()


if __name__ == "__main__":
    main()
