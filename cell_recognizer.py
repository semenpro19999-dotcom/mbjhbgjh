"""
Распознавание клеток Сапёра.

Использует template matching для точного распозна цифр 1-8,
и анализ структуры клетки для определения закрытых/открытых/мин/флагов.
"""

import cv2
import numpy as np
import os


class CellRecognizer:
    """
    Распознавание клеток Сапёра.
    
    Поддерживает два режима:
    1. Template matching — точный, использует эталонные изображения
    2. Color-based — запасной вариант
    
    Автоматически генерирует шаблоны для template matching.
    """

    # Цвета цифр классического Сапёра (BGR)
    NUMBER_COLORS_BGR = {
        1: (180, 50, 30),
        2: (30, 130, 30),
        3: (30, 30, 200),
        4: (130, 30, 30),
        5: (30, 80, 150),
        6: (150, 130, 30),
        7: (20, 20, 20),
        8: (100, 100, 100),
    }

    def __init__(self, cell_size=30, templates_dir=None):
        self.cell_size = cell_size
        self.templates = {}

        # Генерируем эталонные шаблоны
        self._generate_templates()

        # Загружаем пользовательские шаблоны если есть
        if templates_dir and os.path.exists(templates_dir):
            self.load_templates(templates_dir)

    def _generate_templates(self):
        """Генерирует эталонные шаблоны цифр программно."""
        cs = self.cell_size

        # Эталонные цифры
        for number, color in self.NUMBER_COLORS_BGR.items():
            tmpl = np.full((cs, cs, 3), 224, dtype=np.uint8)
            font = cv2.FONT_HERSHEY_SIMPLEX
            scale = cs / 40.0
            thickness = max(1, int(cs / 15))
            text = str(number)
            (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
            tx = (cs - tw) // 2
            ty = (cs + th) // 2
            cv2.putText(tmpl, text, (tx, ty), font, scale, color, thickness, cv2.LINE_AA)
            self.templates[number] = tmpl

    def split_cells(self, image):
        """Разбивает изображение на клетки."""
        cells = []
        height, width = image.shape[:2]

        for y in range(0, height, self.cell_size):
            row = []
            for x in range(0, width, self.cell_size):
                cell = image[y:y+self.cell_size, x:x+self.cell_size]
                if cell.shape[0] == self.cell_size and cell.shape[1] == self.cell_size:
                    row.append(cell)
            if row:
                cells.append(row)

        return cells

    def _is_closed(self, cell):
        """
        Определяет закрытую клетку.
        
        Закрытая клетка:
        - Центр: однородный серый (~192)
        - Границы: 3D-эффект (светлый верх/лево, тёмный низ/право)
        """
        cs = self.cell_size
        gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)

        # Центральная область (без границ)
        margin = cs // 5  # 20% отступ от краёв
        center = gray[margin:cs-margin, margin:cs-margin]
        center_mean = np.mean(center)
        center_std = np.std(center)

        # Центр должен быть однородным серым (160-210)
        if not (160 < center_mean < 210 and center_std < 20):
            return False

        # Проверяем 3D-эффект:
        # Светлая верхняя грань (строки 0-2)
        top_strip = gray[0:2, margin:cs-margin]
        # Тёмная нижняя грань (строки cs-4 до cs-2)
        bottom_strip = gray[cs-4:cs-2, margin:cs-margin]
        # Светлая левая грань
        left_strip = gray[margin:cs-margin, 0:2]
        # Тёмная правая грань
        right_strip = gray[margin:cs-margin, cs-4:cs-2]

        top_mean = np.mean(top_strip)
        bottom_mean = np.mean(bottom_strip)
        left_mean = np.mean(left_strip)
        right_mean = np.mean(right_strip)

        # 3D-эффект: верх светлее низа, лево светлее права
        has_vertical_3d = top_mean > bottom_mean + 5
        has_horizontal_3d = left_mean > right_mean + 5

        return has_vertical_3d and has_horizontal_3d

    def _is_flag(self, cell):
        """
        Определяет флаг по наличию красного треугольника и чёрного шеста.
        
        Не полагается только на цвет, т.к. цифра 3 тоже красная.
        Флаг имеет: красный в верхней части + чёрный вертикальный шест.
        """
        cs = self.cell_size
        hsv = cv2.cvtColor(cell, cv2.COLOR_BGR2HSV)

        # Красный в HSV (два диапазона)
        mask1 = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
        mask2 = cv2.inRange(hsv, np.array([160, 100, 100]), np.array([180, 255, 255]))
        red_mask = mask1 | mask2

        # Также ищем чёрные пиксели (шест флага)
        gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
        black_mask = (gray < 80).astype(np.uint8) * 255

        # Проверяем красный в верхней 2/3 клетки
        upper_23 = red_mask[:cs*2//3, :]
        red_upper = np.sum(upper_23 > 0)

        # Должно быть хотя бы немного красного в верхней части
        if red_upper < 15:
            return False

        # Проверяем наличие чёрного шеста
        # Шест — вертикальная линия чёрных пикселей
        center_col = cs // 2
        col_range = max(2, cs // 8)
        center_strip = black_mask[:, center_col - col_range:center_col + col_range]
        black_in_center = np.sum(center_strip > 0)

        # Шест должен иметь хотя бы несколько чёрных пикселей
        if black_in_center < 15:
            return False

        # Ключевое отличие: флаг имеет ЧЁРНЫЙ ШЕСТ, цифра 3 — нет
        # Цифра 3: только красный текст, без чёрных вертикальных линий
        # Флаг: красный треугольник + чёрный шест
        
        # Проверяем что чёрные пиксели образуют вертикальную линию
        # (а не просто шум)
        black_rows = np.where(np.any(center_strip > 0, axis=1))[0]
        if len(black_rows) < 5:  # Шест должен быть хотя бы 5 пикселей в высоту
            return False

        # Проверяем непрерывность шеста
        if len(black_rows) > 0:
            # Шест должен быть относительно непрерывным
            gaps = np.diff(black_rows)
            max_gap = np.max(gaps) if len(gaps) > 0 else 0
            if max_gap > 5:  # Слишком большие разрывы — не шест
                return False

        return True

    def _is_mine(self, cell):
        """Определяет мину по чёрному кругу или красному фону."""
        cs = self.cell_size
        gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
        
        # Центр клетки
        margin = cs // 4
        center = gray[margin:cs-margin, margin:cs-margin]
        center_mean = np.mean(center)

        # Красный фон (взрыв)
        hsv = cv2.cvtColor(cell, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
        mask2 = cv2.inRange(hsv, np.array([160, 100, 100]), np.array([180, 255, 255]))
        red_mask = mask1 | mask2
        red_ratio = np.sum(red_mask > 0) / (cs * cs)

        # Мина: очень тёмный центр ИЛИ красный фон
        return center_mean < 80 or red_ratio > 0.15

    def _recognize_number_template(self, cell):
        """Распознаёт цифру методом template matching."""
        best_match = None
        best_score = -1

        for number, template in self.templates.items():
            # Убеждаемся что размеры совпадают
            if template.shape != cell.shape:
                t = cv2.resize(template, (cell.shape[1], cell.shape[0]))
            else:
                t = template

            result = cv2.matchTemplate(cell, t, cv2.TM_CCOEFF_NORMED)
            score = result[0][0] if result.size > 0 else -1

            if score > best_score:
                best_score = score
                best_match = number

        # Порог уверенности
        if best_score > 0.65:
            return best_match
        return None

    def _recognize_number_color(self, cell):
        """Распознаёт цифру по цвету (fallback)."""
        cs = self.cell_size
        center = cell[cs//4:3*cs//4, cs//4:3*cs//4]
        center_hsv = cv2.cvtColor(center, cv2.COLOR_BGR2HSV)

        # Ищем не-серые пиксели (цифра)
        gray_mask = cv2.inRange(center_hsv, np.array([0, 0, 170]), np.array([180, 30, 240]))
        non_gray = cv2.bitwise_not(gray_mask)
        total_non_gray = np.sum(non_gray > 0)

        if total_non_gray < cs * cs * 0.01:
            return None

        best_number = None
        best_score = 0

        for number, bgr_color in self.NUMBER_COLORS_BGR.items():
            lower = np.array([max(0, c - 60) for c in bgr_color], dtype=np.uint8)
            upper = np.array([min(255, c + 60) for c in bgr_color], dtype=np.uint8)
            mask = cv2.inRange(center, lower, upper)
            mask = cv2.bitwise_and(mask, non_gray)
            score = np.sum(mask > 0)

            if score > best_score:
                best_score = score
                best_number = number

        threshold = center.shape[0] * center.shape[1] * 0.02
        if best_score > threshold:
            return best_number

        return None

    def recognize(self, cell):
        """
        Распознаёт одну клетку.
        
        Возвращает:
        - '?' — закрытая
        - 'F' — флаг
        - '*' — мина
        - 0-8 — открытая с числом
        """
        if cell.size == 0:
            return '?'

        cs = self.cell_size
        if cell.shape[0] != cs or cell.shape[1] != cs:
            cell = cv2.resize(cell, (cs, cs))

        # 1. Флаг? (красный треугольник на закрытой клетке)
        # Проверяем ПЕРВЫМ, потому что флаг ломает паттерн 3D-границы
        if self._is_flag(cell):
            return 'F'

        # 2. Закрытая клетка? (с 3D-границей)
        if self._is_closed(cell):
            return '?'

        # 3. Мина? (взорвавшаяся)
        if self._is_mine(cell):
            return '*'

        # 4. Открытая клетка — пытаемся распознать цифру
        number = self._recognize_number_template(cell)
        if number is not None:
            return number

        # Fallback: color-based
        number = self._recognize_number_color(cell)
        if number is not None:
            return number

        # 5. Нет цифры → пустая открытая клетка (0)
        gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
        margin = cs // 4
        center = gray[margin:cs-margin, margin:cs-margin]
        if np.mean(center) > 180:
            return 0

        # 6. Неизвестно
        return '?'

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
        """Загружает пользовательские эталонные изображения цифр."""
        loaded = 0
        for i in range(1, 9):
            path = os.path.join(template_dir, f"{i}.png")
            if os.path.exists(path):
                tmpl = cv2.imread(path)
                if tmpl is not None:
                    if tmpl.shape[:2] != (self.cell_size, self.cell_size):
                        tmpl = cv2.resize(tmpl, (self.cell_size, self.cell_size))
                    self.templates[i] = tmpl
                    loaded += 1
        if loaded > 0:
            print(f"  📷 Loaded {loaded} custom templates from {template_dir}")

    def save_debug(self, image, output_path):
        """Сохраняет изображение с подписями распознанных клеток."""
        if image is None:
            return

        cells = self.split_cells(image)
        debug = image.copy()

        for y, row in enumerate(cells):
            for x, cell in enumerate(row):
                val = self.recognize(cell)
                px = x * self.cell_size
                py = y * self.cell_size

                label = str(val)
                color = (0, 0, 255) if val in ('?', '*', 'F') else (0, 255, 0)

                cv2.putText(debug, label, (px + 2, py + self.cell_size - 4),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

        cv2.imwrite(output_path, debug)
        print(f"  💾 Debug image saved to {output_path}")
