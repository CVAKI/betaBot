"""UI module initialization"""
from .board_renderer import BoardRenderer
from .piece_renderer import PieceRenderer
from .chat_panel import ChatPanel
from .game_window import GameWindow

__all__ = ['BoardRenderer', 'PieceRenderer', 'ChatPanel', 'GameWindow']