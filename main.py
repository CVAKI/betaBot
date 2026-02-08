"""
β-bot Enhanced Main Game
Complete implementation with AI strategy, LLM dialogue, and enhanced UI
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
import time
from datetime import datetime

# Core imports
import config

# Chess engine
from chess_engine.board import Board
from chess_engine.game_state import GameState

# Pieces - Fixed imports
from pieces.pawn import Pawn
from pieces.knight import Knight
from pieces.bishop import Bishop
from pieces.rook import Rook
from pieces.queen import Queen
from pieces.king import King
# UI components
from ui.board_renderer import BoardRenderer
from ui.piece_renderer import PieceRenderer
from ui.chat_panel import ChatPanel

# Emotion system
from emotion.emotion_engine import EmotionEngine

# Logging
from utils.logger import setup_logger, log_info, log_error


class EnhancedGameWindow:
    """Enhanced full-screen game window"""

    def __init__(self):
        """Initialize with dynamic screen size"""
        pygame.init()

        # Get display info
        display_info = pygame.display.Info()

        if config.USE_FULLSCREEN:
            self.screen = pygame.display.set_mode(
                (display_info.current_w, display_info.current_h),
                pygame.FULLSCREEN
            )
            self.screen_width = display_info.current_w
            self.screen_height = display_info.current_h
        else:
            self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            self.screen_width = config.SCREEN_WIDTH
            self.screen_height = config.SCREEN_HEIGHT

        pygame.display.set_caption("β-bot: Multi-Agent Chess AI")

        # Calculate responsive layout
        self.layout = self._calculate_layout()

        # Initialize renderers with enhanced versions if available
        try:
            from ui.enhanced_ui import EnhancedBoardRenderer, EnhancedPieceRenderer, EnhancedChatPanel
            self.board_renderer = EnhancedBoardRenderer(self.layout)
            self.piece_renderer = EnhancedPieceRenderer(self.layout)
            self.chat_panel = EnhancedChatPanel(self.layout)
            log_info("Loaded enhanced UI components")
        except ImportError:
            # Fallback to standard renderers
            self.board_renderer = BoardRenderer()
            self.piece_renderer = PieceRenderer()
            self.chat_panel = ChatPanel()
            log_info("Using standard UI components")

        print(f"✅ Window initialized at {self.screen_width}x{self.screen_height}")

    def _calculate_layout(self):
        """Calculate responsive layout"""
        board_size = int(min(self.screen_height * 0.9, self.screen_width * 0.55))
        square_size = board_size // 8

        chat_panel_width = self.screen_width - board_size - 150
        chat_panel_height = self.screen_height - 100

        return {
            'board_size': board_size,
            'square_size': square_size,
            'board_offset_x': 50,
            'board_offset_y': 50,
            'chat_panel_width': chat_panel_width,
            'chat_panel_height': chat_panel_height,
            'chat_panel_x': board_size + 100,
            'chat_panel_y': 50
        }

    def render(self, game_manager):
        """Render all components"""
        try:
            # Clear screen
            self.screen.fill(config.BACKGROUND_COLOR)

            # Render board
            self.board_renderer.draw_board(self.screen)

            # Render pieces
            if hasattr(game_manager, 'board'):
                for piece in game_manager.board.get_all_pieces():
                    if not piece.is_captured:
                        self.piece_renderer.draw_piece(self.screen, piece)

            # Render chat
            if hasattr(game_manager, 'chat_history'):
                self.chat_panel.draw(self.screen, game_manager.chat_history)

        except Exception as e:
            log_error(f"Render error: {e}")

    def handle_event(self, event):
        """Handle window events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                self.toggle_fullscreen()

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed"""
        config.USE_FULLSCREEN = not config.USE_FULLSCREEN

        if config.USE_FULLSCREEN:
            display_info = pygame.display.Info()
            self.screen = pygame.display.set_mode(
                (display_info.current_w, display_info.current_h),
                pygame.FULLSCREEN
            )
            self.screen_width = display_info.current_w
            self.screen_height = display_info.current_h
        else:
            self.screen = pygame.display.set_mode((1600, 900))
            self.screen_width = 1600
            self.screen_height = 900

        # Recalculate layout
        self.layout = self._calculate_layout()

        # Update renderers if they support it
        if hasattr(self.board_renderer, 'update_layout'):
            self.board_renderer.update_layout(self.layout)
        if hasattr(self.piece_renderer, 'update_layout'):
            self.piece_renderer.update_layout(self.layout)
        if hasattr(self.chat_panel, 'update_layout'):
            self.chat_panel.update_layout(self.layout)


class IntegratedGameManager:
    """Enhanced game manager with AI and LLM"""

    def __init__(self):
        self.board = Board()
        self.game_state = GameState()
        self.pieces = []
        self.chat_history = []

        # Try to load enhanced AI systems
        try:
            from ai_brain.enhanced_strategy import SmartDecisionPipeline
            self.decision_pipeline = SmartDecisionPipeline()
            self.has_enhanced_ai = True
            log_info("Loaded enhanced AI strategy")
        except ImportError:
            self.decision_pipeline = None
            self.has_enhanced_ai = False
            log_info("Enhanced AI not available, using basic strategy")

        # Try to load LLM dialogue system
        try:
            from llm_integration.active_dialogue import ActiveDialogueSystem, ProximityChatManager
            self.dialogue_system = ActiveDialogueSystem()
            self.proximity_chat = ProximityChatManager(self.dialogue_system)
            self.has_llm = True
            log_info("Loaded LLM dialogue system")
        except ImportError:
            self.dialogue_system = None
            self.proximity_chat = None
            self.has_llm = False
            log_info("LLM dialogue not available, using fallbacks")

        # Emotion system
        try:
            self.emotion_engine = EmotionEngine()
        except:
            self.emotion_engine = None

        # Game state
        self.is_ai_turn = True
        self.ai_thinking = False
        self.last_move_time = 0
        self.move_delay = 2.0  # Seconds between moves

        # Statistics
        self.total_moves = 0
        self.captures = {'white': 0, 'black': 0}

    def initialize_game(self):
        """Setup initial game state"""
        self._setup_pieces()
        self._add_chat_message("System", "♟️ Game started! White to move.", "NEUTRAL")

        if self.has_enhanced_ai:
            self._add_chat_message("System", "✅ Enhanced AI Strategy active", "CONFIDENT")
        if self.has_llm:
            self._add_chat_message("System", "✅ LLM Dialogue System active", "CONFIDENT")

        print("✅ Game initialized successfully")

    def _setup_pieces(self):
        """Create all 32 pieces"""
        self.pieces.clear()
        self.board.clear_board()

        # White pieces - bottom
        for col in range(8):
            pawn = Pawn('white', 6, col)
            self.pieces.append(pawn)
            self.board.set_piece_at(6, col, pawn)

        # White back rank
        white_pieces = [
            Rook('white', 7, 0),
            Knight('white', 7, 1),
            Bishop('white', 7, 2),
            Queen('white', 7, 3),
            King('white', 7, 4),
            Bishop('white', 7, 5),
            Knight('white', 7, 6),
            Rook('white', 7, 7)
        ]

        for piece in white_pieces:
            self.pieces.append(piece)
            self.board.set_piece_at(piece.row, piece.col, piece)

        # Black pieces - top
        for col in range(8):
            pawn = Pawn('black', 1, col)
            self.pieces.append(pawn)
            self.board.set_piece_at(1, col, pawn)

        black_pieces = [
            Rook('black', 0, 0),
            Knight('black', 0, 1),
            Bishop('black', 0, 2),
            Queen('black', 0, 3),
            King('black', 0, 4),
            Bishop('black', 0, 5),
            Knight('black', 0, 6),
            Rook('black', 0, 7)
        ]

        for piece in black_pieces:
            self.pieces.append(piece)
            self.board.set_piece_at(piece.row, piece.col, piece)

        print(f"  Created {len(self.pieces)} pieces")

    def update(self):
        """Main update loop"""
        if self.ai_thinking:
            return

        current_time = time.time()
        if current_time - self.last_move_time < self.move_delay:
            return

        if self.is_ai_turn:
            self.execute_ai_turn()

    def execute_ai_turn(self):
        """Execute complete AI turn"""
        self.ai_thinking = True

        try:
            current_color = self.game_state.current_player

            # Update emotions
            if self.emotion_engine:
                self.emotion_engine.update_all_emotions(self.board, self.game_state)

            # Get all active pieces
            active_pieces = [p for p in self.board.get_all_pieces(current_color)
                           if not p.is_captured]

            if not active_pieces:
                return

            # Collect move suggestions
            suggestions = []

            for piece in active_pieces:
                if self.has_enhanced_ai:
                    # Use enhanced AI
                    move_data = self.decision_pipeline.get_best_move_for_piece(
                        piece, self.board, self.game_state
                    )
                else:
                    # Use piece's built-in suggest_move
                    move_data = piece.suggest_move(self.board, self.game_state)

                if move_data and move_data.get('score', 0) > -999:
                    suggestions.append({
                        'piece': piece,
                        'from': move_data['from'],
                        'to': move_data['to'],
                        'score': move_data.get('score', 0),
                        'confidence': move_data.get('confidence', 0.5),
                        'reasoning': move_data.get('reasoning', 'strategic move')
                    })

            if not suggestions:
                self._add_chat_message("System", f"{current_color} has no legal moves!", "SAD")
                return

            # Sort by score
            suggestions.sort(key=lambda x: x['score'], reverse=True)

            # Proximity chat (if available)
            if self.has_llm and self.proximity_chat:
                self._trigger_proximity_chats(active_pieces)

            # Queen announces strategy (if LLM available)
            if self.has_llm and self.dialogue_system:
                queen = self._find_piece_by_type(active_pieces, 'queen')
                if queen:
                    board_eval = self._calculate_board_evaluation()
                    queen_message = self.dialogue_system.generate_queen_synthesis(
                        queen, suggestions[:5], board_eval
                    )
                    self._add_chat_message(queen.id, queen_message, queen.current_emotion)

            # Select best move
            best_move = suggestions[0]

            # King approval (if LLM available)
            if self.has_llm and self.dialogue_system:
                king = self._find_piece_by_type(active_pieces, 'king')
                if king:
                    risk_level = self._assess_move_risk(best_move)
                    king_decision = self.dialogue_system.generate_king_approval(
                        king,
                        f"Move {best_move['piece'].piece_type} to {best_move['to']}",
                        risk_level
                    )
                    self._add_chat_message(king.id, king_decision['message'], king.current_emotion)

                    if not king_decision['approved'] and hasattr(king, 'veto_count'):
                        if king.veto_count < 3:
                            king.veto_count += 1
                            if len(suggestions) > 1:
                                best_move = suggestions[1]

            # Execute move
            self._execute_move(best_move)

            # Generate reaction dialogue
            piece = best_move['piece']
            target = self.board.get_piece_at(best_move['to'][0], best_move['to'][1])

            if self.has_llm and self.dialogue_system:
                if target:
                    # Capture reaction
                    reaction = self.dialogue_system.generate_piece_reaction(
                        piece, 'capture',
                        {'captured_piece': target.piece_type}
                    )
                    self._add_chat_message(piece.id, reaction, piece.current_emotion)
                else:
                    # Move reaction
                    reaction = self.dialogue_system.generate_piece_reaction(
                        piece, 'move',
                        {'new_position': best_move['to']}
                    )
                    self._add_chat_message(piece.id, reaction, piece.current_emotion)
            else:
                # Fallback dialogue
                if target:
                    self._add_chat_message(
                        piece.id,
                        f"Captured enemy {target.piece_type}!",
                        piece.current_emotion
                    )
                else:
                    self._add_chat_message(
                        piece.id,
                        f"Moving to {self.board.get_square_name(best_move['to'][0], best_move['to'][1])}",
                        piece.current_emotion
                    )

            # Switch turns
            self.game_state.switch_turn()
            self.total_moves += 1
            self.last_move_time = time.time()

        except Exception as e:
            log_error(f"Error in AI turn: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.ai_thinking = False

    def _execute_move(self, move_data):
        """Execute a move on the board"""
        piece = move_data['piece']
        from_row, from_col = move_data['from']
        to_row, to_col = move_data['to']

        target = self.board.get_piece_at(to_row, to_col)
        if target:
            self.board.capture_piece(target)
            self.captures[piece.color] += 1

        self.board.move_piece(from_row, from_col, to_row, to_col)
        piece.mark_moved()

        from_square = self.board.get_square_name(from_row, from_col)
        to_square = self.board.get_square_name(to_row, to_col)
        print(f"  {piece.color} {piece.piece_type}: {from_square} → {to_square}")

    def _trigger_proximity_chats(self, active_pieces):
        """Trigger proximity conversations"""
        for piece in active_pieces[:3]:
            nearby = self._get_nearby_pieces(piece, active_pieces)
            if nearby and self.proximity_chat:
                message = self.proximity_chat.trigger_proximity_chat(
                    piece, nearby, self.board
                )
                if message:
                    self.chat_history.append(message)

    def _get_nearby_pieces(self, piece, all_pieces):
        """Get pieces within communication range"""
        nearby = []
        for other in all_pieces:
            if other == piece or other.is_captured:
                continue
            distance = abs(piece.row - other.row) + abs(piece.col - other.col)
            if distance <= 2:
                nearby.append(other)
        return nearby

    def _find_piece_by_type(self, pieces, piece_type):
        """Find first piece of given type"""
        for piece in pieces:
            if piece.piece_type == piece_type:
                return piece
        return None

    def _calculate_board_evaluation(self):
        """Calculate board evaluation"""
        current_color = self.game_state.current_player
        our_material = self.board.get_material_count(current_color)
        enemy_color = 'black' if current_color == 'white' else 'white'
        enemy_material = self.board.get_material_count(enemy_color)
        return our_material - enemy_material

    def _assess_move_risk(self, move_data):
        """Assess risk level of a move"""
        piece = move_data['piece']
        king = self.board.find_king(piece.color)

        if king and self.has_enhanced_ai:
            from ai_brain.enhanced_strategy import EnhancedMoveEvaluator
            if EnhancedMoveEvaluator._is_king_threatened(self.board, king):
                return 0.8

        return 0.3

    def _add_chat_message(self, sender, content, emotion):
        """Add message to chat history"""
        message = {
            'sender': sender,
            'content': content,
            'emotion': emotion,
            'timestamp': datetime.now()
        }
        self.chat_history.append(message)

        if len(self.chat_history) > 100:
            self.chat_history = self.chat_history[-100:]

    def reset_game(self):
        """Reset game"""
        self.game_state = GameState()
        self.chat_history.clear()
        self.total_moves = 0
        self.captures = {'white': 0, 'black': 0}
        self._setup_pieces()
        self._add_chat_message("System", "🔄 Game reset! White to move.", "NEUTRAL")

    def handle_mouse_click(self, pos):
        """Handle mouse clicks"""
        pass

    def cleanup(self):
        """Cleanup resources"""
        pass


def main():
    """Main game loop"""
    # Setup logging
    logger = setup_logger('main')
    log_info("=" * 60)
    log_info("β-bot: Enhanced Multi-Agent Chess AI Starting")
    log_info("=" * 60)

    # Initialize window
    game_window = EnhancedGameWindow()
    clock = pygame.time.Clock()

    # Create game manager
    game_manager = IntegratedGameManager()
    game_manager.initialize_game()

    # Game state
    running = True
    paused = False
    show_fps = True

    print("\n🎮 Controls:")
    print("   ESC: Quit")
    print("   SPACE: Pause/Resume")
    print("   F11: Toggle Fullscreen")
    print("   R: Reset Game")
    print("   F: Toggle FPS\n")

    try:
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    log_info("Quit event received")

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        log_info("ESC pressed - quitting")

                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                        status = "⏸️  Paused" if paused else "▶️  Resumed"
                        print(status)
                        log_info(f"Game {status}")

                    elif event.key == pygame.K_r:
                        game_manager.reset_game()
                        print("🔄 Game reset")
                        log_info("Game reset")

                    elif event.key == pygame.K_f:
                        show_fps = not show_fps

                    elif event.key == pygame.K_F11:
                        game_window.toggle_fullscreen()
                        print("🖥️  Toggled fullscreen")

                game_window.handle_event(event)

            # Update game
            if not paused:
                game_manager.update()

            # Render
            game_window.render(game_manager)

            # Show FPS
            if show_fps:
                fps = int(clock.get_fps())
                font = pygame.font.Font(None, 28)
                fps_text = font.render(f"FPS: {fps}", True, (0, 255, 0))
                game_window.screen.blit(fps_text, (10, 10))

            # Show pause indicator
            if paused:
                font = pygame.font.Font(None, 64)
                pause_text = font.render("⏸ PAUSED", True, (255, 255, 0))
                text_rect = pause_text.get_rect(
                    center=(game_window.screen_width // 2, 50)
                )
                bg_rect = text_rect.inflate(40, 20)
                pygame.draw.rect(game_window.screen, (0, 0, 0), bg_rect, border_radius=10)
                game_window.screen.blit(pause_text, text_rect)

            # Update display
            pygame.display.flip()
            clock.tick(config.FPS)

    except KeyboardInterrupt:
        log_info("Keyboard interrupt received")
        print("\n⚠️  Interrupted by user")

    except Exception as e:
        log_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        log_info("Shutting down...")
        print("\n👋 Shutting down β-bot...")

        try:
            game_manager.cleanup()
        except Exception as e:
            log_error(f"Error during cleanup: {e}")

        pygame.quit()
        log_info("β-bot shutdown complete")
        print("✅ Goodbye!\n")


if __name__ == "__main__":
    main()