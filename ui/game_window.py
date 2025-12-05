"""
Game Window Manager
Main window coordination
"""

import pygame
import config
from .board_renderer import BoardRenderer
from .piece_renderer import PieceRenderer
from .chat_panel import ChatPanel


class GameWindow:
    """Main game window manager"""

    def __init__(self, screen):
        """Initialize game window"""
        self.screen = screen
        self.board_renderer = BoardRenderer()
        self.piece_renderer = PieceRenderer()
        self.chat_panel = ChatPanel()

    def render(self, game_manager):
        """Render all game components"""
        try:
            # Render board
            self.board_renderer.draw_board(self.screen)

            # Render pieces
            if hasattr(game_manager, 'board'):
                for piece in game_manager.board.get_all_pieces():
                    if not piece.is_captured:
                        self.piece_renderer.draw_piece(self.screen, piece)

            # Render chat
            if hasattr(game_manager, 'chat_history'):
                self.chat_panel.draw(self.screen, game_manager.chat_history)

        except Exception as e:
            print(f"Error rendering: {e}")

    def handle_event(self, event):
        """Handle window events"""
        pass