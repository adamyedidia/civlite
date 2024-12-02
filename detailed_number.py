class DetailedNumber:
    """A number that can be displayed with a detailed breakdown."""

    def __init__(self, data: dict[str, float] | None = None):
        self._data: dict[str, float] = data if data is not None else {}
        self._value: float = sum(self._data.values())
        self._assert_invariants()

    @property
    def value(self) -> float:
        self._assert_invariants()
        return self._value
    
    def add(self, key: str, value: float):
        if value == 0: return
        if key in self._data:
            self._data[key] += value
        else:
            self._data[key] = value
        self._value += value
        self._assert_invariants()
    
    def _assert_invariants(self):
        assert round(self._value, 4) == round(sum(self._data.values()), 4), f"DetailedNumber._assert_invariants: value mismatch: {round(self._value, 4)} != {round(sum(self._data.values()), 4)}. Data: {self._data}"

    def to_json(self) -> dict:
        self._assert_invariants()
        return {
            "value": self._value,
            "data": self._data,
        }
    
    @staticmethod
    def from_json(json: dict):
        result = DetailedNumber(json["data"])
        assert round(result.value, 4) == round(json["value"], 4), f"DetailedNumber.from_json: value mismatch: {result.value} != {json['value']}. Data: {json['data']}; result: {result._data}"
        result._assert_invariants()
        return result