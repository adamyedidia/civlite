from typing import Optional
from unit import Unit
from yields import Yields
from city import City


class Hex:
    def __init__(self, q: int, r: int, s: int, yields: Yields) -> None:
        assert not (q + r + s)
        self.q = q
        self.r = r
        self.s = s
        self.yields = yields
        self.units: list[Unit] = []
        self.city: Optional[City] = None

