"""
Proximity Manager
Determines which pieces can communicate based on spatial relationships
"""

import config
from typing import List, Set, Tuple


class ProximityManager:
    """Manages proximity-based communication rules"""

    def __init__(self, communication_radius: int = None):
        """
        Initialize proximity manager

        Args:
            communication_radius: Maximum distance for direct communication
        """
        self.communication_radius = communication_radius or config.COMMUNICATION_RADIUS

    def are_pieces_adjacent(self, piece1, piece2) -> bool:
        """
        Check if two pieces are adjacent (including diagonally)

        Returns:
            True if pieces are within 1 square of each other
        """
        row_diff = abs(piece1.row - piece2.row)
        col_diff = abs(piece1.col - piece2.col)
        return max(row_diff, col_diff) <= 1

    def get_distance(self, piece1, piece2) -> int:
        """
        Calculate Chebyshev distance (chessboard distance) between pieces

        Returns:
            Maximum of row difference and column difference
        """
        row_diff = abs(piece1.row - piece2.row)
        col_diff = abs(piece1.col - piece2.col)
        return max(row_diff, col_diff)

    def can_communicate(self, piece1, piece2) -> bool:
        """
        Check if two pieces can directly communicate

        Returns:
            True if within communication radius
        """
        # Queen and King can always communicate with everyone
        if piece1.piece_type in ['queen', 'king'] or piece2.piece_type in ['queen', 'king']:
            return True

        # Otherwise check distance
        distance = self.get_distance(piece1, piece2)
        return distance <= self.communication_radius

    def get_nearby_pieces(self, piece, all_pieces: List,
                          same_color_only: bool = True) -> List:
        """
        Get all pieces within communication range

        Args:
            piece: The piece to check from
            all_pieces: List of all pieces on board
            same_color_only: Only return pieces of same color

        Returns:
            List of pieces within communication range
        """
        nearby = []

        for other_piece in all_pieces:
            # Skip self
            if other_piece == piece:
                continue

            # Skip captured pieces
            if other_piece.is_captured:
                continue

            # Filter by color if requested
            if same_color_only and other_piece.color != piece.color:
                continue

            # Check if in range
            if self.can_communicate(piece, other_piece):
                nearby.append(other_piece)

        return nearby

    def get_pieces_in_radius(self, piece, all_pieces: List,
                             radius: int) -> List:
        """
        Get all pieces within specific radius

        Args:
            piece: Center piece
            all_pieces: All pieces to check
            radius: Maximum distance

        Returns:
            List of pieces within radius
        """
        in_radius = []

        for other_piece in all_pieces:
            if other_piece == piece or other_piece.is_captured:
                continue

            if self.get_distance(piece, other_piece) <= radius:
                in_radius.append(other_piece)

        return in_radius

    def get_communication_groups(self, pieces: List) -> List[Set]:
        """
        Identify groups of pieces that can communicate with each other

        Returns:
            List of sets, each containing piece IDs that can communicate
        """
        groups = []
        processed = set()

        for piece in pieces:
            if piece.id in processed or piece.is_captured:
                continue

            # Start new group
            group = {piece.id}
            queue = [piece]

            while queue:
                current = queue.pop(0)
                nearby = self.get_nearby_pieces(current, pieces)

                for nearby_piece in nearby:
                    if nearby_piece.id not in group:
                        group.add(nearby_piece.id)
                        queue.append(nearby_piece)

            groups.append(group)
            processed.update(group)

        return groups

    def can_relay_message(self, sender, recipient, all_pieces: List) -> bool:
        """
        Check if a message can be relayed through other pieces

        Returns:
            True if there's a communication path between sender and recipient
        """
        # Direct communication
        if self.can_communicate(sender, recipient):
            return True

        # Check for relay path
        visited = set()
        queue = [(sender, 0)]  # (piece, depth)
        max_depth = 5  # Maximum relay chain length

        while queue:
            current, depth = queue.pop(0)

            if depth > max_depth:
                continue

            if current.id in visited:
                continue
            visited.add(current.id)

            # Check nearby pieces
            nearby = self.get_nearby_pieces(current, all_pieces)
            for nearby_piece in nearby:
                if nearby_piece == recipient:
                    return True
                if nearby_piece.id not in visited:
                    queue.append((nearby_piece, depth + 1))

        return False

    def get_communication_map(self, pieces: List) -> dict:
        """
        Create a map of which pieces can communicate with which

        Returns:
            Dictionary mapping piece IDs to lists of reachable piece IDs
        """
        comm_map = {}

        for piece in pieces:
            if piece.is_captured:
                continue

            reachable = []
            for other in pieces:
                if other != piece and not other.is_captured:
                    if self.can_communicate(piece, other):
                        reachable.append(other.id)

            comm_map[piece.id] = reachable

        return comm_map

    def format_proximity_report(self, piece, all_pieces: List) -> str:
        """
        Generate a text report of nearby pieces

        Returns:
            Formatted string describing nearby pieces
        """
        nearby = self.get_nearby_pieces(piece, all_pieces, same_color_only=False)

        if not nearby:
            return f"{piece.id} is isolated - no nearby pieces"

        allies = [p for p in nearby if p.color == piece.color]
        enemies = [p for p in nearby if p.color != piece.color]

        report = f"{piece.id} proximity:\n"
        if allies:
            report += f"  Allies: {', '.join(p.id for p in allies)}\n"
        if enemies:
            report += f"  Enemies: {', '.join(p.id for p in enemies)}\n"

        return report.strip()