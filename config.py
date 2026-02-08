"""
β-bot Configuration File
Centralized configuration and constant definitions
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# ==================== ADD THESE LINES TO THE END OF config.py ====================

# ==================== ENHANCED LLM CONFIGURATION ====================
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_MODEL = 'gemini-1.5-flash'
LLM_TEMPERATURE = 0.9
LLM_MAX_TOKENS = 100

# ==================== ENHANCED UI CONFIGURATION ====================
USE_FULLSCREEN = False  # Set to True for fullscreen mode

# Make sure 'os' is imported at the top of config.py
# If you see "NameError: name 'os' is not defined", add this at the very top:
# import os

# ==================== SCREEN & UI CONSTANTS ====================
# Adjusted for better display on most monitors
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
BOARD_SIZE = 640  # 8x8 board (80 pixels per square)
CHAT_PANEL_WIDTH = 500
FPS = 60

# Board dimensions
BOARD_ROWS = 8
BOARD_COLS = 8
SQUARE_SIZE = BOARD_SIZE // BOARD_ROWS  # 80 pixels per square

# UI Layout
BOARD_OFFSET_X = 20
BOARD_OFFSET_Y = 80
CHAT_PANEL_X = BOARD_SIZE + BOARD_OFFSET_X + 20
CHAT_PANEL_Y = 80

# ==================== COLORS ====================
# Board colors
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT_COLOR = (255, 255, 0, 100)
LEGAL_MOVE_COLOR = (0, 255, 0, 80)

# UI colors
BACKGROUND_COLOR = (30, 30, 40)
CHAT_PANEL_BG = (45, 45, 55)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER = (100, 160, 210)
BUTTON_DISABLED = (100, 100, 100)

# Piece colors (for text/labels)
WHITE_PIECE_COLOR = (255, 255, 255)
BLACK_PIECE_COLOR = (50, 50, 50)

# Emotion colors (for chat messages)
EMOTION_COLORS = {
    'HAPPY': (255, 215, 0),
    'SAD': (135, 206, 250),
    'SCARED': (255, 140, 0),
    'CONFIDENT': (50, 205, 50),
    'ANGRY': (220, 20, 60),
    'NEUTRAL': (200, 200, 200),
    'ANXIOUS': (255, 182, 193),
    'PROUD': (138, 43, 226),
    'RESIGNED': (169, 169, 169)
}

# ==================== IQ RANGES ====================
IQ_RANGES = {
    'queen': {'min': 9.0, 'max': 9.99, 'default': 9.5},
    'king': {'min': 8.0, 'max': 8.99, 'default': 8.5},
    'knight': {'min': 7.0, 'max': 7.99, 'default': 7.5},
    'bishop': {'min': 6.0, 'max': 6.99, 'default': 6.5},
    'rook': {'min': 5.0, 'max': 5.99, 'default': 5.5},
    'pawn': {'min': 1.0, 'max': 4.99, 'default': 3.0}
}

# ==================== LLM CONFIGURATION (GEMINI) ====================
LLM_PROVIDER = 'gemini'  # Using Google Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')  # Load from .env file
GEMINI_MODEL = 'gemini-pro'  # or 'gemini-1.5-flash' for faster responses
LLM_MAX_TOKENS = 150
LLM_TEMPERATURE = 0.8
LLM_REQUEST_TIMEOUT = 10  # seconds

# Cache settings
ENABLE_LLM_CACHE = True
CACHE_SIZE_LIMIT = 1000
CACHE_EXPIRY_SECONDS = 3600

# Rate limiting
LLM_RATE_LIMIT_CALLS = 60
LLM_RATE_LIMIT_WINDOW = 60

# ==================== NEURAL NETWORK CONFIGS ====================
NN_CONFIGS = {
    'queen': {
        'layers': [768, 512, 256, 128, 64],
        'dropout': 0.2,
        'learning_rate': 0.0001,
        'activation': 'relu'
    },
    'king': {
        'layers': [768, 384, 192, 64],
        'dropout': 0.25,
        'learning_rate': 0.00015,
        'activation': 'relu'
    },
    'knight': {
        'layers': [768, 256, 128, 64],
        'dropout': 0.3,
        'learning_rate': 0.0002,
        'activation': 'relu'
    },
    'bishop': {
        'layers': [768, 256, 96, 64],
        'dropout': 0.3,
        'learning_rate': 0.0003,
        'activation': 'relu'
    },
    'rook': {
        'layers': [768, 192, 64],
        'dropout': 0.35,
        'learning_rate': 0.0004,
        'activation': 'relu'
    },
    'pawn': {
        'layers': [768, 128, 64],
        'dropout': 0.4,
        'learning_rate': 0.001,
        'activation': 'relu'
    }
}

NN_INPUT_SIZE = 768

# ==================== GAME RULES ====================
KING_MAX_VETOES = 3
CASTLING_ENABLED = True
EN_PASSANT_ENABLED = True
PAWN_PROMOTION_ENABLED = True
COMMUNICATION_RADIUS = 2

# ==================== FILE PATHS ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
MODELS_DIR = os.path.join(BASE_DIR, 'ai_brain', 'training', 'models')

# Asset subdirectories
PIECES_DIR = os.path.join(ASSETS_DIR, 'pieces')
WHITE_PIECES_DIR = os.path.join(PIECES_DIR, 'white')
BLACK_PIECES_DIR = os.path.join(PIECES_DIR, 'black')
BOARD_DIR = os.path.join(ASSETS_DIR, 'board')
EMOJIS_DIR = os.path.join(ASSETS_DIR, 'emojis')
UI_DIR = os.path.join(ASSETS_DIR, 'ui')
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')

# Piece image files
PIECE_IMAGES = {
    'white': {
        'king': os.path.join(WHITE_PIECES_DIR, 'king.png'),
        'queen': os.path.join(WHITE_PIECES_DIR, 'queen.png'),
        'rook': os.path.join(WHITE_PIECES_DIR, 'rook.png'),
        'bishop': os.path.join(WHITE_PIECES_DIR, 'bishop.png'),
        'knight': os.path.join(WHITE_PIECES_DIR, 'knight.png'),
        'pawn': os.path.join(WHITE_PIECES_DIR, 'pawn.png')
    },
    'black': {
        'king': os.path.join(BLACK_PIECES_DIR, 'king.png'),
        'queen': os.path.join(BLACK_PIECES_DIR, 'queen.png'),
        'rook': os.path.join(BLACK_PIECES_DIR, 'rook.png'),
        'bishop': os.path.join(BLACK_PIECES_DIR, 'bishop.png'),
        'knight': os.path.join(BLACK_PIECES_DIR, 'knight.png'),
        'pawn': os.path.join(BLACK_PIECES_DIR, 'pawn.png')
    }
}

BOARD_IMAGE = os.path.join(BOARD_DIR, 'board.png')

# Emoji files
EMOJI_FILES = {
    'HAPPY': os.path.join(EMOJIS_DIR, 'happy.png'),
    'SAD': os.path.join(EMOJIS_DIR, 'sad.png'),
    'SCARED': os.path.join(EMOJIS_DIR, 'scared.png'),
    'CONFIDENT': os.path.join(EMOJIS_DIR, 'confident.png'),
    'ANGRY': os.path.join(EMOJIS_DIR, 'angry.png'),
    'NEUTRAL': os.path.join(EMOJIS_DIR, 'neutral.png'),
    'ANXIOUS': os.path.join(EMOJIS_DIR, 'anxious.png'),
    'PROUD': os.path.join(EMOJIS_DIR, 'proud.png'),
    'RESIGNED': os.path.join(EMOJIS_DIR, 'resigned.png')
}

# Data files
PERSONALITIES_FILE = os.path.join(DATA_DIR, 'piece_personalities.json')
DIALOGUE_TEMPLATES_FILE = os.path.join(DATA_DIR, 'dialogue_templates.json')
EMOTION_MAPPINGS_FILE = os.path.join(DATA_DIR, 'emotion_mappings.json')
IQ_CONFIGS_FILE = os.path.join(DATA_DIR, 'iq_configurations.json')

# Log directories
GAME_LOGS_DIR = os.path.join(LOGS_DIR, 'game_logs')
CHAT_LOGS_DIR = os.path.join(LOGS_DIR, 'chat_logs')
ERROR_LOGS_DIR = os.path.join(LOGS_DIR, 'error_logs')

# ==================== PERFORMANCE SETTINGS ====================
MAX_PIECE_THINK_TIME = 2.0
MAX_QUEEN_SYNTHESIS_TIME = 5.0
MAX_KING_VALIDATION_TIME = 3.0

MOVE_ANIMATION_DURATION = 0.5
CAPTURE_ANIMATION_DURATION = 0.3
EMOTION_ANIMATION_DURATION = 0.2

# ==================== FONT SETTINGS ====================
FONT_TITLE = 'Arial'
FONT_TITLE_SIZE = 36

FONT_CHAT = 'Courier New'
FONT_CHAT_SIZE = 14

FONT_UI = 'Arial'
FONT_UI_SIZE = 16

FONT_COORDINATES = 'Arial'
FONT_COORDINATES_SIZE = 12

# ==================== DEBUG SETTINGS ====================
DEBUG_MODE = False
SHOW_FPS = True
SHOW_AI_THINKING = True
VERBOSE_LOGGING = False

# ==================== TRAINING SETTINGS ====================
TRAINING_ENABLED = False
BATCH_SIZE = 32
EPOCHS = 100
VALIDATION_SPLIT = 0.2
CHECKPOINT_FREQUENCY = 10

# ==================== PERSONALITY TRAITS ====================
DEFAULT_PERSONALITIES = {
    'queen': {
        'confidence': 0.95,
        'leadership': 0.98,
        'aggression': 0.75,
        'caution': 0.60,
        'loyalty': 0.90
    },
    'king': {
        'confidence': 0.85,
        'leadership': 0.80,
        'aggression': 0.40,
        'caution': 0.95,
        'loyalty': 1.0
    },
    'knight': {
        'confidence': 0.75,
        'leadership': 0.50,
        'aggression': 0.85,
        'caution': 0.45,
        'loyalty': 0.85
    },
    'bishop': {
        'confidence': 0.70,
        'leadership': 0.45,
        'aggression': 0.60,
        'caution': 0.70,
        'loyalty': 0.80
    },
    'rook': {
        'confidence': 0.65,
        'leadership': 0.40,
        'aggression': 0.70,
        'caution': 0.60,
        'loyalty': 0.85
    },
    'pawn': {
        'confidence': 0.30,
        'leadership': 0.10,
        'aggression': 0.50,
        'caution': 0.70,
        'loyalty': 0.95
    }
}

# ==================== PIECE VALUES ====================
PIECE_VALUES = {
    'pawn': 1,
    'knight': 3,
    'bishop': 3,
    'rook': 5,
    'queen': 9,
    'king': 0
}

# ==================== UTILITY FUNCTIONS ====================
def create_directories():
    """Create all necessary directories"""
    directories = [
        ASSETS_DIR, PIECES_DIR, WHITE_PIECES_DIR, BLACK_PIECES_DIR,
        BOARD_DIR, EMOJIS_DIR, UI_DIR, SOUNDS_DIR,
        DATA_DIR, LOGS_DIR, GAME_LOGS_DIR, CHAT_LOGS_DIR,
        ERROR_LOGS_DIR, MODELS_DIR
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def get_piece_iq(piece_type, randomize=True):
    """Get IQ value for a piece type"""
    import random
    config = IQ_RANGES.get(piece_type.lower())
    if not config:
        return 5.0
    if randomize:
        return random.uniform(config['min'], config['max'])
    return config['default']

def validate_config():
    """Validate configuration settings"""
    errors = []

    # Check Gemini API key
    if LLM_PROVIDER == 'gemini':
        if not GEMINI_API_KEY:
            errors.append("Gemini API key not found in .env file. Dialogue generation will use fallbacks.")
        else:
            # Validate key format (basic check)
            if not GEMINI_API_KEY.startswith('AIza'):
                errors.append("Gemini API key format appears invalid. Should start with 'AIza'.")
            else:
                errors.append(f"✅ Gemini API key loaded successfully (ending in ...{GEMINI_API_KEY[-8:]})")

    return errors

# Create directories on import
create_directories()

# Print API key status on import (for debugging)
if __name__ == "__main__":
    print(f"Gemini API Key loaded: {'Yes' if GEMINI_API_KEY else 'No'}")
    if GEMINI_API_KEY:
        print(f"Key preview: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-8:]}")