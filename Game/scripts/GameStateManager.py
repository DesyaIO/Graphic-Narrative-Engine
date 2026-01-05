# Game/scripts/GameStateManager.py
from typing import Dict, Optional
import json

from Game import config
from Game.scripts.TextBlock import TextBlock
from Game.scripts.ChoiceBlock import ChoiceBlock
from Game.scripts.Choice import Choice
from Game.scripts.GameBlock import GameBlock
from Game.utils.ConsoleUtils import print_slow


class GameStateManager:
    def __init__(self):
        self.text_blocks: Dict[str, TextBlock] = {}
        self.choice_blocks: Dict[str, ChoiceBlock] = {}
        self.choices: Dict[str, Choice] = {}

    def load_text_blocks(self, filepath: str):
        """Загружает текстовые блоки из JSON файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for block_id, block_data in data.items():
                self.text_blocks[block_id] = TextBlock.from_dict(block_id, block_data)

            print_slow(f"✅ Загружено текстовых блоков: {len(self.text_blocks)}", config.TEXT_SPEED_FAST)
        except Exception as e:
            print_slow(f"❌ Ошибка загрузки текстовых блоков: {e}", config.TEXT_SPEED_FAST)

    def load_choice_blocks(self, filepath: str):
        """Загружает блоки с выбором из JSON файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for block_id, block_data in data.get("choice_blocks", {}).items():
                self.choice_blocks[block_id] = ChoiceBlock.from_dict(block_id, block_data)

            print_slow(f"✅ Загружено блоков с выбором: {len(self.choice_blocks)}", config.TEXT_SPEED_FAST)
        except Exception as e:
            print_slow(f"❌ Ошибка загрузки блоков с выбором: {e}", config.TEXT_SPEED_FAST)

    def load_choices(self, filepath: str):
        """Загружает варианты выбора из JSON файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for choice_id, choice_data in data.get("choices", {}).items():
                self.choices[choice_id] = Choice.from_dict(choice_id, choice_data)

            print_slow(f"✅ Загружено вариантов выбора: {len(self.choices)}", config.TEXT_SPEED_FAST)
        except Exception as e:
            print_slow(f"❌ Ошибка загрузки вариантов выбора: {e}", config.TEXT_SPEED_FAST)

    def get_block(self, block_id: str) -> Optional[GameBlock]:
        """Возвращает блок по ID (полиморфно!)"""
        if block_id in self.text_blocks:
            return self.text_blocks[block_id]
        elif block_id in self.choice_blocks:
            return self.choice_blocks[block_id]
        return None

    def get_choice(self, choice_id: str) -> Optional[Choice]:
        """Возвращает вариант выбора по ID"""
        return self.choices.get(choice_id)

    def evaluate_condition(self, condition: str, player_flags: Dict[str, bool]) -> bool:
        """Оценивает условие на основе флагов игрока"""
        if condition is None:
            return True

        try:
            # Простая замена флагов
            for flag_name, flag_value in player_flags.items():
                condition = condition.replace(f"{flag_name} == True", str(flag_value))
                condition = condition.replace(f"{flag_name} == False", str(not flag_value))

            # Заменяем операторы
            condition = condition.replace("==", "==")
            condition = condition.replace("!=", "!=")

            return eval(condition)
        except:
            return False