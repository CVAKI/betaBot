"""
Text Renderer - Text rendering utilities
"""

import pygame
import config


class TextRenderer:
    """Handles text rendering with various options"""

    def __init__(self):
        self.fonts = {}
        self._load_fonts()

    def _load_fonts(self):
        """Load different fonts"""
        self.fonts['title'] = pygame.font.Font(None, config.FONT_TITLE_SIZE)
        self.fonts['chat'] = pygame.font.Font(None, config.FONT_CHAT_SIZE)
        self.fonts['ui'] = pygame.font.Font(None, config.FONT_UI_SIZE)
        self.fonts['coordinates'] = pygame.font.Font(None, config.FONT_COORDINATES_SIZE)

    def render_text(self, text, font_name, color, pos, screen,
                    shadow=False, align='left'):
        """Render text with options"""
        font = self.fonts.get(font_name, self.fonts['ui'])

        # Render shadow if requested
        if shadow:
            shadow_surface = font.render(text, True, (0, 0, 0))
            screen.blit(shadow_surface, (pos[0] + 2, pos[1] + 2))

        # Render main text
        text_surface = font.render(text, True, color)

        # Apply alignment
        if align == 'center':
            text_rect = text_surface.get_rect(center=pos)
            screen.blit(text_surface, text_rect)
        elif align == 'right':
            text_rect = text_surface.get_rect()
            text_rect.right = pos[0]
            text_rect.top = pos[1]
            screen.blit(text_surface, text_rect)
        else:  # left
            screen.blit(text_surface, pos)

    def wrap_text(self, text, font_name, max_width):
        """Wrap text to fit within max_width"""
        font = self.fonts.get(font_name, self.fonts['ui'])
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            width, _ = font.size(test_line)

            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def draw_multiline(self, text, font_name, color, pos, screen,
                       max_width, line_spacing=5):
        """Draw multi-line text"""
        lines = self.wrap_text(text, font_name, max_width)
        x, y = pos

        for line in lines:
            self.render_text(line, font_name, color, (x, y), screen)
            y += self.fonts[font_name].get_height() + line_spacing