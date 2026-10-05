class SafetySystem:
    def __init__(self):
        self.running = True

    def mine_detected(self, position=None):
        print("💣 MINE DETECTED!")
        if position:
            print("Position:", position)
        self.running = False
        print("🛑 Bot stopped for safety")

    def stop(self):
        self.running = False
        print("🛑 Emergency stop")

    def is_running(self):
        return self.running
