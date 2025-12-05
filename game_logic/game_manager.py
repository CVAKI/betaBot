"""
Game Manager
Main game flow controller
"""

from chess_engine.board import Board
from chess_engine.game_state import GameState
from pieces import Pawn, Knight, Bishop, Rook, Queen, King


class GameManager:
    """Main game flow controller"""

    def __init__(self):
        """Initialize game manager"""
        self.board = Board()
        self.game_state = GameState()
        self.pieces = []
        self.chat_history = []
        self.selected_piece = None

    def initialize_game(self):
        """Setup initial game state"""
        self._setup_pieces()
        print("✅ Game initialized with all pieces")

    def _setup_pieces(self):
        """Create all 32 pieces in starting positions"""
        # Clear existing pieces
        self.pieces.clear()
        self.board.clear_board()

        # White pieces (bottom)
        # Pawns
        for col in range(8):
            pawn = Pawn('white', 6, col)
            self.pieces.append(pawn)
            self.board.set_piece_at(6, col, pawn)

        # Rooks
        self.pieces.append(Rook('white', 7, 0))
        self.board.set_piece_at(7, 0, self.pieces[-1])
        self.pieces.append(Rook('white', 7, 7))
        self.board.set_piece_at(7, 7, self.pieces[-1])

        # Knights
        self.pieces.append(Knight('white', 7, 1))
        self.board.set_piece_at(7, 1, self.pieces[-1])
        self.pieces.append(Knight('white', 7, 6))
        self.board.set_piece_at(7, 6, self.pieces[-1])

        # Bishops
        self.pieces.append(Bishop('white', 7, 2))
        self.board.set_piece_at(7, 2, self.pieces[-1])
        self.pieces.append(Bishop('white', 7, 5))
        self.board.set_piece_at(7, 5, self.pieces[-1])

        # Queen
        self.pieces.append(Queen('white', 7, 3))
        self.board.set_piece_at(7, 3, self.pieces[-1])

        # King
        self.pieces.append(King('white', 7, 4))
        self.board.set_piece_at(7, 4, self.pieces[-1])

        # Black pieces (top)
        # Pawns
        for col in range(8):
            pawn = Pawn('black', 1, col)
            self.pieces.append(pawn)
            self.board.set_piece_at(1, col, pawn)

        # Rooks
        self.pieces.append(Rook('black', 0, 0))
        self.board.set_piece_at(0, 0, self.pieces[-1])
        self.pieces.append(Rook('black', 0, 7))
        self.board.set_piece_at(0, 7, self.pieces[-1])

        # Knights
        self.pieces.append(Knight('black', 0, 1))
        self.board.set_piece_at(0, 1, self.pieces[-1])
        self.pieces.append(Knight('black', 0, 6))
        self.board.set_piece_at(0, 6, self.pieces[-1])

        # Bishops
        self.pieces.append(Bishop('black', 0, 2))
        self.board.set_piece_at(0, 2, self.pieces[-1])
        self.pieces.append(Bishop('black', 0, 5))
        self.board.set_piece_at(0, 5, self.pieces[-1])

        # Queen
        self.pieces.append(Queen('black', 0, 3))
        self.board.set_piece_at(0, 3, self.pieces[-1])

        # King
        self.pieces.append(King('black', 0, 4))
        self.board.set_piece_at(0, 4, self.pieces[-1])

        print(f"Created {len(self.pieces)} pieces")

    def update(self):
        """Update game state each frame"""
        # For now, just maintain game state
        # AI decision-making will be added later
        pass

    def handle_mouse_click(self, pos):
        """Handle mouse click for piece selection/movement"""
        # This will be implemented for player interaction
        pass

    def reset_game(self):
        """Reset game to initial state"""
        self.game_state = GameState()
        self.chat_history.clear()
        self.selected_piece = None
        self._setup_pieces()

    def cleanup(self):
        """Cleanup game resources"""
        pass