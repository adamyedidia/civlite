import abc

from typing import TYPE_CHECKING, Literal

from detailed_number import DetailedNumber, DetailedNumberWithMultiplier


if TYPE_CHECKING:
    from terrain_template import TerrainTemplate
    from city import City
    from building_template import BuildingType


class Yields:
    def __init__(self, food: int | float = 0, metal: int | float = 0, wood: int | float = 0, science: int | float = 0, unhappiness: int | float = 0, city_power: int | float = 0) -> None:
        self.food = food
        self.metal = metal
        self.wood = wood
        self.science = science
        self.unhappiness = unhappiness
        self.city_power = city_power

    def increase(self, yield_type: str, amount: int) -> None:
        setattr(self, yield_type, self[yield_type] + amount)

    def __eq__(self, other: "Yields") -> bool:
        return self.to_json() == other.to_json()

    def __mul__(self, multiplier: int | float) -> "Yields":
        return Yields(
            food=self.food * multiplier,
            metal=self.metal * multiplier,
            wood=self.wood * multiplier,
            science=self.science * multiplier,
            unhappiness=self.unhappiness * multiplier,
            city_power=self.city_power * multiplier,
        )
    
    def __add__(self, other: "Yields | dict") -> "Yields":
        if isinstance(other, dict):
            other = Yields(**other)
        return Yields(
            food=self.food + other.food,
            metal=self.metal + other.metal,
            wood=self.wood + other.wood,
            science=self.science + other.science,
            unhappiness=self.unhappiness + other.unhappiness,
            city_power=self.city_power + other.city_power,
        )

    def __getitem__(self, item: str) -> int | float:
        return getattr(self, item)

    def total(self) -> int | float:
        return self.food + self.metal + self.wood + self.science + self.unhappiness + self.city_power

    def copy(self) -> "Yields":
        return Yields(
            food=self.food,
            metal=self.metal,
            wood=self.wood,
            science=self.science,
            unhappiness=self.unhappiness,
            city_power=self.city_power,
        )

    def to_json(self) -> dict:
        return {
            "food": self.food,
            "metal": self.metal,
            "wood": self.wood,
            "science": self.science,            
            "unhappiness": self.unhappiness,
            "city_power": self.city_power,
        }
    
    @staticmethod
    def from_json(json: dict) -> "Yields":
        return Yields(
            food=json["food"],
            metal=json["metal"],
            wood=json["wood"],
            science=json["science"],
            unhappiness=json["unhappiness"],
            city_power=json["city_power"],
        )
    
    def pretty_print(self):
        return ", ".join([f"+{amount} {yield_type}" for yield_type, amount in self.to_json().items() if amount > 0])
    
    def __repr__(self) -> str:
        return f"<Yields {self.to_json()}>"

class DetailedYields:
    SUPPORTED_KEYS = ("food", "metal", "wood", "science")
    def __init__(self) -> None:
        self.food = DetailedNumberWithMultiplier()
        self.metal = DetailedNumberWithMultiplier()
        self.wood = DetailedNumberWithMultiplier()
        self.science = DetailedNumberWithMultiplier()
        self.unhappiness = 0  # Almost no sources of this, but we made Conscription Post so we have to support it.

    def add_yields(self, name: str, yields: Yields | dict) -> None:
        if isinstance(yields, Yields):
            assert yields.city_power == 0
            self.unhappiness += yields.unhappiness
        keys = tuple(yields.keys()) if isinstance(yields, dict) else DetailedYields.SUPPORTED_KEYS
        if isinstance(yields, dict):
            assert all(k in DetailedYields.SUPPORTED_KEYS for k in keys)
        for key in keys:
            self[key].add(name, yields[key])

    def __getitem__(self, item: Literal["food", "metal", "wood", "science"]) -> DetailedNumber:
        return getattr(self, item)
        
    def set_multiplier(self, multiplier: int | float) -> None:
        self.food.set_multiplier(multiplier)
        self.wood.set_multiplier(multiplier)
        self.metal.set_multiplier(multiplier)
        self.science.set_multiplier(multiplier)
    
    @property
    def value(self) -> Yields:
        return Yields(
            food=self.food.value,
            metal=self.metal.value,
            wood=self.wood.value,
            science=self.science.value,
            unhappiness=self.unhappiness,
        )

    def to_json(self) -> dict:
        return {
            "food": self.food.to_json(),
            "wood": self.wood.to_json(),
            "metal": self.metal.to_json(),
            "science": self.science.to_json(),
            "unhappiness": self.unhappiness,
        }
    
    @staticmethod
    def from_json(json: dict) -> "DetailedYields":
        dy = DetailedYields()
        dy.food = DetailedNumberWithMultiplier.from_json(json["food"])
        dy.wood = DetailedNumberWithMultiplier.from_json(json["wood"])
        dy.metal = DetailedNumberWithMultiplier.from_json(json["metal"])
        dy.science = DetailedNumberWithMultiplier.from_json(json["science"])
        dy.unhappiness = json["unhappiness"]
        return dy


class YieldsCalculation(abc.ABC):
    @abc.abstractmethod
    def calculate(self, city: 'City') -> Yields:
        raise NotImplementedError
    
    @abc.abstractproperty
    def description(self) -> str:
        raise NotImplementedError
    
class ConstantYields(YieldsCalculation):
    def __init__(self, yields: Yields) -> None:
        self.yields = yields

    def calculate(self, city: 'City') -> Yields:
        return self.yields
    
    @property
    def description(self) -> str:
        return self.yields.pretty_print()

class YieldsPerUniqueTerrainType(YieldsCalculation):
    def __init__(self, yields: Yields) -> None:
        self.yields = yields

    def calculate(self, city: 'City') -> Yields:
        return self.yields * len(city.terrains_dict)
    
    @property
    def description(self) -> str:
        return f"{self.yields.pretty_print()} per unique terrain type."
    
class YieldsPerTerrainType(YieldsCalculation):
    def __init__(self, terrain_type: 'TerrainTemplate | set[TerrainTemplate]', yields: Yields) -> None:
        self.terrain_type: set['TerrainTemplate'] = terrain_type if isinstance(terrain_type, set) else {terrain_type}
        self.yields = yields

    def calculate(self, city: 'City') -> Yields:
        return self.yields * sum(a for t, a in city.terrains_dict.items() if t in self.terrain_type)
    
    @property
    def description(self) -> str:
        return f"{self.yields.pretty_print()} per {', '.join([t.name for t in self.terrain_type])}"
    
class YieldsPerPopulation(YieldsCalculation):
    def __init__(self, yields: Yields) -> None:
        self.yields = yields

    def calculate(self, city: 'City') -> Yields:
        return self.yields * city.population
    
    @property
    def description(self) -> str:
        return f"{self.yields.pretty_print()} per population"
    
class YieldsPerBuildingType(YieldsCalculation):
    def __init__(self, building_type: 'BuildingType', yields: Yields) -> None:
        self.building_type = building_type
        self.yields = yields

    def calculate(self, city: 'City') -> Yields:
        return self.yields * len(city.buildings_of_type(self.building_type))
    
    @property
    def description(self) -> str:
        return f"{self.yields.pretty_print()} per {self.building_type.value} building"