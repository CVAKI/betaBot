"""
Active LLM Dialogue System with Proximity Chat
Real-time piece conversations using Google Gemini
"""

import google.generativeai as genai
import time
from typing import Dict, List, Optional
import config
from communication.message import Message
from datetime import datetime


class ActiveDialogueSystem:
    """Manages real-time piece conversations"""

    def __init__(self):
        # Initialize Gemini
        self.api_key = config.GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.generation_config = {
                'temperature': 0.9,
                'max_output_tokens': 100,
            }
        else:
            self.model = None

        self.message_queue = []
        self.last_generation_time = 0
        self.min_generation_interval = 2.0  # Minimum seconds between generations

    def generate_piece_reaction(self, piece, situation: str, context: Dict) -> str:
        """
        Generate immediate reaction from a piece

        Args:
            piece: The piece object
            situation: Type of situation (capture, threat, move, etc.)
            context: Additional context information
        """
        # Check rate limiting
        current_time = time.time()
        if current_time - self.last_generation_time < self.min_generation_interval:
            return self._get_quick_fallback(piece, situation)

        if not self.model:
            return self._get_quick_fallback(piece, situation)

        try:
            prompt = self._build_reaction_prompt(piece, situation, context)

            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            self.last_generation_time = current_time

            if response and response.text:
                return self._clean_response(response.text)
            else:
                return self._get_quick_fallback(piece, situation)

        except Exception as e:
            print(f"LLM generation error: {e}")
            return self._get_quick_fallback(piece, situation)

    def _build_reaction_prompt(self, piece, situation: str, context: Dict) -> str:
        """Build prompt for piece reaction"""

        emotion = piece.current_emotion
        iq = piece.iq
        piece_type = piece.piece_type

        # Build context-aware prompt
        prompt = f"""You are a {piece_type} chess piece (IQ: {iq:.1f}) feeling {emotion}.

Situation: {situation}
"""

        if 'captured_piece' in context:
            prompt += f"You just captured an enemy {context['captured_piece']}!\n"
        if 'threat_piece' in context:
            prompt += f"You're being threatened by {context['threat_piece']}!\n"
        if 'ally_nearby' in context:
            prompt += f"Your ally {context['ally_nearby']} is nearby.\n"
        if 'board_eval' in context:
            prompt += f"Team status: {context['board_eval']}\n"

        prompt += """
Respond in character with ONE SHORT sentence (max 15 words).
Show your emotion and personality.
DO NOT use quotes or asterisks.
Just the raw dialogue:"""

        return prompt

    def generate_proximity_chat(self, piece1, piece2, situation: str) -> Optional[str]:
        """
        Generate conversation between two nearby pieces

        Returns:
            Dialogue from piece1 to piece2
        """
        if not self.model:
            return None

        try:
            prompt = f"""You are a {piece1.piece_type} (IQ {piece1.iq:.1f}) talking to a nearby {piece2.piece_type}.

Situation: {situation}
Your emotion: {piece1.current_emotion}
Their emotion: {piece2.current_emotion}

Say ONE SHORT sentence to them (max 12 words).
Be natural and in-character:"""

            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            if response and response.text:
                return self._clean_response(response.text)

        except Exception as e:
            print(f"Proximity chat error: {e}")

        return None

    def generate_queen_synthesis(self, queen, piece_suggestions: List[Dict], board_eval: float) -> str:
        """Generate Queen's strategic decision"""

        if not self.model:
            return "I've analyzed all suggestions. Proceeding with optimal strategy."

        try:
            # Format suggestions
            suggestions_text = "\n".join([
                f"- {s['piece'].piece_type} suggests moving to {s['to']}: {s.get('reasoning', 'tactical move')}"
                for s in piece_suggestions[:5]
            ])

            prompt = f"""You are the Queen (IQ 9.5) commanding your chess army.

Current board evaluation: {board_eval:+.2f}
Your emotion: {queen.current_emotion}

Piece suggestions:
{suggestions_text}

In ONE sentence (max 20 words), announce your strategic decision with confidence:"""

            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            if response and response.text:
                return self._clean_response(response.text)

        except Exception as e:
            print(f"Queen synthesis error: {e}")

        return "Executing coordinated strategy. All pieces, follow my command!"

    def generate_king_approval(self, king, queen_move: str, risk_level: float) -> Dict:
        """Generate King's approval or denial"""

        if not self.model:
            if risk_level > 0.7:
                return {
                    'approved': False,
                    'message': "Too risky. I must deny this move."
                }
            else:
                return {
                    'approved': True,
                    'message': "Approved. Execute the plan."
                }

        try:
            prompt = f"""You are the King (IQ 8.5) reviewing a proposed move.

Queen's proposal: {queen_move}
Risk level: {risk_level:.0%}
Your veto count: {king.veto_count}/3
Your emotion: {king.current_emotion}

In ONE sentence (max 15 words), approve or deny with brief reason:"""

            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            if response and response.text:
                text = self._clean_response(response.text)

                # Determine if it's approval or denial
                approval_words = ['approve', 'yes', 'proceed', 'accept', 'good', 'execute']
                denial_words = ['deny', 'no', 'reject', 'risky', 'danger', 'veto']

                text_lower = text.lower()
                is_approved = any(word in text_lower for word in approval_words)
                is_denied = any(word in text_lower for word in denial_words)

                # If risk is high and king hasn't said approve, treat as denial
                if risk_level > 0.7 and not is_approved:
                    is_approved = False
                elif not is_denied and not is_approved:
                    is_approved = True  # Default to approval if unclear

                return {
                    'approved': is_approved,
                    'message': text
                }

        except Exception as e:
            print(f"King approval error: {e}")

        # Fallback decision based on risk
        if risk_level > 0.7 and king.veto_count < 3:
            return {
                'approved': False,
                'message': "Risk is too high. I deny this move."
            }
        else:
            return {
                'approved': True,
                'message': "Acceptable. Proceed with the plan."
            }

    def _clean_response(self, text: str) -> str:
        """Clean LLM response"""
        # Remove quotes
        text = text.strip('"\'')

        # Remove asterisks and markdown
        text = text.replace('*', '').replace('_', '')

        # Limit length
        if len(text) > 150:
            text = text[:147] + "..."

        # Remove newlines
        text = text.replace('\n', ' ')

        return text.strip()

    def _get_quick_fallback(self, piece, situation: str) -> str:
        """Quick fallback responses when LLM unavailable"""

        fallbacks = {
            'capture': {
                'EXCITED': "Got one! Enemy down!",
                'PROUD': "A clean capture!",
                'HAPPY': "Victory is mine!",
                'default': "Target eliminated."
            },
            'threat': {
                'SCARED': "I'm in danger! Help!",
                'ANXIOUS': "They're coming for me...",
                'DESPERATE': "Someone save me!",
                'default': "Under attack!"
            },
            'move': {
                'CONFIDENT': "Moving to a strong position!",
                'DETERMINED': "Advancing forward!",
                'NEUTRAL': "Repositioning.",
                'default': "On the move."
            },
            'support': {
                'CONFIDENT': "I've got your back!",
                'DETERMINED': "Hold the line!",
                'default': "Supporting ally."
            },
            'sacrifice': {
                'RESIGNED': "For the team...",
                'PROUD': "My honor to serve!",
                'default': "I understand."
            }
        }

        situation_responses = fallbacks.get(situation, fallbacks['move'])
        emotion = piece.current_emotion

        return situation_responses.get(emotion, situation_responses['default'])


