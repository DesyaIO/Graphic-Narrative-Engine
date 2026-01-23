from abc import ABC, abstractmethod
from typing import List, Union


class GameBlock(ABC):
    """Абстрактный базовый класс для ВСЕХ блоков игры"""

    @property
    @abstractmethod
    def id(self) -> str:
        """ID блока"""
        pass

    @property
    @abstractmethod
    def next_block(self) -> Union[str, List[str], None]:
        """ID следующего блока (может быть строкой, списком или None)"""
        pass

    @abstractmethod
    def display(self, engine: 'GameEngine'):
        """Отобразить блок в контексте игрового движка"""
        pass

    @abstractmethod
    def process(self, engine: 'GameEngine'):
        """Обработать блок (основная логика)"""
        pass