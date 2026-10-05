import time
import threading

from vision import Vision
from cell_recognizer import CellRecognizer
from board import Board
from solver import Solver
from solver_brain import SolverBrain
from clicker import Clicker
from safety import SafetySystem
from hotkeys import Hotkeys
from selector import select_area

import config


class AIController:
    """
    Главный контроллер AI-бота для Сапёра.
    
    Полный цикл:
    1. Захватить скриншот области игры
    2. Распознать клетки → матрица
    3. Создать Board из матрицы
    4. Передать Board в Solver
    5. Получить ход: ('open', x, y) или ('flag', x, y)
    6. Кликнуть мышкой
    7. Повторять
    """

    def __init__(self):
        self.vision = Vision()
        self.recognizer = CellRecognizer(cell_size=config.CELL_SIZE)
        self.solver = Solver(None)
        self.brain = SolverBrain()
        self.clicker = Clicker(cell_size=config.CELL_SIZE)
        self.safety = SafetySystem()

        self.move_count = 0

    def start(self):
        """Запускает бота."""
        print("🤖 AI controller starting...")

        # 1. Определяем область игры
        board_area = config.BOARD_AREA
        if board_area is None:
            print("📐 Board area not set. Please select the Minesweeper area.")
            print("   Click two corners of the game board on the screenshot.")
            try:
                board_area = select_area()
                config.BOARD_AREA = board_area
                print(f"✅ Area selected: {board_area}")
            except Exception as e:
                print(f"❌ Failed to select area: {e}")
                print("   Set BOARD_AREA manually in config.py")
                return

        self.vision.set_board_area(board_area)
        self.clicker.set_board_area(board_area)

        # 2. Запускаем горячие клавиши в отдельном потоке
        hotkeys = Hotkeys(self.safety)
        hotkey_thread = threading.Thread(target=hotkeys.start, daemon=True)
        hotkey_thread.start()

        print("🎮 Bot is running! Press ESC to stop.")
        print(f"   Board area: {board_area}")
        print(f"   Cell size: {config.CELL_SIZE}px")
        print()

        # 3. Основной цикл
        while self.safety.is_running():
            try:
                self._game_loop_step()
            except Exception as e:
                print(f"⚠️ Error in game loop: {e}")

            time.sleep(config.MOVE_DELAY)

        print(f"\n🏁 Bot stopped. Total moves: {self.move_count}")

    def _game_loop_step(self):
        """Один шаг основного цикла."""
        # Захват экрана
        image = self.vision.capture_board()
        if image is None:
            print("⚠️ Could not capture board")
            return

        # Распознавание
        matrix = self.recognizer.analyze_board(image)
        if not matrix:
            print("⚠️ Board recognition returned empty result")
            return

        # Создаём Board
        board = Board(grid=matrix)

        # Проверка: есть ли хоть одна открытая клетка?
        has_open = any(
            isinstance(cell, int)
            for row in board.grid
            for cell in row
        )

        if not has_open:
            # Поле полностью закрыто — кликаем в центр для первого хода
            center_x = board.width // 2
            center_y = board.height // 2
            print(f"🎯 First move: opening center ({center_x}, {center_y})")
            self.clicker.click(center_x, center_y, 'left')
            self.move_count += 1
            return

        # Проверка взрыва
        if self.vision.detect_explosion(image):
            print("💣 Explosion detected!")
            self.safety.mine_detected()
            return

        # Решаем
        self.solver.board = board
        move = self.solver.get_next_move()

        if move is None:
            # Если Solver не нашёл ход — пробуем SolverBrain
            brain_moves = self.brain.think(board)
            best = self.brain.choose_move(brain_moves)
            if best:
                move = ('open', best[0], best[1])
            else:
                print("🤷 No moves found")
                return

        # Выполняем ход
        action, x, y = move
        self.move_count += 1
        print(f"#{self.move_count} {action.upper()} ({x}, {y})")

        if action == 'open':
            self.clicker.click(x, y, 'left')
        elif action == 'flag':
            self.clicker.click(x, y, 'right')
