"""
Enhanced Full-Screen UI Configuration and Rendering
File: ui/enhanced_ui.py
Place this file in: cvaki-betabot/ui/enhanced_ui.py
"""

import pygame
import os
import config


# Responsive layout calculator
def calculate_layout(screen_width, screen_height):
    """Calculate layout based on screen size"""
    # Board takes 60% of width
    board_size = int(min(screen_height * 0.9, screen_width * 0.55))
    square_size = board_size // 8

    # Chat panel takes remaining space
    chat_panel_width = screen_width - board_size - 150
    chat_panel_height = screen_height - 100

    board_offset_x = 50
    board_offset_y = 50

    chat_panel_x = board_offset_x + board_size + 50
    chat_panel_y = 50

    return {
        'board_size': board_size,
        'square_size': square_size,
        'board_offset_x': board_offset_x,
        'board_offset_y': board_offset_y,
        'chat_panel_width': chat_panel_width,
        'chat_panel_height': chat_panel_height,
        'chat_panel_x': chat_panel_x,
        'chat_panel_y': chat_panel_y
    }


class EnhancedGameWindow:
    """Enhanced full-screen game window"""

    def __init__(self):
        """Initialize with dynamic screen size"""
        pygame.init()

        # Get display info
        display_info = pygame.display.Info()

        # Check if fullscreen is enabled in config
        use_fullscreen = getattr(config, 'USE_FULLSCREEN', False)

        if use_fullscreen:
            self.screen = pygame.display.set_mode(
                (display_info.current_w, display_info.current_h),
                pygame.FULLSCREEN
            )
            self.screen_width = display_info.current_w
            self.screen_height = display_info.current_h
        else:
            screen_width = getattr(config, 'SCREEN_WIDTH', 1600)
            screen_height = getattr(config, 'SCREEN_HEIGHT', 900)
            self.screen = pygame.display.set_mode((screen_width, screen_height))
            self.screen_width = screen_width
            self.screen_height = screen_height

        pygame.display.set_caption("β-bot: Multi-Agent Chess AI")

        # Calculate layout
        self.layout = calculate_layout(self.screen_width, self.screen_height)

        # Initialize renderers
        self.board_renderer = EnhancedBoardRenderer(self.layout)
        self.piece_renderer = EnhancedPieceRenderer(self.layout)
        self.chat_panel = EnhancedChatPanel(self.layout)

        print(f"✅ Enhanced UI initialized at {self.screen_width}x{self.screen_height}")
        print(f"   Board: {self.layout['board_size']}x{self.layout['board_size']}")
        print(f"   Chat: {self.layout['chat_panel_width']}x{self.layout['chat_panel_height']}")

    def render(self, game_manager):
        """Render all components"""
        try:
            # Clear screen
            self.screen.fill(config.BACKGROUND_COLOR)

            # Render board
            self.board_renderer.draw_board(self.screen)

            # Render pieces
            if hasattr(game_manager, 'board'):
                for piece in game_manager.board.get_all_pieces():
                    if not piece.is_captured:
                        self.piece_renderer.draw_piece(self.screen, piece)

            # Render chat
            if hasattr(game_manager, 'chat_history'):
                self.chat_panel.draw(self.screen, game_manager.chat_history)

        except Exception as e:
            print(f"Render error: {e}")

    def handle_event(self, event):
        """Handle window events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                self.toggle_fullscreen()

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed"""
        # Toggle the config value
        config.USE_FULLSCREEN = not getattr(config, 'USE_FULLSCREEN', False)

        if config.USE_FULLSCREEN:
            display_info = pygame.display.Info()
            self.screen = pygame.display.set_mode(
                (display_info.current_w, display_info.current_h),
                pygame.FULLSCREEN
            )
            self.screen_width = display_info.current_w
            self.screen_height = display_info.current_h
        else:
            self.screen = pygame.display.set_mode((1600, 900))
            self.screen_width = 1600
            self.screen_height = 900

        # Recalculate layout
        self.layout = calculate_layout(self.screen_width, self.screen_height)
        self.board_renderer.update_layout(self.layout)
        self.piece_renderer.update_layout(self.layout)
        self.chat_panel.update_layout(self.layout)

        print(f"🖥️  Toggled to {'fullscreen' if config.USE_FULLSCREEN else 'windowed'} mode")


