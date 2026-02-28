from .base_piece import BasePiece


class Pawn(BasePiece):
    def __init__(self, color, row, col):
        super().__init__(color, row, col, 'pawn')

    def get_possible_moves(self, board):
        moves = []
        # White pawns move UP the board (decreasing row: 6 -> 5 -> 4 -> ... -> 0)
        # Black pawns move DOWN the board (increasing row: 1 -> 2 -> 3 -> ... -> 7)
        direction = -1 if self.color == 'white' else 1

        # === FORWARD MOVE (one square) ===
        new_row = self.row + direction
        if board.is_valid_position(new_row, self.col):
            if board.is_square_empty(new_row, self.col):
                moves.append((new_row, self.col))

                # === DOUBLE MOVE (from starting position only) ===
                # White pawns start at row 6, black pawns start at row 1
                starting_row = 6 if self.color == 'white' else 1

                # ✅ FIX: Check actual starting position, not just has_moved flag
                if self.row == starting_row:
                    double_row = self.row + 2 * direction
                    # ✅ FIX: Add validation check
                    if board.is_valid_position(double_row, self.col) and board.is_square_empty(double_row, self.col):
                        moves.append((double_row, self.col))

        # === DIAGONAL CAPTURES ===
        for dc in [-1, 1]:  # Left and right diagonals
            new_col = self.col + dc
            # ✅ CRITICAL FIX: Recalculate capture row instead of reusing new_row
            capture_row = self.row + direction

            if board.is_valid_position(capture_row, new_col):
                target = board.get_piece_at(capture_row, new_col)
                if target and self.is_enemy(target):
                    moves.append((capture_row, new_col))

        return moves