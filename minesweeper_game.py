"""
Встроенный движок Сапёра.

Рендерит игровое поле в numpy-массив (BGR-изображение),
что позволяет тестировать бота без реального экрана.

Также может показывать окно через OpenCV для ручной игры.
"""

import numpy as np
import cv2
import random


# Классические цвета Сапёра (BGR для OpenCV)
COLORS = {
    'closed': (192, 192, 192),       # Серый — закрытая клетка
    'closed_border': (128, 128, 128), # Тёмно-серый — рамка закрытой
    'open': (224, 224, 224),          # Светло-серый — открытая
    'open_border': (180, 180, 180),   # Рамка открытой
    'mine': (0, 0, 0),                # Чёрный — мина
    'mine_bg': (0, 0, 200),           # Красный фон при взрыве
    'flag_pole': (0, 0, 0),           # Чёрный — шест флага
    'flag': (0, 0, 220),              # Красный — флаг
    # Цифры (BGR)
    1: (180, 50, 30),     # Синий
    2: (30, 130, 30),     # Зелёный
    3: (30, 30, 200),     # Красный
    4: (130, 30, 30),     # Тёмно-синий
    5: (30, 80, 150),     # Коричневый
    6: (150, 130, 30),    # Бирюзовый
    7: (20, 20, 20),      # Почти чёрный
    8: (100, 100, 100),   # Серый
}


