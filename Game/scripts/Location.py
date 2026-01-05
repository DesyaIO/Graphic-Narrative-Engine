class Location:
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data):
        if data is None:
            return cls(name="Неизвестно")
        return cls(
            name=data.get('name', 'Неизвестно'),
            description=data.get('description', '')
        )

    def __str__(self):
        return self.name