"""
Enhanced AI Strategy & Decision Pipeline
Implements intelligent move evaluation with king safety priority
"""

import random
from typing import List, Dict, Tuple, Optional
import config


class EnhancedMoveEvaluator:
    """Advanced move evaluation with strategic priorities"""

    # Piece position tables for strategic positioning
    PAWN_TABLE = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [5, 5, 10, 25, 25, 10, 5, 5],
        [0, 0, 0, 20, 20, 0, 0, 0],
        [5, -5, -10, 0, 0, -10, -5, 5],
        [5, 10, 10, -20, -20, 10, 10, 5],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]

    KNIGHT_TABLE = [
        [-50, -40, -30, -30, -30, -30, -40, -50],
        [-40, -20, 0, 0, 0, 0, -20, -40],
        [-30, 0, 10, 15, 15, 10, 0, -30],
        [-30, 5, 15, 20, 20, 15, 5, -30],
        [-30, 0, 15, 20, 20, 15, 0, -30],
        [-30, 5, 10, 15, 15, 10, 5, -30],
        [-40, -20, 0, 5, 5, 0, -20, -40],
        [-50, -40, -30, -30, -30, -30, -40, -50]
    ]

    KING_MIDDLE_TABLE = [
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-20, -30, -30, -40, -40, -30, -30, -20],
        [-10, -20, -20, -20, -20, -20, -20, -10],
        [20, 20, 0, 0, 0, 0, 20, 20],
        [20, 30, 10, 0, 0, 10, 30, 20]
    ]

    @staticmethod
    def evaluate_move(board, piece, move: Tuple[int, int], game_state) -> float:
        """
        Comprehensive move evaluation

        Returns:
            Score (higher is better)
        """
        score = 0.0
        to_row, to_col = move

        # 1. Capture evaluation (HIGHEST PRIORITY)
        target = board.get_piece_at(to_row, to_col)
        if target:
            # Huge bonus for captures
            capture_value = target.get_value() * 100
            piece_value = piece.get_value()

            # Even better if it's a favorable trade
            if target.get_value() >= piece_value:
                score += capture_value * 2
            else:
                score += capture_value

        # 2. King safety (CRITICAL)
        king = board.find_king(piece.color)
        if king:
            # Check if this move protects the king
            king_distance_before = abs(piece.row - king.row) + abs(piece.col - king.col)
            king_distance_after = abs(to_row - king.row) + abs(to_col - king.col)

            # Check if king is under attack
            if EnhancedMoveEvaluator._is_king_threatened(board, king):
                # Heavily prioritize moves that defend the king
                if king_distance_after < king_distance_before:
                    score += 500  # HUGE bonus for defending threatened king

                # Check if this move blocks an attack on king
                if EnhancedMoveEvaluator._blocks_attack_on_king(board, piece, move, king):
                    score += 800  # Even bigger bonus for blocking

        # 3. Center control
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        if (to_row, to_col) in center_squares:
            score += 30

        # 4. Position-based evaluation
        if piece.piece_type == 'pawn':
            pos_score = EnhancedMoveEvaluator.PAWN_TABLE[to_row][to_col]
            score += pos_score
        elif piece.piece_type == 'knight':
            pos_score = EnhancedMoveEvaluator.KNIGHT_TABLE[to_row][to_col]
            score += pos_score
        elif piece.piece_type == 'king':
            # King should stay safe in middle game
            if game_state.move_count < 40:
                pos_score = EnhancedMoveEvaluator.KING_MIDDLE_TABLE[to_row][to_col]
                score += pos_score

        # 5. Mobility (more squares controlled is better)
        # Simulate the move to see how many squares we'd control
        score += EnhancedMoveEvaluator._calculate_mobility_after_move(board, piece, move) * 5

        # 6. Attack enemy king
        enemy_color = 'black' if piece.color == 'white' else 'white'
        enemy_king = board.find_king(enemy_color)
        if enemy_king:
            # Bonus for getting closer to enemy king
            enemy_king_dist = abs(to_row - enemy_king.row) + abs(to_col - enemy_king.col)
            if enemy_king_dist <= 2:
                score += 100  # Close to enemy king

        # 7. Penalize moves that leave piece undefended
        if not EnhancedMoveEvaluator._is_defended_after_move(board, piece, move):
            score -= piece.get_value() * 20

        return score

    @staticmethod
    def _is_king_threatened(board, king) -> bool:
        """Check if king is under immediate threat"""
        enemy_color = 'black' if king.color == 'white' else 'white'
        enemy_pieces = board.get_all_pieces(enemy_color)

        for enemy in enemy_pieces:
            if enemy.is_captured:
                continue
            moves = enemy.get_possible_moves(board)
            if (king.row, king.col) in moves:
                return True
        return False

    @staticmethod
    def _blocks_attack_on_king(board, piece, move, king) -> bool:
        """Check if move blocks an attack on the king"""
        # This is a simplified check
        to_row, to_col = move

        # Check if new position is between an attacker and king
        enemy_color = 'black' if king.color == 'white' else 'white'
        enemy_pieces = board.get_all_pieces(enemy_color)

        for enemy in enemy_pieces:
            if enemy.is_captured:
                continue
            # Check if enemy can attack king
            moves = enemy.get_possible_moves(board)
            if (king.row, king.col) in moves:
                # Check if our move blocks the line
                if EnhancedMoveEvaluator._is_on_line(enemy.row, enemy.col, to_row, to_col, king.row, king.col):
                    return True
        return False

    @staticmethod
    def _is_on_line(x1, y1, x2, y2, x3, y3) -> bool:
        """Check if point (x2,y2) is on line between (x1,y1) and (x3,y3)"""
        # Simplified - just check if it's between them
        if x1 == x3:  # Vertical line
            return x2 == x1 and min(y1, y3) <= y2 <= max(y1, y3)
        if y1 == y3:  # Horizontal line
            return y2 == y1 and min(x1, x3) <= x2 <= max(x1, x3)
        if abs(x3 - x1) == abs(y3 - y1):  # Diagonal
            return abs(x2 - x1) == abs(y2 - y1) and min(x1, x3) <= x2 <= max(x1, x3)
        return False

    @staticmethod
    def _calculate_mobility_after_move(board, piece, move) -> int:
        """Calculate how many squares piece would control after move"""
        # Simplified calculation
        to_row, to_col = move

        # Count squares piece could move to from new position
        directions = {
            'pawn': [(1, 0), (-1, 0)],
            'knight': [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)],
            'bishop': [(-1, -1), (-1, 1), (1, -1), (1, 1)],
            'rook': [(-1, 0), (1, 0), (0, -1), (0, 1)],
            'queen': [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)],
            'king': [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        }

        piece_dirs = directions.get(piece.piece_type, [])
        controlled = 0

        for dr, dc in piece_dirs:
            new_r, new_c = to_row + dr, to_col + dc
            if 0 <= new_r < 8 and 0 <= new_c < 8:
                controlled += 1

        return controlled

    @staticmethod
    def _is_defended_after_move(board, piece, move) -> bool:
        """Check if piece would be defended after moving"""
        to_row, to_col = move

        # Check if any friendly piece can reach this square
        friendly_pieces = board.get_all_pieces(piece.color)

        for ally in friendly_pieces:
            if ally == piece or ally.is_captured:
                continue
            moves = ally.get_possible_moves(board)
            if (to_row, to_col) in moves:
                return True
        return False


