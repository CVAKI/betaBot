from .base_piece import BasePiece


class King(BasePiece):
    def __init__(self, color, row, col):
        super().__init__(color, row, col, 'king')
        self.veto_count = 0

    def get_possible_moves(self, board):
        moves = []
        # One square in any direction
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = self.row + dr, self.col + dc
                if board.is_valid_position(new_row, new_col):
                    target = board.get_piece_at(new_row, new_col)
                    if target is None or self.is_enemy(target):
                        moves.append((new_row, new_col))
        return moves

    def validate_queen_decision(self, queen_move, board, game_state):
        # King's approval/veto logic
        risk_level = self._assess_risk(queen_move, board)

        if risk_level > 0.7 and self.veto_count < 3:
            self.veto_count += 1
            return {'approved': False, 'reason': 'Too risky'}

        return {'approved': True, 'reason': 'Acceptable risk'}