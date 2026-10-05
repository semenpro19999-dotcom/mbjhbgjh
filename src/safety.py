class Safety:
    def __init__(self):
        self.running = True

    def stop(self, reason='manual'):
        self.running = False
        print(f'🛑 Bot stopped: {reason}')

    def ok(self):
        return self.running