class MinesweeperGame:
    """
    Встроенный Сапёр.

    Состояния клеток:
    - 'closed' : закрыта
    - number (0-8) : открыта, число мин-соседей
    - 'mine' : мина (при взрыве)
    - 'flag' : помечена флагом

    Игровые состояния:
    - 'playing' : игра идёт
    - 'won' : победа
    - 'lost' : проигрыш (взрыв)
    - 'ready' : не начата
    """

    def __init__(self, width=9, height=9, mines=10, cell_size=30):
        self.width = width
        self.height = height
        self.mines_count = mines
        self.cell_size = cell_size

        self.grid = [['closed'] * width for _ in range(height)]
        self.mines = set()
        self.flags = set()
        self.state = 'ready'
        self.exploded = None  # (x, y) взорвавшейся мины

    def reset(self):
        """Сброс игры."""
        self.grid = [['closed'] * self.width for _ in range(self.height)]
        self.mines = set()
        self.flags = set()
        self.state = 'ready'
        self.exploded = None

    def _place_mines(self, safe_x, safe_y):
        """Расставляет мины, избегая клетки первого клика и её соседей."""
        safe_zone = set()
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = safe_x + dx, safe_y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    safe_zone.add((nx, ny))

        available = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in safe_zone
        ]

        self.mines = set(random.sample(available, min(self.mines_count, len(available))))

    def _count_mines(self, x, y):
        """Считает мины вокруг клетки."""
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in self.mines:
                    count += 1
        return count

    def click(self, x, y):
        """Открыть клетку. Возвращает состояние после клика."""
        if self.state in ('won', 'lost'):
            return self.state

        if not (0 <= x < self.width and 0 <= y < self.height):
            return self.state

        # Игнорируем флаги и уже открытые
        if (x, y) in self.flags:
            return self.state
        if self.grid[y][x] != 'closed':
            return self.state

        # Первый клик — расставляем мины
        if self.state == 'ready':
            self._place_mines(x, y)
            self.state = 'playing'

        # Мина!
        if (x, y) in self.mines:
            self.grid[y][x] = 'mine'
            self.exploded = (x, y)
            self.state = 'lost'
            return 'lost'

        # Открыть с flood fill для нулей
        self._open_cell(x, y)

        # Проверка победы
        if self._check_win():
            self.state = 'won'
            return 'won'

        return 'playing'

    def _open_cell(self, x, y):
        """Рекурсивное открытие клеток (flood fill для 0)."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        if self.grid[y][x] != 'closed':
            return
        if (x, y) in self.flags:
            return

        count = self._count_mines(x, y)
        self.grid[y][x] = count

        if count == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    self._open_cell(x + dx, y + dy)

    def flag(self, x, y):
        """Поставить/снять флаг."""
        if self.state not in ('playing', 'ready'):
            return
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        if self.grid[y][x] != 'closed':
            return

        if (x, y) in self.flags:
            self.flags.remove((x, y))
        else:
            self.flags.add((x, y))

    def _check_win(self):
        """Проверяет победу: все безопасные клетки открыты."""
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in self.mines and self.grid[y][x] == 'closed':
                    return False
        return True

    def render(self, reveal_all=False):
        """
        Рендерит поле в BGR numpy-массив.

        reveal_all=True — показать все мины (при проигрыше).
        """
        cs = self.cell_size
        img_w = self.width * cs
        img_h = self.height * cs
        img = np.zeros((img_h, img_w, 3), dtype=np.uint8)

        for y in range(self.height):
            for x in range(self.width):
                px = x * cs
                py = y * cs
                cell = self.grid[y][x]
                is_mine = (x, y) in self.mines

                if cell == 'closed':
                    # Закрытая клетка с 3D-эффектом
                    cv2.rectangle(img, (px, py), (px + cs - 1, py + cs - 1),
                                 COLORS['closed'], -1)
                    # Светлая грань сверху-слева
                    cv2.line(img, (px, py), (px + cs - 1, py), (220, 220, 220), 2)
                    cv2.line(img, (px, py), (px, py + cs - 1), (220, 220, 220), 2)
                    # Тёмная грань снизу-справа
                    cv2.line(img, (px + cs - 1, py), (px + cs - 1, py + cs - 1), (100, 100, 100), 2)
                    cv2.line(img, (px, py + cs - 1), (px + cs - 1, py + cs - 1), (100, 100, 100), 2)

                    # Флаг
                    if (x, y) in self.flags:
                        self._draw_flag(img, px, py, cs)

                elif cell == 'mine':
                    # Взорвавшаяся мина
                    if self.exploded == (x, y):
                        cv2.rectangle(img, (px, py), (px + cs - 1, py + cs - 1),
                                     COLORS['mine_bg'], -1)
                    else:
                        cv2.rectangle(img, (px, py), (px + cs - 1, py + cs - 1),
                                     COLORS['open'], -1)
                    self._draw_mine(img, px, py, cs)

                elif isinstance(cell, int):
                    # Открытая клетка
                    cv2.rectangle(img, (px, py), (px + cs - 1, py + cs - 1),
                                 COLORS['open'], -1)
                    cv2.rectangle(img, (px, py), (px + cs - 1, py + cs - 1),
                                 COLORS['open_border'], 1)
                    if cell > 0:
                        self._draw_number(img, px, py, cs, cell)

                # Показать все мины при проигрыше
                if reveal_all and self.state == 'lost':
                    if is_mine and cell == 'closed' and (x, y) != self.exploded:
                        cv2.rectangle(img, (px, py), (px + cs - 1, py + cs - 1),
                                     COLORS['open'], -1)
                        self._draw_mine(img, px, py, cs)

        return img

    def _draw_number(self, img, px, py, cs, number):
        """Рисует цифру в клетке."""
        color = COLORS.get(number, (0, 0, 0))
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = cs / 40.0
        thickness = max(1, int(cs / 15))

        text = str(number)
        (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
        tx = px + (cs - tw) // 2
        ty = py + (cs + th) // 2

        cv2.putText(img, text, (tx, ty), font, scale, color, thickness, cv2.LINE_AA)

    def _draw_mine(self, img, px, py, cs):
        """Рисует мину."""
        cx = px + cs // 2
        cy = py + cs // 2
        r = cs // 4
        cv2.circle(img, (cx, cy), r, COLORS['mine'], -1)
        # Шипы
        for angle in range(0, 360, 45):
            rad = np.deg2rad(angle)
            x1 = cx + int(r * np.cos(rad))
            y1 = cy + int(r * np.sin(rad))
            x2 = cx + int((r + cs // 8) * np.cos(rad))
            y2 = cy + int((r + cs // 8) * np.sin(rad))
            cv2.line(img, (x1, y1), (x2, y2), COLORS['mine'], 2)

    def _draw_flag(self, img, px, py, cs):
        """Рисует флаг."""
        cx = px + cs // 2
        # Шест
        cv2.line(img, (cx, py + cs // 4), (cx, py + 3 * cs // 4),
                COLORS['flag_pole'], 2)
        # Треугольник флага
        pts = np.array([
            [cx, py + cs // 4],
            [cx - cs // 4, py + cs // 3],
            [cx, py + cs // 2]
        ], dtype=np.int32)
        cv2.fillPoly(img, [pts], COLORS['flag'])

    def get_state_matrix(self):
        """
        Возвращает матрицу состояния для сравнения с распознаванием.

        Значения:
        - 'closed' / 'flag' для неоткрытых
        - число 0-8 для открытых
        - 'mine' для мин (при проигрыше)
        """
        matrix = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                cell = self.grid[y][x]
                if (x, y) in self.flags and cell == 'closed':
                    row.append('F')
                elif cell == 'closed':
                    row.append('?')
                elif cell == 'mine':
                    row.append('*')
                else:
                    row.append(cell)
            matrix.append(row)
        return matrix
