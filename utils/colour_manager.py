"""
Color Management Utilities
"""

import config


def get_color(name: str) -> tuple:
    """Get color by name"""
    color_map = {
        'light_square': config.LIGHT_SQUARE,
        'dark_square': config.DARK_SQUARE,
        'highlight': config.HIGHLIGHT_COLOR,
        'legal_move': config.LEGAL_MOVE_COLOR,
        'background': config.BACKGROUND_COLOR,
        'text': config.TEXT_COLOR,
        'button': config.BUTTON_COLOR
    }
    return color_map.get(name, (255, 255, 255))


def lighten(color: tuple, amount: float) -> tuple:
    """Lighten a color by amount (0.0 to 1.0)"""
    return tuple(min(255, int(c + (255 - c) * amount)) for c in color[:3])


def darken(color: tuple, amount: float) -> tuple:
    """Darken a color by amount (0.0 to 1.0)"""
    return tuple(max(0, int(c * (1 - amount))) for c in color[:3])


def blend(color1: tuple, color2: tuple, ratio: float) -> tuple:
    """Blend two colors (ratio 0.0 = color1, 1.0 = color2)"""
    return tuple(int(c1 + (c2 - c1) * ratio)
                for c1, c2 in zip(color1[:3], color2[:3]))