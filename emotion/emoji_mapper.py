"""
Emoji Mapper - Maps emotions to visual representations
"""

import pygame
import os
import config
from .emotion_types import Emotion


class EmojiMapper:
    """Maps emotions to emoji sprites"""

    def __init__(self):
        self.emoji_sprites = {}
        self.text_emojis = {}
        self._load_emoji_sprites()
        self._setup_text_fallbacks()

    def _load_emoji_sprites(self):
        """Load emoji image files"""
        for emotion_name, filepath in config.EMOJI_FILES.items():
            try:
                if os.path.exists(filepath):
                    sprite = pygame.image.load(filepath)
                    # Scale to appropriate size (32x32)
                    sprite = pygame.transform.scale(sprite, (32, 32))
                    self.emoji_sprites[emotion_name] = sprite
            except Exception as e:
                print(f"Warning: Could not load emoji for {emotion_name}: {e}")

    def _setup_text_fallbacks(self):
        """Setup text emoji fallbacks"""
        self.text_emojis = {
            'HAPPY': '😊',
            'SAD': '😢',
            'SCARED': '😰',
            'CONFIDENT': '😤',
            'ANGRY': '😠',
            'NEUTRAL': '😐',
            'ANXIOUS': '😟',
            'PROUD': '😎',
            'RESIGNED': '😔',
            'EXCITED': '🤩',
            'DETERMINED': '😠',
            'HOPEFUL': '🙂',
            'DESPERATE': '😭'
        }

    def get_emoji_sprite(self, emotion: str) -> pygame.Surface:
        """Get emoji sprite for an emotion"""
        return self.emoji_sprites.get(emotion)

    def get_text_emoji(self, emotion: str) -> str:
        """Get text emoji for an emotion"""
        return self.text_emojis.get(emotion, '😐')

    def draw_emoji_on_piece(self, screen, emotion: str, x: int, y: int):
        """Draw emoji overlay on piece"""
        sprite = self.get_emoji_sprite(emotion)
        if sprite:
            # Position at top-right corner of piece
            emoji_x = x + config.SQUARE_SIZE - 35
            emoji_y = y + 3
            screen.blit(sprite, (emoji_x, emoji_y))
        else:
            # Fallback: draw text emoji
            font = pygame.font.Font(None, 24)
            text_emoji = self.get_text_emoji(emotion)
            text_surface = font.render(text_emoji, True, (255, 255, 255))
            screen.blit(text_surface, (x + config.SQUARE_SIZE - 30, y + 5))

    def create_emoji_legend(self, screen, x: int, y: int):
        """Draw emoji legend showing what each emotion means"""
        font = pygame.font.Font(None, 18)
        legend_y = y

        for emotion, emoji in self.text_emojis.items():
            text = f"{emoji} {emotion}"
            surface = font.render(text, True, config.TEXT_COLOR)
            screen.blit(surface, (x, legend_y))
            legend_y += 20