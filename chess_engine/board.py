"""
Chess Board Representation and State Management
Maintains the 8x8 grid and piece positions
"""

import copy
from typing import Optional, List, Tuple


class Board:
    """Represents an 8x8 chess board with piece management"""

    def __init__(self):
        """Initialize an empty board"""
        # 8x8 grid: None for empty squares, Piece objects for occupied
        self.grid = [[None for _ in range(8)] for _ in range(8)]

        # Lists to track pieces
        self.white_pieces = []
        self.black_pieces = []
        self.captured_white = []
        self.captured_black = []

        # Board state
        self.move_count = 0

    def setup_initial_position(self):
        """Setup standard chess starting position"""
        # This will be called by game_manager to populate with Piece objects
        pass

    def get_piece_at(self, row: int, col: int) -> Optional['Piece']:
        """Get piece at specified position"""
        if not self.is_valid_position(row, col):
            return None
        return self.grid[row][col]

    def set_piece_at(self, row: int, col: int, piece: Optional['Piece']):
        """Set piece at specified position"""
        if not self.is_valid_position(row, col):
            return False

        # Remove old piece from tracking if exists
        old_piece = self.grid[row][col]
        if old_piece:
            self._remove_from_tracking(old_piece)

        # Set new piece
        self.grid[row][col] = piece

        # Update piece position and tracking if piece exists
        if piece:
            piece.row = row
            piece.col = col
            self._add_to_tracking(piece)

        return True

    def move_piece(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Move a piece from one square to another"""
        # Validate positions
        if not self.is_valid_position(from_row, from_col) or \
                not self.is_valid_position(to_row, to_col):
            return False

        # Get piece to move
        piece = self.get_piece_at(from_row, from_col)
        if not piece:
            return False

        # Handle capture
        captured = self.get_piece_at(to_row, to_col)
        if captured:
            self.capture_piece(captured)

        # Move piece
        self.grid[from_row][from_col] = None
        self.grid[to_row][to_col] = piece
        piece.row = to_row
        piece.col = to_col
        piece.has_moved = True

        self.move_count += 1
        return True

    def capture_piece(self, piece: 'Piece'):
        """Remove a piece from the board (capture it)"""
        # Remove from board
        if self.grid[piece.row][piece.col] == piece:
            self.grid[piece.row][piece.col] = None

        # Move to captured list
        self._remove_from_tracking(piece)
        if piece.color == 'white':
            self.captured_white.append(piece)
        else:
            self.captured_black.append(piece)

        piece.is_captured = True

    def is_square_empty(self, row: int, col: int) -> bool:
        """Check if a square is empty"""
        if not self.is_valid_position(row, col):
            return False
        return self.grid[row][col] is None

    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if position is within board boundaries"""
        return 0 <= row < 8 and 0 <= col < 8

    def get_piece_by_type_and_color(self, piece_type: str, color: str) -> List['Piece']:
        """Get all pieces of a specific type and color"""
        pieces = self.white_pieces if color == 'white' else self.black_pieces
        return [p for p in pieces if p.piece_type == piece_type]

    def get_all_pieces(self, color: Optional[str] = None) -> List['Piece']:
        """Get all pieces, optionally filtered by color"""
        if color == 'white':
            return self.white_pieces[:]
        elif color == 'black':
            return self.black_pieces[:]
        else:
            return self.white_pieces + self.black_pieces

    def find_king(self, color: str) -> Optional['Piece']:
        """Find the king of specified color"""
        kings = self.get_piece_by_type_and_color('king', color)
        return kings[0] if kings else None

    def get_board_state(self) -> List[List[Optional['Piece']]]:
        """Get a copy of the current board state"""
        return copy.deepcopy(self.grid)

    def count_pieces(self, color: Optional[str] = None) -> int:
        """Count pieces on board"""
        if color == 'white':
            return len(self.white_pieces)
        elif color == 'black':
            return len(self.black_pieces)
        else:
            return len(self.white_pieces) + len(self.black_pieces)

    def get_material_count(self, color: str) -> int:
        """Calculate total material value for a color"""
        from config import PIECE_VALUES
        pieces = self.white_pieces if color == 'white' else self.black_pieces
        return sum(PIECE_VALUES.get(p.piece_type, 0) for p in pieces)

    def to_fen_position(self) -> str:
        """Convert board position to FEN notation (position part only)"""
        fen_rows = []
        for row in self.grid:
            fen_row = ""
            empty_count = 0
            for square in row:
                if square is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    # Use piece notation
                    symbol = square.get_symbol()
                    fen_row += symbol
            if empty_count > 0:
                fen_row += str(empty_count)
            fen_rows.append(fen_row)
        return '/'.join(fen_rows)

    def print_board(self):
        """Print ASCII representation of the board (for debugging)"""
        print("\n  a b c d e f g h")
        print("  ---------------")
        for row in range(8):
            print(f"{8 - row}|", end="")
            for col in range(8):
                piece = self.grid[row][col]
                if piece:
                    print(piece.get_symbol(), end=" ")
                else:
                    print(".", end=" ")
            print(f"|{8 - row}")
        print("  ---------------")
        print("  a b c d e f g h\n")

    def get_square_name(self, row: int, col: int) -> str:
        """Convert row, col to algebraic notation (e.g., e4)"""
        if not self.is_valid_position(row, col):
            return "??"
        files = "abcdefgh"
        ranks = "87654321"
        return f"{files[col]}{ranks[row]}"

    def get_position_from_notation(self, notation: str) -> Tuple[int, int]:
        """Convert algebraic notation to row, col"""
        if len(notation) != 2:
            return (-1, -1)

        files = "abcdefgh"
        ranks = "87654321"

        try:
            col = files.index(notation[0])
            row = ranks.index(notation[1])
            return (row, col)
        except (ValueError, IndexError):
            return (-1, -1)

    def clear_board(self):
        """Remove all pieces from the board"""
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.white_pieces.clear()
        self.black_pieces.clear()
        self.captured_white.clear()
        self.captured_black.clear()
        self.move_count = 0

    def clone(self) -> 'Board':
        """Create a deep copy of this board"""
        return copy.deepcopy(self)

    # Private helper methods
    def _add_to_tracking(self, piece: 'Piece'):
        """Add piece to appropriate tracking list"""
        if piece.color == 'white':
            if piece not in self.white_pieces:
                self.white_pieces.append(piece)
        else:
            if piece not in self.black_pieces:
                self.black_pieces.append(piece)

    def _remove_from_tracking(self, piece: 'Piece'):
        """Remove piece from tracking list"""
        if piece.color == 'white':
            if piece in self.white_pieces:
                self.white_pieces.remove(piece)
        else:
            if piece in self.black_pieces:
                self.black_pieces.remove(piece)

    def get_attacked_squares(self, color: str) -> set:
        """Get all squares attacked by pieces of a color"""
        attacked = set()
        pieces = self.white_pieces if color == 'white' else self.black_pieces

        for piece in pieces:
            # This will be implemented when we have piece move logic
            # For now, return empty set
            pass

        return attacked

    def is_square_attacked(self, row: int, col: int, by_color: str) -> bool:
        """Check if a square is under attack by a specific color"""
        # This will be implemented with proper move generation
        return False

    def __repr__(self):
        """String representation"""
        return f"Board(white_pieces={len(self.white_pieces)}, black_pieces={len(self.black_pieces)}, moves={self.move_count})"