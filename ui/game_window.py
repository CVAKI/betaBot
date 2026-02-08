"""
Game Window Manager with Move Highlights
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

        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.subtitle_font = pygame.font.Font(None, 20)
        self.info_font = pygame.font.Font(None, 18)

    def render(self, game_manager):
        """Render all game components"""
        try:
            # Draw title bar
            self._draw_title()

            # Get highlights from game manager
            highlights = game_manager.get_highlighted_squares()

            # Render board with highlights
            self.board_renderer.draw_board(self.screen, highlights)

            # Render pieces
            if hasattr(game_manager, 'board'):
                for piece in game_manager.board.get_all_pieces():
                    if not piece.is_captured:
                        self.piece_renderer.draw_piece(self.screen, piece)

            # Render chat
            if hasattr(game_manager, 'chat_history'):
                self.chat_panel.draw(self.screen, game_manager.chat_history)

            # Draw game info
            self._draw_game_info(game_manager)

        except Exception as e:
            print(f"Error rendering: {e}")

    def _draw_title(self):
        """Draw the game title"""
        # Title
        title_text = self.title_font.render("β-bot Chess AI", True, (100, 200, 255))
        title_rect = title_text.get_rect(center=(config.SCREEN_WIDTH // 2, 30))
        self.screen.blit(title_text, title_rect)

        # Subtitle
        subtitle_text = self.subtitle_font.render("Multi-Agent Hierarchical Chess", True, (180, 180, 180))
        subtitle_rect = subtitle_text.get_rect(center=(config.SCREEN_WIDTH // 2, 55))
        self.screen.blit(subtitle_text, subtitle_rect)

    def _draw_game_info(self, game_manager):
        """Draw game information panel"""
        if not hasattr(game_manager, 'game_state'):
            return

        # Position below board
        x = config.BOARD_OFFSET_X
        y = config.BOARD_OFFSET_Y + config.BOARD_SIZE + 30

        # AI Mode indicator
        ai_status = "🤖 AI MODE" if game_manager.ai_mode else "🎮 MANUAL MODE"
        ai_color = (100, 255, 100) if game_manager.ai_mode else (255, 200, 100)
        ai_text = self.info_font.render(ai_status, True, ai_color)
        self.screen.blit(ai_text, (x, y))

        # Current turn
        current_player = game_manager.game_state.current_player
        turn_color = (255, 255, 255) if current_player == 'white' else (200, 200, 200)

        turn_text = self.info_font.render(
            f"Current Turn: {current_player.upper()}",
            True,
            turn_color
        )
        self.screen.blit(turn_text, (x + 200, y))

        # AI thinking indicator
        if game_manager.ai_thinking:
            thinking_text = self.info_font.render(
                "⏳ AI Thinking...",
                True,
                (255, 255, 0)
            )
            self.screen.blit(thinking_text, (x + 400, y))

        # Selected piece info (manual mode)
        if not game_manager.ai_mode and game_manager.selected_piece:
            piece = game_manager.selected_piece
            selected_text = self.info_font.render(
                f"Selected: {piece.color} {piece.piece_type} | Legal moves: {len(game_manager.legal_moves)}",
                True,
                (100, 255, 100)
            )
            self.screen.blit(selected_text, (x, y + 25))

        # Last move
        if game_manager.last_move:
            last_move_text = self.info_font.render(
                f"Last move: {game_manager.last_move['notation']}",
                True,
                (200, 200, 100)
            )
            self.screen.blit(last_move_text, (x, y + 50))

        # Material count
        white_material = game_manager.board.get_material_count('white')
        black_material = game_manager.board.get_material_count('black')
        material_diff = white_material - black_material

        material_text = self.info_font.render(
            f"Material: White {white_material} | Black {black_material} ({material_diff:+d})",
            True,
            (200, 200, 200)
        )
        self.screen.blit(material_text, (x, y + 75))

    def handle_event(self, event):
        """Handle window events"""
        pass