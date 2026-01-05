# Game/scripts/TextBlock.py
from typing import List, Optional, Union
from Game.scripts.GameBlock import GameBlock

from Game import config
from Game.utils.ConsoleUtils import print_slow, clear_console


class TextBlock(GameBlock):
    def __init__(self,
                 block_id: str,
                 body: str,
                 next_block: Union[str, List[str], None],
                 previous_block: Union[str, List[str], None] = None,
                 conditions: Optional[str] = None):
        self._id = block_id
        self._body = body
        self._next_block = next_block
        self._previous_block = previous_block
        self._conditions = conditions

    @property
    def id(self) -> str:
        return self._id

    @property
    def body(self) -> str:
        return self._body

    @property
    def next_block(self) -> Union[str, List[str], None]:
        return self._next_block

    @property
    def previous_block(self) -> Union[str, List[str], None]:
        return self._previous_block

    @property
    def conditions(self) -> Optional[str]:
        return self._conditions

    def display(self, engine: 'GameEngine'):
        """Отобразить текстовый блок"""
        text = self._body
        text = engine.format_text_with_variables(text)

        clear_console()
        hide_time = self._id in config.HIDE_TIME_BLOCKS
        engine.display_game_header(hide_time)

        print_slow("=" * 60, config.TEXT_SPEED_FAST)

        paragraphs = text.split('\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                print_slow(paragraph, config.TEXT_SPEED_NORMAL)
            else:
                print()

        print_slow("=" * 60, config.TEXT_SPEED_FAST)
        input("\n↵ Нажмите Enter чтобы продолжить...")

    def process(self, engine: 'GameEngine'):
        """Обработать текстовый блок"""
        # Проверяем условия
        if self._conditions and not engine.state_manager.evaluate_condition(
                self._conditions, engine.player.flags):
            print_slow("⏩ Пропускаем блок...", config.TEXT_SPEED_FAST)
            engine.go_to_next_block(self)
            return

        self.display(engine)
        engine.go_to_next_block(self)

    @classmethod
    def from_dict(cls, block_id: str, data: dict):
        return cls(
            block_id=block_id,
            body=data.get("body", ""),
            next_block=data.get("next_block"),
            previous_block=data.get("previous_block"),
            conditions=data.get("conditions")
        )

    def to_dict(self):
        return {
            "body": self._body,
            "next_block": self._next_block,
            "previous_block": self._previous_block,
            "conditions": self._conditions
        }