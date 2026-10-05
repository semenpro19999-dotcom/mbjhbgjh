"""
End-to-end тест: бот играет во встроенный Сапёр.

Проверяет:
1. Рендеринг игры → изображение
2. Распознавание изображения → матрица
3. Solver → ход
4. Применение хода → новое состояние
5. Повторять до победы/проигрыша
"""

import sys
from minesweeper_game import MinesweeperGame
from cell_recognizer import CellRecognizer
from board import Board
from solver import Solver


def test_recognition_accuracy(game, recognizer):
    """
    Проверяет точность распознавания ВИДИМОГО состояния.
    
    Закрытые клетки (кроме флагов) должны распознаваться как '?'.
    Флаги как 'F'.
    Открытые клетки как их числа.
    Мины (при проигрыше) как '*'.
    """
    img = game.render()
    recognized = recognizer.analyze_board(img)
    
    # Получаем ВИДИМОЕ состояние (то что игрок видит на экране)
    visible = []
    for y in range(game.height):
        row = []
        for x in range(game.width):
            cell = game.grid[y][x]
            if cell == 'closed':
                if (x, y) in game.flags:
                    row.append('F')
                else:
                    row.append('?')
            elif cell == 'mine':
                row.append('*')
            else:
                row.append(cell)
        visible.append(row)

    correct = 0
    total = 0
    errors = []

    for y in range(game.height):
        for x in range(game.width):
            expected = visible[y][x]
            recognized_val = recognized[y][x] if y < len(recognized) and x < len(recognized[y]) else None

            total += 1
            if expected == recognized_val:
                correct += 1
            else:
                errors.append((x, y, expected, recognized_val))

    accuracy = correct / total * 100 if total > 0 else 0
    return accuracy, errors


def play_game(width=9, height=9, mines=10, cell_size=30, max_moves=200, verbose=True):
    """
    Бот играет одну партию.

    Возвращает:
    - result: 'won' / 'lost' / 'timeout'
    - moves: количество ходов
    - accuracy: средняя точность распознавания
    """
    game = MinesweeperGame(width, height, mines, cell_size)
    recognizer = CellRecognizer(cell_size=cell_size)
    solver = Solver(None)

    move_count = 0
    accuracies = []

    if verbose:
        print(f"🎮 Starting game: {width}x{height}, {mines} mines")
        print()

    while move_count < max_moves:
        # Рендер
        img = game.render()

        # Распознавание
        matrix = recognizer.analyze_board(img)
        if not matrix:
            if verbose:
                print("❌ Recognition returned empty")
            return 'error', move_count, 0

        # Проверка точности
        acc, errors = test_recognition_accuracy(game, recognizer)
        accuracies.append(acc)

        if verbose and acc < 90:
            print(f"⚠️ Move {move_count}: accuracy {acc:.1f}%")
            for x, y, actual, recognized in errors[:5]:
                print(f"   ({x},{y}): expected {actual}, got {recognized}")

        # Создаём Board
        board = Board(grid=matrix)

        # Первый ход — в центр
        if game.state == 'ready':
            cx, cy = width // 2, height // 2
            if verbose:
                print(f"#{move_count} FIRST CLICK ({cx}, {cy})")
            game.click(cx, cy)
            move_count += 1
            continue

        # Проверяем состояние
        if game.state == 'won':
            if verbose:
                print(f"🏆 WON in {move_count} moves!")
            return 'won', move_count, sum(accuracies) / len(accuracies)

        if game.state == 'lost':
            if verbose:
                print(f"💣 LOST at move {move_count}")
            return 'lost', move_count, sum(accuracies) / len(accuracies)

        # Решаем
        solver.board = board
        move = solver.get_next_move()

        if move is None:
            if verbose:
                print(f"❌ No move found at move {move_count}")
            return 'stuck', move_count, sum(accuracies) / len(accuracies)

        # Применяем ход
        action, x, y = move
        if verbose:
            print(f"#{move_count} {action.upper()} ({x}, {y})", end='')

        if action == 'open':
            result = game.click(x, y)
            if verbose:
                print(f" → {result}")
        elif action == 'flag':
            game.flag(x, y)
            if verbose:
                print()

        move_count += 1

    if verbose:
        print(f"⏱️ TIMEOUT after {max_moves} moves")
    return 'timeout', move_count, sum(accuracies) / len(accuracies)


def run_tests(num_games=10):
    """Запускает серию игр и собирает статистику."""
    print("=" * 60)
    print("MINESWEEPER AI END-TO-END TEST")
    print("=" * 60)
    print()

    results = {'won': 0, 'lost': 0, 'timeout': 0, 'stuck': 0, 'error': 0}
    total_moves = []
    total_accuracy = []

    for i in range(num_games):
        print(f"\n{'='*60}")
        print(f"GAME {i+1}/{num_games}")
        print(f"{'='*60}\n")

        result, moves, accuracy = play_game(
            width=9, height=9, mines=10, cell_size=30,
            max_moves=100, verbose=(i == 0)  # Детали только для первой игры
        )

        results[result] += 1
        if result in ('won', 'lost'):
            total_moves.append(moves)
        total_accuracy.append(accuracy)

        print(f"Result: {result.upper()}, Moves: {moves}, Accuracy: {accuracy:.1f}%")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Games played: {num_games}")
    print(f"Won: {results['won']} ({results['won']/num_games*100:.1f}%)")
    print(f"Lost: {results['lost']} ({results['lost']/num_games*100:.1f}%)")
    print(f"Timeout: {results['timeout']}")
    print(f"Stuck: {results['stuck']}")
    print(f"Errors: {results['error']}")
    if total_moves:
        print(f"Avg moves (won/lost): {sum(total_moves)/len(total_moves):.1f}")
    if total_accuracy:
        print(f"Avg accuracy: {sum(total_accuracy)/len(total_accuracy):.1f}%")
    print("=" * 60)

    return results


if __name__ == '__main__':
    num_games = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    run_tests(num_games)
