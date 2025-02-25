class DetailedNumber:
    """A number that can be displayed with a detailed breakdown."""

    def __init__(self, data: dict[str, float] | None = None, min_zero: bool = False):
        self._data: dict[str, float] = data if data is not None else {}
        self._min_zero = min_zero

    def items(self):
        return self._data.items()

    @property
    def value(self) -> float:
        return self._calculate_value()
    
    def add(self, key: str, value: float):
        if value == 0: return
        if key in self._data:
            self._data[key] += value
        else:
            self._data[key] = value
    
    def _calculate_value(self):
        total: float = sum(self._data.values())
        if self._min_zero:
            total = max(total, 0)
        return total

    def to_json(self) -> dict:
        result = {
            "value": self.value,
            "data": self._data,
        }
        if self._min_zero:
            result["min_zero"] = True
        return result
        
    @staticmethod
    def from_json(json: dict):
        result = DetailedNumber(json["data"], min_zero=json.get('min_zero', False))
        assert round(result.value, 4) == round(json["value"], 4), f"DetailedNumber.from_json: value mismatch: {result.value} != {json['value']}. Data: {json['data']}; result: {result._data}"
        return result
    
    def __repr__(self)  -> str:
        return str(self.to_json())
    
class DetailedNumberWithMultiplier:
    def __init__(self) -> None:
        self._pre_mult = DetailedNumber()
        self._multiplier: float | None = None
        self._post_mult = DetailedNumber()

    def add_pre_multiplier(self, key: str, value: float):
        assert self._multiplier is None, f"can't add more pre-multiplier after multiplier is set. Probably it would be fine to remove this requirement of the API, but it seemed more logical to try to enforce it until we have a reason not to."
        self._pre_mult.add(key, value)

    def add_post_multiplier(self, key: str, value: float):
        assert self._multiplier is not None, "Can't add post-multiplier until multiplier is set. Probably it would be fine to remove this requirement of the API, but it seemed more logical to try to enforce it until we have a reason not to."
        self._post_mult.add(key, value)

    def add(self, key: str, value: float):
        if self._multiplier is None:
            self.add_pre_multiplier(key, value)
        else:
            self.add_post_multiplier(key, value)

    def set_multiplier(self, value):
        self._multiplier = value

    @property
    def value(self):
        if self._multiplier is None:
            return self._pre_mult.value
        else:
            return self._multiplier * self._pre_mult.value + self._post_mult.value
        
    def to_json(self):
        return {
            "pre_mult": self._pre_mult.to_json(),
            "multiplier": self._multiplier,
            "post_mult": self._post_mult.to_json(),
            "value": self.value,
        }
    
    @staticmethod
    def from_json(json) -> 'DetailedNumberWithMultiplier':
        dn = DetailedNumberWithMultiplier()
        dn._pre_mult = DetailedNumber.from_json(json["pre_mult"])
        dn._post_mult = DetailedNumber.from_json(json["post_mult"])
        dn._multiplier = json["multiplier"]
        return dn
