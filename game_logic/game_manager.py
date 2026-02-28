"""
Game Manager with AI Movement System - FIXED VERSION
Key fixes:
1. Strong anti-repetition: tracks full position history (A→B→A = blocked)
2. Move scoring: penalizes returning to previous square
3. Variety injection: forces different piece types when repetition detected
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
        self.board = Board()
        self.game_state = GameState()
        self.pieces = []
        self.chat_history = []

        self.selected_piece = None
        self.selected_position = None
        self.legal_moves = []
        self.last_move = None

        # ✅ FIX: Enhanced repetition tracking
        self.recent_moves = []          # List of (piece_id, from_pos, to_pos) tuples
        self.position_hashes = []       # Full board position hashes
        self.piece_last_positions = {}  # piece_id -> list of recent positions

        self.ai_mode = True
        self.ai_thinking = False
        self.ai_think_timer = 0
        self.ai_think_delay = 2.0
        self.current_ai_decision = None
        self.move_count = 0

    def initialize_game(self):
        self._setup_pieces()
        pos_hash = self._get_position_hash()
        self.position_hashes.append(pos_hash)
        print("✅ Game initialized with all pieces")

    def _setup_pieces(self):
        self.pieces.clear()
        self.board.clear_board()

        for col in range(8):
            pawn = Pawn('white', 6, col)
            self.pieces.append(pawn)
            self.board.set_piece_at(6, col, pawn)

        back_rank_white = [
            Rook('white', 7, 0), Knight('white', 7, 1), Bishop('white', 7, 2),
            Queen('white', 7, 3), King('white', 7, 4),
            Bishop('white', 7, 5), Knight('white', 7, 6), Rook('white', 7, 7)
        ]
        for piece in back_rank_white:
            self.pieces.append(piece)
            self.board.set_piece_at(piece.row, piece.col, piece)

        for col in range(8):
            pawn = Pawn('black', 1, col)
            self.pieces.append(pawn)
            self.board.set_piece_at(1, col, pawn)

        back_rank_black = [
            Rook('black', 0, 0), Knight('black', 0, 1), Bishop('black', 0, 2),
            Queen('black', 0, 3), King('black', 0, 4),
            Bishop('black', 0, 5), Knight('black', 0, 6), Rook('black', 0, 7)
        ]
        for piece in back_rank_black:
            self.pieces.append(piece)
            self.board.set_piece_at(piece.row, piece.col, piece)

        print(f"Created {len(self.pieces)} pieces")

    def toggle_ai_mode(self):
        self.ai_mode = not self.ai_mode
        print(f"🤖 AI Mode: {'ON' if self.ai_mode else 'OFF'}")

    def update(self):
        if self.ai_mode and not self.ai_thinking:
            self.ai_think_timer += 1 / 60
            if self.ai_think_timer >= self.ai_think_delay:
                self.ai_think_timer = 0
                self._execute_ai_turn()

    def _execute_ai_turn(self):
        self.ai_thinking = True
        try:
            current_color = self.game_state.current_player

            # ✅ FIX: Check for 3-fold repetition - force new approach
            if self._is_threefold_repetition():
                print("⚠️  Repetition detected! Forcing varied play.")
                self._force_varied_move(current_color)
                return

            proposals = self._collect_piece_proposals(current_color)
            if not proposals:
                print(f"No legal moves for {current_color}!")
                return

            queen = self._find_piece('queen', current_color)
            if queen:
                chosen_proposal = self._queen_synthesize(queen, proposals)
            else:
                chosen_proposal = self._select_best_proposal(proposals)

            king = self._find_piece('king', current_color)
            if king:
                approved = self._king_validate(king, chosen_proposal)
                if not approved:
                    remaining = [p for p in proposals if p != chosen_proposal]
                    if remaining:
                        chosen_proposal = self._select_best_proposal(remaining)

            self._execute_proposal(chosen_proposal)

        except Exception as e:
            print(f"AI error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.ai_thinking = False

    def _is_threefold_repetition(self) -> bool:
        """
        ✅ FIX: Real threefold repetition detection.
        Returns True if the current position has appeared 3 times.
        """
        if len(self.position_hashes) < 5:
            return False
        current_hash = self._get_position_hash()
        count = self.position_hashes.count(current_hash)
        return count >= 3

    def _force_varied_move(self, color):
        """
        ✅ FIX: When repetition detected, pick ANY move that creates a new position.
        Prioritizes pieces that HAVEN'T moved recently.
        """
        pieces = [p for p in self.pieces if p.color == color and not p.is_captured]

        # Find pieces that haven't contributed to repetition
        recent_piece_ids = {move[0] for move in self.recent_moves[-6:]}
        fresh_pieces = [p for p in pieces if p.id not in recent_piece_ids]

        candidates = fresh_pieces if fresh_pieces else pieces
        random.shuffle(candidates)

        for piece in candidates:
            moves = piece.get_possible_moves(self.board)
            if moves:
                # Pick a move that leads to a NEW position
                for move in moves:
                    # Simulate: would this create a new position?
                    candidate_hash = self._simulate_position_hash(piece, move)
                    if candidate_hash not in self.position_hashes:
                        proposal = {
                            'piece': piece,
                            'from': (piece.row, piece.col),
                            'to': move,
                            'score': 1.0
                        }
                        self._execute_proposal(proposal)
                        self._add_chat_message(
                            piece.id,
                            "Trying a different approach!",
                            'CONFIDENT'
                        )
                        return

        # Absolute fallback: just make any legal move
        for piece in pieces:
            moves = piece.get_possible_moves(self.board)
            if moves:
                proposal = {
                    'piece': piece,
                    'from': (piece.row, piece.col),
                    'to': random.choice(moves),
                    'score': 0.0
                }
                self._execute_proposal(proposal)
                return

    def _simulate_position_hash(self, piece, move) -> str:
        """Quick hash simulation without actually moving"""
        positions = []
        for p in self.pieces:
            if p.is_captured:
                continue
            if p == piece:
                # Use the simulated new position
                positions.append(f"{p.id}:{move[0]},{move[1]}")
            else:
                positions.append(f"{p.id}:{p.row},{p.col}")
        return "|".join(sorted(positions))

    def _collect_piece_proposals(self, color):
        proposals = []
        pieces = [p for p in self.pieces if p.color == color and not p.is_captured]

        piece_priority = self._get_piece_priority()

        for piece_type in piece_priority:
            type_pieces = [p for p in pieces if p.piece_type == piece_type]

            for piece in type_pieces:
                legal_moves = piece.get_possible_moves(self.board)
                if not legal_moves:
                    continue

                # ✅ FIX: Strong repetition filter
                filtered_moves = self._filter_repetitive_moves_v2(piece, legal_moves)
                if not filtered_moves:
                    filtered_moves = legal_moves  # Fallback

                best_move = self._score_and_select_move(piece, filtered_moves)
                if best_move is None:
                    continue

                proposal = {
                    'piece': piece,
                    'from': (piece.row, piece.col),
                    'to': best_move,
                    'score': self._calculate_move_score(piece, best_move)
                }
                proposals.append(proposal)

                if random.random() < 0.2:
                    move_name = self.board.get_square_name(best_move[0], best_move[1])
                    self._add_chat_message(piece.id, f"I suggest moving to {move_name}", piece.current_emotion)

        return proposals

    def _filter_repetitive_moves_v2(self, piece, moves):
        """
        ✅ FIX: Stronger repetition filter.
        Blocks any move that would recreate a recently seen position.
        """
        if not self.recent_moves:
            return moves

        filtered = []
        for move in moves:
            candidate_hash = self._simulate_position_hash(piece, move)

            # Block if this position appeared in last 6 positions
            recent_hashes = self.position_hashes[-6:]
            if candidate_hash in recent_hashes:
                continue  # Skip - would cause repetition

            # Also block direct back-and-forth for this piece
            piece_history = self.piece_last_positions.get(piece.id, [])
            if move in piece_history[-2:]:  # Don't return to recent squares
                continue

            filtered.append(move)

        return filtered if filtered else moves

    def _get_piece_priority(self):
        if self.move_count < 10:
            return ['pawn', 'knight', 'bishop', 'queen', 'rook', 'king']
        elif self.move_count < 30:
            return ['knight', 'bishop', 'queen', 'pawn', 'rook', 'king']
        else:
            return ['queen', 'rook', 'king', 'knight', 'bishop', 'pawn']

    def _score_and_select_move(self, piece, moves):
        if not moves:
            return None

        scored = [(self._calculate_move_score(piece, m), m) for m in moves]
        scored.sort(reverse=True, key=lambda x: x[0])

        # Pick from top 3 with randomness to avoid deterministic loops
        top_moves = scored[:min(3, len(scored))]
        return random.choice(top_moves)[1]

    def _calculate_move_score(self, piece, move):
        score = 0.0
        to_row, to_col = move

        # Center control bonus
        center_distance = abs(to_row - 3.5) + abs(to_col - 3.5)
        score += (7 - center_distance) * 0.5

        # ✅ FIX: Heavy penalty for returning to a recently occupied square
        piece_history = self.piece_last_positions.get(piece.id, [])
        if move in piece_history:
            occurrences = piece_history.count(move)
            score -= occurrences * 5.0  # Strong deterrent

        # Capture bonus
        target = self.board.get_piece_at(to_row, to_col)
        if target and piece.is_enemy(target):
            score += target.get_value() * 3

        # Development bonus
        if piece.piece_type in ['knight', 'bishop']:
            if piece.color == 'white' and piece.row == 7:
                score += 2.0
            elif piece.color == 'black' and piece.row == 0:
                score += 2.0

        # Pawn advancement
        if piece.piece_type == 'pawn':
            if piece.color == 'white':
                score += (6 - to_row) * 0.8
            else:
                score += (to_row - 1) * 0.8

        # King safety in opening
        if piece.piece_type == 'king' and self.move_count < 10:
            score -= 5.0

        # ✅ FIX: Slightly larger random factor to break ties and avoid loops
        score += random.random() * 1.0

        return score

    def _find_piece(self, piece_type, color):
        for piece in self.pieces:
            if piece.piece_type == piece_type and piece.color == color and not piece.is_captured:
                return piece
        return None

    def _queen_synthesize(self, queen, proposals):
        best_proposal = max(proposals, key=lambda p: p.get('score', 0))
        move_name = self.board.get_square_name(best_proposal['to'][0], best_proposal['to'][1])
        if random.random() < 0.4:
            self._add_chat_message(queen.id, f"👑 I choose: {best_proposal['piece'].piece_type} to {move_name}", 'CONFIDENT')
        return best_proposal

    def _select_best_proposal(self, proposals):
        if not proposals:
            return None
        return max(proposals, key=lambda p: p.get('score', 0))

    def _king_validate(self, king, proposal):
        risk = 0.1
        if random.random() > 0.85 and king.veto_count < config.KING_MAX_VETOES:
            king.veto_count += 1
            self._add_chat_message(king.id, f"❌ I have doubts. Denied ({king.veto_count}/3)", 'ANXIOUS')
            return False
        if random.random() < 0.25:
            self._add_chat_message(king.id, "✅ Approved. Execute!", 'CONFIDENT')
        return True

    def _execute_proposal(self, proposal):
        piece = proposal['piece']
        from_pos = proposal['from']
        to_pos = proposal['to']
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        target = self.board.get_piece_at(to_row, to_col)
        is_capture = target is not None

        success = self.board.move_piece(from_row, from_col, to_row, to_col)
        if success:
            piece.mark_moved()

            # ✅ FIX: Record detailed move history
            self.recent_moves.append((piece.id, from_pos, to_pos))
            if len(self.recent_moves) > 20:
                self.recent_moves.pop(0)

            # ✅ FIX: Track per-piece position history
            if piece.id not in self.piece_last_positions:
                self.piece_last_positions[piece.id] = []
            self.piece_last_positions[piece.id].append(to_pos)
            if len(self.piece_last_positions[piece.id]) > 6:
                self.piece_last_positions[piece.id].pop(0)

            # ✅ FIX: Record full board position hash
            pos_hash = self._get_position_hash()
            self.position_hashes.append(pos_hash)
            if len(self.position_hashes) > 50:
                self.position_hashes.pop(0)

            self.move_count += 1

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

            if is_capture:
                piece.set_emotion('PROUD')
                if random.random() < 0.4:
                    self._add_chat_message(piece.id, f"🎯 Captured {target.piece_type}!", 'PROUD')
            else:
                piece.set_emotion('CONFIDENT')

            self.game_state.switch_turn()
            print(f"➡️  Turn: {self.game_state.current_player}")

    def _get_position_hash(self):
        positions = []
        for piece in self.pieces:
            if not piece.is_captured:
                positions.append(f"{piece.id}:{piece.row},{piece.col}")
        return "|".join(sorted(positions))

    def handle_mouse_click(self, pos):
        if self.ai_mode:
            return
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
        x, y = pos
        if (x < config.BOARD_OFFSET_X or x >= config.BOARD_OFFSET_X + config.BOARD_SIZE or
                y < config.BOARD_OFFSET_Y or y >= config.BOARD_OFFSET_Y + config.BOARD_SIZE):
            return None
        col = (x - config.BOARD_OFFSET_X) // config.SQUARE_SIZE
        row = (y - config.BOARD_OFFSET_Y) // config.SQUARE_SIZE
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None

    def _try_select_piece(self, row, col):
        piece = self.board.get_piece_at(row, col)
        if piece and piece.color == self.game_state.current_player:
            self.selected_piece = piece
            self.selected_position = (row, col)
            self.legal_moves = piece.get_possible_moves(self.board)
        else:
            self._deselect_piece()

    def _deselect_piece(self):
        self.selected_piece = None
        self.selected_position = None
        self.legal_moves = []

    def _move_piece_manual(self, to_row, to_col):
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
            if is_capture:
                piece.set_emotion('PROUD')
            self.game_state.switch_turn()
            self._deselect_piece()

    def _add_chat_message(self, sender, content, emotion='NEUTRAL'):
        message = {'sender': sender, 'content': content, 'emotion': emotion, 'recipients': ['ALL']}
        self.chat_history.append(message)
        if len(self.chat_history) > 50:
            self.chat_history = self.chat_history[-50:]

    def get_highlighted_squares(self):
        return {
            'selected': self.selected_position,
            'legal_moves': self.legal_moves,
            'last_move': self.last_move
        }

    def reset_game(self):
        self.game_state = GameState()
        self.chat_history.clear()
        self.selected_piece = None
        self.selected_position = None
        self.legal_moves = []
        self.last_move = None
        self.ai_thinking = False
        self.ai_think_timer = 0
        self.recent_moves.clear()
        self.position_hashes.clear()
        self.piece_last_positions.clear()
        self.move_count = 0
        self._setup_pieces()
        self.position_hashes.append(self._get_position_hash())
        print("Game reset!")

    def cleanup(self):
        pass