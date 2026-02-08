"""
Board Renderer with Move Highlights
"""

import pygame
import config
import os


class BoardRenderer:
    """Renders the chess board with highlights"""

    def __init__(self):
        """Initialize board renderer"""
        # Try to load board image
        if os.path.exists(config.BOARD_IMAGE):
            try:
                self.board_image = pygame.image.load(config.BOARD_IMAGE)
                self.board_image = pygame.transform.scale(
                    self.board_image,
                    (config.BOARD_SIZE, config.BOARD_SIZE)
                )
                self.has_image = True
            except Exception as e:
                print(f"Could not load board image: {e}")
                self.has_image = False
        else:
            self.has_image = False

    def draw_board(self, screen, highlights=None):
        """
        Draw the chess board with optional highlights

        Args:
            screen: Pygame screen surface
            highlights: Dictionary with 'selected', 'legal_moves', 'last_move'
        """
        if self.has_image:
            # Draw loaded image
            screen.blit(self.board_image,
                        (config.BOARD_OFFSET_X, config.BOARD_OFFSET_Y))
        else:
            # Draw board with colored squares
            self._draw_squares(screen)

        # Draw highlights on top of board
        if highlights:
            self._draw_highlights(screen, highlights)

        # Draw coordinates
        self._draw_coordinates(screen)

    def _draw_squares(self, screen):
        """Draw alternating colored squares"""
        for row in range(8):
            for col in range(8):
                # Determine square color
                color = config.LIGHT_SQUARE if (row + col) % 2 == 0 else config.DARK_SQUARE

                # Calculate position
                x = config.BOARD_OFFSET_X + col * config.SQUARE_SIZE
                y = config.BOARD_OFFSET_Y + row * config.SQUARE_SIZE

                # Draw square
                rect = pygame.Rect(x, y, config.SQUARE_SIZE, config.SQUARE_SIZE)
                pygame.draw.rect(screen, color, rect)

    def _draw_highlights(self, screen, highlights):
        """Draw highlighted squares"""
        # Draw last move highlight
        if highlights.get('last_move'):
            last_move = highlights['last_move']
            self._draw_square_highlight(screen, last_move['from'], (255, 255, 0, 80))
            self._draw_square_highlight(screen, last_move['to'], (255, 255, 0, 80))

        # Draw selected piece highlight
        if highlights.get('selected'):
            self._draw_square_highlight(screen, highlights['selected'], (100, 200, 255, 120))

        # Draw legal move indicators
        if highlights.get('legal_moves'):
            for move_pos in highlights['legal_moves']:
                self._draw_move_indicator(screen, move_pos)

    def _draw_square_highlight(self, screen, position, color):
        """Draw a colored highlight on a square"""
        if not position:
            return

        row, col = position
        x = config.BOARD_OFFSET_X + col * config.SQUARE_SIZE
        y = config.BOARD_OFFSET_Y + row * config.SQUARE_SIZE

        # Create semi-transparent surface
        highlight_surface = pygame.Surface((config.SQUARE_SIZE, config.SQUARE_SIZE))
        highlight_surface.set_alpha(color[3] if len(color) > 3 else 128)
        highlight_surface.fill(color[:3])

        screen.blit(highlight_surface, (x, y))

        # Draw border
        rect = pygame.Rect(x, y, config.SQUARE_SIZE, config.SQUARE_SIZE)
        pygame.draw.rect(screen, color[:3], rect, 3)

    def _draw_move_indicator(self, screen, position):
        """Draw a circle indicator for legal moves"""
        row, col = position
        x = config.BOARD_OFFSET_X + col * config.SQUARE_SIZE + config.SQUARE_SIZE // 2
        y = config.BOARD_OFFSET_Y + row * config.SQUARE_SIZE + config.SQUARE_SIZE // 2

        # Draw semi-transparent circle
        circle_surface = pygame.Surface((config.SQUARE_SIZE, config.SQUARE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(circle_surface, (0, 255, 0, 100),
                          (config.SQUARE_SIZE // 2, config.SQUARE_SIZE // 2),
                          config.SQUARE_SIZE // 6)

        screen.blit(circle_surface,
                   (x - config.SQUARE_SIZE // 2, y - config.SQUARE_SIZE // 2))

    def _draw_coordinates(self, screen):
        """Draw file and rank labels"""
        font = pygame.font.Font(None, config.FONT_COORDINATES_SIZE)
        files = "abcdefgh"
        ranks = "87654321"

        for i, letter in enumerate(files):
            # Bottom file labels (a-h)
            text = font.render(letter, True, config.TEXT_COLOR)
            text_rect = text.get_rect()
            x = config.BOARD_OFFSET_X + i * config.SQUARE_SIZE + config.SQUARE_SIZE // 2
            y = config.BOARD_OFFSET_Y + config.BOARD_SIZE + 5
            text_rect.center = (x, y)
            screen.blit(text, text_rect)

        for i, number in enumerate(ranks):
            # Left rank labels (8-1)
            text = font.render(number, True, config.TEXT_COLOR)
            text_rect = text.get_rect()
            x = config.BOARD_OFFSET_X - 15
            y = config.BOARD_OFFSET_Y + i * config.SQUARE_SIZE + config.SQUARE_SIZE // 2
            text_rect.center = (x, y)
            screen.blit(text, text_rect)