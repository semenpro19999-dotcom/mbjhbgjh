import time

try:
    import keyboard
except ImportError:
    keyboard = None


class Hotkeys:
    def __init__(self, safety):
        self.safety = safety

    def start(self):
        if keyboard is None:
            print("Hotkeys unavailable in this environment")
            return

        keyboard.add_hotkey("esc", self.safety.stop)
        print("ESC = emergency stop")

        while self.safety.is_running():
            time.sleep(0.1)
