from game.scripts.GameEngine import GameEngine

def main():
    """Точка входа в программу"""
    try:
        # Создаем и запускаем игру
        game = GameEngine()
        game.start_game()

    except KeyboardInterrupt:
        print("\n\n🛑 Игра прервана пользователем")


if __name__ == "__main__":
    main()