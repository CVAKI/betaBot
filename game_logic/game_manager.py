"""
Game Manager with AI Movement System
Pieces think, discuss, Queen synthesizes, King approves
ENHANCED: Now with anti-repetition logic and smart move selection
"""

from chess_engine.board import Board
from chess_engine.game_state import GameState
from pieces.pawn import Pawn
from pieces.knight import Knight
from pieces.bishop import Bishop
from pieces.rook import Rook
from pieces.queen import Queen
from pieces.king import King
import config
import random
import time


class GameManager:
    """Main game flow controller with AI decision-making"""

    def __init__(self):
        """Initialize game manager"""
        self.board = Board()
        self.game_state = GameState()
        self.pieces = []
        self.chat_history = []

        # Selection state (for manual play)
        self.selected_piece = None
        self.selected_position = None
        self.legal_moves = []

        # Move history
        self.last_move = None

        # ✅ NEW: Anti-repetition tracking
        self.move_history = []  # List of all moves made
        self.position_history = []  # Track board positions
        self.last_moves_by_piece = {}  # Track last move for each piece

        # AI state
        self.ai_mode = True  # True = AI plays both sides, False = manual
        self.ai_thinking = False
        self.ai_think_timer = 0
        self.ai_think_delay = 2.0  # Seconds between AI moves
        self.current_ai_decision = None

        # ✅ NEW: Game phase tracking
        self.move_count = 0

    def initialize_game(self):
        """Setup initial game state"""
        self._setup_pieces()
        self.position_history.append(self._get_position_hash())
        print("✅ Game initialized with all pieces")
        print(f"🤖 AI Mode: {'ON' if self.ai_mode else 'OFF'}")

    def _setup_pieces(self):
        """Create all 32 pieces in starting positions"""
        self.pieces.clear()
        self.board.clear_board()

        # White pieces (bottom)
        for col in range(8):
            pawn = Pawn('white', 6, col)
            self.pieces.append(pawn)
            self.board.set_piece_at(6, col, pawn)

        self.pieces.append(Rook('white', 7, 0))
        self.board.set_piece_at(7, 0, self.pieces[-1])
        self.pieces.append(Rook('white', 7, 7))
        self.board.set_piece_at(7, 7, self.pieces[-1])

        self.pieces.append(Knight('white', 7, 1))
        self.board.set_piece_at(7, 1, self.pieces[-1])
        self.pieces.append(Knight('white', 7, 6))
        self.board.set_piece_at(7, 6, self.pieces[-1])

        self.pieces.append(Bishop('white', 7, 2))
        self.board.set_piece_at(7, 2, self.pieces[-1])
        self.pieces.append(Bishop('white', 7, 5))
        self.board.set_piece_at(7, 5, self.pieces[-1])

        self.pieces.append(Queen('white', 7, 3))
        self.board.set_piece_at(7, 3, self.pieces[-1])

        self.pieces.append(King('white', 7, 4))
        self.board.set_piece_at(7, 4, self.pieces[-1])

        # Black pieces (top)
        for col in range(8):
            pawn = Pawn('black', 1, col)
            self.pieces.append(pawn)
            self.board.set_piece_at(1, col, pawn)

        self.pieces.append(Rook('black', 0, 0))
        self.board.set_piece_at(0, 0, self.pieces[-1])
        self.pieces.append(Rook('black', 0, 7))
        self.board.set_piece_at(0, 7, self.pieces[-1])

        self.pieces.append(Knight('black', 0, 1))
        self.board.set_piece_at(0, 1, self.pieces[-1])
        self.pieces.append(Knight('black', 0, 6))
        self.board.set_piece_at(0, 6, self.pieces[-1])

        self.pieces.append(Bishop('black', 0, 2))
        self.board.set_piece_at(0, 2, self.pieces[-1])
        self.pieces.append(Bishop('black', 0, 5))
        self.board.set_piece_at(0, 5, self.pieces[-1])

        self.pieces.append(Queen('black', 0, 3))
        self.board.set_piece_at(0, 3, self.pieces[-1])

        self.pieces.append(King('black', 0, 4))
        self.board.set_piece_at(0, 4, self.pieces[-1])

        print(f"Created {len(self.pieces)} pieces")

    def toggle_ai_mode(self):
        """Toggle between AI and manual play"""
        self.ai_mode = not self.ai_mode
        print(f"🤖 AI Mode: {'ON' if self.ai_mode else 'OFF'}")
        self._add_chat_message(
            "System",
            f"AI Mode {'ENABLED' if self.ai_mode else 'DISABLED'}",
            'NEUTRAL'
        )

    def update(self):
        """Update game state each frame"""
        if self.ai_mode and not self.ai_thinking:
            # Time to make AI move
            self.ai_think_timer += 1/60  # Assuming 60 FPS

            if self.ai_think_timer >= self.ai_think_delay:
                self.ai_think_timer = 0
                self._execute_ai_turn()

    def _execute_ai_turn(self):
        """Execute one AI turn with the full decision pipeline"""
        self.ai_thinking = True

        try:
            current_color = self.game_state.current_player

            # Stage 1: Collect proposals from all pieces (WITH FILTERING)
            proposals = self._collect_piece_proposals(current_color)

            if not proposals:
                print(f"No legal moves for {current_color}!")
                self.ai_thinking = False
                return

            # Stage 2: Find Queen
            queen = self._find_piece('queen', current_color)

            # Stage 3: Queen synthesizes strategy (ENHANCED)
            if queen:
                chosen_proposal = self._queen_synthesize(queen, proposals)
            else:
                # Fallback if Queen is captured
                chosen_proposal = self._select_smart_proposal(proposals)

            # Stage 4: King validates
            king = self._find_piece('king', current_color)
            if king:
                approved = self._king_validate(king, chosen_proposal)
                if not approved:
                    # King denied, choose another (but not the same one!)
                    remaining = [p for p in proposals if p != chosen_proposal]
                    if remaining:
                        chosen_proposal = self._select_smart_proposal(remaining)
                    else:
                        chosen_proposal = random.choice(proposals)

            # Stage 5: Execute the move
            self._execute_proposal(chosen_proposal)

        except Exception as e:
            print(f"AI error: {e}")
            import traceback
            traceback.print_exc()

        self.ai_thinking = False

    def _collect_piece_proposals(self, color):
        """Collect move proposals from all pieces of given color (ENHANCED)"""
        proposals = []

        pieces = [p for p in self.pieces if p.color == color and not p.is_captured]

        # ✅ NEW: Prioritize piece types based on game phase
        piece_priority = self._get_piece_priority()

        for piece_type in piece_priority:
            type_pieces = [p for p in pieces if p.piece_type == piece_type]

            for piece in type_pieces:
                legal_moves = piece.get_possible_moves(self.board)

                if not legal_moves:
                    continue

                # ✅ FILTER: Remove repetitive moves
                filtered_moves = self._filter_repetitive_moves(piece, legal_moves)

                if not filtered_moves:
                    filtered_moves = legal_moves  # Fallback if all filtered

                # ✅ ENHANCED: Score moves instead of random selection
                best_move = self._score_and_select_move(piece, filtered_moves)

                proposal = {
                    'piece': piece,
                    'from': (piece.row, piece.col),
                    'to': best_move,
                    'score': self._calculate_move_score(piece, best_move)
                }

                proposals.append(proposal)

                # Piece announces its suggestion (occasionally)
                if random.random() < 0.3:  # 30% chance to announce
                    move_name = self.board.get_square_name(best_move[0], best_move[1])
                    self._add_chat_message(
                        piece.id,
                        f"I suggest moving to {move_name}",
                        piece.current_emotion
                    )

        print(f"📝 Collected {len(proposals)} proposals from {color} pieces")
        return proposals

    def _get_piece_priority(self):
        """Get piece types in priority order based on game phase"""
        # Opening (first 10 moves): Develop pawns and minor pieces
        if self.move_count < 10:
            return ['pawn', 'knight', 'bishop', 'queen', 'rook', 'king']
        # Mid-game: Tactical pieces
        elif self.move_count < 30:
            return ['knight', 'bishop', 'queen', 'pawn', 'rook', 'king']
        # End-game: King becomes active
        else:
            return ['queen', 'rook', 'king', 'knight', 'bishop', 'pawn']

    def _filter_repetitive_moves(self, piece, moves):
        """Filter out moves that cause immediate repetition"""
        filtered = []

        for move in moves:
            # Check if this piece just moved FROM this square
            last_move_info = self.last_moves_by_piece.get(piece.id)

            if last_move_info:
                # Don't move back to where you just came from
                if move == last_move_info['from']:
                    continue

            # Check if this exact move was made very recently
            move_sig = f"{piece.id}:{move}"
            recent_count = sum(1 for m in self.move_history[-6:] if m == move_sig)

            if recent_count >= 2:  # Skip if done twice in last 6 moves
                continue

            filtered.append(move)

        return filtered if filtered else moves

    def _score_and_select_move(self, piece, moves):
        """Score moves and select the best one"""
        if not moves:
            return None

        scored = []

        for move in moves:
            score = self._calculate_move_score(piece, move)
            scored.append((score, move))

        # Sort by score (highest first)
        scored.sort(reverse=True, key=lambda x: x[0])

        # Add some randomness: pick from top 3
        top_moves = scored[:min(3, len(scored))]
        return random.choice(top_moves)[1]

    def _calculate_move_score(self, piece, move):
        """Calculate score for a move"""
        score = 0.0
        to_row, to_col = move

        # ✅ Center control bonus
        center_distance = abs(to_row - 3.5) + abs(to_col - 3.5)
        score += (7 - center_distance) * 0.5

        # ✅ Capture bonus
        target = self.board.get_piece_at(to_row, to_col)
        if target and piece.is_enemy(target):
            score += target.get_value() * 3  # High priority!

        # ✅ Development bonus (get pieces off back rank)
        if piece.piece_type in ['knight', 'bishop']:
            if piece.color == 'white' and piece.row == 7:
                score += 2.0
            elif piece.color == 'black' and piece.row == 0:
                score += 2.0

        # ✅ Pawn advancement bonus
        if piece.piece_type == 'pawn':
            if piece.color == 'white':
                score += (6 - to_row) * 0.8
            else:
                score += (to_row - 1) * 0.8

        # ✅ King safety penalty (don't move king early)
        if piece.piece_type == 'king' and self.move_count < 10:
            score -= 5.0

        # Small random factor for variety
        score += random.random() * 0.3

        return score

    def _find_piece(self, piece_type, color):
        """Find a specific piece type"""
        for piece in self.pieces:
            if piece.piece_type == piece_type and piece.color == color and not piece.is_captured:
                return piece
        return None

    def _queen_synthesize(self, queen, proposals):
        """Queen synthesizes all proposals into best strategy (ENHANCED)"""
        # Choose proposal with highest score
        best_proposal = max(proposals, key=lambda p: p.get('score', 0))

        move_name = self.board.get_square_name(
            best_proposal['to'][0],
            best_proposal['to'][1]
        )

        # Queen announces decision occasionally
        if random.random() < 0.5:  # 50% chance
            self._add_chat_message(
                queen.id,
                f"👑 I choose: {best_proposal['piece'].piece_type} to {move_name}",
                'CONFIDENT'
            )

        print(f"👑 Queen chose: {best_proposal['piece'].piece_type} to {move_name}")

        return best_proposal

    def _select_smart_proposal(self, proposals):
        """Select best proposal when Queen is not available"""
        if not proposals:
            return None
        return max(proposals, key=lambda p: p.get('score', 0))

    def _king_validate(self, king, proposal):
        """King validates Queen's decision"""
        # Simple validation: approve most moves, occasionally deny risky ones
        risk = random.random()

        # Calculate actual risk based on move
        piece = proposal['piece']
        to_row, to_col = proposal['to']

        # High risk if moving into danger
        actual_risk = 0.1

        # Check if move puts piece in danger
        # (Simple check - could be enhanced)
        target = self.board.get_piece_at(to_row, to_col)
        if not target and piece.get_value() >= 5:  # Valuable piece
            actual_risk += 0.3

        if actual_risk > 0.7 and king.veto_count < config.KING_MAX_VETOES:
            # King denies
            king.veto_count += 1
            self._add_chat_message(
                king.id,
                f"❌ Too risky! Denied ({king.veto_count}/3)",
                'ANXIOUS'
            )
            print(f"👑 King DENIED (veto {king.veto_count}/3)")
            return False
        else:
            # King approves
            if random.random() < 0.3:  # 30% chance to announce
                self._add_chat_message(
                    king.id,
                    "✅ Approved. Execute!",
                    'CONFIDENT'
                )
            print(f"👑 King APPROVED")
            return True

    def _execute_proposal(self, proposal):
        """Execute the chosen move"""
        piece = proposal['piece']
        from_pos = proposal['from']
        to_pos = proposal['to']

        from_row, from_col = from_pos
        to_row, to_col = to_pos

        # Check for capture
        target = self.board.get_piece_at(to_row, to_col)
        is_capture = target is not None

        # Make the move
        success = self.board.move_piece(from_row, from_col, to_row, to_col)

        if success:
            piece.mark_moved()

            # ✅ Record move in history
            move_sig = f"{piece.id}:{to_pos}"
            self.move_history.append(move_sig)
            if len(self.move_history) > 50:
                self.move_history.pop(0)

            # ✅ Track last move for this piece
            self.last_moves_by_piece[piece.id] = {
                'from': from_pos,
                'to': to_pos
            }

            # ✅ Track position for repetition detection
            pos_hash = self._get_position_hash()
            self.position_history.append(pos_hash)

            # ✅ Increment move counter
            self.move_count += 1

            # Record move
            move_notation = f"{piece.get_symbol()}{self.board.get_square_name(to_row, to_col)}"
            if is_capture:
                move_notation = f"{piece.get_symbol()}x{self.board.get_square_name(to_row, to_col)}"

            self.last_move = {
                'from': from_pos,
                'to': to_pos,
                'piece': piece,
                'notation': move_notation,
                'capture': is_capture
            }

            print(f"✅ Move {self.move_count}: {move_notation}")

            # Celebration message
            if is_capture:
                piece.set_emotion('PROUD')
                if random.random() < 0.4:  # 40% chance
                    self._add_chat_message(
                        piece.id,
                        f"🎯 Captured {target.piece_type}!",
                        'PROUD'
                    )
            else:
                piece.set_emotion('CONFIDENT')

            # Switch turns
            self.game_state.switch_turn()
            print(f"➡️  Turn: {self.game_state.current_player}")

    def _get_position_hash(self):
        """Get simple hash of current position"""
        positions = []
        for piece in self.pieces:
            if not piece.is_captured:
                positions.append(f"{piece.id}:{piece.row},{piece.col}")
        return "|".join(sorted(positions))

    def handle_mouse_click(self, pos):
        """Handle mouse click for manual play"""
        if self.ai_mode:
            return  # Ignore clicks in AI mode

        # Convert pixel coordinates to board position
        board_pos = self._pixel_to_board(pos)

        if board_pos is None:
            self._deselect_piece()
            return

        row, col = board_pos

        if self.selected_piece:
            if (row, col) in self.legal_moves:
                self._move_piece_manual(row, col)
            else:
                self._try_select_piece(row, col)
        else:
            self._try_select_piece(row, col)

    def _pixel_to_board(self, pos):
        """Convert pixel coordinates to board (row, col)"""
        x, y = pos

        if (x < config.BOARD_OFFSET_X or
            x >= config.BOARD_OFFSET_X + config.BOARD_SIZE or
            y < config.BOARD_OFFSET_Y or
            y >= config.BOARD_OFFSET_Y + config.BOARD_SIZE):
            return None

        col = (x - config.BOARD_OFFSET_X) // config.SQUARE_SIZE
        row = (y - config.BOARD_OFFSET_Y) // config.SQUARE_SIZE

        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None

    def _try_select_piece(self, row, col):
        """Try to select a piece (manual mode)"""
        piece = self.board.get_piece_at(row, col)

        if piece and piece.color == self.game_state.current_player:
            self.selected_piece = piece
            self.selected_position = (row, col)
            self.legal_moves = piece.get_possible_moves(self.board)

            print(f"Selected: {piece.color} {piece.piece_type}")
        else:
            self._deselect_piece()

    def _deselect_piece(self):
        """Deselect piece"""
        self.selected_piece = None
        self.selected_position = None
        self.legal_moves = []

    def _move_piece_manual(self, to_row, to_col):
        """Move piece manually"""
        if not self.selected_piece:
            return

        from_row, from_col = self.selected_position
        piece = self.selected_piece

        target = self.board.get_piece_at(to_row, to_col)
        is_capture = target is not None

        success = self.board.move_piece(from_row, from_col, to_row, to_col)

        if success:
            piece.mark_moved()

            move_notation = f"{piece.get_symbol()}{self.board.get_square_name(to_row, to_col)}"
            if is_capture:
                move_notation = f"{piece.get_symbol()}x{self.board.get_square_name(to_row, to_col)}"

            self.last_move = {
                'from': (from_row, from_col),
                'to': (to_row, to_col),
                'piece': piece,
                'notation': move_notation,
                'capture': is_capture
            }

            print(f"Move: {move_notation}")

            if is_capture:
                piece.set_emotion('PROUD')

            self.game_state.switch_turn()
            self._deselect_piece()

    def _add_chat_message(self, sender, content, emotion='NEUTRAL'):
        """Add message to chat"""
        message = {
            'sender': sender,
            'content': content,
            'emotion': emotion,
            'recipients': ['ALL']
        }
        self.chat_history.append(message)

        if len(self.chat_history) > 50:
            self.chat_history = self.chat_history[-50:]

    def get_highlighted_squares(self):
        """Get squares to highlight"""
        highlights = {
            'selected': self.selected_position,
            'legal_moves': self.legal_moves,
            'last_move': self.last_move
        }
        return highlights

    def reset_game(self):
        """Reset game"""
        self.game_state = GameState()
        self.chat_history.clear()
        self.selected_piece = None
        self.selected_position = None
        self.legal_moves = []
        self.last_move = None
        self.ai_thinking = False
        self.ai_think_timer = 0

        # ✅ Reset new tracking variables
        self.move_history.clear()
        self.position_history.clear()
        self.last_moves_by_piece.clear()
        self.move_count = 0

        self._setup_pieces()
        self.position_history.append(self._get_position_hash())
        print("Game reset!")

    def cleanup(self):
        """Cleanup"""
        pass