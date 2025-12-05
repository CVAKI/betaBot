"""
Save and Load Game State
"""

import json
import pickle
import os
from datetime import datetime
import config


def save_game(filename: str, game_state, board, chat_history):
    """Save complete game state"""
    # Ensure directory exists
    save_dir = os.path.join(config.LOGS_DIR, 'saved_games')
    os.makedirs(save_dir, exist_ok=True)

    filepath = os.path.join(save_dir, filename)

    # Prepare data
    save_data = {
        'timestamp': datetime.now().isoformat(),
        'game_state': _serialize_game_state(game_state),
        'board': _serialize_board(board),
        'chat_history': [msg.to_dict() for msg in chat_history],
        'version': '1.0'
    }

    # Save as JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, indent=2)

    return filepath


def load_game(filename: str):
    """Load game state from file"""
    filepath = os.path.join(config.LOGS_DIR, 'saved_games', filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Save file not found: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        save_data = json.load(f)

    return save_data


def _serialize_game_state(game_state) -> dict:
    """Convert game state to serializable format"""
    return {
        'current_player': game_state.current_player,
        'move_history': game_state.move_history,
        'castling_rights': game_state.castling_rights,
        'king_veto_count': game_state.king_veto_count,
        'game_phase': game_state.game_phase
    }


def _serialize_board(board) -> dict:
    """Convert board to serializable format"""
    pieces_data = []
    for piece in board.get_all_pieces():
        pieces_data.append(piece.to_dict())

    return {
        'pieces': pieces_data,
        'move_count': board.move_count
    }


def export_pgn(game_state, filename: str):
    """Export game in PGN format"""
    # Placeholder for PGN export
    pass