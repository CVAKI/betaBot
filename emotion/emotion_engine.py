"""
Emotion Engine - Determines piece emotions based on game state
"""

from .emotion_types import Emotion, EmotionContext
import config


class EmotionEngine:
    """Analyzes game state and assigns emotions to pieces"""

    def __init__(self):
        self.emotion_history = {}  # Track emotion changes

    def determine_emotion(self, piece, board, game_state) -> str:
        """
        Determine appropriate emotion for a piece

        Returns:
            Emotion name as string
        """
        # Check various threat levels and situations
        threat_level = self._calculate_threat_level(piece, board)
        support_level = self._calculate_support_level(piece, board)
        position_quality = self._evaluate_position(piece, board)

        # Determine emotion based on situation
        if threat_level > 0.8:
            return 'SCARED'
        elif threat_level > 0.5 and support_level < 0.3:
            return 'ANXIOUS'
        elif support_level > 0.7:
            return 'CONFIDENT'
        elif self._is_isolated(piece, board):
            return 'ANXIOUS'
        elif position_quality > 0.7:
            return 'PROUD'
        elif self._recently_captured(piece):
            return 'HAPPY'
        else:
            return 'NEUTRAL'

    def _calculate_threat_level(self, piece, board) -> float:
        """Calculate how threatened a piece is (0.0 to 1.0)"""
        threat = 0.0

        # Check if piece is under attack
        attackers = self._get_attackers(piece, board)
        defenders = self._get_defenders(piece, board)

        if attackers:
            # Normalize by piece value
            attacker_value = sum(a.get_value() for a in attackers)
            defender_value = sum(d.get_value() for d in defenders)
            piece_value = piece.get_value()

            if defender_value < attacker_value:
                threat = min(1.0, (attacker_value - defender_value) / 10.0)

            # Higher value pieces are more scared when threatened
            if piece_value >= 5:  # Rook or Queen
                threat *= 1.5

        return min(1.0, threat)

    def _calculate_support_level(self, piece, board) -> float:
        """Calculate how well supported a piece is (0.0 to 1.0)"""
        defenders = self._get_defenders(piece, board)
        nearby_allies = self._count_nearby_allies(piece, board)

        support = len(defenders) * 0.3 + nearby_allies * 0.1
        return min(1.0, support)

    def _evaluate_position(self, piece, board) -> float:
        """Evaluate how good a piece's position is (0.0 to 1.0)"""
        score = 0.5  # Base neutral score

        # Center control bonus
        center_distance = abs(piece.row - 3.5) + abs(piece.col - 3.5)
        score += (7 - center_distance) * 0.05

        # Mobility bonus
        legal_moves = piece.get_possible_moves(board)
        score += len(legal_moves) * 0.02

        return min(1.0, score)

    def _is_isolated(self, piece, board) -> bool:
        """Check if piece is isolated from teammates"""
        nearby_allies = self._count_nearby_allies(piece, board)
        return nearby_allies == 0

    def _get_attackers(self, piece, board) -> list:
        """Get enemy pieces attacking this piece"""
        attackers = []
        enemy_color = 'black' if piece.color == 'white' else 'white'
        enemy_pieces = board.get_all_pieces(enemy_color)

        for enemy in enemy_pieces:
            possible_moves = enemy.get_possible_moves(board)
            if (piece.row, piece.col) in possible_moves:
                attackers.append(enemy)

        return attackers

    def _get_defenders(self, piece, board) -> list:
        """Get friendly pieces defending this piece"""
        defenders = []
        friendly_pieces = board.get_all_pieces(piece.color)

        for ally in friendly_pieces:
            if ally == piece:
                continue
            possible_moves = ally.get_possible_moves(board)
            if (piece.row, piece.col) in possible_moves:
                defenders.append(ally)

        return defenders

    def _count_nearby_allies(self, piece, board, radius: int = 2) -> int:
        """Count friendly pieces within radius"""
        count = 0
        friendly_pieces = board.get_all_pieces(piece.color)

        for ally in friendly_pieces:
            if ally == piece or ally.is_captured:
                continue
            distance = piece.distance_to(ally.row, ally.col)
            if distance <= radius:
                count += 1

        return count

    def _recently_captured(self, piece) -> bool:
        """Check if piece recently captured an enemy"""
        # This would need move history tracking
        # Placeholder for now
        return False

    def update_all_emotions(self, board, game_state):
        """Update emotions for all pieces on the board"""
        all_pieces = board.get_all_pieces()

        for piece in all_pieces:
            if not piece.is_captured:
                new_emotion = self.determine_emotion(piece, board, game_state)
                piece.set_emotion(new_emotion)

                # Track emotion history
                if piece.id not in self.emotion_history:
                    self.emotion_history[piece.id] = []
                self.emotion_history[piece.id].append(new_emotion)