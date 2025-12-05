"""
Button UI Component
"""

import pygame
import config


class Button:
    """Clickable button UI element"""

    def __init__(self, x, y, width, height, text, color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color or config.BUTTON_COLOR
        self.hover_color = config.BUTTON_HOVER
        self.disabled_color = config.BUTTON_DISABLED
        self.is_hovered = False
        self.is_enabled = True
        self.font = pygame.font.Font(None, config.FONT_UI_SIZE)

    def draw(self, screen):
        """Draw the button"""
        # Determine color
        if not self.is_enabled:
            color = self.disabled_color
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.color

        # Draw button rectangle
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, config.TEXT_COLOR, self.rect, 2, border_radius=5)

        # Draw text
        text_surface = self.font.render(self.text, True, config.TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        """Handle mouse events"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_enabled and self.rect.collidepoint(event.pos):
                return True
        return False

    def is_clicked(self, mouse_pos) -> bool:
        """Check if button is clicked"""
        return self.is_enabled and self.rect.collidepoint(mouse_pos)

    def set_enabled(self, enabled: bool):
        """Enable or disable the button"""
        self.is_enabled = enabled

    def set_text(self, text: str):
        """Change button text"""
        self.text = text