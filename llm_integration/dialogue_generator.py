"""
Dialogue Generator
Generates contextual piece conversations using LLM
"""

from typing import Dict, Optional
from .llm_client import LLMClient
from .prompt_templates import PromptTemplates
from .cache_manager import CacheManager
import config


class DialogueGenerator:
    """Generates contextual dialogue for chess pieces"""

    def __init__(self):
        """Initialize dialogue generator"""
        self.llm_client = LLMClient()
        self.cache_manager = CacheManager()
        self.prompt_templates = PromptTemplates()

        # Statistics
        self.total_generations = 0
        self.cache_hits = 0
        self.fallback_uses = 0

    def generate_piece_dialogue(self, piece, situation: str,
                                context: Dict) -> str:
        """
        Generate dialogue for a piece

        Args:
            piece: Piece object
            situation: Situation type
            context: Dictionary with context information

        Returns:
            Generated dialogue string
        """
        self.total_generations += 1

        # Prepare context with piece information
        full_context = {
            'iq': piece.iq,
            'piece_type': piece.piece_type,
            'position': self._format_position(piece),
            'emotion': piece.current_emotion,
            **context
        }

        # Check cache first
        cache_key_context = {
            'piece_type': piece.piece_type,
            'situation': situation,
            'emotion': piece.current_emotion
        }

        # Build prompt
        prompt = self.prompt_templates.build_prompt(
            piece.piece_type,
            situation,
            **full_context
        )

        # Try cache
        cached_response = self.cache_manager.get(prompt, cache_key_context)
        if cached_response:
            self.cache_hits += 1
            return cached_response

        # Generate with LLM
        if self.llm_client.is_connected():
            response = self.llm_client.generate(prompt)

            if response:
                # Clean and validate response
                response = self._clean_response(response)

                # Cache it
                self.cache_manager.set(prompt, response, cache_key_context)

                return response

        # Fallback to pre-written responses
        self.fallback_uses += 1
        return self.prompt_templates.get_fallback_response(
            situation,
            piece.current_emotion
        )

    def generate_quick_response(self, piece, context: str) -> str:
        """
        Generate a quick response without full context

        Args:
            piece: Piece object
            context: Brief context string

        Returns:
            Generated response
        """
        self.total_generations += 1

        # Build simple prompt
        prompt = self.prompt_templates.build_simple_prompt(
            piece.piece_type,
            piece.iq,
            piece.current_emotion,
            context
        )

        # Try LLM
        if self.llm_client.is_connected():
            response = self.llm_client.generate(prompt)
            if response:
                return self._clean_response(response)

        # Fallback
        self.fallback_uses += 1
        return f"{self._get_emotion_emoji(piece.current_emotion)} Acknowledged."

    def generate_queen_synthesis(self, queen, suggestions: list,
                                 board_eval: float) -> Dict:
        """
        Generate Queen's strategic synthesis

        Args:
            queen: Queen piece object
            suggestions: List of piece suggestions
            board_eval: Board evaluation score

        Returns:
            Dictionary with decision and reasoning
        """
        # Format suggestions
        top_suggestions = "\n".join([
            f"- {s['piece']}: {s['move']} (confidence: {s['confidence']:.2f})"
            for s in suggestions[:5]
        ])

        context = {
            'iq': queen.iq,
            'suggestion_count': len(suggestions),
            'top_suggestions': top_suggestions,
            'evaluation': f"{board_eval:+.2f}",
            'emotion': queen.current_emotion
        }

        prompt = self.prompt_templates.build_prompt(
            'queen',
            'queen_strategy',
            **context
        )

        response = self.llm_client.generate(prompt)

        if response:
            return {
                'reasoning': self._clean_response(response),
                'emotion': queen.current_emotion
            }
        else:
            return {
                'reasoning': "Analyzing all suggestions. Proceeding with optimal strategy.",
                'emotion': 'CONFIDENT'
            }

    def generate_king_validation(self, king, queen_move: str,
                                 queen_reasoning: str, risk_level: float) -> Dict:
        """
        Generate King's approval/denial reasoning

        Args:
            king: King piece object
            queen_move: The move Queen proposed
            queen_reasoning: Queen's reasoning
            risk_level: Risk assessment (0.0 to 1.0)

        Returns:
            Dictionary with decision and reasoning
        """
        context = {
            'iq': king.iq,
            'queen_move': queen_move,
            'queen_reasoning': queen_reasoning,
            'risk_level': f"{risk_level:.2%}",
            'veto_count': king.veto_count,
            'emotion': king.current_emotion
        }

        prompt = self.prompt_templates.build_prompt(
            'king',
            'king_approval',
            **context
        )

        response = self.llm_client.generate(prompt)

        if response:
            return {
                'reasoning': self._clean_response(response),
                'emotion': king.current_emotion
            }
        else:
            if risk_level > 0.7:
                return {
                    'reasoning': "Risk is too high. I must deny this move.",
                    'emotion': 'ANXIOUS'
                }
            else:
                return {
                    'reasoning': "The strategy is sound. Approved.",
                    'emotion': 'CONFIDENT'
                }

    def _format_position(self, piece) -> str:
        """Format piece position as algebraic notation"""
        files = 'abcdefgh'
        ranks = '87654321'
        return f"{files[piece.col]}{ranks[piece.row]}"

    def _clean_response(self, response: str) -> str:
        """Clean and validate LLM response"""
        # Remove quotes if present
        response = response.strip('"\'')

        # Limit length
        if len(response) > 200:
            response = response[:197] + "..."

        # Remove unwanted formatting
        response = response.replace('*', '').replace('_', '')

        return response.strip()

    def _get_emotion_emoji(self, emotion: str) -> str:
        """Get emoji for emotion"""
        emoji_map = {
            'HAPPY': '😊', 'SAD': '😢', 'SCARED': '😰',
            'CONFIDENT': '😤', 'ANGRY': '😠', 'NEUTRAL': '😐',
            'ANXIOUS': '😟', 'PROUD': '😎', 'RESIGNED': '😔'
        }
        return emoji_map.get(emotion, '😐')

    def get_statistics(self) -> Dict:
        """Get generation statistics"""
        cache_stats = self.cache_manager.get_stats()

        return {
            'total_generations': self.total_generations,
            'cache_hits': self.cache_hits,
            'fallback_uses': self.fallback_uses,
            'llm_connected': self.llm_client.is_connected(),
            'cache_stats': cache_stats
        }

    def __repr__(self):
        return f"DialogueGenerator(generations={self.total_generations}, cache_hits={self.cache_hits})"