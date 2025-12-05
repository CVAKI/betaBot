import pygame
import config


class BoardRenderer:
    def __init__(self):
        # Load board image (7000x7000, will scale down)
        self.board_image = pygame.image.load(config.BOARD_IMAGE)
        self.board_image = pygame.transform.scale(
            self.board_image,
            (config.BOARD_SIZE, config.BOARD_SIZE)
        )

    def draw_board(self, screen):
        # Draw board background
        screen.blit(self.board_image,
                    (config.BOARD_OFFSET_X, config.BOARD_OFFSET_Y))

        # Draw coordinates
        self._draw_coordinates(screen)

    def _draw_coordinates(self, screen):
        font = pygame.font.Font(None, config.FONT_COORDINATES_SIZE)
        files = "abcdefgh"

        for i, letter in enumerate(files):
            # Bottom coordinates
            text = font.render(letter, True, config.TEXT_COLOR)
            x = config.BOARD_OFFSET_X + i * config.SQUARE_SIZE + config.SQUARE_SIZE // 2
            y = config.BOARD_OFFSET_Y + config.BOARD_SIZE + 5
            screen.blit(text, (x, y))