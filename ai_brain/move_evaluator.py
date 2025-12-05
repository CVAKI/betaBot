"""
Move Evaluator - Board Position Evaluation Utilities
Provides evaluation functions for board positions and moves
"""

import config


class MoveEvaluator:
    """Evaluates board positions and move quality"""

    @staticmethod
    def evaluate_board(board, color):
        """
        Calculate overall board evaluation score

        Args:
            board: Board object
            color: 'white' or 'black'

        Returns:
            float: Evaluation score (positive = good for color)
        """
        score = 0.0

        # Material count
        score += MoveEvaluator.calculate_material(board, color)

        # Positional factors
        score += MoveEvaluator.assess_piece_activity(board, color)
        score += MoveEvaluator.assess_king_safety(board, color)
        score += MoveEvaluator.assess_pawn_structure(board, color)
        score += MoveEvaluator.assess_center_control(board, color)

        return score

    @staticmethod
    def calculate_material(board, color):
        """Calculate material advantage"""
        own_material = board.get_material_count(color)
        enemy_color = 'black' if color == 'white' else 'white'
        enemy_material = board.get_material_count(enemy_color)
        return own_material - enemy_material

    @staticmethod
    def assess_piece_activity(board, color):
        """Assess how active pieces are"""
        score = 0.0
        pieces = board.get_all_pieces(color)

        for piece in pieces:
            # Reward pieces for having more possible moves
            moves = piece.get_possible_moves(board)
            score += len(moves) * 0.1

            # Reward pieces for being closer to center
            center_distance = abs(piece.row - 3.5) + abs(piece.col - 3.5)
            score += (7 - center_distance) * 0.05

        return score

    @staticmethod
    def assess_king_safety(board, color):
        """Assess king safety"""
        score = 0.0
        king = board.find_king(color)

        if not king:
            return -100.0  # King missing = catastrophic

        # Penalize exposed king in middle game
        if board.move_count > 10:
            # King should be castled or in corner
            if king.col in [0, 1, 6, 7]:
                score += 2.0
            else:
                score -= 1.0

        # Check if king has pieces nearby for protection
        nearby_allies = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = king.row + dr, king.col + dc
                if board.is_valid_position(r, c):
                    piece = board.get_piece_at(r, c)
                    if piece and piece.color == color:
                        nearby_allies += 1

        score += nearby_allies * 0.5

        return score

    @staticmethod
    def assess_pawn_structure(board, color):
        """Assess pawn structure quality"""
        score = 0.0
        pawns = board.get_piece_by_type_and_color('pawn', color)

        # Reward advanced pawns
        for pawn in pawns:
            if color == 'white':
                advancement = 6 - pawn.row
            else:
                advancement = pawn.row - 1
            score += advancement * 0.1

        # Penalize doubled pawns (same file)
        files = {}
        for pawn in pawns:
            files[pawn.col] = files.get(pawn.col, 0) + 1
        for count in files.values():
            if count > 1:
                score -= 0.5 * (count - 1)

        return score

    @staticmethod
    def assess_center_control(board, color):
        """Assess control of center squares"""
        score = 0.0
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]

        for row, col in center_squares:
            piece = board.get_piece_at(row, col)
            if piece:
                if piece.color == color:
                    score += 0.5
                else:
                    score -= 0.3

        return score

    @staticmethod
    def evaluate_move_quality(move, board, game_state):
        """
        Evaluate the quality of a specific move

        Returns:
            float: Move quality score
        """
        score = 0.0

        from_row, from_col = move['from']
        to_row, to_col = move['to']

        # Check if it's a capture
        target = board.get_piece_at(to_row, to_col)
        if target:
            # Reward captures based on value difference
            piece = board.get_piece_at(from_row, from_col)
            score += target.get_value() - piece.get_value() * 0.1

        # Reward moves toward center in opening
        if board.move_count < 10:
            center_distance_before = abs(from_row - 3.5) + abs(from_col - 3.5)
            center_distance_after = abs(to_row - 3.5) + abs(to_col - 3.5)
            if center_distance_after < center_distance_before:
                score += 0.5

        return score