import secrets


def coords_tuple(coords_str: str) -> tuple[int, int, int]:
    coords = coords_str.split(",")
    return (int(coords[0]), int(coords[1]), int(coords[2]))


def coords_str(coords: tuple[int, int, int]) -> str:
    return f"{coords[0]},{coords[1]},{coords[2]}"


def generate_unique_id() -> str:
    return secrets.token_hex(10)
