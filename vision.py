import pyautogui
import cv2
import numpy as np


class Vision:
    def screenshot(self):
        image = pyautogui.screenshot()
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    def crop(self, image, area):
        x1, y1, x2, y2 = area
        return image[y1:y2, x1:x2]
