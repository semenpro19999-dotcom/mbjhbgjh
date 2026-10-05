import sys
from ai_controller import AIController


def main():
    print("=" * 40)
    print("🤖 Minesweeper AI v1.0")
    print("=" * 40)
    print()
    print("Controls:")
    print("  ESC — emergency stop")
    print()

    bot = AIController()

    try:
        bot.start()
    except KeyboardInterrupt:
        print("\n⛔ Interrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
