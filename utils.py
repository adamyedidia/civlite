import secrets
import hashlib
import random

def coords_tuple(coords_str: str) -> tuple[int, int, int]:
    coords = coords_str.split(",")
    return (int(coords[0]), int(coords[1]), int(coords[2]))


def coords_str(coords: tuple[int, int, int]) -> str:
    return f"{coords[0]},{coords[1]},{coords[2]}"


def generate_unique_id(prefix='') -> str:
    return prefix + ''.join(random.choices('0123456789abcdef', k=10))


def get_all_coords_up_to_n(n) -> list[tuple[int, int, int]]:
    all_coords = []
    for q in range(-n, n + 1):
        for r in range(max(-n, -q - n), min(n, -q + n) + 1):
            all_coords.append((q, r, -q - r))

    return all_coords


def swap_two_elements_of_list(l: list, i: int, j: int) -> list:
    l[i], l[j] = l[j], l[i]
    return l


def dream_key(game_id: str, player_num: int, turn_num: int) -> str:
    return f'dream_game_state:{game_id}:{player_num}:{turn_num}'

def staged_moves_key(game_id: str, player_num: int, turn_num: int) -> str:
    return f'staged_moves:{game_id}:{player_num}:{turn_num}'


def dream_key_from_civ_perspectives(game_id: str, player_num: int, turn_num: int) -> str:
    return f'dream_game_state_from_civ_perspectives:{game_id}:{player_num}:{turn_num}'

def moves_processing_key(game_id: str, turn_num: int) -> str:
    return f'moves_processing:{game_id}:{turn_num}'

def deterministic_hash(value: str) -> int:
    # Use SHA-256 hash function from hashlib and return an integer
    hash_object = hashlib.sha256(value.encode())
    # Convert the hash to a hexadecimal string, then to an integer
    return int(hash_object.hexdigest(), 16)