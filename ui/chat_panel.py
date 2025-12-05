import pygame
import config


class ChatPanel:
    def __init__(self):
        self.font = pygame.font.Font(None, config.FONT_CHAT_SIZE)
        self.scroll_offset = 0
        self.max_messages = 50

    def draw(self, screen, chat_history):
        # Draw panel background
        panel_rect = pygame.Rect(
            config.CHAT_PANEL_X,
            config.CHAT_PANEL_Y,
            config.CHAT_PANEL_WIDTH,
            config.SCREEN_HEIGHT - 100
        )
        pygame.draw.rect(screen, config.CHAT_PANEL_BG, panel_rect)

        # Draw messages
        y_offset = config.CHAT_PANEL_Y + 10
        for message in chat_history[-self.max_messages:]:
            self._draw_message(screen, message, y_offset)
            y_offset += 25