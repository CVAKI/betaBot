from .base_piece import BasePiece


class Bishop(BasePiece):
    def __init__(self, color, row, col):
        super().__init__(color, row, col, 'bishop')

    def get_possible_moves(self, board):
        moves = []
        # Diagonal moves
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in directions:
            for dist in range(1, 8):
                new_row = self.row + dr * dist
                new_col = self.col + dc * dist

                if not board.is_valid_position(new_row, new_col):
                    break

                target = board.get_piece_at(new_row, new_col)
                if target is None:
                    moves.append((new_row, new_col))
                elif self.is_enemy(target):
                    moves.append((new_row, new_col))
                    break
                else:
                    break

        return moves