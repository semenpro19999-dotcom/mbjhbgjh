class SafetySystem:
    """Система безопасности бота."""

    def __init__(self):
        self.running = True
        self.stop_reason = None

    def mine_detected(self, position=None):
        """Остановка при обнаружении взрыва."""
        print("💣 MINE DETECTED!")
        if position:
            print("  Position:", position)
        self.running = False
        self.stop_reason = "mine"
        print("🛑 Bot stopped for safety")

    def stop(self, reason="manual"):
        """Ручная или аварийная остановка."""
        self.running = False
        self.stop_reason = reason
        print(f"🛑 Emergency stop ({reason})")

    def is_running(self):
        """Проверяет, работает ли бот."""
        return self.running
