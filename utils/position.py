"""
Position and Coordinate Utilities
"""


def algebraic_to_index(notation: str) -> tuple:
    """Convert algebraic notation (e.g., 'e4') to array indices"""
    if len(notation) != 2:
        return (-1, -1)

    files = 'abcdefgh'
    ranks = '87654321'

    try:
        col = files.index(notation[0].lower())
        row = ranks.index(notation[1])
        return (row, col)
    except (ValueError, IndexError):
        return (-1, -1)


def index_to_algebraic(row: int, col: int) -> str:
    """Convert array indices to algebraic notation"""
    if not (0 <= row < 8 and 0 <= col < 8):
        return '??'

    files = 'abcdefgh'
    ranks = '87654321'
    return f"{files[col]}{ranks[row]}"


def index_to_pixel(row: int, col: int, board_offset_x, board_offset_y, square_size) -> tuple:
    """Convert board indices to pixel coordinates"""
    x = board_offset_x + col * square_size
    y = board_offset_y + row * square_size
    return (x, y)


def pixel_to_index(x: int, y: int, board_offset_x, board_offset_y, square_size) -> tuple:
    """Convert pixel coordinates to board indices"""
    col = (x - board_offset_x) // square_size
    row = (y - board_offset_y) // square_size

    if 0 <= row < 8 and 0 <= col < 8:
        return (row, col)
    return (-1, -1)


def get_distance(pos1: tuple, pos2: tuple) -> int:
    """Calculate Chebyshev distance between two positions"""
    return max(abs(pos1[0] - pos2[0]), abs(pos1[1] - pos2[1]))


def get_manhattan_distance(pos1: tuple, pos2: tuple) -> int:
    """Calculate Manhattan distance"""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])