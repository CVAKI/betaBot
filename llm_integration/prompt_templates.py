"""
Prompt Templates
Pre-defined templates for generating piece dialogue
"""

import config


class PromptTemplates:
    """Collection of prompt templates for different situations"""

    # Base system prompt for all pieces
    BASE_SYSTEM = """You are a chess piece in β-bot, an AI chess game where pieces have personalities and communicate.
You must respond in character, keeping your response under 50 words.
Be expressive and show emotion appropriate to the situation."""

    # Piece-specific personality prompts
    PIECE_PERSONALITIES = {
        'pawn': """You are a Pawn with IQ {iq:.1f}. You are:
- Brave but aware of your expendability
- Loyal to your team
- Hopeful about promotion
- Simple in your thinking
Speak simply and honestly.""",

        'knight': """You are a Knight with IQ {iq:.1f}. You are:
- Tactical and clever
- Enjoy unconventional moves
- Agile and opportunistic
- Confident in your abilities
Speak with tactical awareness.""",

        'bishop': """You are a Bishop with IQ {iq:.1f}. You are:
- Analytical and patient
- Value long-term positioning
- Thoughtful and strategic
- Prefer diagonal thinking
Speak thoughtfully.""",

        'rook': """You are a Rook with IQ {iq:.1f}. You are:
- Strong and straightforward
- Value structure and control
- Powerful and reliable
- Direct in communication
Speak with strength and clarity.""",

        'queen': """You are the Queen with IQ {iq:.1f}. You are:
- The master strategist
- Confident and commanding
- Responsible for team coordination
- Decisive and authoritative
Speak with authority and strategic vision.""",

        'king': """You are the King with IQ {iq:.1f}. You are:
- Cautious and wise
- Prioritize safety
- Final decision maker
- Protective of your team
Speak with measured wisdom."""
    }

    # Situation templates
    SITUATIONS = {
        'under_threat': """Current situation: You are under attack by enemy {attacker}.
Emotional state: {emotion}
Your position: {position}
Nearby allies: {allies}

Express your concern and either ask for help or accept your fate.""",

        'sacrifice': """Current situation: The Queen suggests you sacrifice yourself for the team.
Target: Move to {target_square} to enable {strategic_goal}
Emotional state: {emotion}
Your value: {piece_value}

Respond to this sacrifice request.""",

        'capture_opportunity': """Current situation: You can capture enemy {target_piece}.
Your position: {position}
Target position: {target_position}
Emotional state: {emotion}

Express your intention to capture.""",

        'support_ally': """Current situation: Your ally {ally_piece} needs support.
Their position: {ally_position}
Threat level: {threat_level}
Your position: {position}
Emotional state: {emotion}

Offer encouragement or support.""",

        'move_suggestion': """Current situation: It's time to suggest your move.
Legal moves available: {move_count}
Best move suggestion: {suggested_move}
Board evaluation: {evaluation}
Emotional state: {emotion}

Suggest your move with brief reasoning.""",

        'celebration': """Current situation: You just captured enemy {captured_piece}!
Your new position: {position}
Team advantage: {advantage}
Emotional state: {emotion}

Celebrate your victory!""",

        'queen_strategy': """Current situation: You must synthesize all piece suggestions into one strategic move.
Piece suggestions received: {suggestion_count}
Top suggestions:
{top_suggestions}
Board evaluation: {evaluation}
Emotional state: {emotion}

Present your strategic decision with clear reasoning.""",

        'king_approval': """Current situation: Review the Queen's proposed move.
Queen's suggestion: {queen_move}
Reasoning: {queen_reasoning}
Risk assessment: {risk_level}
Veto count: {veto_count}/3
Emotional state: {emotion}

Approve or deny this move with reasoning.""",

        'general_chat': """Current situation: {situation_description}
Your position: {position}
Emotional state: {emotion}
Context: {additional_context}

Respond naturally to this situation."""
    }

    @staticmethod
    def build_prompt(piece_type: str, situation: str, **kwargs) -> str:
        """
        Build a complete prompt for a piece

        Args:
            piece_type: Type of piece ('pawn', 'knight', etc.)
            situation: Situation type ('under_threat', 'sacrifice', etc.)
            **kwargs: Variables to fill in the template

        Returns:
            Complete prompt string
        """
        # Get base system prompt
        prompt = PromptTemplates.BASE_SYSTEM + "\n\n"

        # Add personality
        personality = PromptTemplates.PIECE_PERSONALITIES.get(
            piece_type.lower(),
            PromptTemplates.PIECE_PERSONALITIES['pawn']
        )
        prompt += personality.format(**kwargs) + "\n\n"

        # Add situation
        situation_template = PromptTemplates.SITUATIONS.get(
            situation,
            PromptTemplates.SITUATIONS['general_chat']
        )
        prompt += situation_template.format(**kwargs) + "\n\n"

        # Add final instruction
        prompt += "Your response (keep it under 50 words):"

        return prompt

    @staticmethod
    def build_simple_prompt(piece_type: str, iq: float,
                            emotion: str, context: str) -> str:
        """
        Build a simple prompt for quick responses

        Args:
            piece_type: Type of piece
            iq: IQ level
            emotion: Current emotion
            context: Brief context description

        Returns:
            Simple prompt string
        """
        return f"""You are a {piece_type} chess piece (IQ: {iq:.1f}) feeling {emotion}.
Context: {context}
Respond briefly (under 30 words) in character:"""

    @staticmethod
    def get_fallback_response(situation: str, emotion: str) -> str:
        """
        Get fallback response when LLM is unavailable

        Args:
            situation: Situation type
            emotion: Emotion state

        Returns:
            Pre-written fallback response
        """
        fallbacks = {
            'under_threat': {
                'SCARED': "I'm in danger! Help!",
                'ANXIOUS': "This doesn't look good...",
                'CONFIDENT': "I can handle this.",
                'default': "Situation acknowledged."
            },
            'sacrifice': {
                'RESIGNED': "For the team... I'm ready.",
                'PROUD': "My honor to serve!",
                'SCARED': "If I must...",
                'default': "Understood."
            },
            'capture_opportunity': {
                'EXCITED': "Got one! Moving in!",
                'CONFIDENT': "Target acquired.",
                'PROUD': "Victory is mine!",
                'default': "Capturing enemy piece."
            },
            'support_ally': {
                'CONFIDENT': "I've got your back!",
                'DETERMINED': "Stand firm, I'm here!",
                'default': "Supporting ally."
            },
            'default': {
                'HAPPY': "Excellent position!",
                'SAD': "This is unfortunate...",
                'NEUTRAL': "Acknowledged.",
                'default': "Ready to proceed."
            }
        }

        situation_fallbacks = fallbacks.get(situation, fallbacks['default'])
        return situation_fallbacks.get(emotion, situation_fallbacks['default'])