class SmartDecisionPipeline:
    """Intelligent decision-making for piece moves"""

    def __init__(self):
        self.evaluator = EnhancedMoveEvaluator()

    def get_best_move_for_piece(self, piece, board, game_state) -> Optional[Dict]:
        """
        Get the best move for a piece using strategic evaluation
        """
        legal_moves = piece.get_legal_moves(board, game_state)

        if not legal_moves:
            return None

        # Evaluate all moves
        move_scores = []
        for move in legal_moves:
            score = self.evaluator.evaluate_move(board, piece, move, game_state)
            move_scores.append({
                'from': (piece.row, piece.col),
                'to': move,
                'score': score,
                'piece': piece
            })

        # Sort by score (descending)
        move_scores.sort(key=lambda x: x['score'], reverse=True)

        # Return best move
        best = move_scores[0]

        # Add confidence based on score difference
        if len(move_scores) > 1:
            score_diff = best['score'] - move_scores[1]['score']
            confidence = min(0.99, 0.5 + (score_diff / 200))
        else:
            confidence = 0.8

        return {
            'from': best['from'],
            'to': best['to'],
            'confidence': confidence,
            'score': best['score'],
            'reasoning': self._generate_reasoning(best, board)
        }

    def _generate_reasoning(self, move_data, board) -> str:
        """Generate human-readable reasoning for a move"""
        to_row, to_col = move_data['to']
        target = board.get_piece_at(to_row, to_col)

        if target:
            return f"Capturing {target.piece_type} at {board.get_square_name(to_row, to_col)}"
        elif move_data['score'] > 500:
            return f"Defending our king by moving to {board.get_square_name(to_row, to_col)}"
        elif move_data['score'] > 100:
            return f"Strong tactical move to {board.get_square_name(to_row, to_col)}"
        else:
            return f"Moving to {board.get_square_name(to_row, to_col)}"


# Update the base_piece.py suggest_move method to use this
def enhanced_suggest_move(piece, board, game_state) -> Optional[Dict]:
    """Enhanced move suggestion using smart evaluation"""
    pipeline = SmartDecisionPipeline()
    return pipeline.get_best_move_for_piece(piece, board, game_state)