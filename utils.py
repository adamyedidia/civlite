import secrets


def coords_tuple(coords_str: str) -> tuple[int, int, int]:
    coords = coords_str.split(",")
    return (int(coords[0]), int(coords[1]), int(coords[2]))


def coords_str(coords: tuple[int, int, int]) -> str:
    return f"{coords[0]},{coords[1]},{coords[2]}"


def generate_unique_id() -> str:
    return secrets.token_hex(10)


def get_all_coords_up_to_n(n) -> list[tuple[int, int, int]]:
    all_coords = []
    for q in range(-n, n + 1):
        for r in range(max(-n, -q - n), min(n, -q + n) + 1):
            all_coords.append((q, r, -q - r))

    return all_coords


def swap_two_elements_of_list(l: list, i: int, j: int) -> list:
    l[i], l[j] = l[j], l[i]
    return l