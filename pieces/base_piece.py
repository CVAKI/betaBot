"""
Base Piece Class
Abstract base class for all chess pieces with AI capabilities
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict
import random
import config


class BasePiece(ABC):
    """Abstract base class for all chess pieces"""

    def __init__(self, color: str, row: int, col: int, piece_type: str, iq: float = None):
        """
        Initialize a chess piece

        Args:
            color: 'white' or 'black'
            row: Starting row position (0-7)
            col: Starting column position (0-7)
            piece_type: Type of piece ('pawn', 'knight', etc.)
            iq: Intelligence quotient (auto-assigned if None)
        """
        self.color = color
        self.row = row
        self.col = col
        self.piece_type = piece_type

        # Assign IQ based on piece type
        if iq is None:
            self.iq = config.get_piece_iq(piece_type, randomize=True)
        else:
            self.iq = iq

        # Movement tracking
        self.has_moved = False
        self.move_count = 0

        # State
        self.is_captured = False
        self.is_selected = False

        # Emotion and personality
        self.current_emotion = 'NEUTRAL'
        self.personality = self._load_personality()

        # AI brain (will be initialized by game manager)
        self.brain = None

        # Communication
        self.message_queue = []

        # Unique identifier
        self.id = f"{color}_{piece_type}_{row}_{col}"

    def _load_personality(self) -> Dict[str, float]:
        """Load personality traits from config"""
        return config.DEFAULT_PERSONALITIES.get(self.piece_type, {
            'confidence': 0.5,
            'leadership': 0.5,
            'aggression': 0.5,
            'caution': 0.5,
            'loyalty': 0.5
        })

    @abstractmethod
    def get_possible_moves(self, board) -> List[Tuple[int, int]]:
        """
        Get all possible moves for this piece (before checking legality)
        Must be implemented by subclasses

        Returns:
            List of (row, col) tuples representing possible destination squares
        """
        pass

    def get_legal_moves(self, board, game_state) -> List[Tuple[int, int]]:
        """
        Get all legal moves (possible moves that don't leave king in check)

        Returns:
            List of (row, col) tuples representing legal moves
        """
        possible_moves = self.get_possible_moves(board)
        legal_moves = []

        # Filter out moves that would leave own king in check
        for move in possible_moves:
            if self._is_move_legal(board, game_state, move):
                legal_moves.append(move)

        return legal_moves

    def _is_move_legal(self, board, game_state, move: Tuple[int, int]) -> bool:
        """Check if a move is legal (doesn't expose king to check)"""
        # This will be implemented with proper check detection
        # For now, accept all possible moves as legal
        return True

    def suggest_move(self, board, game_state) -> Optional[Dict]:
        """
        Use AI brain to suggest a move

        Returns:
            Dictionary with move suggestion and confidence:
            {
                'from': (row, col),
                'to': (row, col),
                'confidence': float,
                'reasoning': str
            }
        """
        if self.brain is None:
            # Fallback: random legal move
            legal_moves = self.get_legal_moves(board, game_state)
            if not legal_moves:
                return None

            chosen_move = random.choice(legal_moves)
            return {
                'from': (self.row, self.col),
                'to': chosen_move,
                'confidence': 0.5,
                'reasoning': "Random move (no AI brain loaded)"
            }

        # Use AI brain to evaluate and suggest move
        return self.brain.suggest_move(board, game_state, self)

    def evaluate_board(self, board) -> float:
        """
        Evaluate the current board position from this piece's perspective

        Returns:
            Score (positive = good for this piece's color)
        """
        if self.brain:
            return self.brain.evaluate_position(board, self.color)

        # Fallback: simple material count
        return board.get_material_count(self.color) - \
            board.get_material_count('black' if self.color == 'white' else 'white')

    def set_emotion(self, emotion: str):
        """Set the current emotion of the piece"""
        valid_emotions = ['HAPPY', 'SAD', 'SCARED', 'CONFIDENT',
                          'ANGRY', 'NEUTRAL', 'ANXIOUS', 'PROUD', 'RESIGNED']
        if emotion in valid_emotions:
            self.current_emotion = emotion

    def get_emotion(self) -> str:
        """Get current emotion"""
        return self.current_emotion

    def generate_dialogue(self, context: str, situation: Dict) -> str:
        """
        Generate contextual dialogue for this piece

        Args:
            context: Situation type ('under_threat', 'sacrifice', etc.)
            situation: Dictionary with game state info

        Returns:
            Dialogue string
        """
        # This will integrate with LLM in full implementation
        # For now, return basic templated responses
        templates = {
            'under_threat': [
                f"I'm in danger! Can anyone help?",
                f"They're targeting me...",
                f"I need support!"
            ],
            'sacrifice': [
                f"For the kingdom!",
                f"My sacrifice won't be in vain",
                f"It's been an honor serving"
            ],
            'capture': [
                f"Got one!",
                f"Enemy piece eliminated",
                f"Victory is ours!"
            ],
            'support': [
                f"I've got your back",
                f"Together we're stronger",
                f"I'll protect you"
            ]
        }

        responses = templates.get(context, ["..."])
        return random.choice(responses)

    def send_message(self, recipient, message: str):
        """Send a message to another piece or the command hierarchy"""
        # Will be handled by communication hub
        pass

    def receive_message(self, sender, message: str):
        """Receive a message from another piece"""
        self.message_queue.append({
            'sender': sender,
            'message': message,
            'emotion': sender.get_emotion() if hasattr(sender, 'get_emotion') else 'NEUTRAL'
        })

    def get_symbol(self) -> str:
        """Get chess notation symbol for this piece"""
        symbols = {
            'king': 'K',
            'queen': 'Q',
            'rook': 'R',
            'bishop': 'B',
            'knight': 'N',
            'pawn': 'P'
        }
        symbol = symbols.get(self.piece_type, '?')
        return symbol if self.color == 'white' else symbol.lower()

    def get_position(self) -> Tuple[int, int]:
        """Get current position"""
        return (self.row, self.col)

    def set_position(self, row: int, col: int):
        """Set position"""
        self.row = row
        self.col = col

    def get_value(self) -> int:
        """Get material value of this piece"""
        return config.PIECE_VALUES.get(self.piece_type, 0)

    def is_enemy(self, other_piece: 'BasePiece') -> bool:
        """Check if another piece is an enemy"""
        return other_piece and other_piece.color != self.color

    def is_ally(self, other_piece: 'BasePiece') -> bool:
        """Check if another piece is an ally"""
        return other_piece and other_piece.color == self.color

    def distance_to(self, row: int, col: int) -> int:
        """Calculate Manhattan distance to a square"""
        return abs(self.row - row) + abs(self.col - col)

    def is_adjacent_to(self, row: int, col: int) -> bool:
        """Check if a square is adjacent (for communication)"""
        return max(abs(self.row - row), abs(self.col - col)) <= config.COMMUNICATION_RADIUS

    def mark_moved(self):
        """Mark that this piece has moved"""
        self.has_moved = True
        self.move_count += 1

    def __repr__(self):
        """String representation"""
        pos = f"{'abcdefgh'[self.col]}{'87654321'[self.row]}"
        return f"{self.color.capitalize()} {self.piece_type.capitalize()} at {pos} (IQ: {self.iq:.1f})"

    def __str__(self):
        """User-friendly string"""
        return f"{self.color} {self.piece_type}"

    def to_dict(self) -> Dict:
        """Convert piece to dictionary (for serialization)"""
        return {
            'id': self.id,
            'color': self.color,
            'piece_type': self.piece_type,
            'position': [self.row, self.col],
            'iq': self.iq,
            'has_moved': self.has_moved,
            'move_count': self.move_count,
            'is_captured': self.is_captured,
            'emotion': self.current_emotion,
            'personality': self.personality
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'BasePiece':
        """Create piece from dictionary"""
        # This will be implemented when we have all piece subclasses
        pass