class EnhancedBoardRenderer:
    """Board renderer with dynamic sizing"""

    def __init__(self, layout):
        self.layout = layout

    def update_layout(self, layout):
        """Update layout when screen size changes"""
        self.layout = layout

    def draw_board(self, screen):
        """Draw board with dynamic sizing"""
        board_size = self.layout['board_size']
        square_size = self.layout['square_size']
        offset_x = self.layout['board_offset_x']
        offset_y = self.layout['board_offset_y']

        # Draw squares
        for row in range(8):
            for col in range(8):
                color = config.LIGHT_SQUARE if (row + col) % 2 == 0 else config.DARK_SQUARE

                x = offset_x + col * square_size
                y = offset_y + row * square_size

                rect = pygame.Rect(x, y, square_size, square_size)
                pygame.draw.rect(screen, color, rect)

        # Draw border
        border_rect = pygame.Rect(offset_x - 2, offset_y - 2, board_size + 4, board_size + 4)
        pygame.draw.rect(screen, config.TEXT_COLOR, border_rect, 3)

        # Draw coordinates
        font_size = max(14, square_size // 8)
        font = pygame.font.Font(None, font_size)
        files = "abcdefgh"
        ranks = "87654321"

        for i in range(8):
            # Files (bottom)
            text = font.render(files[i], True, config.TEXT_COLOR)
            x = offset_x + i * square_size + square_size // 2 - text.get_width() // 2
            y = offset_y + board_size + 10
            screen.blit(text, (x, y))

            # Ranks (left)
            text = font.render(ranks[i], True, config.TEXT_COLOR)
            x = offset_x - 25
            y = offset_y + i * square_size + square_size // 2 - text.get_height() // 2
            screen.blit(text, (x, y))


class EnhancedPieceRenderer:
    """Piece renderer with dynamic sizing"""

    def __init__(self, layout):
        self.layout = layout
        self.piece_images = {}
        self._load_piece_images()

    def update_layout(self, layout):
        """Update layout and reload images with new size"""
        self.layout = layout
        self._load_piece_images()

    def _load_piece_images(self):
        """Load and scale piece images"""
        square_size = self.layout['square_size']

        for color in ['white', 'black']:
            self.piece_images[color] = {}
            for piece_type in ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']:
                path = config.PIECE_IMAGES[color][piece_type]

                try:
                    if os.path.exists(path):
                        img = pygame.image.load(path)
                        img = pygame.transform.scale(img, (square_size, square_size))
                        self.piece_images[color][piece_type] = img
                    else:
                        self.piece_images[color][piece_type] = self._create_placeholder(
                            color, piece_type, square_size
                        )
                except Exception as e:
                    self.piece_images[color][piece_type] = self._create_placeholder(
                        color, piece_type, square_size
                    )

    def _create_placeholder(self, color, piece_type, size):
        """Create placeholder piece when image not available"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        circle_color = (255, 255, 255) if color == 'white' else (50, 50, 50)
        center = size // 2
        radius = size // 3

        pygame.draw.circle(surface, circle_color, (center, center), radius)
        pygame.draw.circle(surface, (128, 128, 128), (center, center), radius, 2)

        # Draw letter
        font_size = max(24, size // 3)
        font = pygame.font.Font(None, font_size)
        symbols = {'king': 'K', 'queen': 'Q', 'rook': 'R',
                   'bishop': 'B', 'knight': 'N', 'pawn': 'P'}
        text = font.render(symbols.get(piece_type, '?'), True, (200, 0, 0))
        text_rect = text.get_rect(center=(center, center))
        surface.blit(text, text_rect)

        return surface

    def draw_piece(self, screen, piece):
        """Draw piece with emotion overlay"""
        square_size = self.layout['square_size']
        offset_x = self.layout['board_offset_x']
        offset_y = self.layout['board_offset_y']

        img = self.piece_images.get(piece.color, {}).get(piece.piece_type)

        if img:
            x = offset_x + piece.col * square_size
            y = offset_y + piece.row * square_size

            screen.blit(img, (x, y))

            # Draw emotion emoji (larger and more visible)
            emoji_map = {
                'HAPPY': '😊', 'SAD': '😢', 'SCARED': '😰',
                'CONFIDENT': '😤', 'ANGRY': '😠', 'NEUTRAL': '😐',
                'ANXIOUS': '😟', 'PROUD': '😎', 'RESIGNED': '😔',
                'EXCITED': '🤩', 'DETERMINED': '💪', 'DESPERATE': '😭'
            }
            emoji = emoji_map.get(piece.current_emotion, '😐')

            emoji_font_size = max(20, square_size // 4)
            emoji_font = pygame.font.Font(None, emoji_font_size)
            emoji_surface = emoji_font.render(emoji, True, (255, 255, 255))

            emoji_x = x + square_size - emoji_surface.get_width() - 5
            emoji_y = y + 5

            # Draw background circle for emoji visibility
            circle_center = (emoji_x + emoji_surface.get_width() // 2,
                             emoji_y + emoji_surface.get_height() // 2)
            circle_radius = emoji_surface.get_width() // 2 + 3
            pygame.draw.circle(screen, (0, 0, 0), circle_center, circle_radius)

            screen.blit(emoji_surface, (emoji_x, emoji_y))


class EnhancedChatPanel:
    """Enhanced chat panel with larger, more readable text"""

    def __init__(self, layout):
        self.layout = layout
        self.scroll_offset = 0
        self.max_visible_messages = 25

        # Calculate font size based on panel width
        base_font_size = max(16, layout['chat_panel_width'] // 50)
        self.font = pygame.font.Font(None, base_font_size)
        self.title_font = pygame.font.Font(None, base_font_size + 8)

    def update_layout(self, layout):
        """Update layout and recalculate font sizes"""
        self.layout = layout
        base_font_size = max(16, layout['chat_panel_width'] // 50)
        self.font = pygame.font.Font(None, base_font_size)
        self.title_font = pygame.font.Font(None, base_font_size + 8)

    def draw(self, screen, chat_history):
        """Draw enhanced chat panel with better styling"""
        panel_x = self.layout['chat_panel_x']
        panel_y = self.layout['chat_panel_y']
        panel_width = self.layout['chat_panel_width']
        panel_height = self.layout['chat_panel_height']

        # Draw background with shadow effect
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        # Draw shadow
        shadow_rect = panel_rect.copy()
        shadow_rect.x += 5
        shadow_rect.y += 5
        pygame.draw.rect(screen, (20, 20, 20), shadow_rect, border_radius=10)

        # Draw main panel
        pygame.draw.rect(screen, config.CHAT_PANEL_BG, panel_rect, border_radius=10)
        pygame.draw.rect(screen, config.TEXT_COLOR, panel_rect, 3, border_radius=10)

        # Draw title
        title = self.title_font.render("♟️ Piece Communications", True, (255, 215, 0))
        screen.blit(title, (panel_x + 20, panel_y + 15))

        # Draw subtitle
        subtitle_font = pygame.font.Font(None, self.font.get_height() - 2)
        subtitle = subtitle_font.render("Real-time AI Conversations", True, (180, 180, 180))
        screen.blit(subtitle, (panel_x + 20, panel_y + 45))

        # Draw separator line
        pygame.draw.line(screen, (100, 100, 100),
                         (panel_x + 10, panel_y + 70),
                         (panel_x + panel_width - 10, panel_y + 70), 2)

        # Draw messages
        y_offset = panel_y + 85
        message_height = self.font.get_height() + 12

        if chat_history:
            recent_messages = chat_history[-self.max_visible_messages:]

            for message in recent_messages:
                if y_offset + message_height > panel_y + panel_height - 20:
                    break

                self._draw_message(screen, message, panel_x, y_offset, panel_width)
                y_offset += message_height
        else:
            # Show placeholder when no messages
            placeholder = self.font.render("Waiting for first move...", True, (120, 120, 120))
            screen.blit(placeholder, (panel_x + 30, y_offset))

    def _draw_message(self, screen, message, panel_x, y_offset, panel_width):
        """Draw individual message with color coding and styling"""
        # Get message data (handle both dict and object formats)
        if isinstance(message, dict):
            sender = message.get('sender', 'Unknown')
            content = message.get('content', '')
            emotion = message.get('emotion', 'NEUTRAL')
        else:
            sender = getattr(message, 'sender', 'Unknown')
            content = getattr(message, 'content', '')
            emotion = getattr(message, 'emotion', 'NEUTRAL')

        # Get emoji for emotion
        emoji_map = {
            'HAPPY': '😊', 'SAD': '😢', 'SCARED': '😰',
            'CONFIDENT': '😤', 'ANGRY': '😠', 'NEUTRAL': '😐',
            'ANXIOUS': '😟', 'PROUD': '😎', 'RESIGNED': '😔',
            'EXCITED': '🤩', 'DETERMINED': '💪', 'DESPERATE': '😭'
        }
        emoji = emoji_map.get(emotion, '😐')

        # Color code by piece type for better readability
        sender_lower = sender.lower()
        if 'queen' in sender_lower:
            sender_color = (255, 215, 0)  # Gold
        elif 'king' in sender_lower:
            sender_color = (138, 43, 226)  # Purple
        elif 'knight' in sender_lower:
            sender_color = (100, 200, 255)  # Light blue
        elif 'pawn' in sender_lower:
            sender_color = (200, 200, 200)  # Gray
        elif 'bishop' in sender_lower:
            sender_color = (255, 150, 100)  # Orange
        elif 'rook' in sender_lower:
            sender_color = (100, 255, 100)  # Green
        elif 'system' in sender_lower:
            sender_color = (255, 255, 100)  # Yellow
        else:
            sender_color = (150, 255, 150)  # Light green

        # Draw message background
        msg_rect = pygame.Rect(panel_x + 15, y_offset - 3, panel_width - 30,
                               self.font.get_height() + 8)
        pygame.draw.rect(screen, (50, 50, 60), msg_rect, border_radius=5)

        # Draw emoji
        emoji_surface = self.font.render(emoji, True, (255, 255, 255))
        screen.blit(emoji_surface, (panel_x + 20, y_offset))

        # Draw sender name with color
        sender_text = self.font.render(f"{sender}:", True, sender_color)
        screen.blit(sender_text, (panel_x + 50, y_offset))

        # Draw content with word wrapping
        content_x = panel_x + 50 + sender_text.get_width() + 10
        max_content_width = panel_width - (content_x - panel_x) - 25

        content_surface = self.font.render(content, True, (255, 255, 255))

        if content_surface.get_width() > max_content_width:
            # Truncate long messages
            truncated_content = content[:60] + "..."
            content_surface = self.font.render(truncated_content, True, (255, 255, 255))

        screen.blit(content_surface, (content_x, y_offset))