"""
Piece Renderer
Renders chess pieces with emotion overlays
"""

import pygame
import config
import os


class PieceRenderer:
    """Renders chess pieces"""

    def __init__(self):
        """Initialize piece renderer"""
        self.piece_images = {}
        self.emoji_images = {}
        self._load_piece_images()
        self._load_emoji_images()

    def _load_piece_images(self):
        """Load piece images from assets"""
        for color in ['white', 'black']:
            self.piece_images[color] = {}
            for piece_type in ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']:
                path = config.PIECE_IMAGES[color][piece_type]

                try:
                    if os.path.exists(path):
                        # Load and scale image
                        img = pygame.image.load(path)
                        img = pygame.transform.scale(img, (config.SQUARE_SIZE, config.SQUARE_SIZE))
                        self.piece_images[color][piece_type] = img
                    else:
                        # Create placeholder surface
                        self.piece_images[color][piece_type] = self._create_placeholder(color, piece_type)
                except Exception as e:
                    print(f"Error loading {color} {piece_type}: {e}")
                    self.piece_images[color][piece_type] = self._create_placeholder(color, piece_type)

    def _create_placeholder(self, color, piece_type):
        """Create a placeholder surface when image not found"""
        surface = pygame.Surface((config.SQUARE_SIZE, config.SQUARE_SIZE), pygame.SRCALPHA)

        # Draw colored circle
        circle_color = (255, 255, 255) if color == 'white' else (0, 0, 0)
        center = config.SQUARE_SIZE // 2
        radius = config.SQUARE_SIZE // 3
        pygame.draw.circle(surface, circle_color, (center, center), radius)

        # Draw border
        pygame.draw.circle(surface, (128, 128, 128), (center, center), radius, 2)

        # Draw piece letter
        font = pygame.font.Font(None, 36)
        symbols = {'king': 'K', 'queen': 'Q', 'rook': 'R', 'bishop': 'B', 'knight': 'N', 'pawn': 'P'}
        text = font.render(symbols.get(piece_type, '?'), True, (255, 0, 0))
        text_rect = text.get_rect(center=(center, center))
        surface.blit(text, text_rect)

        return surface

    def _load_emoji_images(self):
        """Load emoji images"""
        for emotion_name, filepath in config.EMOJI_FILES.items():
            try:
                if os.path.exists(filepath):
                    sprite = pygame.image.load(filepath)
                    sprite = pygame.transform.scale(sprite, (32, 32))
                    self.emoji_images[emotion_name] = sprite
            except Exception as e:
                print(f"Could not load emoji {emotion_name}: {e}")

    def draw_piece(self, screen, piece):
        """Draw a piece on the board"""
        try:
            # Get piece image
            img = self.piece_images.get(piece.color, {}).get(piece.piece_type)

            if img:
                # Calculate screen position
                x = config.BOARD_OFFSET_X + piece.col * config.SQUARE_SIZE
                y = config.BOARD_OFFSET_Y + piece.row * config.SQUARE_SIZE

                # Draw piece
                screen.blit(img, (x, y))

                # Draw emotion emoji
                self._draw_emotion(screen, piece, x, y)
        except Exception as e:
            print(f"Error drawing piece: {e}")

    def _draw_emotion(self, screen, piece, x, y):
        """Draw emotion emoji overlay on piece"""
        try:
            emotion = piece.current_emotion

            # Try to use sprite
            if emotion in self.emoji_images:
                emoji_sprite = self.emoji_images[emotion]
                emoji_x = x + config.SQUARE_SIZE - 35
                emoji_y = y + 3
                screen.blit(emoji_sprite, (emoji_x, emoji_y))
            else:
                # Fallback: draw text emoji
                emoji_map = {
                    'HAPPY': '😊', 'SAD': '😢', 'SCARED': '😰',
                    'CONFIDENT': '😤', 'ANGRY': '😠', 'NEUTRAL': '😐',
                    'ANXIOUS': '😟', 'PROUD': '😎', 'RESIGNED': '😔'
                }
                emoji_text = emoji_map.get(emotion, '😐')

                font = pygame.font.Font(None, 24)
                text_surface = font.render(emoji_text, True, (255, 255, 255))
                screen.blit(text_surface, (x + config.SQUARE_SIZE - 30, y + 5))
        except Exception as e:
            pass  # Silently fail emoji rendering