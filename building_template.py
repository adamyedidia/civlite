from typing import Union


class BuildingTemplate:
    def __init__(self, name: str, type: str, cost: str, abilities: list[list[Union[str, list]]]):
        self.name = name
        self.type = type
        self.cost = cost
        self.abilities: list[Ability] = ABILITIES[abilities[0]](*abilities[1])  # type: ignore

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "cost": self.cost,
            "abilities": [ability.to_json() for ability in self.abilities],
        }
    
    @staticmethod
    def from_json(json: dict) -> "BuildingTemplate":
        return BuildingTemplate(
            name=json["name"],
            type=json["type"],
            cost=json["cost"],
            abilities=[[ability["name"], ability["numbers"]] for ability in json["abilities"]],
        )
