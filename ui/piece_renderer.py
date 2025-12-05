import pygame
import config


class PieceRenderer:
    def __init__(self):
        self.piece_images = self._load_piece_images()
        self.emoji_images = self._load_emoji_images()

    def _load_piece_images(self):
        images = {}
        for color in ['white', 'black']:
            images[color] = {}
            for piece_type in ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']:
                path = config.PIECE_IMAGES[color][piece_type]
                # Load 500x500 image and scale to square size
                img = pygame.image.load(path)
                img = pygame.transform.scale(img, (config.SQUARE_SIZE, config.SQUARE_SIZE))
                images[color][piece_type] = img
        return images

    def draw_piece(self, screen, piece):
        # Get piece image
        img = self.piece_images[piece.color][piece.piece_type]

        # Calculate screen position
        x = config.BOARD_OFFSET_X + piece.col * config.SQUARE_SIZE
        y = config.BOARD_OFFSET_Y + piece.row * config.SQUARE_SIZE

        # Draw piece
        screen.blit(img, (x, y))

        # Draw emotion emoji
        self._draw_emotion(screen, piece, x, y)