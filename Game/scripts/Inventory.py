from typing import List

from Game.scripts.Item import Item


class Inventory:
    def __init__(self, items: List[Item] = None):
        self._items = items if items is not None else []

    def add_item(self, item: Item):
        """Добавляет предмет в инвентарь"""
        self._items.append(item)

    def remove_item(self, item_name: str) -> bool:
        """Удаляет предмет из инвентаря по имени"""
        for i, item in enumerate(self._items):
            if item.name == item_name:
                self._items.pop(i)
                return True
        return False

    def has_item(self, item_name: str) -> bool:
        """Проверяет, есть ли предмет в инвентаре"""
        return any(item.name == item_name for item in self._items)

    def get_items(self) -> List[Item]:
        """Возвращает список предметов"""
        return self._items.copy()

    def to_dict(self):
        return {
            'items': [item.to_dict() for item in self._items]
        }

    @classmethod
    def from_dict(cls, data):
        if data is None:
            return cls()

        items_data = data.get("items", [])
        items = []
        for item_data in items_data:
            item = Item.from_dict(item_data)
            if item:
                items.append(item)

        return cls(items=items)