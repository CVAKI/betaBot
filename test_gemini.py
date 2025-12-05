"""
Test Gemini Integration
"""

from llm_integration import DialogueGenerator
from pieces.pawn import Pawn
import config


def test_gemini():
    # Create a test pawn
    pawn = Pawn('white', 6, 3)
    pawn.set_emotion('SCARED')

    # Initialize dialogue generator
    gen = DialogueGenerator()

    # Test dialogue generation
    context = {
        'attacker': 'enemy knight',
        'allies': 'none'
    }

    dialogue = gen.generate_piece_dialogue(
        piece=pawn,
        situation='under_threat',
        context=context
    )

    print(f"Pawn says: {dialogue}")
    print(f"\nStatistics: {gen.get_statistics()}")


if __name__ == "__main__":
    test_gemini()