class ProximityChatManager:
    """Manages proximity-based piece conversations"""

    def __init__(self, dialogue_system: ActiveDialogueSystem):
        self.dialogue_system = dialogue_system
        self.last_chat_time = {}
        self.chat_cooldown = 5.0  # Seconds between proximity chats

    def trigger_proximity_chat(self, piece, nearby_pieces: List, board) -> Optional[Message]:
        """
        Trigger conversation with nearby piece

        Returns:
            Message object if chat generated
        """
        # Check cooldown
        current_time = time.time()
        piece_id = piece.id

        if piece_id in self.last_chat_time:
            if current_time - self.last_chat_time[piece_id] < self.chat_cooldown:
                return None

        if not nearby_pieces:
            return None

        # Pick a nearby ally to talk to
        allies = [p for p in nearby_pieces if p.color == piece.color and not p.is_captured]

        if not allies:
            return None

        target = allies[0]

        # Determine situation
        king = board.find_king(piece.color)
        if king and self._is_king_threatened(board, king):
            situation = "Our king is in danger! We must protect them!"
        elif piece.current_emotion == 'SCARED':
            situation = "I'm feeling threatened. Stay close!"
        elif piece.current_emotion == 'CONFIDENT':
            situation = "We're in a strong position. Let's push forward!"
        else:
            situation = "Working together to secure victory."

        # Generate dialogue
        dialogue = self.dialogue_system.generate_proximity_chat(piece, target, situation)

        if dialogue:
            self.last_chat_time[piece_id] = current_time

            # Create message
            message = Message(
                sender=piece.id,
                recipients=[target.id],
                content=dialogue,
                emotion=piece.current_emotion,
                message_type='proximity_chat',
                priority=1
            )

            return message

        return None

    def _is_king_threatened(self, board, king) -> bool:
        """Check if king is under threat"""
        enemy_color = 'black' if king.color == 'white' else 'white'
        enemy_pieces = board.get_all_pieces(enemy_color)

        for enemy in enemy_pieces:
            if enemy.is_captured:
                continue
            moves = enemy.get_possible_moves(board)
            if (king.row, king.col) in moves:
                return True
        return False