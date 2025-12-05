"""
Board Renderer
Draws the chess board
"""

import pygame
import config
import os


class BoardRenderer:
    """Renders the chess board"""

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

    def draw_board(self, screen):
        """Draw the chess board"""
        if self.has_image:
            # Draw loaded image
            screen.blit(self.board_image,
                        (config.BOARD_OFFSET_X, config.BOARD_OFFSET_Y))
        else:
            # Draw board with colored squares
            self._draw_squares(screen)

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