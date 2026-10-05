import cv2
import numpy as np


class CellRecognizer:
    """Распознавание клеток сапёра.

    Пока используется базовый анализ изображения.
    Следующий этап: OCR/шаблоны цифр 0-8.
    """

    def __init__(self, cell_size=30):
        self.cell_size = cell_size

    def split_cells(self, image):
        cells = []

        height, width = image.shape[:2]

        for y in range(0, height, self.cell_size):
            row = []
            for x in range(0, width, self.cell_size):
                cell = image[y:y+self.cell_size, x:x+self.cell_size]
                row.append(cell)
            cells.append(row)

        return cells

    def recognize(self, cell):
        gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)

        brightness = np.mean(gray)

        if brightness < 50:
            return '*'

        return '?'

    def analyze_board(self, image):
        cells = self.split_cells(image)
        board = []

        for row in cells:
            board.append([self.recognize(cell) for cell in row])

        return board
