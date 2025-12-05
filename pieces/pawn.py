from .base_piece import BasePiece


class Pawn(BasePiece):
    def __init__(self, color, row, col):
        super().__init__(color, row, col, 'pawn')

    def get_possible_moves(self, board):
        moves = []
        direction = -1 if self.color == 'white' else 1

        # Forward move
        new_row = self.row + direction
        if board.is_valid_position(new_row, self.col):
            if board.is_square_empty(new_row, self.col):
                moves.append((new_row, self.col))

                # Double move from starting position
                if not self.has_moved:
                    double_row = self.row + 2 * direction
                    if board.is_square_empty(double_row, self.col):
                        moves.append((double_row, self.col))

        # Captures
        for dc in [-1, 1]:
            new_col = self.col + dc
            if board.is_valid_position(new_row, new_col):
                target = board.get_piece_at(new_row, new_col)
                if target and self.is_enemy(target):
                    moves.append((new_row, new_col))

        return moves