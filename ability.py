from typing import Any


class Ability:
    def __init__(self, name: str, description: str, numbers: list):
        self.name = name
        self.description = description
        self.numbers = numbers
        
    def to_json(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "numbers": [str(n) for n in self.numbers],
        }