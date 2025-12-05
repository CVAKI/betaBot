from .base_piece import BasePiece


class Knight(BasePiece):
    def __init__(self, color, row, col):
        super().__init__(color, row, col, 'knight')

    def get_possible_moves(self, board):
        moves = []
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]

        for dr, dc in knight_moves:
            new_row, new_col = self.row + dr, self.col + dc
            if board.is_valid_position(new_row, new_col):
                target = board.get_piece_at(new_row, new_col)
                if target is None or self.is_enemy(target):
                    moves.append((new_row, new_col))

        return moves