import os
import sys
import time

# Блок следующих 3х функций невероятно поможет по ходу игры красиво выводить / форматировать / драмматизировать и оживлять игру. Они будут считать console_utils :3

def print_slow(text: str, delay: float = 0.07):
    """Печатает текст побуквенно с задержкой"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def clear_console():
    """Очищает консоль"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_game_name():
    """Выводит название игры"""
    game_name = """
    ╔══════════════════════════════════════════╗
    ║   Инженерная графика: MAI                ║
    ║   Ingenernaya grafikcs: MAI              ║
    ╚══════════════════════════════════════════╝
    """
    print(game_name)
