"""
Chat Panel
Displays piece communications
"""

import pygame
import config


class ChatPanel:
    """Chat interface display component"""

    def __init__(self):
        """Initialize chat panel"""
        self.font = pygame.font.Font(None, config.FONT_CHAT_SIZE)
        self.scroll_offset = 0
        self.max_messages = 50

    def draw(self, screen, chat_history):
        """Draw chat panel with messages"""
        try:
            # Draw panel background
            panel_rect = pygame.Rect(
                config.CHAT_PANEL_X,
                config.CHAT_PANEL_Y,
                config.CHAT_PANEL_WIDTH,
                config.SCREEN_HEIGHT - 100
            )
            pygame.draw.rect(screen, config.CHAT_PANEL_BG, panel_rect)

            # Draw border
            pygame.draw.rect(screen, config.TEXT_COLOR, panel_rect, 2)

            # Draw title
            title_font = pygame.font.Font(None, 24)
            title = title_font.render("Piece Communications", True, config.TEXT_COLOR)
            screen.blit(title, (config.CHAT_PANEL_X + 10, config.CHAT_PANEL_Y + 10))

            # Draw messages
            y_offset = config.CHAT_PANEL_Y + 40

            if chat_history:
                for message in chat_history[-self.max_messages:]:
                    if y_offset < config.SCREEN_HEIGHT - 100:
                        self._draw_message(screen, message, y_offset)
                        y_offset += 25
            else:
                # Show placeholder text
                placeholder_text = self.font.render("No messages yet...", True, (150, 150, 150))
                screen.blit(placeholder_text, (config.CHAT_PANEL_X + 20, y_offset))

        except Exception as e:
            print(f"Error drawing chat panel: {e}")

    def _draw_message(self, screen, message, y_offset):
        """Draw a single message"""
        try:
            # Format: "[time] Sender: message"
            if isinstance(message, dict):
                sender = message.get('sender', 'Unknown')
                content = message.get('content', '')
                emotion = message.get('emotion', 'NEUTRAL')
            else:
                # Handle message object
                sender = getattr(message, 'sender', 'Unknown')
                content = getattr(message, 'content', '')
                emotion = getattr(message, 'emotion', 'NEUTRAL')

            # Get emoji
            emoji_map = {
                'HAPPY': '😊', 'SAD': '😢', 'SCARED': '😰',
                'CONFIDENT': '😤', 'ANGRY': '😠', 'NEUTRAL': '😐',
                'ANXIOUS': '😟', 'PROUD': '😎', 'RESIGNED': '😔'
            }
            emoji = emoji_map.get(emotion, '😐')

            # Format message text
            message_text = f"{emoji} {sender}: {content}"

            # Render text
            text_surface = self.font.render(message_text, True, config.TEXT_COLOR)

            # Truncate if too long
            max_width = config.CHAT_PANEL_WIDTH - 40
            if text_surface.get_width() > max_width:
                # Truncate text
                truncated = message_text[:60] + "..."
                text_surface = self.font.render(truncated, True, config.TEXT_COLOR)

            screen.blit(text_surface, (config.CHAT_PANEL_X + 10, y_offset))

        except Exception as e:
            print(f"Error drawing message: {e}")