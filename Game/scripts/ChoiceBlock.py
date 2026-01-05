# Game/scripts/ChoiceBlock.py
from typing import List, Optional, Union
from Game.scripts.GameBlock import GameBlock

from Game import config
from Game.scripts.Choice import Choice
from Game.utils.ConsoleUtils import print_slow, clear_console


class ChoiceBlock(GameBlock):
    def __init__(self,
                 block_id: str,
                 name: str,
                 available_choices: List[str],
                 previous_block: Union[str, List[str], None] = None):
        self._id = block_id
        self._name = name
        self._available_choices = available_choices
        self._previous_block = previous_block

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def available_choices(self) -> List[str]:
        return self._available_choices

    @property
    def previous_block(self) -> Union[str, List[str], None]:
        return self._previous_block

    @property
    def next_block(self) -> Union[str, List[str], None]:
        # У ChoiceBlock нет фиксированного следующего блока
        # Следующий блок определяется выбором игрока
        return None

    def display(self, engine: 'GameEngine'):
        """Отобразить блок с выбором"""
        clear_console()
        engine.display_game_header()

        title = engine.format_text_with_variables(self._name)
        print_slow("=" * 60, config.TEXT_SPEED_FAST)
        print_slow(title, config.TEXT_SPEED_NORMAL)
        print_slow("=" * 60, config.TEXT_SPEED_FAST)
        print_slow("", config.TEXT_SPEED_FAST)

    def process(self, engine: 'GameEngine'):
        """Обработать блок с выбором"""
        self.display(engine)

        # Доступные выборы
        available_choices = []
        for choice_id in self._available_choices:
            choice = engine.state_manager.get_choice(choice_id)
            if choice and engine.is_choice_available(choice):
                available_choices.append(choice)

        if not available_choices:
            print_slow("😔 Нет доступных вариантов...", config.TEXT_SPEED_FAST)
            input("\n↵ Нажмите Enter чтобы продолжить...")
            return

        # Отображаем варианты
        print_slow("📋 Доступные варианты:", config.TEXT_SPEED_NORMAL)
        print_slow("-" * 40, config.TEXT_SPEED_FAST)

        for i, choice in enumerate(available_choices, 1):
            time_cost = choice.time_cost
            if isinstance(time_cost, int):
                time_info = f" [⏰ {time_cost} мин]"
            elif isinstance(time_cost, str):
                time_info = " [⏰ ??? мин]"
            else:
                time_info = " [⚡ мгновенно]"

            print_slow(f"{i}. {choice.name}{time_info}", config.TEXT_SPEED_SLOW)

        print_slow("-" * 40, config.TEXT_SPEED_FAST)
        print_slow("", config.TEXT_SPEED_FAST)

        # Получаем выбор игрока
        engine.get_player_choice(available_choices)

    @classmethod
    def from_dict(cls, block_id: str, data: dict):
        return cls(
            block_id=block_id,
            name=data.get("name", ""),
            available_choices=data.get("available_choices", []),
            previous_block=data.get("previous_block")
        )

    def to_dict(self):
        return {
            "name": self._name,
            "available_choices": self._available_choices,
            "previous_block": self._previous_block
        }