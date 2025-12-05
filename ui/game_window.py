import pygame
import config


class GameWindow:
    def __init__(self, screen):
        self.screen = screen
        self.board_renderer = BoardRenderer()
        self.piece_renderer = PieceRenderer()
        self.chat_panel = ChatPanel()

    def render(self, game_manager):
        # Render board
        self.board_renderer.draw_board(self.screen)

        # Render pieces
        for piece in game_manager.board.get_all_pieces():
            self.piece_renderer.draw_piece(self.screen, piece)

        # Render chat
        self.chat_panel.draw(self.screen, game_manager.chat_history)

    def handle_event(self, event):
        pass