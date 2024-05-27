class WonderTemplate:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def __repr__(self):
        return f"<WonderTemplate {self.name})>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WonderTemplate):
            return False
        return self.name == other.name
    
    def __hash__(self) -> int:
        return hash(self.name)

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "age": self.age,
        }
