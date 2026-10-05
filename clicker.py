import pyautogui
import time


class Clicker:
    """Управление мышью для кликов по игровому полю."""

    def __init__(self, board_area=None, cell_size=30):
        self.board_area = board_area  # (x1, y1, x2, y2)
        self.cell_size = cell_size

    def set_board_area(self, area):
        self.board_area = area

    def click(self, x, y, button='left'):
        """
        Кликает по клетке (x, y) на игровом поле.
        x, y — координаты клетки в матрице (не пиксели).
        """
        if self.board_area is None:
            print("⚠️ Board area not set!")
            return

        # Переводим координаты клетки в пиксели экрана
        pixel_x = self.board_area[0] + x * self.cell_size + self.cell_size // 2
        pixel_y = self.board_area[1] + y * self.cell_size + self.cell_size // 2

        print(f"  🖱️ {button} click at cell ({x},{y}) → pixel ({pixel_x},{pixel_y})")

        if button == 'left':
            pyautogui.click(pixel_x, pixel_y)
        elif button == 'right':
            pyautogui.rightClick(pixel_x, pixel_y)

    def left_click(self, x, y):
        """Клик левой кнопкой по пиксельным координатам."""
        pyautogui.click(x, y)

    def right_click(self, x, y):
        """Клик правой кнопкой по пиксельным координатам."""
        pyautogui.rightClick(x, y)
