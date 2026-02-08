"""
Pieces Module
Exports all chess piece classes
"""

from pieces.base_piece import BasePiece
from pieces.pawn import Pawn
from pieces.knight import Knight
from pieces.bishop import Bishop
from pieces.rook import Rook
from pieces.queen import Queen
from pieces.king import King

__all__ = [
    'BasePiece',
    'Pawn',
    'Knight',
    'Bishop',
    'Rook',
    'Queen',
    'King'
]