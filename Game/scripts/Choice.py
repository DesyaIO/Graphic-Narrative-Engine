from dataclasses import dataclass
from typing import Optional, List, Union

from Game.scripts.Item import Item


@dataclass
class Choice:
    id: str
    name: str
    description: str
    time_cost: int
    condition: Optional[str]
    given_flag: str
    given_item: Optional[Item] = None
    next_block: Union[str, List[str], None] = None
    end_condition: Optional[str] = None
    end: Optional[int] = None
    end_description: Optional[str] = None
    circle: bool = False

    @classmethod
    def from_dict(cls, choice_id: str, data: dict):
        return cls(
            id=choice_id,
            name=data.get("name", ""),
            description=data.get("description", ""),
            time_cost=data.get("time_cost", 0),
            condition=data.get("condition"),
            given_flag=data.get("given_flag", ""),
            given_item=data.get("given_item", None),
            next_block=data.get("next_block"),
            end_condition=data.get("end_condition"),
            end=data.get("end"),
            end_description=data.get("end_description"),
            circle=data.get("circle", False)
        )

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "time_cost": self.time_cost,
            "condition": self.condition,
            "given_flag": self.given_flag,
            "next_block": self.next_block,
            "end_condition": self.end_condition,
            "end": self.end,
            "end_description": self.end_description,
            "circle": self.circle
        }