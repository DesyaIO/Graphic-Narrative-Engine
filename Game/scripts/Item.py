class Item:
    def __init__(self, name: str, description: str = "", power: int = 0):
        self.name = name
        self.description = description
        self.power = power

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'power': self.power
        }

    @classmethod
    def from_dict(cls, data):
        if data is None:
            return None
        return cls(
            name=data.get('name', ''),
            description=data.get('description', ''),
            power=data.get('power', 0)
        )