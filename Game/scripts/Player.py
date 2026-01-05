from dataclasses import dataclass, field
from typing import List, Dict
from Game.scripts.Inventory import Inventory



@dataclass
class Player:
    _name: str
    _time_left: int
    _inventory: Inventory
    _flags: Dict[str, bool] = field(default_factory=lambda: {
        "eat_1": False,
        "eat_2": False,
        "eat_3": False,
        "is_washing": False,
        "has_photo_work": False,
        "is_sleep_day": False,
        "has_mega_file": False,
        "tram_thunderstorm": False,
        "big_eared_passenger" : False,
        "bad_album": False,
        "norm_album": False,
        "mega_album": False,
        "mega_brain": False,
    })
    _choices_history: List[str] = field(default_factory=list)  # История ID выбранных выборов
    _current_block_id: str = "text_000"  # Текущий блок игры

    @property
    def name(self):
        return self._name

    @property
    def flags(self):
        return self._flags

    @property
    def choices_history(self):
        return self._choices_history

    @property
    def current_block_id(self):
        return self._current_block_id

    @current_block_id.setter
    def current_block_id(self, value: str):
        self._current_block_id = value

    def add_choice_to_history(self, choice_id: str):
        self._choices_history.append(choice_id)

    def set_flag(self, flag_name: str, value: bool = True):
        if flag_name:  # Проверяем, что флаг не пустая строка
            self._flags[flag_name] = value

    def update_time(self, time_cost: int):
        """Обновление времени игрока"""
        if isinstance(time_cost, int):
            self._time_left -= time_cost
            if self._time_left < 0:
                self._time_left = 0

    def to_dict(self):
        return {
            'name': self._name,
            'time_left': self._time_left,
            'inventory': self._inventory.to_dict(),
            'flags': self._flags,
            'choices_history': self._choices_history,
            'current_block_id': self._current_block_id
        }

    @classmethod
    def from_dict(cls, data):
        if data is None:
            return None

        name = data.get("name")
        time_left = data.get("time_left", 840)
        inventory = Inventory.from_dict(data.get("inventory"))
        flags = data.get("flags", {})
        choices_history = data.get("choices_history", [])
        current_block_id = data.get("current_block_id", "text_000")

        player = cls(
            _name=name,
            _time_left=time_left,
            _inventory=inventory
        )
        
        player._flags = flags
        player._choices_history = choices_history
        player._current_block_id = current_block_id
        return player