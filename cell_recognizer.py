import cv2
import numpy as np


class CellRecognizer:
    """Распознавание клеток сапёра.
    
    Распознаёт:
    - Закрытые клетки (серый фон) → '?'
    - Мины (чёрный/красный) → '*'
    - Флаги → 'F'
    - Цифры 1-8 по цвету
    - Пустые клетки → 0
    """

    # Цвета цифр в классическом Сапёр (BGR формат для OpenCV)
    NUMBER_COLORS = {
        1: (255, 0, 0),      # Синий
        2: (0, 128, 0),      # Зелёный
        3: (0, 0, 255),      # Красный
        4: (128, 0, 0),      # Тёмно-синий
        5: (0, 64, 128),     # Коричневый
        6: (128, 128, 0),    # Бирюзовый
        7: (0, 0, 0),        # Чёрный
        8: (128, 128, 128),  # Серый
    }

    def __init__(self, cell_size=30):
        self.cell_size = cell_size
        self.templates = {}

    def split_cells(self, image):
        """Разбивает изображение на клетки."""
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
        """Распознаёт одну клетку."""
        if cell.size == 0:
            return '?'

        gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(cell, cv2.COLOR_BGR2HSV)
        
        height, width = cell.shape[:2]
        center_region = cell[height//4:3*height//4, width//4:3*width//4]
        
        # Средние значения
        brightness = np.mean(gray)
        center_brightness = np.mean(cv2.cvtColor(center_region, cv2.COLOR_BGR2GRAY))
        
        # 1. Закрытая клетка: серый фон, высокая яркость, однородная
        if brightness > 180 and np.std(gray) < 30:
            return '?'
        
        # 2. Мина: очень тёмная или красная
        if brightness < 60:
            return '*'
        
        # Проверяем красный цвет (мина после взрыва)
        red_lower = np.array([0, 100, 100])
        red_upper = np.array([10, 255, 255])
        red_mask = cv2.inRange(hsv, red_lower, red_upper)
        if np.sum(red_mask) > (height * width * 0.3):
            return '*'
        
        # 3. Флаг: красный треугольник
        if np.sum(red_mask) > (height * width * 0.1) and brightness > 100:
            return 'F'
        
        # 4. Открытая клетка: светлый фон
        if brightness > 200:
            # Пытаемся распознать цифру по цвету
            number = self._recognize_number_by_color(cell, hsv)
            if number is not None:
                return number
            return 0
        
        # 5. Неизвестно
        return '?'

    def _recognize_number_by_color(self, cell, hsv):
        """Распознаёт цифру по доминирующему цвету."""
        height, width = cell.shape[:2]
        center = cell[height//4:3*height//4, width//4:3*width//4]
        
        # Проверяем каждый цвет
        best_number = None
        best_score = 0
        
        for number, bgr_color in self.NUMBER_COLORS.items():
            # Создаём маску для этого цвета
            lower = np.array([max(0, c - 50) for c in bgr_color])
            upper = np.array([min(255, c + 50) for c in bgr_color])
            
            mask = cv2.inRange(center, lower, upper)
            score = np.sum(mask)
            
            if score > best_score and score > (center.shape[0] * center.shape[1] * 20):
                best_score = score
                best_number = number
        
        return best_number

    def analyze_board(self, image):
        """Анализирует всё поле и возвращает матрицу."""
        if image is None or image.size == 0:
            return []

        cells = self.split_cells(image)
        board = []

        for row in cells:
            board.append([self.recognize(cell) for cell in row])

        return board

    def load_templates(self, template_dir):
        """Загружает эталонные изображения цифр для template matching."""
        import os
        self.templates = {}
        
        if not os.path.exists(template_dir):
            print(f"Template directory {template_dir} not found")
            return
        
        for i in range(1, 9):
            path = os.path.join(template_dir, f"{i}.png")
            if os.path.exists(path):
                self.templates[i] = cv2.imread(path, 0)
        
        print(f"Loaded {len(self.templates)} templates")
