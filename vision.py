import pyautogui
import cv2
import numpy as np

from config import BOARD_AREA


class Vision:
    """Захват экрана и вырезание области игры."""

    def __init__(self, board_area=None):
        self.board_area = board_area or BOARD_AREA

    def set_board_area(self, area):
        self.board_area = area

    def screenshot(self):
        """Делает скриншот всего экрана."""
        image = pyautogui.screenshot()
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    def crop(self, image, area):
        """Вырезает область из изображения."""
        if area is None:
            return None
        x1, y1, x2, y2 = area
        return image[y1:y2, x1:x2]

    def capture_board(self):
        """Захватывает только область Сапёра."""
        if self.board_area is None:
            return None
        screen = self.screenshot()
        return self.crop(screen, self.board_area)

    def detect_explosion(self, image):
        """
        Обнаруживает взрыв по красному цвету на поле.
        Возвращает True если обнаружен взрыв.
        """
        if image is None:
            return False

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Красный цвет в HSV (два диапазона, т.к. красный переходит через 0)
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = mask1 | mask2

        total_pixels = image.shape[0] * image.shape[1]
        red_pixels = np.sum(red_mask) / 255

        # Если >5% красных пикселей — вероятно взрыв
        return red_pixels / total_pixels > 0.05
