import pyautogui


class Clicker:
    def left_click(self, x, y):
        pyautogui.click(x, y)

    def right_click(self, x, y):
        pyautogui.rightClick(x, y)
